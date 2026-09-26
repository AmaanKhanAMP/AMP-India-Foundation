"""Pre-retrieval query classifier for the AMP chatbot.

Runs BEFORE intent detection and knowledge / RAG retrieval so unrelated
questions never enter the AMP knowledge pipeline.

Categories (extensible):
  - GREETING
  - SMALL_TALK
  - AMP_KNOWLEDGE   → only this path may search the knowledge base / vectors
  - GENERAL_KNOWLEDGE
  - OUT_OF_SCOPE
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from services.intent_detector import (
    detect_conversation,
    normalize_text,
    tokenize,
)
from services.module_faqs import is_followup_question, is_leadership_question
from services.session_context import SessionContext


class QueryCategory(str, Enum):
    GREETING = "greeting"
    SMALL_TALK = "small_talk"
    AMP_KNOWLEDGE = "amp_knowledge"
    GENERAL_KNOWLEDGE = "general_knowledge"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True)
class ClassificationResult:
    category: QueryCategory
    confidence: float
    reason: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Response templates (category-level; intent replies may override greetings)
# ---------------------------------------------------------------------------

GENERAL_KNOWLEDGE_RESPONSE = (
    "I'm the official AMP India Foundation AI Assistant, so I'm best equipped "
    "to answer questions about our scholarships, events, projects, donations, "
    "volunteering, and other foundation-related information. I may not be able "
    "to answer general knowledge questions like this."
)

OUT_OF_SCOPE_RESPONSE = (
    "I'm here to assist with information about AMP India Foundation. "
    "Please ask me about our programs, scholarships, events, volunteering, "
    "donations, or other foundation-related topics."
)

# ---------------------------------------------------------------------------
# Keyword / pattern banks (easy to extend)
# ---------------------------------------------------------------------------

# Prefer distinctive AMP domain terms. Avoid ultra-generic words like
# "about", "support", "apply", "job" as sole triggers (use AMP_PHRASES instead).
AMP_KEYWORDS = frozenset(
    {
        "amp",
        "aif",
        "foundation",
        "scholarship",
        "scholarships",
        "event",
        "events",
        "project",
        "projects",
        "program",
        "programs",
        "programme",
        "programmes",
        "donation",
        "donate",
        "donations",
        "volunteer",
        "volunteering",
        "volunteers",
        "contact",
        "education",
        "healthcare",
        "medical",
        "empowerment",
        "youth",
        "gallery",
        "mission",
        "vision",
        "mentorship",
        "mentor",
        "employment",
        "placement",
        "training",
        "etp",
        "crowdfunding",
        "ifsc",
        "nagpada",
        "initiative",
        "initiatives",
        "ngo",
        "philanthropy",
        "underprivileged",
        "orphan",
        "orphans",
        "livelihood",
        "shg",
        "vocational",
    }
)

AMP_PHRASES = (
    "amp india",
    "india foundation",
    "skill development",
    "women empowerment",
    "youth program",
    "youth programmes",
    "youth programs",
    "higher education",
    "how can i donate",
    "how do i donate",
    "become a volunteer",
    "support us",
    "about amp",
    "about the foundation",
    "about your foundation",
    "centre of excellence",
    "centers of excellence",
    "centres of excellence",
    "job fair",
    "medical camp",
    "health camp",
    "financial support",
    "bank details",
    "how to apply",
    "scholarship apply",
    "apply for scholarship",
)

# Conversational intents already handled by detect_conversation → SMALL_TALK bucket
# (except pure greetings → GREETING)
_SMALL_TALK_INTENTS = frozenset(
    {"gratitude", "farewell", "acknowledgment", "help", "identity"}
)

_HOW_ARE_YOU = re.compile(
    r"\b(?:how are you|how r u|how're you|how are u|how's it going|"
    r"how is it going|whats up|what's up|sup)\b",
    re.IGNORECASE,
)

# Clear general-knowledge / trivia / coding / weather signals
GENERAL_KNOWLEDGE_PATTERNS = (
    re.compile(r"\bwhat color\b", re.I),
    re.compile(r"\bcolour of the sky\b", re.I),
    re.compile(r"\bwho invented\b", re.I),
    re.compile(r"\bhow many planets\b", re.I),
    re.compile(r"\bwhat is ai\b", re.I),
    re.compile(r"\bwhat is artificial intelligence\b", re.I),
    re.compile(r"\btell me a joke\b", re.I),
    re.compile(r"\bjoke\b", re.I),
    re.compile(r"\bwhat is python\b", re.I),
    re.compile(r"\bweather\b", re.I),
    re.compile(r"\btemperature\b", re.I),
    re.compile(r"\bforecast\b", re.I),
    re.compile(r"\bcapital of\b", re.I),
    re.compile(r"\bwho is the president\b", re.I),
    re.compile(r"\bwho is the prime minister\b", re.I),
    re.compile(r"\bmath\b", re.I),
    re.compile(r"\bcalculate\b", re.I),
    re.compile(r"\bsolve\b", re.I),
    re.compile(r"^\s*\d+\s*[\+\-\*/x×÷^]\s*\d+", re.I),
    re.compile(r"\bprogramming\b", re.I),
    re.compile(r"\bjavascript\b", re.I),
    re.compile(r"\btypescript\b", re.I),
    re.compile(r"\bhtml\b", re.I),
    re.compile(r"\bcss\b", re.I),
    re.compile(r"\bcode (?:this|for me|a)\b", re.I),
    re.compile(r"\bwrite (?:a |me )?(?:poem|story|essay|code)\b", re.I),
    re.compile(r"\btranslate\b", re.I),
    re.compile(r"\bdefinition of\b", re.I),
    re.compile(r"\bmeaning of\b", re.I),
    re.compile(r"\btrivia\b", re.I),
    re.compile(r"\bgoogle\b", re.I),
    re.compile(r"\bfootball\b", re.I),
    re.compile(r"\bcricket score\b", re.I),
    re.compile(r"\bstock (?:price|market)\b", re.I),
    re.compile(r"\bcrypto(?:currency)?\b", re.I),
    re.compile(r"\bbitcoin\b", re.I),
)

# Unsafe / clearly unsupported requests
OUT_OF_SCOPE_PATTERNS = (
    re.compile(r"\bhack\b", re.I),
    re.compile(r"\bcrack (?:wifi|wi-?fi|password)\b", re.I),
    re.compile(r"\bsteal\b", re.I),
    re.compile(r"\billegal\b", re.I),
    re.compile(r"\bweapon\b", re.I),
    re.compile(r"\bbomb\b", re.I),
    re.compile(r"\bporn\b", re.I),
    re.compile(r"\bnsfw\b", re.I),
    re.compile(r"\bdrug(?:s)?\b", re.I),
    re.compile(r"\bmake (?:me )?money fast\b", re.I),
)


def classify_query(
    message: str,
    context: SessionContext | None = None,
) -> ClassificationResult:
    """Classify a user message before any knowledge / RAG retrieval."""
    raw = (message or "").strip()
    if not raw:
        return ClassificationResult(
            category=QueryCategory.OUT_OF_SCOPE,
            confidence=0.0,
            reason="empty",
        )

    normalized = normalize_text(raw)
    ctx = context or SessionContext()

    # 1) Safety / unsupported first
    if _matches_any(normalized, OUT_OF_SCOPE_PATTERNS):
        return ClassificationResult(
            category=QueryCategory.OUT_OF_SCOPE,
            confidence=0.95,
            reason="unsafe_or_unsupported_pattern",
        )

    # 2) Greeting / small-talk (reuse conversational detector)
    conversational = detect_conversation(raw)
    if conversational is not None:
        intent, conf, meta = conversational
        if intent == "greeting":
            return ClassificationResult(
                category=QueryCategory.GREETING,
                confidence=conf,
                reason="greeting_detector",
                meta={"intent": intent, **(meta or {})},
            )
        if intent in _SMALL_TALK_INTENTS:
            return ClassificationResult(
                category=QueryCategory.SMALL_TALK,
                confidence=conf,
                reason="small_talk_detector",
                meta={"intent": intent, **(meta or {})},
            )

    # Explicit "how are you" (not always caught as short greeting)
    if _HOW_ARE_YOU.search(normalized) and not _has_amp_signal(normalized):
        return ClassificationResult(
            category=QueryCategory.SMALL_TALK,
            confidence=0.96,
            reason="how_are_you",
            meta={"intent": "how_are_you"},
        )

    # 2b) Leadership / org questions → AMP path (never general-knowledge)
    if is_leadership_question(normalized):
        return ClassificationResult(
            category=QueryCategory.AMP_KNOWLEDGE,
            confidence=0.93,
            reason="leadership_question",
            meta={"intent_hint": "leadership", "amp_score": 0.93},
        )

    amp_score = _amp_relevance_score(normalized)

    # 3) Strong AMP signal → knowledge / RAG path
    if amp_score >= 0.55:
        return ClassificationResult(
            category=QueryCategory.AMP_KNOWLEDGE,
            confidence=round(min(0.99, amp_score), 3),
            reason="amp_keywords",
            meta={"amp_score": amp_score},
        )

    # 3b) Contextual follow-up inheriting session topic (fee? who can apply?)
    if ctx.last_topic and is_followup_question(raw):
        return ClassificationResult(
            category=QueryCategory.AMP_KNOWLEDGE,
            confidence=0.88,
            reason="session_followup",
            meta={
                "amp_score": amp_score,
                "followup": True,
                "inherit_topic": ctx.last_topic,
                "inherit_intent": ctx.last_intent,
                "inherit_entity": ctx.last_entity,
            },
        )

    # 4) General knowledge / trivia / coding / weather
    if _matches_any(normalized, GENERAL_KNOWLEDGE_PATTERNS):
        return ClassificationResult(
            category=QueryCategory.GENERAL_KNOWLEDGE,
            confidence=0.9,
            reason="general_knowledge_pattern",
            meta={"amp_score": amp_score},
        )

    # Heuristic: question-shaped with zero AMP signal → general knowledge
    # Skip when a session topic exists and this looks like a short follow-up.
    if (
        amp_score < 0.25
        and _looks_like_general_question(normalized)
        and not (ctx.last_topic and len(tokenize(normalized)) <= 8)
    ):
        return ClassificationResult(
            category=QueryCategory.GENERAL_KNOWLEDGE,
            confidence=0.8,
            reason="general_question_no_amp_signal",
            meta={"amp_score": amp_score},
        )

    # Weak AMP signal still worth trying knowledge (e.g. "upcoming workshops")
    if amp_score >= 0.35:
        return ClassificationResult(
            category=QueryCategory.AMP_KNOWLEDGE,
            confidence=round(amp_score, 3),
            reason="weak_amp_signal",
            meta={"amp_score": amp_score},
        )

    # Short clarification while a topic is active
    if ctx.last_topic and len(tokenize(normalized)) <= 6:
        return ClassificationResult(
            category=QueryCategory.AMP_KNOWLEDGE,
            confidence=0.75,
            reason="short_context_followup",
            meta={
                "followup": True,
                "inherit_topic": ctx.last_topic,
                "inherit_intent": ctx.last_intent,
                "inherit_entity": ctx.last_entity,
            },
        )

    # 5) Default: unrelated to AMP
    return ClassificationResult(
        category=QueryCategory.OUT_OF_SCOPE,
        confidence=0.7,
        reason="no_amp_relevance",
        meta={"amp_score": amp_score},
    )


def _matches_any(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    return any(p.search(text) for p in patterns)


def _has_amp_signal(text: str) -> bool:
    return _amp_relevance_score(text) >= 0.55


def _amp_relevance_score(text: str) -> float:
    """Score 0..1 for how strongly the message relates to AMP topics."""
    if not text:
        return 0.0

    score = 0.0
    tokens = set(tokenize(text))

    for phrase in AMP_PHRASES:
        if phrase in text:
            score = max(score, 0.92)

    hits = tokens & AMP_KEYWORDS
    if hits:
        # More distinct AMP tokens → higher confidence
        score = max(score, min(0.95, 0.55 + 0.12 * len(hits)))

    # Very strong org mentions
    if "amp" in tokens or "aif" in tokens:
        score = max(score, 0.9)
    if "foundation" in tokens and ("india" in tokens or "amp" in tokens):
        score = max(score, 0.93)

    return score


def _looks_like_general_question(text: str) -> bool:
    """True for classic open trivia / factual questions with no AMP context."""
    if not text:
        return False

    starters = (
        "what is ",
        "what are ",
        "what was ",
        "what were ",
        "what color",
        "what colour",
        "who is ",
        "who was ",
        "who invented",
        "who created",
        "where is ",
        "where are ",
        "when was ",
        "when is ",
        "why is ",
        "why do ",
        "how many ",
        "how much ",
        "how does ",
        "how do ",
        "how to ",
        "tell me ",
        "explain ",
        "define ",
    )
    if any(text.startswith(s) for s in starters):
        return True

    # Pure math like "2+2" / "what is 15*4"
    if re.fullmatch(r"[\d\s\+\-\*/x×÷\^\.\(\)]+", text):
        return True

    return False


def category_response(category: QueryCategory) -> str | None:
    """Default reply for non-retrieval categories (None = use existing generators)."""
    if category == QueryCategory.GENERAL_KNOWLEDGE:
        return GENERAL_KNOWLEDGE_RESPONSE
    if category == QueryCategory.OUT_OF_SCOPE:
        return OUT_OF_SCOPE_RESPONSE
    return None
