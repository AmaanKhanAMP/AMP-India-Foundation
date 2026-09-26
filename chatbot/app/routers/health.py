"""Health, readiness, and production metrics."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import get_settings
from app.schemas.chat import HealthResponse, StatusResponse
from app.services.analytics_service import snapshot as analytics_snapshot
from app.services.health_checks import run_health_checks
from app.services.memory_service import memory_service
from app.services.startup import get_warmup_status

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness — process is up. Deep checks live at /api/ready."""
    return HealthResponse(status="ok", service="aif-chatbot")


@router.get("/ready")
async def ready() -> JSONResponse:
    """Readiness: Pinecone, embeddings, CMS API, database."""
    report = run_health_checks()
    code = 200 if report.get("status") == "ok" else 200
    # Always 200 so load balancers that treat 503 as hard-down don't kill chat.
    # Chat remains available in degraded mode.
    return JSONResponse({**report, "success": True}, status_code=code)


@router.get("/metrics")
async def metrics() -> JSONResponse:
    return JSONResponse({"success": True, "metrics": analytics_snapshot()})


@router.get("/status", response_model=StatusResponse)
async def status() -> StatusResponse:
    settings = get_settings()
    memory_service.stats()
    warmup = get_warmup_status()
    return StatusResponse(
        service=settings.app_name,
        version=__version__,
        environment=settings.app_env,
        gemini_configured=settings.gemini_configured and warmup.gemini,
        pinecone_configured=settings.pinecone_configured and warmup.pinecone,
        rag_ready=settings.rag_ready and warmup.index,
        embedding_model=settings.gemini_embedding_model,
        chat_model=settings.gemini_chat_model,
    )
