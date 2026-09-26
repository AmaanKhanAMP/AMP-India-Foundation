"""FastAPI entrypoint for the AMP India Foundation AI chatbot."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import __version__
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.middleware.rate_limit import limiter
from app.routers import chat, health, ingest
from app.services.prompt_service import SAFE_ERROR_RESPONSE

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    Path(settings.documents_dir).mkdir(parents=True, exist_ok=True)
    logger.info(
        "startup",
        version=__version__,
        rag_ready=settings.rag_ready,
        env=settings.app_env,
    )
    try:
        from app.services.startup import warm_services

        warmup = await warm_services()
        logger.info(
            "warmup_complete",
            gemini=warmup.gemini,
            pinecone=warmup.pinecone,
            index=warmup.index,
            clients_warmed=warmup.clients_warmed,
            errors=warmup.errors,
        )
    except Exception as exc:
        logger.error("warmup_failed", error=str(type(exc).__name__))
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(ingest.router, prefix="/api")

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_request: Request, _exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Invalid request.",
                "response": "Please send a valid chat message.",
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception):
        logger.error("unhandled_error", error=str(type(exc).__name__))
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error.",
                "response": SAFE_ERROR_RESPONSE,
            },
        )

    return app


app = create_app()
