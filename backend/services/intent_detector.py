"""Keyword / partial / fuzzy intent detection for Phase 2 chatbot.

Phase 3 can replace ``detect_intent`` with an LLM classifier while keeping
the same return shape: ``(intent, confidence, meta)``.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

# Intent id → trigger phrases / keywords (longer phrases scored higher)
INTENT_KEYWORDS: dict[str, list[str]] = {
    "scholarship": [
        "scholarship",
        "scholarships",
        "scholarship programs",
        "financial support",
        "higher education scholarship",
        "apply for scholarship",
        "student funding",
        "education fund",
        "orphans basic education",
    ],
    "events": [
        "event",
        "events",
        "upcoming events",
        "next event",
        "any events",
        "when is the next event",
        "workshop",
        "job fair",
        "medical camp",
        "summit",
        "schedule",
        "programme date",
    ],
    "donation": [
        "donate",
        "donation",
        "donations",
        "how can i donate",
        "support us",
        "contribute",
        "contribution",
        "bank details",
        "ifsc",
        "charity",
        "give money",
        "fund amp",
    ],
    "volunteer": [
        "volunteer",
        "volunteering",
        "become a volunteer",
        "how can i volunteer",
        "join as volunteer",
        "register volunteer",
        "goodwill volunteer",
    ],
    "medical": [
        "medical",
        "medical projects",
        "healthcare",
        "health care",
        "health camp",
        "free medicine",
        "critical illness",
        "hospital",
        "clinic",
    ],
    "projects": [
        "project",
        "projects",
        "programs",
        "programmes",
        "initiatives",
        "what projects",
        "our projects",
    ],
    "education": [
        "education",
        "vocational",
        "skill development",
        "skills training",
        "nsdc",
        "ace academy",
        "competitive exams",
        "national talent search",
        "nts",
    ],
    "employment": [
        "employment",
        "job",
        "jobs",
        "placement",
        "job fair",
        "employability",
        "career",
        "hiring",
        "etp",
    ],
    "empowerment": [
        "empowerment",
        "women empowerment",
        "livelihood",
        "self help group",
        "shg",
        "women programs",
    ],
    "youth": [
        "youth",
        "youth programs",
        "mentorship",
        "mentor",
        "student mentorship",
        "young people",
    ],
    "contact": [
        "contact",
        "phone",
        "email",
        "address",
        "office",
        "call",
        "reach you",
        "how can i contact",
        "location",
        "helpline",
    ],
    "about": [
        "about amp",
        "about",
        "what is amp",
        "amp india foundation",
        "organisation",
        "organization",
        "ngo",
    ],
    "mission": [
        "mission",
        "your mission",
        "primary mission",
        "purpose",
    ],
    "vision": [
        "vision",
        "your vision",
        "central vision",
    ],
    "faq": [
        "faq",
        "frequently asked",
        "common questions",
    ],
    "greeting": [
        "hello",
        "hi",
        "hii",
        "hiii",
        "hiiii",
        "hey",
        "heyy",
        "heyyy",
        "good morning",
        "good afternoon",
        "good evening",
        "namaste",
        "hola",
        "assalamualaikum",
        "assalamu alaikum",
        "asalamualaikum",
        "salam",
        "salaam",
    ],
    "gratitude": [
        "thanks",
        "thank you",
        "thankyou",
        "thx",
        "ty",
        "much appreciated",
    ],
    "farewell": [
        "bye",
        "goodbye",
        "good bye",
        "see you",
        "see ya",
        "take care",
        "later",
    ],
    "acknowledgment": [
        "ok",
        "okay",
        "k",
        "kk",
        "alright",
        "all right",
        "got it",
        "cool",
        "sure",
        "nice",
        "great",
    ],
    "help": [
        "help",
        "help me",
        "what can you do",
        "how can you help",
        "what do you do",
        "options",
        "menu",
    ],
    "identity": [
        "who are you",
        "what are you",
        "your name",
        "who r u",
        "what is your name",
    ],
    "more": [
        "more",
        "more options",
        "other topics",
        "what else",
        "help topics",
    ],
}

# Map sub-intents to knowledge document ids used by the response builder
INTENT_TO_DOC: dict[str, str] = {
    "scholarship": "scholarships",
    "events": "events",
    "donation": "donation",
    "volunteer": "volunteer",
    "medical": "projects",
    "projects": "projects",
    "education": "projects",
    "employment": "projects",
    "empowerment": "projects",
    "youth": "projects",
    "contact": "contact",
    "about": "about",
    "mission": "about",
    "vision": "about",
    "faq": "faq",
    "more": "navigation",
    "greeting": "about",
    "gratitude": "about",
    "farewell": "about",
    "acknowledgment": "about",
    "help": "navigation",
    "identity": "about",
}

# Short-message conversational intents checked before knowledge matching
CONVERSATIONAL_INTENTS = frozenset(
    {
        "greeting",
        "gratitude",
        "farewell",
        "acknowledgment",
        "help",
        "identity",
    }
)

_WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")

# Punctuation-tolerant greeting forms (hii, hiii, hello!, etc.)
_GREETING_EXACT = re.compile(
    r"^(?:"
    r"hi+|hello+|hey+|hola|"
    r"good\s*morning|good\s*afternoon|good\s*evening|"
    r"namaste|"
    r"assalamu?\s*alaikum|asalamualaikum|salam+|salaam+"
    r")[!?.]*$",
    re.IGNORECASE,
)

_GRATITUDE_EXACT = re.compile(
    r"^(?:thanks|thank\s*you|thankyou|thx|ty|much\s*appreciated)[!?.]*$",
    re.IGNORECASE,
)

_FAREWELL_EXACT = re.compile(
    r"^(?:bye+|goodbye|good\s*bye|see\s*you|see\s*ya|take\s*care|later)[!?.]*$",
    re.IGNORECASE,
)

_ACK_EXACT = re.compile(
    r"^(?:ok|okay|k|kk|alright|all\s*right|got\s*it|cool|sure|nice|great)[!?.]*$",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    """Lowercase, strip, collapse whitespace."""
    if not text:
        return ""
    lowered = text.lower().strip()
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(normalize_text(text))


def detect_conversation(message: str) -> tuple[str, float, dict[str, Any]] | None:
    """Detect greetings / small-talk before knowledge intent matching.

    Returns ``(intent, confidence, meta)`` or ``None`` when not conversational.
    """
    raw = (message or "").strip()
    if not raw:
        return None

    # Keep punctuation for exact patterns; also try normalized alphanumeric form
    compact = re.sub(r"[^\w\s]", "", normalize_text(raw))
    compact = re.sub(r"\s+", " ", compact).strip()

    if _GREETING_EXACT.match(compact) or _GREETING_EXACT.match(raw.strip()):
        kind = _greeting_kind(compact)
        return "greeting", 0.99, {"source": "conversation", "greeting_kind": kind}

    if _GRATITUDE_EXACT.match(compact):
        return "gratitude", 0.99, {"source": "conversation"}

    if _FAREWELL_EXACT.match(compact):
        return "farewell", 0.99, {"source": "conversation"}

    if _ACK_EXACT.match(compact):
        return "acknowledgment", 0.99, {"source": "conversation"}

    # Phrase-level conversational intents (may include light extras)
    normalized = normalize_text(raw)
    tokens = tokenize(normalized)

    identity_phrases = (
        "who are you",
        "what are you",
        "your name",
        "who r u",
        "what is your name",
        "what's your name",
        "whats your name",
    )
    for phrase in identity_phrases:
        if phrase in normalized and len(tokens) <= 8:
            return "identity", 0.97, {"source": "conversation"}

    help_phrases = (
        "what can you do",
        "how can you help",
        "what do you do",
        "help me",
    )
    for phrase in help_phrases:
        if phrase in normalized and len(tokens) <= 10:
            return "help", 0.97, {"source": "conversation"}

    if normalized in {"help", "options", "menu"}:
        return "help", 0.97, {"source": "conversation"}

    # Very short messages that are only a greeting keyword (+ optional emoji noise)
    if len(tokens) <= 3:
        for intent in ("greeting", "gratitude", "farewell", "acknowledgment"):
            for keyword in INTENT_KEYWORDS.get(intent, []):
                if _phrase_in_message(normalized, keyword) or compact == normalize_text(
                    keyword
                ):
                    # Avoid treating "help topics" style content as pure greeting
                    if intent == "greeting" and any(
                        t in tokens
                        for t in (
                            "scholarship",
                            "event",
                            "donate",
                            "volunteer",
                            "contact",
                            "project",
                        )
                    ):
                        continue
                    meta = {"source": "conversation"}
                    if intent == "greeting":
                        meta["greeting_kind"] = _greeting_kind(compact or normalized)
                    return intent, 0.95, meta

    return None


def _greeting_kind(text: str) -> str:
    t = normalize_text(text)
    if "assalam" in t or "asalam" in t or t in {"salam", "salaam"}:
        return "salam"
    if t.startswith("hi") and not t.startswith("high"):
        return "hi"
    if t.startswith("hello"):
        return "hello"
    if t.startswith("hey"):
        return "hey"
    if "morning" in t:
        return "morning"
    if "afternoon" in t:
        return "afternoon"
    if "evening" in t:
        return "evening"
    if "hola" in t:
        return "hola"
    if "namaste" in t:
        return "namaste"
    return "hello"


def _fuzzy_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _phrase_in_message(message: str, phrase: str) -> bool:
    """True when ``phrase`` appears as whole word(s), not a substring of a larger word."""
    if not phrase:
        return False
    pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
    return re.search(pattern, message) is not None


def _score_keyword(message: str, keyword: str) -> float:
    """Score a single keyword/phrase against the user message."""
    kw = normalize_text(keyword)
    if not kw:
        return 0.0

    # Exact phrase as whole words (strongest) — avoids "hi" matching inside "thing"
    if _phrase_in_message(message, kw):
        length_bonus = min(0.08, len(kw.split()) * 0.02)
        return min(1.0, 0.92 + length_bonus)

    # Word-level partial match for multi-word keywords
    msg_tokens = set(tokenize(message))
    kw_tokens = tokenize(kw)
    if not kw_tokens:
        return 0.0

    if len(kw_tokens) == 1:
        token = kw_tokens[0]
        if token in msg_tokens:
            return 0.88
        # Prefix / stem-ish partial (e.g. scholarship / scholarships)
        # Skip very short tokens to reduce false positives
        if len(token) < 4:
            return 0.0
        for mt in msg_tokens:
            if len(mt) < 4:
                continue
            if mt.startswith(token) or token.startswith(mt):
                return 0.78
            if len(token) >= 5 and _fuzzy_ratio(mt, token) >= 0.84:
                return 0.72
        return 0.0

    overlap = sum(1 for t in kw_tokens if t in msg_tokens)
    if overlap == len(kw_tokens):
        return 0.9
    if overlap >= max(1, len(kw_tokens) - 1):
        return 0.75 + (0.05 * overlap / len(kw_tokens))

    # Fuzzy phrase similarity for near misses (require meaningful length)
    if len(kw) < 6:
        return 0.0
    ratio = _fuzzy_ratio(message, kw)
    if ratio >= 0.78:
        return ratio * 0.85
    return 0.0


def detect_intent(
    message: str,
    knowledge: dict[str, Any] | None = None,
) -> tuple[str, float, dict[str, Any]]:
    """Detect the best intent for ``message``.

    Returns:
        (intent_id, confidence 0..1, meta dict)
    """
    normalized = normalize_text(message)
    if not normalized:
        return "unknown", 0.0, {"reason": "empty"}

    # Conversational small-talk / greetings take priority over knowledge keywords
    conversational = detect_conversation(message)
    if conversational is not None:
        return conversational

    best_intent = "unknown"
    best_score = 0.0
    best_keyword = ""

    for intent, keywords in INTENT_KEYWORDS.items():
        # Skip conversational intents here — already handled above
        if intent in CONVERSATIONAL_INTENTS:
            continue
        for keyword in keywords:
            score = _score_keyword(normalized, keyword)
            if score > best_score:
                best_score = score
                best_intent = intent
                best_keyword = keyword

    # Secondary pass: knowledge-document keywords (helps project subtopics)
    if knowledge:
        for doc_id, doc in knowledge.items():
            doc_keywords = doc.get("keywords") or []
            for keyword in doc_keywords:
                score = _score_keyword(normalized, str(keyword)) * 0.96
                # Prefer mapped intents; map doc ids to intents when stronger
                mapped_intent = _doc_to_intent(doc_id)
                if score > best_score:
                    best_score = score
                    best_intent = mapped_intent
                    best_keyword = str(keyword)

            # Initiative-level keywords inside projects.json
            for initiative in doc.get("initiatives") or []:
                for keyword in initiative.get("keywords") or []:
                    score = _score_keyword(normalized, str(keyword))
                    if score > best_score:
                        best_score = score
                        best_intent = initiative.get("id") or "projects"
                        best_keyword = str(keyword)

            for item in doc.get("items") or []:
                for keyword in item.get("keywords") or []:
                    score = _score_keyword(normalized, str(keyword)) * 0.95
                    if score > best_score:
                        best_score = score
                        best_intent = "faq" if doc_id == "faq" else _doc_to_intent(doc_id)
                        best_keyword = str(keyword)

    # Soft threshold — below this we treat as unknown (FAQ search may still help)
    if best_score < 0.55:
        return "unknown", best_score, {
            "matched_keyword": best_keyword,
            "raw_intent": best_intent,
        }

    return best_intent, round(min(best_score, 0.99), 3), {
        "matched_keyword": best_keyword,
        "document": INTENT_TO_DOC.get(best_intent),
    }


def _doc_to_intent(doc_id: str) -> str:
    reverse = {
        "scholarships": "scholarship",
        "events": "events",
        "donation": "donation",
        "volunteer": "volunteer",
        "projects": "projects",
        "contact": "contact",
        "about": "about",
        "faq": "faq",
        "navigation": "more",
    }
    return reverse.get(doc_id, doc_id)
