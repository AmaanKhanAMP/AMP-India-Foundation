"""Input validation, prompt-injection guards, and legacy classification helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.core.config import get_settings
from app.services.intent_router import Intent, detect_injection, normalize, route_intent
from app.services.prompt_service import GENERAL_KNOWLEDGE_FALLBACK, OUT_OF_SCOPE_RESPONSE, t

# Re-export for existing imports / tests
__all__ = [
    "QueryCategory",
    "Classification",
    "sanitize_message",
    "detect_injection",
    "classify_query",
    "normalize",
]


class QueryCategory(str, Enum):
    """Legacy coarse categories mapped from Intent."""

    GREETING = "greeting"
    SMALL_TALK = "small_talk"
    AMP_KNOWLEDGE = "amp_knowledge"
    GENERAL_KNOWLEDGE = "general_knowledge"
    OUT_OF_SCOPE = "out_of_scope"
    INJECTION = "injection"


@dataclass
class Classification:
    category: QueryCategory
    confidence: float
    reason: str = ""
    safe_message: Optional[str] = None


_INTENT_TO_CATEGORY = {
    Intent.GREETING: QueryCategory.GREETING,
    Intent.SMALL_TALK: QueryCategory.SMALL_TALK,
    Intent.GOODBYE: QueryCategory.SMALL_TALK,
    Intent.GENERAL_KNOWLEDGE: QueryCategory.GENERAL_KNOWLEDGE,
    Intent.CLARIFICATION_NEEDED: QueryCategory.GENERAL_KNOWLEDGE,
    Intent.SECURITY_REQUEST: QueryCategory.INJECTION,
    Intent.CONTACT: QueryCategory.AMP_KNOWLEDGE,
    Intent.DONATIONS: QueryCategory.AMP_KNOWLEDGE,
    Intent.SCHOLARSHIPS: QueryCategory.AMP_KNOWLEDGE,
    Intent.EVENTS: QueryCategory.AMP_KNOWLEDGE,
    Intent.PROJECTS: QueryCategory.AMP_KNOWLEDGE,
    Intent.EDUCATION: QueryCategory.AMP_KNOWLEDGE,
    Intent.ECONOMIC_EMPOWERMENT: QueryCategory.AMP_KNOWLEDGE,
    Intent.FORM_CLARIFY: QueryCategory.AMP_KNOWLEDGE,
    Intent.GIBBERISH: QueryCategory.OUT_OF_SCOPE,
    Intent.LOCATION_STATEMENT: QueryCategory.SMALL_TALK,
    Intent.LINK_CLARIFY: QueryCategory.AMP_KNOWLEDGE,
    Intent.CASUAL_CHAT: QueryCategory.SMALL_TALK,
    Intent.ASSISTANT_IDENTITY: QueryCategory.SMALL_TALK,
    Intent.VOLUNTEERING: QueryCategory.AMP_KNOWLEDGE,
    Intent.EMPLOYMENT: QueryCategory.AMP_KNOWLEDGE,
    Intent.MEDICAL: QueryCategory.AMP_KNOWLEDGE,
    Intent.MENTORSHIP: QueryCategory.AMP_KNOWLEDGE,
    Intent.TRAINING: QueryCategory.AMP_KNOWLEDGE,
    Intent.AMP_KNOWLEDGE: QueryCategory.AMP_KNOWLEDGE,
    Intent.INJECTION: QueryCategory.INJECTION,
    Intent.OUT_OF_SCOPE: QueryCategory.OUT_OF_SCOPE,
}


def sanitize_message(message: str) -> str:
    """Strip control chars and enforce max length."""
    settings = get_settings()
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", message or "")
    cleaned = cleaned.strip()
    if len(cleaned) > settings.max_message_length:
        cleaned = cleaned[: settings.max_message_length]
    return cleaned


_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_?\s-]?key|pinecone|gemini|openai)\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{8,}"),
    re.compile(r"(?i)\b(AIza|sk-|pcsk_|AQ\.)[A-Za-z0-9_\-]{10,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9\-_\.]{10,}"),
)


def scrub_secrets(text: str) -> str:
    """Redact accidental secret leakage from model output before returning to clients."""
    cleaned = text or ""
    for pattern in _SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    return cleaned


def classify_query(message: str, has_session_topic: bool = False) -> Classification:
    """Backward-compatible wrapper around the intent router."""
    route = route_intent(message, has_session_topic=has_session_topic)
    category = _INTENT_TO_CATEGORY.get(route.intent, QueryCategory.GENERAL_KNOWLEDGE)
    safe = route.canned_response
    if route.intent == Intent.GENERAL_KNOWLEDGE and not safe:
        safe = t(GENERAL_KNOWLEDGE_FALLBACK)
    if route.intent == Intent.OUT_OF_SCOPE and not safe:
        safe = t(OUT_OF_SCOPE_RESPONSE) if isinstance(OUT_OF_SCOPE_RESPONSE, dict) else OUT_OF_SCOPE_RESPONSE
    if isinstance(safe, dict):
        safe = t(safe)
    return Classification(
        category=category,
        confidence=route.confidence,
        reason=route.reason or route.intent.value,
        safe_message=safe,
    )
