"""Lightweight production analytics — process-local counters + structured logs.

No external DB required. Exposed via /api/status enrichment and chat meta.
"""

from __future__ import annotations

import threading
import time
from collections import Counter
from typing import Any, Dict, Optional

_LOCK = threading.Lock()
_INTENT_COUNTS: Counter = Counter()
_SOURCE_COUNTS: Counter = Counter()
_FALLBACK_COUNTS: Counter = Counter()
_TOP_QUESTIONS: Counter = Counter()
_UNANSWERED: Counter = Counter()
_GEMINI_CALLS = 0
_PINECONE_CALLS = 0
_BUILTIN_CALLS = 0
_CACHE_SERVED = 0
_TOTAL_LATENCY_MS = 0.0
_REQUESTS = 0
_STARTED_AT = time.time()
_EXCEPTION_COUNTS: Counter = Counter()
_RETRIEVAL_ATTEMPTS = 0
_RETRIEVAL_HITS = 0
_PINECONE_LATENCY_MS = 0.0
_CMS_CALLS = 0
_CMS_LATENCY_MS = 0.0
_CMS_OK = 0


def record_chat(
    *,
    intent: str,
    response_source: str,
    fallback_level: str = "",
    question: str = "",
    latency_ms: float = 0.0,
    gemini_used: bool = False,
    pinecone_used: bool = False,
    builtin_used: bool = False,
    cache_hit: bool = False,
    unanswered: bool = False,
) -> None:
    global _GEMINI_CALLS, _PINECONE_CALLS, _BUILTIN_CALLS, _CACHE_SERVED
    global _TOTAL_LATENCY_MS, _REQUESTS
    with _LOCK:
        _REQUESTS += 1
        _TOTAL_LATENCY_MS += float(latency_ms or 0.0)
        _INTENT_COUNTS[intent or "unknown"] += 1
        _SOURCE_COUNTS[response_source or "unknown"] += 1
        if fallback_level:
            _FALLBACK_COUNTS[fallback_level] += 1
        q = (question or "").strip().lower()[:120]
        if q:
            _TOP_QUESTIONS[q] += 1
        if unanswered:
            _UNANSWERED[q or "(empty)"] += 1
        if gemini_used:
            _GEMINI_CALLS += 1
        if pinecone_used:
            _PINECONE_CALLS += 1
        if builtin_used:
            _BUILTIN_CALLS += 1
        if cache_hit:
            _CACHE_SERVED += 1


def record_exception(kind: str) -> None:
    with _LOCK:
        _EXCEPTION_COUNTS[kind or "unknown"] += 1


def record_retrieval(*, hit: bool, pinecone_ms: float = 0.0) -> None:
    global _RETRIEVAL_ATTEMPTS, _RETRIEVAL_HITS, _PINECONE_LATENCY_MS
    with _LOCK:
        _RETRIEVAL_ATTEMPTS += 1
        if hit:
            _RETRIEVAL_HITS += 1
        _PINECONE_LATENCY_MS += float(pinecone_ms or 0.0)


def record_cms_probe(*, ok: bool, latency_ms: float = 0.0) -> None:
    global _CMS_CALLS, _CMS_OK, _CMS_LATENCY_MS
    with _LOCK:
        _CMS_CALLS += 1
        _CMS_LATENCY_MS += float(latency_ms or 0.0)
        if ok:
            _CMS_OK += 1


def snapshot() -> Dict[str, Any]:
    with _LOCK:
        req = max(_REQUESTS, 1)
        retrievals = max(_RETRIEVAL_ATTEMPTS, 1)
        cms_n = max(_CMS_CALLS, 1)
        pine_n = max(_PINECONE_CALLS, 1)
        return {
            "uptime_seconds": round(time.time() - _STARTED_AT, 1),
            "requests": _REQUESTS,
            "avg_latency_ms": round(_TOTAL_LATENCY_MS / req, 2),
            "gemini_calls": _GEMINI_CALLS,
            "pinecone_calls": _PINECONE_CALLS,
            "builtin_calls": _BUILTIN_CALLS,
            "cache_served": _CACHE_SERVED,
            "gemini_rate": round(_GEMINI_CALLS / req, 4),
            "retrieval_attempts": _RETRIEVAL_ATTEMPTS,
            "retrieval_hits": _RETRIEVAL_HITS,
            "retrieval_success_rate": round(_RETRIEVAL_HITS / retrievals, 4),
            "pinecone_avg_latency_ms": round(_PINECONE_LATENCY_MS / pine_n, 2),
            "cms_probes": _CMS_CALLS,
            "cms_ok": _CMS_OK,
            "cms_avg_latency_ms": round(_CMS_LATENCY_MS / cms_n, 2),
            "exception_count": sum(_EXCEPTION_COUNTS.values()),
            "exceptions_by_kind": dict(_EXCEPTION_COUNTS.most_common(20)),
            "fallback_frequency": dict(_FALLBACK_COUNTS.most_common(10)),
            "intent_distribution": dict(_INTENT_COUNTS.most_common(20)),
            "response_sources": dict(_SOURCE_COUNTS.most_common(15)),
            "fallback_usage": dict(_FALLBACK_COUNTS.most_common(10)),
            "top_questions": [
                {"q": q, "n": n} for q, n in _TOP_QUESTIONS.most_common(15)
            ],
            "unanswered": [
                {"q": q, "n": n} for q, n in _UNANSWERED.most_common(15)
            ],
        }


def confidence_for_source(response_source: str) -> float:
    """Internal confidence score per brief."""
    src = (response_source or "").upper()
    if src in {"BUILTIN_KNOWLEDGE", "CACHE"}:
        return 1.0
    if src in {"CMS", "PINECONE_ONLY"} and "CMS" in src:
        return 0.95
    if src == "PINECONE_ONLY":
        return 0.90
    if src in {"PINECONE+GEMINI", "GEMINI"}:
        return 0.70
    if src in {"LOCAL_KNOWLEDGE", "EMERGENCY_KNOWLEDGE"}:
        return 0.92
    if src in {"FINAL_APOLOGY", "NO_RESULT", "DOMAIN_ONLY"}:
        return 0.0
    return 0.75
