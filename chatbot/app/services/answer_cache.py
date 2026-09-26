"""In-process answer cache for static AMP questions — zero Gemini/Pinecone cost.

Cache key: language + normalized question (+ optional intent).
TTL-based; cleared on knowledge ingest via clear_answer_cache().
"""

from __future__ import annotations

import hashlib
import threading
import time
from typing import Any, Dict, Optional, Tuple

_LOCK = threading.Lock()
_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_TTL_SECONDS = 3600  # 1 hour for static facts
_MAX_ENTRIES = 512

# Stats for analytics
_HITS = 0
_MISSES = 0


def _key(language: str, normalized_question: str, intent: str = "") -> str:
    raw = f"{(language or 'en').lower()}|{(intent or '').lower()}|{(normalized_question or '').strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_cached_answer(
    *,
    language: str,
    normalized_question: str,
    intent: str = "",
) -> Optional[Dict[str, Any]]:
    global _HITS, _MISSES
    k = _key(language, normalized_question, intent)
    with _LOCK:
        item = _CACHE.get(k)
        if not item:
            _MISSES += 1
            return None
        expires, payload = item
        if time.time() > expires:
            _CACHE.pop(k, None)
            _MISSES += 1
            return None
        _HITS += 1
        return dict(payload)


def set_cached_answer(
    *,
    language: str,
    normalized_question: str,
    intent: str,
    response: str,
    confidence: float,
    response_source: str,
) -> None:
    if not (response or "").strip():
        return
    k = _key(language, normalized_question, intent)
    payload = {
        "response": response,
        "confidence": confidence,
        "response_source": response_source,
        "intent": intent,
    }
    with _LOCK:
        if len(_CACHE) >= _MAX_ENTRIES:
            # Drop oldest ~25%
            for old in list(_CACHE.keys())[: max(1, _MAX_ENTRIES // 4)]:
                _CACHE.pop(old, None)
        _CACHE[k] = (time.time() + _TTL_SECONDS, payload)


def clear_answer_cache() -> None:
    with _LOCK:
        _CACHE.clear()


def cache_stats() -> Dict[str, Any]:
    with _LOCK:
        total = _HITS + _MISSES
        return {
            "hits": _HITS,
            "misses": _MISSES,
            "hit_rate": round(_HITS / total, 4) if total else 0.0,
            "size": len(_CACHE),
            "ttl_seconds": _TTL_SECONDS,
        }
