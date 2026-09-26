"""Chat endpoints (JSON + SSE streaming)."""

from __future__ import annotations

import json
from typing import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.logging import get_logger
from app.core.config import get_settings
from app.middleware.rate_limit import limiter
from app.schemas.chat import ChatRequest, ChatResponse, ErrorResponse
from app.services.ai_service import ai_service
from app.services.memory_service import memory_service
from app.services.prompt_service import SAFE_ERROR_RESPONSE
from app.services.security_service import sanitize_message

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=ChatResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
@limiter.limit("30/minute")
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    """Non-streaming chat — compatible with the existing widget contract."""
    settings = get_settings()
    message = sanitize_message(body.message)
    if len(message) > settings.max_message_length:
        return ChatResponse(
            success=False,
            response="Your message is too long. Please shorten it and try again.",
            session_id=body.session_id or "unknown",
            intent="error",
        )

    try:
        result = await ai_service.chat(
            message=message,
            session_id=body.session_id,
            page=body.page,
        )
        return ChatResponse(**result)
    except Exception:
        logger.exception("chat_json_failed")
        return ChatResponse(
            success=True,
            response=SAFE_ERROR_RESPONSE,
            session_id=body.session_id or "unknown",
            intent="error",
            meta={"pipeline": "router_recovery", "response_source": "ALL_SOURCES_FAILED"},
        )


@router.post("/stream")
@limiter.limit("30/minute")
async def chat_stream(request: Request, body: ChatRequest) -> StreamingResponse:
    """SSE streaming chat — tokens delivered progressively."""
    settings = get_settings()
    message = sanitize_message(body.message)
    session_id = memory_service.ensure_session(body.session_id)

    async def event_generator() -> AsyncIterator[str]:
        try:
            sid_payload = json.dumps({"session_id": session_id})
            yield f"event: meta\ndata: {sid_payload}\n\n"

            if len(message) > settings.max_message_length:
                payload = json.dumps(
                    {"token": "Your message is too long. Please shorten it and try again."}
                )
                yield f"event: token\ndata: {payload}\n\n"
                yield "event: done\ndata: {}\n\n"
                return

            async for token in ai_service.stream_chat(
                message=message,
                session_id=session_id,
                page=body.page,
            ):
                payload = json.dumps({"token": token})
                yield f"event: token\ndata: {payload}\n\n"

            yield "event: done\ndata: {}\n\n"
        except Exception:
            logger.exception("chat_stream_failed")
            payload = json.dumps({"token": SAFE_ERROR_RESPONSE})
            yield f"event: token\ndata: {payload}\n\n"
            yield "event: error\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
