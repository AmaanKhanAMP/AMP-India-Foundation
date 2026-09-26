"""LLM-free answer builder from retrieved Pinecone documents.

Used whenever Gemini is unavailable (429 / 503 / timeout / etc.).
Pinecone remains the source of truth — this module only rewrites wording.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

from app.services.knowledge_formatter import format_from_chunks, format_local_hit
from app.services.language_service import Language
from app.services.types import Document


@dataclass
class FallbackResult:
    text: str
    source: str  # PINECONE_ONLY | LOCAL_KNOWLEDGE | NO_RESULT


def _lang(language: Language | str) -> str:
    if isinstance(language, Language):
        return language.value
    return str(language or "en")


def _strip_noise(text: str) -> str:
    text = text or ""
    text = re.sub(r"(?im)^#{1,6}\s+", "", text)
    text = re.sub(r"(?im)^\[source:[^\]]*\]\s*", "", text)
    text = re.sub(r"\*\*|__", "", text)
    text = re.sub(r"(?im)^\s*Q:\s*", "", text)
    text = re.sub(r"(?im)^\s*A:\s*", "", text)
    text = re.sub(r"(?im)\bQ:\s*", "", text)
    text = re.sub(r"(?im)\bA:\s*", "", text)
    text = re.sub(
        r"(?im)^\s*(?:Projects?\s*&\s*Programs?|About(?:\s+Us)?|Contact(?:\s+Us)?)"
        r"(?:\s*[—\-:]\s*AMP India Foundation)?\s*$",
        "",
        text,
    )
    text = re.sub(r"(?im)^(Would you also like|Kya aap yeh bhi).*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _dedupe_sentences(text: str) -> str:
    parts = re.split(r"(?<=[.!?।])\s+", text.strip())
    seen = set()
    kept: List[str] = []
    for part in parts:
        key = re.sub(r"\s+", " ", part.strip().lower())
        if len(key) < 8 or key in seen:
            continue
        seen.add(key)
        kept.append(part.strip())
    return " ".join(kept).strip()


def _merge_docs(docs: Sequence[Document], limit: int = 4) -> str:
    blocks: List[str] = []
    seen_norm = set()
    for doc in docs[:limit]:
        raw = _strip_noise(doc.page_content or "")
        if not raw:
            continue
        norm = re.sub(r"\s+", " ", raw.lower())[:220]
        if norm in seen_norm:
            continue
        seen_norm.add(norm)
        blocks.append(raw)
    return "\n\n".join(blocks)


def _contact_block(blob: str, language: str) -> Optional[str]:
    phone = re.search(r"(\+91[\s-]?\d{10}|\b8291101312\b)", blob)
    email = re.search(r"[\w.+-]+@ampindiafoundation\.org", blob, re.I)
    hours = None
    if re.search(r"9:00|monday\s+to\s+saturday|सोमवार", blob, re.I):
        hours = "Monday to Saturday, 9:00 AM to 6:00 PM"
    address = None
    if re.search(r"nagpada|halima|400008", blob, re.I):
        m = re.search(
            r"(Room\s*9[^\n.]{0,140}(?:Nagpada|Mumbai)[^\n.]{0,40}400008)",
            blob,
            re.I,
        )
        address = (
            re.sub(r"\s+", " ", m.group(1)).strip(" .")
            if m
            else (
                "Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, "
                "A Clare Road, Nagpada, Mumbai - 400008"
            )
        )

    if not (phone or email or address):
        return None

    phone_s = None
    if phone:
        phone_s = phone.group(1).strip()
        if phone_s.isdigit() or phone_s.startswith("8291"):
            phone_s = f"+91 {phone_s.replace('+91', '').strip()}"

    if language == Language.HINDI.value:
        lines = ["आप AMP India Foundation से निम्नलिखित विवरण से संपर्क कर सकते हैं:"]
        if phone_s:
            lines.append(f"फ़ोन: {phone_s}")
        if email:
            lines.append(f"ईमेल: {email.group(0)}")
        if address:
            lines.append(f"पता: {address}")
        if hours:
            lines.append(f"समय: {hours}")
        return "\n".join(lines)

    if language == Language.HINGLISH.value:
        lines = ["Aap AMP India Foundation se in details se contact kar sakte hain:"]
        if phone_s:
            lines.append(f"Phone: {phone_s}")
        if email:
            lines.append(f"Email: {email.group(0)}")
        if address:
            lines.append(f"Address: {address}")
        if hours:
            lines.append(f"Timings: {hours}")
        return "\n".join(lines)

    lines = ["You can contact AMP India Foundation using the following details:"]
    if phone_s:
        lines.append(f"Phone: {phone_s}")
    if email:
        lines.append(f"Email: {email.group(0)}")
    if address:
        lines.append(f"Address: {address}")
    if hours:
        lines.append(f"Office timings: {hours}")
    return "\n".join(lines)


def generate_from_documents(
    docs: Iterable[Document],
    *,
    question: str,
    language: Language | str = Language.ENGLISH,
    intent: Optional[object] = None,
) -> FallbackResult:
    """
    Build a clean conversational answer from Pinecone documents.
    Always routes through Response Composer — never dumps raw chunks.
    """
    doc_list = [d for d in docs if (d.page_content or "").strip()]
    if not doc_list:
        return FallbackResult(text="", source="NO_RESULT")

    # Prefer Response Composer (natural answers, no headings/FAQ dumps)
    try:
        from app.services.intent_router import Intent
        from app.services.response_composer import compose_from_documents

        intent_enum = intent if isinstance(intent, Intent) else None
        composed = compose_from_documents(
            doc_list,
            question=question,
            intent=intent_enum,
            language=language,
        )
        if composed:
            return FallbackResult(text=composed, source="PINECONE_ONLY")
    except Exception:
        pass

    # Keep only the matching event section when the question is section-specific
    question_l = (question or "").lower()
    section_want = None
    if re.search(r"\b(featured events?|feature event)\b", question_l):
        section_want = "featured_event"
    elif re.search(
        r"\b(past events?|previous events?|old events?|last events?|happened in)\b",
        question_l,
    ):
        section_want = "past_events"
    elif re.search(
        r"\b(upcoming|future|next|coming events?|events? (?:are )?(?:happening|coming)|"
        r"medical\s*camps?)\b",
        question_l,
    ):
        section_want = "upcoming_events"

    if section_want:
        filtered = [
            d
            for d in doc_list
            if str((d.metadata or {}).get("section") or "").lower() == section_want
            or (
                section_want == "upcoming_events"
                and "upcoming event" in (d.page_content or "").lower()
            )
            or (
                section_want == "upcoming_events"
                and "home event" in (d.page_content or "").lower()
            )
            or (
                section_want == "featured_event"
                and "featured event" in (d.page_content or "").lower()
            )
            or (
                section_want == "past_events"
                and "past event" in (d.page_content or "").lower()
            )
        ]
        if filtered:
            doc_list = filtered

    lang = _lang(language)
    question_l = (question or "").lower()

    # Only treat as contact when the USER asked for contact/location —
    # never because event venues happen to mention Nagpada/Mumbai.
    non_contact_topic = bool(
        re.search(
            r"\b(event|events|upcoming|featured|past events?|job\s*fair|workshop|"
            r"medical\s*camp|employment\s*drive|volunteer|scholarship|donat|"
            r"project|projects|program|healthcare|mission|vision)\b",
            question_l,
        )
    )
    contactish = (not non_contact_topic) and bool(
        re.search(
            r"\b(phone|email|address|contact|location|where|kaha|kahan|reach|"
            r"office|timing|timings|hours|helpline)\b",
            question_l,
        )
    )
    if contactish:
        merged = _merge_docs(doc_list)
        block = _contact_block(merged, lang)
        if block:
            return FallbackResult(text=block, source="PINECONE_ONLY")

    # Intent-aware natural rewrite from chunks (events/projects/etc.)
    text = format_from_chunks(doc_list, question=question, language=language)
    if not text.strip():
        merged = _merge_docs(doc_list)
        text = _dedupe_sentences(_strip_noise(merged))[:900]

    # Event-specific natural list when we have sectioned event docs
    if section_want and doc_list:
        event_text = _format_event_list(doc_list, section_want, lang)
        if event_text:
            text = event_text

    text = format_local_hit(text, language=language)
    text = _dedupe_sentences(text)
    if not text.strip():
        return FallbackResult(text="", source="NO_RESULT")
    return FallbackResult(text=text.strip(), source="PINECONE_ONLY")


def _parse_event_sort_key(doc: Document, *, upcoming: bool) -> tuple:
    """Sort key: upcoming nearest-first; past most-recent-first."""
    meta = doc.metadata or {}
    raw = (
        str(meta.get("event_date") or meta.get("date") or "")
        or ""
    )
    if not raw:
        m = re.search(r"(?im)^Date:\s*(.+)$", doc.page_content or "")
        raw = m.group(1).strip() if m else ""
    # Try ISO-ish / common formats
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%B %d, %Y", "%d %B %Y"):
        try:
            from datetime import datetime

            dt = datetime.strptime(raw[:32].strip(), fmt)
            # upcoming: ascending; past: descending → invert via negation
            return (0, dt.timestamp() if upcoming else -dt.timestamp())
        except Exception:
            continue
    # Unknown dates last for upcoming, first-ish for past
    return (1, 0.0)


def _format_event_list(docs: Sequence[Document], section: str, language: str) -> str:
    """Build a clean upcoming/past/featured-only answer from event chunks (max 5)."""
    upcoming = section == "upcoming_events"
    past = section == "past_events"
    ordered = list(docs)
    if upcoming or past:
        ordered = sorted(
            ordered,
            key=lambda d: _parse_event_sort_key(d, upcoming=upcoming),
        )
    items: List[str] = []
    for doc in ordered[:5]:
        content = _strip_noise(doc.page_content or "")
        if not content:
            continue
        title = (doc.metadata or {}).get("event_title")
        if not title:
            m = re.search(
                r"(?im)^##\s*(?:Upcoming event|Featured event|Home event|Past event)\s*:\s*(.+)$",
                doc.page_content or "",
            )
            title = m.group(1).strip() if m else None
        desc = None
        dm = re.search(r"(?im)^Description:\s*(.+)$", doc.page_content or "")
        if dm:
            desc = dm.group(1).strip()
        date = None
        dt = re.search(r"(?im)^Date:\s*(.+)$", doc.page_content or "")
        if dt:
            date = dt.group(1).strip()
        venue = None
        vm = re.search(r"(?im)^Venue:\s*(.+)$", doc.page_content or "")
        if vm:
            venue = vm.group(1).strip()
        line = title or content.split("\n")[0][:100]
        extras = []
        if date:
            extras.append(date)
        if venue:
            extras.append(venue)
        if extras:
            line = f"{line} ({', '.join(extras)})"
        if desc:
            line = f"{line} — {desc}"
        items.append(f"• {line}")

    if not items:
        return ""

    if language == Language.HINDI.value:
        if section == "past_events":
            intro = "AMP India Foundation के पिछले कार्यक्रम:"
        elif section == "featured_event":
            intro = "AMP India Foundation का फीचर्ड इवेंट:"
        else:
            intro = "AMP India Foundation के आगामी कार्यक्रम:"
    elif language == Language.HINGLISH.value:
        if section == "past_events":
            intro = "AMP India Foundation ke past events:"
        elif section == "featured_event":
            intro = "AMP India Foundation ka featured event:"
        else:
            intro = "AMP India Foundation ke upcoming events:"
    else:
        if section == "past_events":
            intro = "Here are AMP India Foundation's past events:"
        elif section == "featured_event":
            intro = "Here is AMP India Foundation's featured event:"
        else:
            intro = "Here are AMP India Foundation's upcoming events:"

    return intro + "\n\n" + "\n".join(items[:5])



def generate_from_local(
    text: str,
    *,
    language: Language | str = Language.ENGLISH,
) -> FallbackResult:
    cleaned = format_local_hit(text or "", language=language)
    cleaned = _dedupe_sentences(_strip_noise(cleaned))
    if not cleaned:
        return FallbackResult(text="", source="NO_RESULT")
    return FallbackResult(text=cleaned, source="LOCAL_KNOWLEDGE")
