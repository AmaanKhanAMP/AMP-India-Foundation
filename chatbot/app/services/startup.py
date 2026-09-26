"""Warm Gemini / Pinecone / embedding clients on application startup."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WarmupStatus:
    gemini: bool = False
    pinecone: bool = False
    index: bool = False
    clients_warmed: bool = False
    errors: List[str] = field(default_factory=list)


_STATUS = WarmupStatus()


def get_warmup_status() -> WarmupStatus:
    return _STATUS


async def warm_services() -> WarmupStatus:
    """Initialize reusable clients and run a lightweight health check."""
    global _STATUS
    status = WarmupStatus()
    settings = get_settings()

    # 1) Gemini client
    try:
        if settings.gemini_configured:
            from app.services.gemini_client import get_gemini_client

            get_gemini_client()
            status.gemini = True
            print("✓ Gemini initialized")
            logger.info("warmup_gemini_ok", model=settings.gemini_chat_model)
        else:
            status.errors.append("gemini_not_configured")
            print("✗ Gemini not configured")
    except Exception as exc:
        status.errors.append(f"gemini:{type(exc).__name__}")
        print("✗ Gemini initialization failed")
        logger.error("warmup_gemini_failed", error=str(type(exc).__name__))

    # 2) Pinecone client + index
    try:
        if settings.pinecone_configured:
            from app.services.rag_service import get_index, get_pinecone_client

            get_pinecone_client()
            status.pinecone = True
            print("✓ Pinecone connected")
            logger.info("warmup_pinecone_ok")

            index = get_index()
            index.describe_index_stats()
            status.index = True
            print("✓ Index loaded")
            logger.info(
                "warmup_index_ok",
                index=settings.pinecone_index_name,
                namespace=settings.pinecone_namespace,
            )
        else:
            status.errors.append("pinecone_not_configured")
            print("✗ Pinecone not configured")
    except Exception as exc:
        status.errors.append(f"pinecone:{type(exc).__name__}")
        print("✗ Pinecone / index warmup failed")
        logger.error("warmup_pinecone_failed", error=str(type(exc).__name__))

    # 3) Warm FAQ cache + embedding client (+ optional retrieval ping)
    try:
        from app.services.embedding_service import get_embeddings
        from app.services.faq_cache import get_faq_cache

        get_faq_cache()
        embeddings = get_embeddings()

        if status.gemini:
            _ = embeddings.embed_query("AMP India Foundation")

        if status.gemini and status.index:
            from app.services.rag_service import rag_service

            await rag_service.retrieve("AMP contact phone")

        status.clients_warmed = True
        print("✓ Clients warmed")
        logger.info("warmup_clients_ok")
    except Exception as exc:
        status.errors.append(f"clients:{type(exc).__name__}")
        print("✗ Client warmup failed")
        logger.error(
            "warmup_clients_failed",
            error=str(type(exc).__name__),
            detail=str(exc)[:160],
        )

    _STATUS = status
    return status
