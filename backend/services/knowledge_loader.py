"""In-memory knowledge-base loader for the chatbot.

JSON files under ``backend/knowledge/`` are read once and cached for the
process lifetime so every chat request avoids disk I/O.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# backend/knowledge relative to this file: services/ -> backend/
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

# Canonical file set (volunteer included for quick-action support)
KNOWLEDGE_FILES = (
    "about.json",
    "scholarships.json",
    "events.json",
    "projects.json",
    "donation.json",
    "contact.json",
    "faq.json",
    "navigation.json",
    "volunteer.json",
)

_lock = threading.Lock()
_cache: dict[str, Any] | None = None


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Knowledge file must be a JSON object: {path.name}")
    return data


def load_knowledge(force_reload: bool = False) -> dict[str, Any]:
    """Return the full knowledge map keyed by document id (e.g. ``events``)."""
    global _cache

    if _cache is not None and not force_reload:
        return _cache

    with _lock:
        if _cache is not None and not force_reload:
            return _cache

        loaded: dict[str, Any] = {}
        for filename in KNOWLEDGE_FILES:
            path = KNOWLEDGE_DIR / filename
            if not path.is_file():
                logger.warning("Knowledge file missing: %s", path)
                continue
            try:
                doc = _read_json(path)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                logger.error("Failed to load %s: %s", filename, exc)
                continue

            doc_id = str(doc.get("id") or path.stem)
            loaded[doc_id] = doc

        _cache = loaded
        logger.info("Knowledge base loaded (%d documents).", len(loaded))
        return _cache


def get_document(doc_id: str) -> dict[str, Any] | None:
    """Fetch a single knowledge document by id."""
    return load_knowledge().get(doc_id)


def list_document_ids() -> list[str]:
    return list(load_knowledge().keys())


def clear_cache() -> None:
    """Test helper — drop the in-memory cache."""
    global _cache
    with _lock:
        _cache = None
