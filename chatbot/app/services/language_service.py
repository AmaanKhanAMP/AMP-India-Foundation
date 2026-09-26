"""Detect English / Hindi / Hinglish and keep session language preference."""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional


class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    HINGLISH = "hinglish"


_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

# Common Roman-Hindi / Hinglish tokens
_HINGLISH_TOKENS = {
    "mujhe",
    "mujhko",
    "mera",
    "meri",
    "mere",
    "mai",
    "main",
    "tum",
    "tumhara",
    "tumhari",
    "tujhe",
    "tujhse",
    "tumse",
    "aap",
    "aapka",
    "aapki",
    "kaise",
    "kaisa",
    "kaisi",
    "kaun",
    "kya",
    "kyun",
    "kab",
    "kahan",
    "kaha",
    "hai",
    "hain",
    "ho",
    "hua",
    "hu",
    "hun",
    "rahe",
    "raha",
    "rahi",
    "rahen",
    "bore",
    "paise",
    "paisa",
    "wajah",
    "door",
    "gareeb",
    "garib",
    "bane",
    "banu",
    "padhai",
    "padhaai",
    "karna",
    "kare",
    "karein",
    "karo",
    "kar",
    "chahiye",
    "chaahiye",
    "batao",
    "bataiye",
    "bataye",
    "madad",
    "jaankari",
    "jankari",
    "ke",
    "ki",
    "ko",
    "se",
    "par",
    "aur",
    "nahi",
    "nahin",
    "please",
    "plz",
    "sir",
    "ji",
    "bhai",
    "didi",
    "naukri",
    "rozgar",
    "mele",
    "mela",
    "bane",
    "banu",
    "banana",
    "liye",
    "ke liye",
}


def detect_language(message: str, session_language: Optional[str] = None) -> Language:
    """
    Auto-detect language.
    - Explicit switch phrases → requested language
    - Devanagari → Hindi
    - Roman Hindi markers → Hinglish
    - Else English (or continue session preference for short follow-ups)
    """
    text = (message or "").strip()
    if not text:
        return Language(session_language) if session_language in {l.value for l in Language} else Language.ENGLISH

    lower = text.lower()
    # Explicit language preference switches
    if re.search(
        r"\b(hindi\s*(me|mein|m[eé])\s*(baat|bolo|reply|jawab)|"
        r"baat\s*(karo|kijiye)\s*hindi|"
        r"hindi\s*akshar|"
        r"devanagari|"
        r"reply in hindi|answer in hindi|speak hindi)\b",
        lower,
    ):
        return Language.HINDI
    if re.search(
        r"\b(english\s*please|in english|reply in english|answer in english|"
        r"speak english|english\s*me\s*(baat|bolo))\b",
        lower,
    ):
        return Language.ENGLISH
    if re.search(
        r"\b(hinglish|roman hindi|roman\s*me|english\s*letters?\s*me)\b",
        lower,
    ):
        return Language.HINGLISH

    if _DEVANAGARI_RE.search(text):
        return Language.HINDI

    tokens = set(re.findall(r"[a-zA-Z']+", lower))
    hinglish_hits = tokens & _HINGLISH_TOKENS

    # Strong Hinglish: multiple roman-hindi tokens, or classic patterns
    if len(hinglish_hits) >= 2:
        return Language.HINGLISH
    if re.search(
        r"\b(mujhe|kaise|chahiye|batao|naukri|ke liye|kya hai|kab hai|kaise kare|kaise bane|"
        r"kaha hai|kahan hai|gareeb hu|garib hu|mai gareeb|main gareeb|"
        r"tum kaun|aap kaun|kya kar rahe|paise chahiye|madad chahiye|help chahiye|"
        r"tujhse|bore ho)\b",
        lower,
    ):
        return Language.HINGLISH

    # Pure English conversational phrases should stay English even mid-Hinglish session
    if re.fullmatch(
        r"(hi+|hii+|hello+|hey+|yo|thanks|thank you|thankyou|bye+|goodbye|"
        r"good\s*(morning|afternoon|evening|night)|goodnight|"
        r"how are you(?: doing)?|how'?s your day|what'?s up|whatsup|"
        r"take care|see you|ok|okay)",
        lower.strip(" !?."),
    ):
        return Language.ENGLISH

    # Short follow-ups: keep session language
    if session_language in {Language.HINDI.value, Language.HINGLISH.value} and len(tokens) <= 6:
        return Language(session_language)

    return Language.ENGLISH


def resolve_session_language(
    detected: Language,
    message: str,
    session_language: Optional[str],
) -> Language:
    """
    Remember preferred language for the session.
    Explicit English greetings/thanks stay English for that turn but do not
    wipe Hindi/Hinglish preference unless the user clearly switches.
    """
    compact = re.sub(r"[^\w\s]", "", (message or "").strip().lower())
    english_switch = compact in {
        "hi",
        "hello",
        "hey",
        "thanks",
        "thank you",
        "bye",
        "goodbye",
        "ok",
        "okay",
    }
    explicit_english = bool(
        re.search(r"\b(english please|in english|reply in english|speak english)\b", compact)
    )
    explicit_hindi = bool(
        re.search(r"\b(hindi me|hindi mein|hindi akshar|reply in hindi|speak hindi)\b", compact)
    )

    if explicit_hindi or detected == Language.HINDI:
        return Language.HINDI
    if explicit_english:
        return Language.ENGLISH
    if detected == Language.HINGLISH:
        return Language.HINGLISH
    if english_switch and session_language in {Language.HINDI.value, Language.HINGLISH.value}:
        # Keep session preference for ongoing chat; greeting replies still localized separately
        return Language(session_language)
    if detected == Language.ENGLISH and len(compact.split()) >= 4:
        return Language.ENGLISH
    if session_language in {l.value for l in Language}:
        return Language(session_language)
    return detected
