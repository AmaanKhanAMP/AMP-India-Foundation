"""Admin ingest endpoints — reindex knowledge / CMS incremental sync / upload."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.chat import IngestResponse
from app.services.document_service import (
    SUPPORTED_EXTENSIONS,
    ingest_documents_dir,
    ingest_file,
    ingest_knowledge_dir,
    ingest_sources_batch,
    ingest_text,
)
from app.services.contact_facts import write_live_facts

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger(__name__)


class SourcePayload(BaseModel):
    source: str = Field(..., min_length=1, max_length=128)
    text: str = Field(default="")
    category: Optional[str] = Field(default=None, max_length=128)


class CmsSyncRequest(BaseModel):
    reason: Optional[str] = None
    sources: List[SourcePayload] = Field(default_factory=list)
    delete_missing_cms: bool = False
    cms_source_prefix: str = "cms_"
    delete_sources: List[str] = Field(default_factory=list)
    extra_delete_prefixes: List[str] = Field(default_factory=list)
    live_facts: Optional[Dict[str, Any]] = None
    force: bool = False


class SourceIngestRequest(BaseModel):
    source: str = Field(..., min_length=1, max_length=128)
    text: str = Field(default="")
    category: Optional[str] = None
    skip_unchanged: bool = True


def _authorize(token: str | None) -> None:
    settings = get_settings()
    expected = (settings.admin_ingest_token or "").strip()
    if not expected or expected == "change-me":
        raise HTTPException(status_code=503, detail="Ingest token is not configured.")
    if not token or token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized.")


@router.post("/ingest/knowledge", response_model=IngestResponse)
async def ingest_knowledge(x_admin_token: str | None = Header(default=None)) -> IngestResponse:
    _authorize(x_admin_token)
    result = ingest_knowledge_dir()
    return IngestResponse(
        success=True,
        indexed=result["indexed"],
        message=result["message"],
        sources=result["sources"],
    )


@router.post("/ingest/documents", response_model=IngestResponse)
async def ingest_documents(x_admin_token: str | None = Header(default=None)) -> IngestResponse:
    _authorize(x_admin_token)
    result = ingest_documents_dir()
    return IngestResponse(
        success=True,
        indexed=result["indexed"],
        message=result["message"],
        sources=result["sources"],
    )


@router.post("/ingest/source", response_model=IngestResponse)
async def ingest_single_source(
    body: SourceIngestRequest,
    x_admin_token: str | None = Header(default=None),
) -> IngestResponse:
    """Incremental upsert for one named knowledge source (CMS / API)."""
    _authorize(x_admin_token)
    count, source, status = ingest_text(
        body.source,
        body.text,
        category=body.category,
        skip_unchanged=body.skip_unchanged,
    )
    return IngestResponse(
        success=True,
        indexed=count,
        message=f"Source {source}: {status} ({count} chunks).",
        sources=[source] if source else [],
    )


@router.post("/ingest/cms-sync", response_model=IngestResponse)
async def cms_sync(
    body: CmsSyncRequest = CmsSyncRequest(),
    x_admin_token: str | None = Header(default=None),
) -> IngestResponse:
    """
    CMS / knowledge sync.

    With a JSON body of sources → incremental per-source upsert (preferred).
    Without a body → full re-index of knowledge/ + documents/ directories.
    """
    _authorize(x_admin_token)

    if body.sources:
        payload: List[Dict[str, Any]] = [
            {
                "source": s.source,
                "text": s.text,
                "category": s.category or s.source,
            }
            for s in body.sources
        ]
        result = ingest_sources_batch(
            payload,
            skip_unchanged=not body.force,
            delete_missing_prefix=body.cms_source_prefix if body.delete_missing_cms else None,
            delete_sources=body.delete_sources,
            extra_delete_prefixes=body.extra_delete_prefixes,
        )
        if body.live_facts:
            write_live_facts(body.live_facts)
        logger.info(
            "cms_sync_incremental",
            reason=body.reason,
            indexed=result["indexed"],
            sources=result["sources"],
            deleted=result.get("deleted", 0),
        )
        return IngestResponse(
            success=True,
            indexed=result["indexed"],
            deleted=result.get("deleted", 0),
            message=result["message"],
            sources=result["sources"],
        )

    # Fallback: full directory reindex (manual / empty body)
    knowledge = ingest_knowledge_dir()
    documents = ingest_documents_dir()
    indexed = knowledge["indexed"] + documents["indexed"]
    sources = list(dict.fromkeys(knowledge["sources"] + documents["sources"]))
    return IngestResponse(
        success=True,
        indexed=indexed,
        message=f"Full sync complete. Indexed {indexed} chunks.",
        sources=sources,
    )


@router.post("/ingest/upload", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    x_admin_token: str | None = Header(default=None),
) -> IngestResponse:
    _authorize(x_admin_token)
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    dest_dir = Path(settings.documents_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / Path(file.filename or "upload.txt").name

    max_bytes = settings.max_upload_mb * 1024 * 1024
    size = 0
    with dest.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                handle.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail="File too large.")
            handle.write(chunk)

    try:
        count, source, status = ingest_file(dest, skip_unchanged=False)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to index document.") from None

    return IngestResponse(
        success=True,
        indexed=count,
        message=f"Indexed {count} chunks from {source} ({status}).",
        sources=[source],
    )
