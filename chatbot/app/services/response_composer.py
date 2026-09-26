"""Response Composer — turn facts/context into natural assistant replies.

Retrieved documents are CONTEXT ONLY. Never return raw Pinecone/CMS/markdown.
Every outbound answer must pass through compose() / clean_response().
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Sequence

from app.services.builtin_answers import answer_builtin, wants_bank_details
from app.services.intent_router import Intent
from app.services.language_service import Language
from app.services.types import Document

# Soft word budget by topic (approx; not hard truncation mid-sentence unless huge)
_MAX_WORDS = {
    "greeting": 40,
    "contact": 80,
    "location": 90,
    "donation": 110,
    "volunteer": 110,
    "healthcare": 110,
    "employment": 120,
    "scholarship": 110,
    "about": 100,
    "projects": 120,
    "events": 150,
    "default": 130,
}

_SOURCE_NOISE = re.compile(
    r"(?i)\b("
    r"cms_events|cms_gallery|cms_footer|cms_home|cms_projects|cms_testimonials|"
    r"backend_events|backend_contact|backend_about|backend_faq|backend_projects|"
    r"backend_donations|backend_volunteer|backend_scholarships|"
    r"about_aif|faq\.txt|donations\.md|projects\.md|knowledge/"
    r")\b"
)

_HEADING_LINE = re.compile(
    r"^(?:#{1,6}\s+.*|"
    r"projects?\s*&\s*programs?.*|"
    r"scholarship programs?|"
    r"donate\s*/\s*support us|"
    r"support us\s*—.*|"
    r"amp india foundation\s*—\s*.*|"
    r"section:\s*\S+|"
    r"title:\s*.*|summary:\s*.*"
    r")\s*$",
    re.I | re.M,
)

_FAQ_LINE = re.compile(
    r"^\s*(?:Q:|A:)\s*.*$|"
    r"^\s*what (?:jobs|services|programs?|projects?) do you (?:provide|offer)\??\s*$|"
    r"^\s*how can i (?:donate|volunteer|apply)\??\s*$",
    re.I | re.M,
)

_META_LINE = re.compile(
    r"^\s*\[source:[^\]]*\]\s*|"
    r"^\s*source\s*:\s*\S+",
    re.I | re.M,
)


def clean_response(text: str, *, max_words: int = 150) -> str:
    """Strip retrieval artifacts before the user ever sees the answer."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n")
    # Remove fenced code / heavy markdown emphasis
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\*\*|__", "", text)
    text = _SOURCE_NOISE.sub("", text)

    kept: List[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            if kept and kept[-1] != "":
                kept.append("")
            continue
        if _HEADING_LINE.match(s) or _FAQ_LINE.match(s) or _META_LINE.match(s):
            continue
        if re.match(r"(?i)^(question|answer|faq|source)\s*:", s):
            continue
        if re.match(r"(?i)^(projects?\s*&\s*programs?|donation\.md)\b", s):
            continue
        if s.lower() in {
            "projects & programs",
            "scholarship programs",
            "donate / support us",
            "support us",
            "what jobs do you provide?",
        }:
            continue
        # Drop lines that are only document titles
        if re.fullmatch(r"(?i)amp india foundation[\s\w&/\-—–]*", s) and len(s) < 60:
            if "located" not in s.lower() and "foundation is" not in s.lower():
                continue
        kept.append(s)

    text = "\n".join(kept)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    # Collapse duplicated adjacent paragraphs / repeated phone
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    deduped: List[str] = []
    seen = set()
    phone_once = False
    for p in paras:
        key = re.sub(r"\s+", " ", p.lower())[:160]
        if key in seen:
            continue
        if "8291101312" in key:
            if phone_once and key.startswith(("phone", "for assistance", "madad", "सहायता")):
                continue
            phone_once = True
        seen.add(key)
        deduped.append(p)
    text = "\n\n".join(deduped)

    words = text.split()
    if len(words) > max_words:
        # Prefer cutting at sentence boundary
        cut = " ".join(words[:max_words])
        if "." in cut:
            cut = cut.rsplit(".", 1)[0] + "."
        text = cut.strip()
    return text.strip()


def _budget_for(intent: Optional[Intent], question: str) -> int:
    q = (question or "").lower()
    if intent == Intent.CONTACT or re.search(r"\b(address|location|timing)\b", q):
        return _MAX_WORDS["contact"]
    if intent in {Intent.UPCOMING_EVENTS, Intent.PAST_EVENTS, Intent.FEATURED_EVENT, Intent.EVENTS}:
        return _MAX_WORDS["events"]
    if intent == Intent.DONATIONS:
        return _MAX_WORDS["donation"]
    if intent == Intent.VOLUNTEERING:
        return _MAX_WORDS["volunteer"]
    if intent == Intent.EMPLOYMENT:
        return _MAX_WORDS["employment"]
    if intent == Intent.MEDICAL:
        return _MAX_WORDS["healthcare"]
    if intent == Intent.SCHOLARSHIPS:
        return _MAX_WORDS["scholarship"]
    if intent == Intent.AMP_KNOWLEDGE:
        return _MAX_WORDS["about"]
    if intent == Intent.PROJECTS:
        return _MAX_WORDS["projects"]
    if intent == Intent.EDUCATION:
        return _MAX_WORDS["projects"]
    if intent == Intent.ECONOMIC_EMPOWERMENT:
        return _MAX_WORDS["projects"]
    return _MAX_WORDS["default"]


def _looks_like_raw_retrieval(text: str) -> bool:
    if not text:
        return True
    lower = text.lower()
    if re.search(r"(?m)^(#{1,6}\s|q:\s|a:\s|section:\s|title:\s|\[source:)", text, re.I):
        return True
    if "projects & programs" in lower or "scholarship programs" in lower:
        return True
    if "what jobs do you provide" in lower:
        return True
    if lower.startswith("amp india foundation —") or lower.startswith("amp india foundation -"):
        return True
    # Many FAQ dumps start by repeating a question
    if re.match(r"(?i)^(what|how|when|where|why)\b.+\?\s", text) and "\n" in text[:120]:
        return True
    return False


def _compose_events(docs: Sequence[Document], language: str, *, intent: Optional[Intent] = None) -> str:
    items: List[str] = []
    ordered = list(docs)
    upcoming = intent == Intent.UPCOMING_EVENTS
    past = intent == Intent.PAST_EVENTS
    if upcoming or past:
        def _key(doc: Document) -> tuple:
            meta = doc.metadata or {}
            raw = str(meta.get("event_date") or meta.get("date") or "")
            if not raw:
                m = re.search(r"(?im)^Date:\s*(.+)$", doc.page_content or "")
                raw = m.group(1).strip() if m else ""
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%B %d, %Y", "%d %B %Y"):
                try:
                    from datetime import datetime

                    dt = datetime.strptime(raw[:32].strip(), fmt)
                    return (0, dt.timestamp() if upcoming else -dt.timestamp())
                except Exception:
                    continue
            return (1, 0.0)

        ordered = sorted(ordered, key=_key)

    for doc in ordered[:5]:
        raw = doc.page_content or ""
        raw = re.sub(r"(?im)^#{1,6}\s*", "", raw)
        raw = re.sub(r"(?im)^section:\s*\S+\s*", "", raw)
        lines = [ln.strip(" -•*") for ln in raw.splitlines() if ln.strip()]
        if not lines:
            continue
        title = lines[0]
        title = re.sub(r"(?i)^(upcoming|past|featured|home)\s*event:\s*", "", title).strip()
        extra = []
        for ln in lines[1:4]:
            if re.search(r"(?i)date|venue|location|time|hyderabad|mumbai|delhi", ln):
                extra.append(ln)
        block = title
        if extra:
            block = f"{title} — " + "; ".join(extra[:2])
        if block and block.lower() not in {i.lower() for i in items}:
            items.append(block)
    if not items:
        return ""
    if language == "hi":
        head = "AMP India Foundation के इवेंट्स:"
    elif language == "hinglish":
        head = "AMP India Foundation ke events:"
    else:
        if intent == Intent.PAST_EVENTS:
            head = "Here are AMP India Foundation's past events:"
        elif intent == Intent.FEATURED_EVENT:
            head = "Here is AMP India Foundation's featured event:"
        elif intent == Intent.UPCOMING_EVENTS:
            head = "Here are AMP India Foundation's upcoming events:"
        else:
            head = "Here are AMP India Foundation events:"
    bullets = "\n".join(f"• {i}" for i in items[:5])
    return f"{head}\n\n{bullets}"



def compose_from_documents(
    docs: Iterable[Document],
    *,
    question: str,
    intent: Optional[Intent] = None,
    language: Language | str = Language.ENGLISH,
) -> str:
    """Build a natural answer from retrieved docs without dumping chunks."""
    lang = language.value if isinstance(language, Language) else str(language or "en")
    doc_list = [d for d in docs if (d.page_content or "").strip()]

    # Prefer verified builtin rewrite when intent is static-shaped
    builtin = answer_builtin(question, intent=intent, language=language)
    if builtin and intent not in {
        Intent.UPCOMING_EVENTS,
        Intent.PAST_EVENTS,
        Intent.FEATURED_EVENT,
        Intent.EVENTS,
    }:
        return clean_response(builtin, max_words=_budget_for(intent, question))

    if wants_bank_details(question):
        bank = answer_builtin(question, intent=Intent.DONATIONS, language=language)
        if bank:
            return clean_response(bank, max_words=_budget_for(Intent.DONATIONS, question))

    if intent in {
        Intent.UPCOMING_EVENTS,
        Intent.PAST_EVENTS,
        Intent.FEATURED_EVENT,
        Intent.EVENTS,
    }:
        text = _compose_events(doc_list, lang, intent=intent)
        if text:
            return clean_response(text, max_words=_budget_for(intent, question))

    # Generic: take factual sentences, not headings
    facts: List[str] = []
    for doc in doc_list[:4]:
        raw = doc.page_content or ""
        raw = re.sub(r"(?im)^#{1,6}\s+.*$", "", raw)
        raw = re.sub(r"(?im)^(q|a):\s*", "", raw)
        for sent in re.split(r"(?<=[.!?।])\s+", raw):
            s = sent.strip()
            if len(s) < 25:
                continue
            if _looks_like_raw_retrieval(s):
                continue
            if re.match(r"(?i)^(what|how|when|where)\b.+\?$", s):
                continue
            facts.append(s)
            if len(facts) >= 4:
                break
        if len(facts) >= 4:
            break

    if not facts and builtin:
        return clean_response(builtin, max_words=_budget_for(intent, question))

    if not facts:
        return ""

    if lang == "hi":
        lead = "संक्षेप में:"
    elif lang == "hinglish":
        lead = "Short me:"
    else:
        lead = ""

    body = " ".join(facts[:3])
    text = f"{lead}\n\n{body}".strip() if lead else body
    return clean_response(text, max_words=_budget_for(intent, question))


def compose_final(
    *,
    question: str,
    draft: Optional[str],
    intent: Optional[Intent] = None,
    language: Language | str = Language.ENGLISH,
    docs: Optional[Sequence[Document]] = None,
) -> str:
    """
    Final gate before returning to the user.
    If draft looks like raw retrieval, rebuild from builtin/docs.
    """
    budget = _budget_for(intent, question)
    draft = (draft or "").strip()

    if draft and not _looks_like_raw_retrieval(draft):
        return clean_response(draft, max_words=budget)

    if docs:
        rebuilt = compose_from_documents(
            docs, question=question, intent=intent, language=language
        )
        if rebuilt:
            return rebuilt

    builtin = answer_builtin(question, intent=intent, language=language)
    if builtin:
        return clean_response(builtin, max_words=budget)

    if draft:
        return clean_response(draft, max_words=budget)
    return ""
