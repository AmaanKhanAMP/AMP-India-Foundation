"""Verified local knowledge fallback when Pinecone confidence is low."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.config import get_settings
from app.services.contact_facts import ADDRESS, EMAIL, OFFICE_TIMINGS, PHONE
from app.services.intent_router import Intent
from app.services.language_service import Language


@dataclass
class LocalHit:
    text: str
    source: str
    score: float


_VERIFIED: List[Tuple[Tuple[str, ...], dict]] = [
    (
        ("phone", "mobile", "telephone", "number", "call", "helpline"),
        {
            Language.ENGLISH.value: (
                f"You can reach AMP India Foundation by phone at {PHONE}. "
                f"Office hours are {OFFICE_TIMINGS}."
            ),
            Language.HINDI.value: (
                f"आप AMP India Foundation से {PHONE} पर संपर्क कर सकते हैं। "
                f"कार्यालय समय: {OFFICE_TIMINGS}।"
            ),
            Language.HINGLISH.value: (
                f"Aap AMP India Foundation se {PHONE} par contact kar sakte hain. "
                f"Office timing: {OFFICE_TIMINGS}."
            ),
        },
    ),
    (
        ("email", "e-mail", "mail"),
        {
            Language.ENGLISH.value: (
                f"You can email AMP India Foundation at {EMAIL}. "
                "We typically reply within 24 hours."
            ),
            Language.HINDI.value: (
                f"AMP India Foundation को {EMAIL} पर ईमेल करें। "
                "हम आमतौर पर 24 घंटे में उत्तर देते हैं।"
            ),
            Language.HINGLISH.value: (
                f"AMP India Foundation ko {EMAIL} par email karein. "
                "Hum usually 24 hours me reply karte hain."
            ),
        },
    ),
    (
        ("address", "location", "where", "reach", "office", "kaha", "kahan", "nagpada"),
        {
            Language.ENGLISH.value: (
                f"The AMP India Foundation office is at {ADDRESS}. "
                f"You can also call {PHONE} or email {EMAIL}."
            ),
            Language.HINDI.value: (
                f"AMP India Foundation का कार्यालय: {ADDRESS}. "
                f"फ़ोन: {PHONE}, ईमेल: {EMAIL}."
            ),
            Language.HINGLISH.value: (
                f"AMP India Foundation ka office: {ADDRESS}. "
                f"Phone: {PHONE}, email: {EMAIL}."
            ),
        },
    ),
    (
        ("timing", "timings", "hours", "open", "kitne baje"),
        {
            Language.ENGLISH.value: (
                f"AMP India Foundation office timings are {OFFICE_TIMINGS}. "
                "The office is closed on Sundays."
            ),
            Language.HINDI.value: (
                f"कार्यालय समय: {OFFICE_TIMINGS}. रविवार को बंद रहता है।"
            ),
            Language.HINGLISH.value: (
                f"Office timing: {OFFICE_TIMINGS}. Sunday ko band rehta hai."
            ),
        },
    ),
    (
        ("contact",),
        {
            Language.ENGLISH.value: (
                f"You can contact AMP India Foundation at {PHONE}, email {EMAIL}. "
                f"Office timings: {OFFICE_TIMINGS}. Address: {ADDRESS}."
            ),
            Language.HINDI.value: (
                f"संपर्क: {PHONE}, ईमेल: {EMAIL}. समय: {OFFICE_TIMINGS}. पता: {ADDRESS}."
            ),
            Language.HINGLISH.value: (
                f"Contact: {PHONE}, email: {EMAIL}. Timing: {OFFICE_TIMINGS}. Address: {ADDRESS}."
            ),
        },
    ),
    (
        ("volunteer", "volunteering"),
        {
            Language.ENGLISH.value: (
                "You can become a volunteer with AMP India Foundation by registering through the "
                "official volunteer registration form at https://tinyurl.com/AIFVolunteerRegn. "
                f"After registration, the team will contact you. You may also call {PHONE} "
                f"or email {EMAIL}."
            ),
            Language.HINDI.value: (
                "आप AMP India Foundation के साथ स्वयंसेवक बनने के लिए "
                "https://tinyurl.com/AIFVolunteerRegn पर पंजीकरण कर सकते हैं। "
                f"पंजीकरण के बाद टीम संपर्क करेगी। फ़ोन: {PHONE}, ईमेल: {EMAIL}."
            ),
            Language.HINGLISH.value: (
                "Aap AMP India Foundation ke saath volunteer banne ke liye "
                "https://tinyurl.com/AIFVolunteerRegn par register kar sakte hain. "
                f"Registration ke baad team contact karegi. Phone: {PHONE}, email: {EMAIL}."
            ),
        },
    ),
    (
        ("donate", "donation", "ifsc", "bank"),
        {
            Language.ENGLISH.value: (
                "You can support AMP India Foundation via direct bank transfer to Kotak Mahindra — "
                "Account Name: AMP India Foundation, Account Number: 3114476665, "
                "IFSC: KKBK0001348 (Savings). For help, call "
                f"{PHONE} or email {EMAIL}."
            ),
            Language.HINDI.value: (
                "AMP India Foundation का समर्थन Kotak Mahindra बैंक ट्रांसफर से करें — "
                "खाता: AMP India Foundation, संख्या: 3114476665, IFSC: KKBK0001348. "
                f"मदद: {PHONE} / {EMAIL}."
            ),
            Language.HINGLISH.value: (
                "AMP India Foundation ko Kotak Mahindra bank transfer se support kar sakte hain — "
                "Account: AMP India Foundation, Number: 3114476665, IFSC: KKBK0001348. "
                f"Help: {PHONE} / {EMAIL}."
            ),
        },
    ),
]


def _lang_key(language: Language | str) -> str:
    if isinstance(language, Language):
        return language.value
    return str(language or "en")


@lru_cache
def _knowledge_snippets() -> List[Tuple[str, str]]:
    settings = get_settings()
    root = Path(settings.knowledge_dir)
    snippets: List[Tuple[str, str]] = []
    if not root.is_dir():
        return snippets
    for path in sorted(root.glob("*")):
        if path.suffix.lower() not in {".txt", ".md"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        block = re.sub(r"\s+", " ", text).strip()[:1200]
        if block:
            snippets.append((path.stem, block))
    return snippets


def lookup_local(
    query: str,
    *,
    intent: Optional[Intent] = None,
    language: Language | str = Language.ENGLISH,
) -> Optional[LocalHit]:
    q = (query or "").lower()
    lang = _lang_key(language)
    best: Optional[LocalHit] = None

    for keywords, answers in _VERIFIED:
        hits = [kw for kw in keywords if kw in q]
        if not hits:
            if intent == Intent.CONTACT and keywords == ("contact",):
                hits = ["contact"]
            elif intent == Intent.VOLUNTEERING and "volunteer" in keywords:
                hits = ["volunteer"]
            elif intent == Intent.DONATIONS and "donate" in keywords:
                hits = ["donate"]
            else:
                continue
        score = len(hits) * 2.0 + max(len(h) for h in hits) / 10.0
        answer = answers.get(lang) or answers[Language.ENGLISH.value]
        if best is None or score > best.score:
            best = LocalHit(text=answer, source=f"verified:{hits[0]}", score=score)

    if best and best.score >= 2.0:
        return best

    tokens = set(re.findall(r"[a-z0-9]{3,}", q))
    file_best: Optional[LocalHit] = None
    for source, block in _knowledge_snippets():
        block_l = block.lower()
        overlap = sum(1 for tok in tokens if tok in block_l)
        if overlap < 2:
            continue
        score = float(overlap)
        if source.replace("_", " ") in q or any(tok in source for tok in tokens):
            score += 2.0
        if file_best is None or score > file_best.score:
            preview = block[:500].rsplit(".", 1)[0] + "."
            file_best = LocalHit(text=preview.strip(), source=f"knowledge:{source}", score=score)

    if file_best and file_best.score >= 3.0:
        return file_best

    return best if best and best.score >= 1.5 else None


def naturalize_faq_answer(raw: str, language: Language | str = Language.ENGLISH) -> str:
    """Legacy helper — prefer knowledge_formatter.format_from_chunks for Pinecone text."""
    from app.services.knowledge_formatter import format_local_hit

    return format_local_hit(raw or "", language=language)
