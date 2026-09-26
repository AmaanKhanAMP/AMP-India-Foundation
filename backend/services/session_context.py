"""In-memory per-session conversation context for rule-based follow-ups.

Stores:
  - last_intent
  - last_topic
  - last_entity
"""

from __future__ import annotations

import threading
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SessionContext:
    last_intent: str | None = None
    last_topic: str | None = None
    last_entity: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_lock = threading.Lock()
_STORE: dict[str, SessionContext] = {}

_NON_TOPIC_INTENTS = frozenset(
    {
        "greeting",
        "gratitude",
        "farewell",
        "acknowledgment",
        "help",
        "identity",
        "how_are_you",
        "general_knowledge",
        "out_of_scope",
        "unknown",
        "more",
    }
)

INTENT_TO_TOPIC: dict[str, str] = {
    "scholarship": "scholarship",
    "volunteer": "volunteer",
    "donation": "donation",
    "events": "events",
    "employment": "job_fair",
    "contact": "contact",
    "about": "about",
    "mission": "about",
    "vision": "about",
    "medical": "medical",
    "education": "education",
    "projects": "projects",
    "empowerment": "empowerment",
    "youth": "youth",
    "leadership": "leadership",
    "job_fair": "job_fair",
}


def get_context(session_id: str | None) -> SessionContext:
    if not session_id:
        return SessionContext()
    with _lock:
        ctx = _STORE.get(session_id)
        if ctx is None:
            return SessionContext()
        return SessionContext(
            last_intent=ctx.last_intent,
            last_topic=ctx.last_topic,
            last_entity=ctx.last_entity,
        )


def update_context(
    session_id: str | None,
    *,
    intent: str | None,
    topic: str | None = None,
    entity: str | None = None,
) -> SessionContext:
    """Update session memory after a successful topical turn."""
    if not session_id:
        return SessionContext()

    with _lock:
        ctx = _STORE.get(session_id) or SessionContext()
        previous_topic = ctx.last_topic

        if intent and intent not in _NON_TOPIC_INTENTS:
            ctx.last_intent = intent

        resolved_topic = topic or INTENT_TO_TOPIC.get(intent or "")
        if resolved_topic:
            ctx.last_topic = resolved_topic
            if previous_topic and previous_topic != resolved_topic and entity is None:
                # Topic switched — drop stale entity unless caller sets a new one
                ctx.last_entity = None

        if entity:
            ctx.last_entity = entity

        _STORE[session_id] = ctx
        return SessionContext(
            last_intent=ctx.last_intent,
            last_topic=ctx.last_topic,
            last_entity=ctx.last_entity,
        )


def clear_context(session_id: str | None) -> None:
    if not session_id:
        return
    with _lock:
        _STORE.pop(session_id, None)
