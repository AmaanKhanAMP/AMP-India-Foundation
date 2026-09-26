"""Live dependency probes — Pinecone, CMS/API, database, embeddings."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.analytics_service import record_cms_probe, record_exception

logger = get_logger(__name__)


def _probe(name: str, fn) -> Dict[str, Any]:
    t0 = time.perf_counter()
    try:
        extra = fn() or {}
        ms = round((time.perf_counter() - t0) * 1000, 1)
        return {"name": name, "ok": True, "latency_ms": ms, **extra}
    except Exception as exc:
        ms = round((time.perf_counter() - t0) * 1000, 1)
        record_exception(f"health_{name}")
        logger.error("health_probe_failed", probe=name, error=type(exc).__name__)
        return {"name": name, "ok": False, "latency_ms": ms, "error": type(exc).__name__}


def _pinecone() -> Dict[str, Any]:
    settings = get_settings()
    if not settings.pinecone_configured:
        raise RuntimeError("not_configured")
    from app.services.rag_service import get_index

    stats = get_index().describe_index_stats()
    total = getattr(stats, "total_vector_count", None)
    if total is None and isinstance(stats, dict):
        total = stats.get("total_vector_count")
    return {"vectors": int(total or 0), "index": settings.pinecone_index_name}


def _embeddings() -> Dict[str, Any]:
    settings = get_settings()
    if not settings.gemini_configured:
        raise RuntimeError("not_configured")
    from app.services.embedding_service import get_embeddings

    get_embeddings()
    return {"model": settings.gemini_embedding_model, "configured": True}


def _cms_and_database() -> Dict[str, Any]:
    settings = get_settings()
    base = (settings.cms_api_url or "http://127.0.0.1:5000").rstrip("/")
    url = f"{base}/api/health"
    t0 = time.perf_counter()
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "aif-chatbot-health/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            code = getattr(resp, "status", 200)
    except urllib.error.HTTPError as exc:
        code = exc.code
        raw = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
    except Exception:
        ms = round((time.perf_counter() - t0) * 1000, 1)
        record_cms_probe(ok=False, latency_ms=ms)
        raise
    ms = round((time.perf_counter() - t0) * 1000, 1)
    payload: Dict[str, Any] = {}
    try:
        parsed = json.loads(raw) if raw else {}
        if isinstance(parsed, dict):
            payload = parsed
    except ValueError:
        payload = {}
    db_ok = str(payload.get("database") or "").lower() in {"connected", "ok", "up"}
    cms_ok = code == 200 and str(payload.get("status") or "").lower() in {"success", "ok", "healthy"}
    record_cms_probe(ok=cms_ok, latency_ms=ms)
    if not cms_ok:
        raise RuntimeError("cms_unavailable")
    return {
        "cms_ok": True,
        "database_ok": db_ok,
        "cms_latency_ms": ms,
    }


def run_health_checks() -> Dict[str, Any]:
    pine = _probe("pinecone", _pinecone)
    embed = _probe("embeddings", _embeddings)
    cms = _probe("cms_api", _cms_and_database)
    database = {
        "name": "database",
        "ok": bool(cms.get("ok") and cms.get("database_ok")),
        "latency_ms": cms.get("latency_ms", 0),
    }
    if not cms.get("ok"):
        database["ok"] = False
        database["error"] = cms.get("error") or "cms_unreachable"
    checks = [pine, embed, cms, database]
    all_ok = all(c.get("ok") for c in checks)
    return {
        "status": "ok" if all_ok else "degraded",
        "checks": {c["name"]: c for c in checks},
        "chat_available": True,
    }
