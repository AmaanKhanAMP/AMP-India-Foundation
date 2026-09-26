"""Chat orchestration for Phase 2 (knowledge-based, no LLM).

Pipeline:
  normalize → detect intent → search knowledge → build response → persist

Phase 3 can replace ``build_response`` / ``generate_reply`` with an LLM
while keeping ``process_message`` and the API contract unchanged.
"""

from __future__ import annotations

import logging
import re
import uuid
from difflib import SequenceMatcher
from typing import Any

from extensions import db
from models.chat_message import ChatMessage
from services.intent_detector import (
    CONVERSATIONAL_INTENTS,
    INTENT_TO_DOC,
    detect_intent,
    normalize_text,
    tokenize,
)
from services.knowledge_loader import get_document, load_knowledge
from services.module_faqs import (
    IDENTITY_RESPONSE,
    LEADERSHIP_NOT_FOUND,
    detect_entity,
    is_followup_question,
    is_leadership_question,
    search_module_faq,
    topic_fallback,
)
from services.query_classifier import (
    QueryCategory,
    category_response,
    classify_query,
)
from services.session_context import (
    INTENT_TO_TOPIC,
    get_context,
    update_context,
)

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I couldn't find that information yet. Please contact AMP India Foundation "
    "or ask another question."
)

# Trailing page-link lines we never want to spam across replies
_LINK_LINE_RE = re.compile(
    r"(?im)^(?:more details|learn more|see all events|explore projects|"
    r"volunteer page|more info)\s*:\s*\S+\s*$"
)
_PATH_RE = re.compile(
    r"(?i)/(?:support-us|about|events|projects(?:/[a-z0-9-]+)?|volunteer|contact)\b"
)

CONNECTION_ERROR_RESPONSE = (
    "I'm having trouble connecting right now. Please try again in a moment."
)

MIN_CONFIDENCE = 0.55

QUICK_ACTIONS_PRIMARY = [
    {
        "id": "scholarship",
        "label": "Scholarships",
        "icon": "🎓",
        "text": "Tell me about Scholarship Programs",
        "intent": "scholarship",
    },
    {
        "id": "events",
        "label": "Events",
        "icon": "📅",
        "text": "What upcoming events do you have?",
        "intent": "events",
    },
    {
        "id": "donate",
        "label": "Donate",
        "icon": "❤️",
        "text": "How can I donate to AMP India Foundation?",
        "intent": "donation",
    },
]

QUICK_ACTIONS_MORE = [
    {
        "id": "volunteer",
        "label": "Volunteer",
        "icon": "🤝",
        "text": "How can I become a volunteer?",
        "intent": "volunteer",
    },
    {
        "id": "medical",
        "label": "Medical",
        "icon": "🏥",
        "text": "Tell me about Medical Projects",
        "intent": "medical",
    },
    {
        "id": "contact",
        "label": "Contact",
        "icon": "📞",
        "text": "How can I contact AMP India Foundation?",
        "intent": "contact",
    },
]


def get_quick_actions() -> dict[str, Any]:
    """Return primary + more quick actions for GET /api/chat/quick-actions."""
    return {
        "primary": QUICK_ACTIONS_PRIMARY,
        "more": QUICK_ACTIONS_MORE,
        "all": QUICK_ACTIONS_PRIMARY + QUICK_ACTIONS_MORE,
    }


def ensure_session_id(session_id: str | None) -> str:
    if session_id and isinstance(session_id, str) and session_id.strip():
        return session_id.strip()[:128]
    return str(uuid.uuid4())


def process_message(
    message: str,
    session_id: str | None = None,
    page: str | None = None,
) -> dict[str, Any]:
    """Main entry: answer a user message from the knowledge base.

    Returns a dict matching the Phase 2/3 API contract:
    ``success``, ``intent``, ``confidence``, ``response``, ``session_id``.
    """
    session = ensure_session_id(session_id)
    normalized = normalize_text(message)
    ctx = get_context(session)

    if not normalized:
        result = {
            "success": True,
            "intent": "unknown",
            "confidence": 0.0,
            "response": (
                "Please type a question about scholarships, events, donations, "
                "projects, volunteering, or contact details."
            ),
            "session_id": session,
            "meta": {"context": ctx.to_dict()},
        }
        _persist(session, message or "", result["response"], result["intent"], page)
        return result

    # ------------------------------------------------------------------
    # 1) Query classification (BEFORE intent detection / knowledge / RAG)
    # ------------------------------------------------------------------
    classification = classify_query(message, context=ctx)
    category = classification.category
    meta: dict[str, Any] = {
        "category": category.value,
        "classification_reason": classification.reason,
        **(classification.meta or {}),
        "context_before": ctx.to_dict(),
    }

    # Non-AMP categories: never touch the knowledge base / vector search
    if category != QueryCategory.AMP_KNOWLEDGE:
        intent, confidence, response = _handle_non_amp_category(
            category, classification, normalized
        )
        meta["intent"] = intent
        response = _sanitize_response_links(
            str(response).strip(),
            intent=intent,
            session_id=session,
        )
        result = {
            "success": True,
            "intent": intent,
            "confidence": float(confidence),
            "response": response,
            "session_id": session,
            "meta": {**meta, "context": get_context(session).to_dict()},
        }
        _persist(session, message, result["response"], intent, page)
        return result

    # ------------------------------------------------------------------
    # 2) AMP knowledge path — leadership, module FAQ follow-ups, then KB
    # ------------------------------------------------------------------
    knowledge = load_knowledge()
    followup = bool(classification.meta.get("followup"))
    active_topic = classification.meta.get("inherit_topic") or ctx.last_topic
    active_entity = classification.meta.get("inherit_entity") or ctx.last_entity
    active_intent = classification.meta.get("inherit_intent") or ctx.last_intent

    # Leadership / founder / chairman questions
    if is_leadership_question(normalized) or classification.meta.get("intent_hint") == "leadership":
        intent, confidence, response = (
            "leadership",
            0.9,
            LEADERSHIP_NOT_FOUND,
        )
        meta["source"] = "leadership"
        update_context(session, intent=intent, topic="leadership")
        response = _sanitize_response_links(response, intent=intent, session_id=session)
        result = {
            "success": True,
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "session_id": session,
            "meta": {**meta, "context": get_context(session).to_dict()},
        }
        _persist(session, message, result["response"], intent, page)
        return result

    # Context-aware module FAQ (short follow-ups — do NOT dump full module text)
    if followup or (active_topic and is_followup_question(message)):
        faq_hit = search_module_faq(normalized, active_topic, active_entity)
        if faq_hit:
            intent = active_intent or INTENT_TO_TOPIC.get(active_topic or "", active_topic) or "faq"
            # Prefer topic-aligned intent for memory
            topic_intent = {
                "scholarship": "scholarship",
                "volunteer": "volunteer",
                "donation": "donation",
                "events": "events",
                "job_fair": "employment",
            }.get(faq_hit["topic"], intent)
            confidence = faq_hit["confidence"]
            response = faq_hit["answer"]
            meta["source"] = "module_faq"
            meta["faq_topic"] = faq_hit["topic"]
            update_context(
                session,
                intent=topic_intent,
                topic=faq_hit["topic"],
                entity=active_entity,
            )
            result = {
                "success": True,
                "intent": topic_intent,
                "confidence": float(confidence),
                "response": response,
                "session_id": session,
                "meta": {**meta, "context": get_context(session).to_dict()},
            }
            _persist(session, message, result["response"], topic_intent, page)
            return result

        # Follow-up with topic but no FAQ match — topic-specific short fallback
        if active_topic and (followup or is_followup_question(message)):
            response = topic_fallback(active_topic)
            intent = active_intent or "unknown"
            confidence = 0.4
            meta["source"] = "topic_fallback"
            # Keep topic memory alive
            update_context(
                session,
                intent=intent if intent != "unknown" else None,
                topic=active_topic,
                entity=active_entity,
            )
            result = {
                "success": True,
                "intent": intent,
                "confidence": confidence,
                "response": response,
                "session_id": session,
                "meta": {**meta, "context": get_context(session).to_dict()},
            }
            _persist(session, message, result["response"], intent, page)
            return result

    intent, confidence, intent_meta = detect_intent(normalized, knowledge)
    meta.update(intent_meta or {})

    # Inherit prior topic when intent is weak but session has context
    if (intent == "unknown" or confidence < MIN_CONFIDENCE) and active_topic:
        faq_hit = search_module_faq(normalized, active_topic, active_entity)
        if faq_hit:
            topic_intent = {
                "scholarship": "scholarship",
                "volunteer": "volunteer",
                "donation": "donation",
                "events": "events",
                "job_fair": "employment",
            }.get(faq_hit["topic"], active_intent or "faq")
            update_context(
                session,
                intent=topic_intent,
                topic=faq_hit["topic"],
                entity=active_entity,
            )
            result = {
                "success": True,
                "intent": topic_intent,
                "confidence": float(faq_hit["confidence"]),
                "response": faq_hit["answer"],
                "session_id": session,
                "meta": {
                    **meta,
                    "source": "module_faq_inherited",
                    "context": get_context(session).to_dict(),
                },
            }
            _persist(session, message, result["response"], topic_intent, page)
            return result

    if intent in CONVERSATIONAL_INTENTS:
        response = generate_reply(intent, confidence, normalized, knowledge, intent_meta)
    elif intent == "unknown" or confidence < MIN_CONFIDENCE:
        global_faq = search_faq(normalized, knowledge.get("faq") or {})
        if global_faq:
            intent = "faq"
            confidence = max(confidence, global_faq["confidence"])
            response = global_faq["answer"]
            meta["source"] = "faq_search"
        else:
            kb_hit = search_knowledge(normalized, knowledge)
            if kb_hit and kb_hit["confidence"] >= 0.62:
                intent = kb_hit["intent"]
                confidence = kb_hit["confidence"]
                response = kb_hit["response"]
                meta["source"] = "knowledge_search"
            else:
                response = topic_fallback(active_topic) if active_topic else FALLBACK_RESPONSE
                intent = "unknown"
                confidence = round(confidence, 3)
                meta["source"] = "fallback"
    else:
        # Full topical answer (not a short follow-up)
        entity_hint = detect_entity(normalized, intent)
        if entity_hint == "National Mega Job Fair" or intent == "employment":
            response = _format_job_fair_brief(knowledge.get("events") or {})
            intent = "employment"
            meta["source"] = "job_fair_brief"
        else:
            response = generate_reply(
                intent, confidence, normalized, knowledge, intent_meta
            )
            meta["source"] = "intent_reply"

    if not response or not str(response).strip():
        response = topic_fallback(active_topic) if active_topic else FALLBACK_RESPONSE

    response = _sanitize_response_links(
        str(response).strip(),
        intent=intent,
        session_id=session,
    )

    # Refresh session memory for topical AMP answers
    entity = detect_entity(normalized, intent)
    if not entity and active_entity:
        new_topic = INTENT_TO_TOPIC.get(intent or "")
        if new_topic and new_topic == active_topic:
            entity = active_entity
        elif intent in {"events", "employment"} and active_topic in {"events", "job_fair"}:
            entity = active_entity

    if intent not in CONVERSATIONAL_INTENTS and intent != "unknown":
        update_context(session, intent=intent, entity=entity)
    elif intent == "unknown" and active_topic:
        update_context(
            session,
            intent=active_intent,
            topic=active_topic,
            entity=active_entity,
        )

    result = {
        "success": True,
        "intent": intent,
        "confidence": float(confidence),
        "response": response,
        "session_id": session,
        "meta": {**meta, "context": get_context(session).to_dict()},
    }

    _persist(session, message, result["response"], intent, page)
    return result


OUT_OF_SCOPE_FALLBACK = (
    "I'm here to assist with information about AMP India Foundation. "
    "Please ask me about our programs, scholarships, events, volunteering, "
    "donations, or other foundation-related topics."
)


def _handle_non_amp_category(
    category: QueryCategory,
    classification,
    normalized: str,
) -> tuple[str, float, str]:
    """Build replies for categories that must not hit the AMP knowledge base."""
    canned = category_response(category)
    conf = classification.confidence
    meta = classification.meta or {}

    if category == QueryCategory.GREETING:
        intent = meta.get("intent") or "greeting"
        # Use existing greeting variants (hi / salam / hello, etc.)
        reply = generate_reply(intent, conf, normalized, {}, meta)
        return intent, conf, reply

    if category == QueryCategory.SMALL_TALK:
        intent = meta.get("intent") or "help"
        if intent == "how_are_you":
            return (
                "how_are_you",
                conf,
                (
                    "I'm doing well, thank you! 😊 I'm here to help with "
                    "AMP India Foundation — scholarships, events, projects, "
                    "donations, volunteering, and contact information. "
                    "What would you like to know?"
                ),
            )
        reply = generate_reply(intent, conf, normalized, {}, meta)
        return intent, conf, reply

    if category == QueryCategory.GENERAL_KNOWLEDGE:
        return "general_knowledge", conf, canned or ""

    # OUT_OF_SCOPE and any future non-retrieval categories
    return category.value, conf, canned or OUT_OF_SCOPE_FALLBACK


def generate_reply(
    intent: str,
    confidence: float,
    message: str,
    knowledge: dict[str, Any],
    meta: dict[str, Any] | None = None,
) -> str:
    """Build a natural-language reply from knowledge.

    Swap this function in Phase 3 for an LLM-backed generator.
    """
    if intent in CONVERSATIONAL_INTENTS:
        return _conversational_reply(intent, meta)

    if intent == "more":
        return _help_topics_reply()

    if intent == "mission":
        about = knowledge.get("about") or {}
        mission = about.get("mission") or FALLBACK_RESPONSE
        return f"Our mission: {mission}"

    if intent == "vision":
        about = knowledge.get("about") or {}
        vision = about.get("vision") or about.get("mission") or FALLBACK_RESPONSE
        return f"Our vision: {vision}"

    if intent == "faq":
        hit = search_faq(message, knowledge.get("faq") or {})
        if hit:
            return hit["answer"]
        return _format_about(knowledge.get("about") or {})

    builders = {
        "scholarship": lambda: _format_scholarships(knowledge.get("scholarships") or {}),
        "events": lambda: _format_events(knowledge.get("events") or {}),
        "donation": lambda: _format_donation(knowledge.get("donation") or {}),
        "volunteer": lambda: _format_volunteer(knowledge.get("volunteer") or {}),
        "contact": lambda: _format_contact(knowledge.get("contact") or {}),
        "about": lambda: _format_about(knowledge.get("about") or {}),
        "projects": lambda: _format_projects(knowledge.get("projects") or {}, None),
        "medical": lambda: _format_projects(knowledge.get("projects") or {}, "medical"),
        "education": lambda: _format_projects(knowledge.get("projects") or {}, "education"),
        "employment": lambda: _format_projects(knowledge.get("projects") or {}, "employment"),
        "empowerment": lambda: _format_projects(knowledge.get("projects") or {}, "empowerment"),
        "youth": lambda: _format_projects(knowledge.get("projects") or {}, "mentorship"),
    }

    builder = builders.get(intent)
    if builder:
        text = builder()
        if text:
            return text

    doc_id = INTENT_TO_DOC.get(intent)
    if doc_id:
        doc = get_document(doc_id) or knowledge.get(doc_id)
        if doc and doc.get("summary"):
            return str(doc["summary"])

    return FALLBACK_RESPONSE


def search_faq(message: str, faq_doc: dict[str, Any]) -> dict[str, Any] | None:
    """Find the best FAQ answer via keyword + fuzzy matching."""
    items = faq_doc.get("items") or []
    if not items:
        return None

    msg = normalize_text(message)
    msg_tokens = set(tokenize(msg))
    best: dict[str, Any] | None = None
    best_score = 0.0

    for item in items:
        question = normalize_text(str(item.get("question") or ""))
        answer = str(item.get("answer") or "").strip()
        if not answer:
            continue

        score = SequenceMatcher(None, msg, question).ratio()

        for kw in item.get("keywords") or []:
            kw_n = normalize_text(str(kw))
            if kw_n and kw_n in msg:
                score = max(score, 0.88)
            kw_tokens = set(tokenize(kw_n))
            if kw_tokens and kw_tokens.issubset(msg_tokens):
                score = max(score, 0.82)

        # Token overlap with question
        q_tokens = set(tokenize(question))
        if q_tokens:
            overlap = len(msg_tokens & q_tokens) / max(len(q_tokens), 1)
            score = max(score, overlap * 0.9)

        if score > best_score:
            best_score = score
            best = {
                "question": item.get("question"),
                "answer": answer,
                "confidence": round(min(score, 0.97), 3),
            }

    if best and best_score >= 0.58:
        return best
    return None


def search_knowledge(
    message: str,
    knowledge: dict[str, Any],
) -> dict[str, Any] | None:
    """Broad search across document summaries and nested text fields."""
    msg = normalize_text(message)
    msg_tokens = set(tokenize(msg))
    best: dict[str, Any] | None = None
    best_score = 0.0

    for doc_id, doc in knowledge.items():
        blobs: list[str] = []
        if doc.get("summary"):
            blobs.append(str(doc["summary"]))
        if doc.get("title"):
            blobs.append(str(doc["title"]))
        for kw in doc.get("keywords") or []:
            blobs.append(str(kw))

        for key in ("programs", "upcoming", "flagship", "initiatives", "avenues", "objectives"):
            for item in doc.get(key) or []:
                if isinstance(item, dict):
                    blobs.append(str(item.get("name") or item.get("title") or ""))
                    blobs.append(str(item.get("description") or ""))

        haystack = normalize_text(" ".join(blobs))
        if not haystack:
            continue

        ratio = SequenceMatcher(None, msg, haystack[:400]).ratio()
        token_hits = sum(1 for t in msg_tokens if len(t) > 3 and t in haystack)
        score = max(ratio, min(0.95, token_hits * 0.12))

        for kw in doc.get("keywords") or []:
            if normalize_text(str(kw)) in msg:
                score = max(score, 0.8)

        if score > best_score:
            best_score = score
            intent = {
                "scholarships": "scholarship",
                "donation": "donation",
                "events": "events",
                "volunteer": "volunteer",
                "contact": "contact",
                "about": "about",
                "projects": "projects",
                "faq": "faq",
            }.get(doc_id, doc_id)
            # Prefer structured reply when possible
            response = generate_reply(intent, score, msg, knowledge, None)
            best = {
                "intent": intent,
                "confidence": round(score, 3),
                "response": response,
            }

    return best


# ---------------------------------------------------------------------------
# Conversational replies
# ---------------------------------------------------------------------------

def _help_topics_reply() -> str:
    return (
        "I can help you with:\n"
        "• Scholarships\n"
        "• Events\n"
        "• Projects\n"
        "• Donations\n"
        "• Volunteering\n"
        "• Contact Information\n"
        "• General Questions\n\n"
        "How can I assist you today?"
    )


def _conversational_reply(intent: str, meta: dict[str, Any] | None = None) -> str:
    meta = meta or {}
    kind = meta.get("greeting_kind") or "hello"

    if intent == "greeting":
        if kind == "salam":
            return (
                "Wa Alaikum Assalam! 🌸\n"
                "Welcome to AMP India Foundation. How may I assist you today?"
            )
        if kind == "hi":
            return (
                "Hi there! 😊\n"
                "Welcome to AMP India Foundation. What would you like to know today?"
            )
        if kind in {"hey", "hola"}:
            return (
                "Hey! 👋 Welcome to AMP India Foundation.\n"
                "Ask me about scholarships, events, projects, donations, "
                "volunteering, or contact details."
            )
        if kind == "morning":
            return (
                "Good morning! ☀️ Welcome to AMP India Foundation.\n"
                "How can I help you today?"
            )
        if kind == "afternoon":
            return (
                "Good afternoon! Welcome to AMP India Foundation.\n"
                "How can I help you today?"
            )
        if kind == "evening":
            return (
                "Good evening! Welcome to AMP India Foundation.\n"
                "How can I help you today?"
            )
        # Default full welcome (hello / namaste / others)
        return (
            "Hello! 👋 Welcome to AMP India Foundation.\n\n"
            "I'm your AI Assistant. I can help you with:\n"
            "• Scholarships\n"
            "• Events\n"
            "• Projects\n"
            "• Donations\n"
            "• Volunteering\n"
            "• Contact Information\n"
            "• General Questions\n\n"
            "How can I assist you today?"
        )

    if intent == "gratitude":
        return (
            "You're welcome! 😊 If you have another question about AMP India "
            "Foundation, I'm happy to help."
        )

    if intent == "farewell":
        return (
            "Goodbye! 👋 Thank you for visiting AMP India Foundation. "
            "Feel free to come back anytime."
        )

    if intent == "acknowledgment":
        return (
            "Got it! If you'd like details on scholarships, events, donations, "
            "projects, volunteering, or contact info, just ask."
        )

    if intent == "identity":
        return IDENTITY_RESPONSE

    if intent == "help":
        return _help_topics_reply()

    return _help_topics_reply()


# ---------------------------------------------------------------------------
# Link hygiene
# ---------------------------------------------------------------------------

def _sanitize_response_links(
    response: str,
    intent: str | None,
    session_id: str | None,
) -> str:
    """Remove boilerplate page-link footers; never repeat the same path twice."""
    if not response:
        return response

    # Drop generic "More details: /…" style trailing lines always
    cleaned = _LINK_LINE_RE.sub("", response)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    # Paths are only kept when clearly relevant to the intent
    allowed_paths = _allowed_paths_for_intent(intent)
    paths_in_reply = set(_PATH_RE.findall(cleaned))

    # Remove site paths that are not relevant to this intent
    for path in paths_in_reply:
        if path.rstrip("/").lower() not in {p.rstrip("/").lower() for p in allowed_paths}:
            cleaned = re.sub(re.escape(path), "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    # Never repeat a path that appeared in the previous bot reply
    previous = _previous_bot_response(session_id)
    if previous:
        prev_paths = {p.lower() for p in _PATH_RE.findall(previous)}
        for path in list(_PATH_RE.findall(cleaned)):
            if path.lower() in prev_paths:
                cleaned = re.sub(re.escape(path), "", cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(
                    r"(?im)^(?:more details|learn more|see all events|"
                    r"explore projects|volunteer page)\s*:?\s*$",
                    "",
                    cleaned,
                )

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def _allowed_paths_for_intent(intent: str | None) -> set[str]:
    """Site paths that may appear for a given intent (empty = none)."""
    mapping = {
        "donation": {"/support-us"},
        "volunteer": set(),  # external registration URL is fine; no /volunteer spam
        "events": set(),
        "scholarship": set(),
        "contact": set(),
        "about": set(),
        "mission": set(),
        "vision": set(),
        "projects": set(),
        "medical": set(),
        "education": set(),
        "employment": set(),
        "empowerment": set(),
        "youth": set(),
        "faq": set(),
    }
    return mapping.get(intent or "", set())


def _previous_bot_response(session_id: str | None) -> str | None:
    if not session_id:
        return None
    try:
        row = (
            ChatMessage.query.filter_by(session_id=session_id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )
        return row.bot_response if row else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Response formatters
# ---------------------------------------------------------------------------

def _format_scholarships(doc: dict[str, Any]) -> str:
    if not doc:
        return FALLBACK_RESPONSE
    lines = [doc.get("summary") or "AMP India Foundation offers scholarship programs."]
    programs = doc.get("programs") or []
    if programs:
        lines.append("\nCurrent support areas:")
        for prog in programs:
            name = prog.get("name")
            desc = prog.get("description")
            if name:
                lines.append(f"• {name}: {desc}" if desc else f"• {name}")
    if doc.get("how_to_apply"):
        lines.append(f"\nHow to apply: {doc['how_to_apply']}")
    related = doc.get("related_event") or {}
    if related.get("title"):
        lines.append(
            f"\nRelated event: {related['title']} — {related.get('date', '')} "
            f"({related.get('venue', '')})."
        )
    return "\n".join(lines).strip()


def _format_job_fair_brief(doc: dict[str, Any]) -> str:
    """Short Job Fair answer — avoids dumping the full events catalogue."""
    upcoming = doc.get("upcoming") or []
    match = None
    for event in upcoming:
        title = normalize_text(str(event.get("title") or ""))
        if "job fair" in title or "placement" in title:
            match = event
            break
    if not match:
        return (
            "AMP India Foundation hosts the National Mega Job Fair & Placement Drive "
            "to connect skilled youth with employers. It is free to attend unless "
            "otherwise mentioned. Ask me about registration, documents, or placement."
        )
    return (
        f"{match.get('title')} — {match.get('date', 'TBA')} "
        f"({match.get('venue', 'TBA')}).\n"
        f"{match.get('description', '')}\n\n"
        "It is free to attend unless otherwise mentioned in the event details. "
        "You can ask about registration, documents, eligibility, or placement."
    ).strip()


def _format_events(doc: dict[str, Any]) -> str:
    if not doc:
        return FALLBACK_RESPONSE
    lines = [doc.get("summary") or "Here are upcoming AMP India Foundation events."]

    featured = doc.get("featured") or {}
    if featured.get("title"):
        lines.append(
            f"\nFeatured: {featured['title']} — {featured.get('date', '')}"
            f"{', ' + featured['time'] if featured.get('time') else ''} "
            f"at {featured.get('venue', 'TBA')}."
        )
        if featured.get("description"):
            lines.append(featured["description"])

    upcoming = doc.get("upcoming") or []
    if upcoming:
        lines.append("\nUpcoming events:")
        for event in upcoming[:6]:
            lines.append(
                f"• {event.get('title')} — {event.get('date', 'TBA')} "
                f"({event.get('venue', 'TBA')})"
            )
            if event.get("description"):
                lines.append(f"  {event['description']}")

    return "\n".join(lines).strip()


def _format_donation(doc: dict[str, Any]) -> str:
    if not doc:
        return FALLBACK_RESPONSE
    bank = doc.get("bank") or {}
    summary = doc.get("summary") or (
        "You can donate to AMP India Foundation via bank transfer."
    )
    # Weave Support Us naturally — no separate "More details" footer
    if "support us" not in summary.lower():
        summary = summary.rstrip()
        if not summary.endswith("."):
            summary += "."
        summary = (
            f"{summary} You can donate through the Support Us page "
            "or use the bank details below."
        )
    lines = [
        summary,
        "",
        "Bank account details:",
        f"• Bank: {bank.get('bank_name', '—')}",
        f"• Account Name: {bank.get('account_name', '—')}",
        f"• Account Number: {bank.get('account_number', '—')}",
        f"• Account Type: {bank.get('account_type', '—')}",
        f"• IFSC: {bank.get('ifsc', '—')}",
    ]
    return "\n".join(lines).strip()


def _format_volunteer(doc: dict[str, Any]) -> str:
    if not doc:
        return FALLBACK_RESPONSE
    url = doc.get("registration_url") or "https://tinyurl.com/AIFVolunteerRegn"
    lines = [
        doc.get("summary") or "You can volunteer with AMP India Foundation.",
        "",
        doc.get("how_to_join") or "",
        f"\nRegister here: {url}",
    ]
    return "\n".join(line for line in lines if line is not None).strip()


def _format_contact(doc: dict[str, Any]) -> str:
    if not doc:
        return FALLBACK_RESPONSE
    lines = [
        "You can reach AMP India Foundation using the details below:",
        "",
        f"Address: {doc.get('address', '—')}",
        f"Phone: {doc.get('phone', '—')} ({doc.get('phone_hours', '')})",
        f"Email: {doc.get('email', '—')} — {doc.get('email_note', '')}",
    ]
    return "\n".join(lines).strip()


def _format_about(doc: dict[str, Any]) -> str:
    if not doc:
        return FALLBACK_RESPONSE
    lines = [
        doc.get("summary") or "AMP India Foundation is a registered non-profit organisation.",
        "",
        f"Mission: {doc.get('mission', '')}",
    ]
    avenues = doc.get("avenues") or []
    if avenues:
        lines.append("\nKey focus areas:")
        for item in avenues:
            lines.append(f"• {item.get('title')}: {item.get('description', '')}")
    return "\n".join(lines).strip()


def _format_projects(doc: dict[str, Any], focus_id: str | None) -> str:
    if not doc:
        return FALLBACK_RESPONSE

    if focus_id:
        for initiative in doc.get("initiatives") or []:
            if initiative.get("id") == focus_id:
                return (
                    f"{initiative.get('name')}: {initiative.get('description')}"
                )

    lines = [doc.get("summary") or "AMP India Foundation runs several programs."]
    flagship = doc.get("flagship") or []
    if flagship:
        lines.append("\nFlagship programs:")
        for item in flagship:
            lines.append(f"• {item.get('name')}: {item.get('description', '')}")

    initiatives = doc.get("initiatives") or []
    if initiatives:
        lines.append("\nStrategic initiatives:")
        for item in initiatives:
            lines.append(f"• {item.get('name')}: {item.get('description', '')}")

    return "\n".join(lines).strip()


def _persist(
    session_id: str,
    user_message: str,
    bot_response: str,
    intent: str | None,
    page: str | None = None,
) -> None:
    """Best-effort chat history write — never fail the user-facing reply."""
    try:
        record = ChatMessage(
            session_id=session_id,
            user_message=user_message or "",
            bot_response=bot_response or FALLBACK_RESPONSE,
            intent=(intent or "unknown")[:64],
            page=(page[:255] if page else None),
        )
        db.session.add(record)
        db.session.commit()
    except Exception:
        logger.exception("Failed to persist chat message for session %s", session_id)
        try:
            db.session.rollback()
        except Exception:
            pass


def get_session_history(session_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Optional helper for future UI history restore."""
    if not session_id:
        return []
    rows = (
        ChatMessage.query.filter_by(session_id=session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return [row.to_dict() for row in rows]
