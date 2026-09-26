"""Query Normalization Layer — typo / phonetic / synonym fixes BEFORE intent.

Zero Gemini/OpenAI cost. Optional RapidFuzz (≥85%) for out-of-dictionary tokens.
Never mutates verified knowledge — only the user query used for routing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from app.services.text_normalize import SPELL_FIXES, apply_spell_fixes, normalize_whitespace

# Extended spell / phonetic map (applied before RapidFuzz)
_EXTRA_FIXES: Tuple[Tuple[str, str], ...] = (
    # Islamic greetings
    ("asalam walekum", "assalamualaikum"),
    ("asalamualaikum", "assalamualaikum"),
    ("asalamualakium", "assalamualaikum"),
    ("asalamwalekum", "assalamualaikum"),
    ("assalam walekum", "assalamualaikum"),
    ("assalamualaikum", "assalamualaikum"),
    ("assalamu alaikum", "assalamualaikum"),
    ("salaam alaikum", "assalamualaikum"),
    ("salam alaikum", "assalamualaikum"),
    ("asalam", "assalamualaikum"),
    ("assalam", "assalamualaikum"),
    ("salaam", "assalamualaikum"),
    ("slam", "assalamualaikum"),
    ("slm", "assalamualaikum"),
    ("walekum", "wa alaikum assalam"),
    ("walaikum", "wa alaikum assalam"),
    ("walikum", "wa alaikum assalam"),
    ("khudahafiz", "khuda hafiz"),
    ("allahafiz", "allah hafiz"),
    ("jazakalla", "jazakallah"),
    ("alhamdulilah", "alhamdulillah"),
    ("inshaallah", "inshallah"),
    ("insha allah", "inshallah"),
    # Volunteer
    ("voluntar", "volunteer"),
    ("voluntre", "volunteer"),
    ("volnteer", "volunteer"),
    ("volenteer", "volunteer"),
    ("volunter", "volunteer"),
    ("regestration", "registration"),
    ("registraton", "registration"),
    # Employment
    ("emplyoment", "employment"),
    ("emploment", "employment"),
    ("emploiment", "employment"),
    ("emplyment", "employment"),
    ("nokri", "naukri"),
    ("rojgar", "rozgar"),
    ("kaam chahiye", "job chahiye"),
    ("need work", "need job"),
    ("i need work", "i need a job"),
    # Healthcare
    ("helthcare", "healthcare"),
    ("health care", "healthcare"),
    ("helth care", "healthcare"),
    ("medical help", "healthcare"),
    ("doctor help", "healthcare"),
    ("hospital help", "healthcare"),
    # Scholarship
    ("scholar ship", "scholarship"),
    ("scholer", "scholarship"),
    ("scholership", "scholarship"),
    ("scholarhsip", "scholarship"),
    # Donation
    ("donte", "donate"),
    ("donat", "donate"),
    ("donatione", "donation"),
    ("zakat", "donation"),
    ("sadaqah", "donation"),
    ("sadaqa", "donation"),
    # Events
    ("upcomming", "upcoming"),
    ("upoming", "upcoming"),
    ("ivent", "event"),
    ("ivents", "events"),
    ("featured event", "featured event"),
    # Contact
    ("adress", "address"),
    ("adresss", "address"),
    ("addres", "address"),
    ("contat", "contact"),
    ("contcat", "contact"),
    ("phone no", "phone number"),
    ("mobile no", "phone number"),
    ("email id", "email"),
    ("ofis", "office"),
    # Org
    ("amp india", "amp india foundation"),
    ("aidf", "aif"),
    ("asslam", "assalamualaikum"),
    ("what u guys do", "what do you do"),
    ("what you guys do", "what do you do"),
    ("aif ka number", "aif phone number"),
    ("amp ka number", "amp phone number"),
    ("kashmir wala", "kashmir"),
    ("job fair kashmir", "kashmir job fair"),
)

# Token-level dictionary for fuzzy matching (canonical spellings)
_CANONICAL_TOKENS = sorted(
    {
        "assalamualaikum",
        "volunteer",
        "volunteering",
        "employment",
        "scholarship",
        "scholarships",
        "healthcare",
        "donation",
        "donations",
        "donate",
        "address",
        "contact",
        "office",
        "phone",
        "email",
        "upcoming",
        "events",
        "event",
        "featured",
        "registration",
        "naukri",
        "rozgar",
        "placement",
        "interview",
        "resume",
        "mission",
        "vision",
        "project",
        "projects",
        "program",
        "programs",
        "foundation",
        "scholarship",
        "medical",
        "treatment",
        "hospital",
        "timing",
        "timings",
        "location",
        "mumbai",
        "nagpada",
        "bank",
        "ifsc",
        "account",
        "support",
        "empowerment",
        "education",
        "mentorship",
        "training",
        "gallery",
        "testimonial",
        "testimonials",
    },
    key=len,
    reverse=True,
)

# Phrase synonyms → routing hint phrase (appended lightly for intent)
_SYNONYM_EXPAND: Tuple[Tuple[str, str], ...] = (
    (r"\b(job chahiye|naukri chahiye|kaam chahiye|need work|looking for work)\b", " employment job "),
    (r"\b(zakat|sadaqah|sadaqa)\b", " donation support us "),
    (r"\b(medical help|doctor help|hospital help|treatment help)\b", " healthcare medical "),
    (r"\b(padhai|education help)\b", " education scholarship "),
    (r"\b(sewa|seva)\b", " volunteer "),
)

_FUZZY_THRESHOLD = 85
_FUZZY_AVAILABLE = False
try:
    from rapidfuzz import fuzz, process  # type: ignore

    _FUZZY_AVAILABLE = True
except ImportError:  # pragma: no cover
    fuzz = None  # type: ignore
    process = None  # type: ignore


@dataclass
class NormalizedQuery:
    original: str
    normalized: str
    routing_text: str
    fixes_applied: List[str]
    fuzzy_used: bool = False


def _collapse_repeats(text: str) -> str:
    # heellloo → heello (keep doubles for salaam etc. lightly)
    return re.sub(r"(.)\1{2,}", r"\1\1", text)


def _apply_extra_fixes(text: str) -> Tuple[str, List[str]]:
    out = text
    applied: List[str] = []
    for bad, good in _EXTRA_FIXES:
        pattern = rf"(?<![a-zA-Z]){re.escape(bad)}(?![a-zA-Z])"
        new_out, n = re.subn(pattern, good, out, flags=re.I)
        if n:
            applied.append(f"{bad}→{good}")
            out = new_out
    return out, applied


def _fuzzy_fix_tokens(text: str) -> Tuple[str, List[str], bool]:
    if not _FUZZY_AVAILABLE or not text:
        return text, [], False
    tokens = re.findall(r"[A-Za-z\u0900-\u097F']+|[^A-Za-z\u0900-\u097F\s]+|\s+", text)
    applied: List[str] = []
    used = False
    out_parts: List[str] = []
    for tok in tokens:
        if not re.fullmatch(r"[A-Za-z']+", tok) or len(tok) < 4:
            out_parts.append(tok)
            continue
        lower = tok.lower()
        if lower in _CANONICAL_TOKENS:
            out_parts.append(tok)
            continue
        # Skip very common English stopwords
        if lower in {
            "that",
            "this",
            "with",
            "from",
            "have",
            "what",
            "when",
            "where",
            "your",
            "about",
            "please",
            "could",
            "would",
            "there",
            "their",
            "which",
            "foundation",
        }:
            out_parts.append(tok)
            continue
        match = process.extractOne(
            lower,
            _CANONICAL_TOKENS,
            scorer=fuzz.ratio,
            score_cutoff=_FUZZY_THRESHOLD,
        )
        if match:
            canon, score, _ = match
            if canon != lower:
                applied.append(f"{lower}≈{canon}({score})")
                used = True
                # Preserve capitalization lightly
                if tok[0].isupper():
                    canon = canon.capitalize()
                out_parts.append(canon)
                continue
        out_parts.append(tok)
    return "".join(out_parts), applied, used


def _expand_synonyms(text: str) -> str:
    out = text
    for pattern, expansion in _SYNONYM_EXPAND:
        if re.search(pattern, out, re.I):
            out = f"{out} {expansion}"
    return normalize_whitespace(out)


def normalize_query(message: str) -> NormalizedQuery:
    """
    Full normalization pipeline for routing (not for display of original).
    Order: whitespace → collapse repeats → dictionary fixes → RapidFuzz → synonyms.
    """
    original = message or ""
    text = normalize_whitespace(original)
    text = _collapse_repeats(text)
    applied: List[str] = []

    text = apply_spell_fixes(text)
    text, extra = _apply_extra_fixes(text)
    applied.extend(extra)

    fuzzy_text, fuzzy_applied, fuzzy_used = _fuzzy_fix_tokens(text)
    text = fuzzy_text
    applied.extend(fuzzy_applied)

    routing = _expand_synonyms(text)
    # Also keep a clean normalized form without synonym padding for display/cache keys
    normalized = normalize_whitespace(text)

    return NormalizedQuery(
        original=original,
        normalized=normalized,
        routing_text=routing,
        fixes_applied=applied,
        fuzzy_used=fuzzy_used,
    )


_KEYBOARD = re.compile(
    r"^(?:asdf+|qwer(?:ty)?|zxcv+|hjkl+|qwerty|djdjdj+|asdasd+|aaa+|zzz+|xxx+)[a-z]*$",
    re.I,
)


def looks_gibberish(message: str) -> bool:
    """True for spam, keyboard smash, or meaningless character runs."""
    text = (message or "").strip()
    if not text:
        return False
    if re.search(r"[\u0900-\u097F\u0600-\u06FF]", text):
        return False
    compact = re.sub(r"[\s\W_]+", "", text, flags=re.UNICODE)
    if not compact:
        return True
    if len(compact) <= 1:
        return True
    if re.fullmatch(r"\d{4,}", compact):
        return True
    if re.fullmatch(r"(.)\1{4,}", compact, re.I):
        return True
    if re.search(r"(.)\1{3,}", compact, re.I) and len(compact) <= 16:
        return True
    lower = compact.lower()
    if _KEYBOARD.match(lower):
        return True
    # Repeated syllables: lalala, jsjsjs — only on a single smashed token
    if " " not in text and re.search(r"(.{2,3})\1{2,}", lower):
        return True
    if " " not in text and len(lower) >= 12:
        if len(set(lower)) / len(lower) <= 0.28:
            return True
    letters = re.findall(r"[a-zA-Z]", compact)
    vowels = re.findall(r"[aeiouAEIOU]", compact)
    if len(letters) >= 6 and len(vowels) == 0:
        return True
    if len(letters) >= 5 and len(set(lower)) <= 3 and len(vowels) <= 1:
        return True
    if " " not in text and len(letters) >= 10:
        ratio = len(vowels) / max(len(letters), 1)
        if ratio < 0.18:
            return True
    return False


# Back-compat helpers used elsewhere
def normalize_for_match(text: str) -> str:
    return normalize_query(text).normalized.lower()
