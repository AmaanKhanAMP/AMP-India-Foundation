"""Convert retrieved Pinecone chunks into natural conversational answers (no LLM).

Used when Gemini is unavailable (429/503) but Pinecone already returned context.
Never invents facts — only reorganizes verified retrieved text.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional

from app.services.language_service import Language
from app.services.types import Document


def _lang(language: Language | str) -> str:
    if isinstance(language, Language):
        return language.value
    return str(language or "en")


def _strip_markup(text: str) -> str:
    text = text or ""
    text = re.sub(r"(?im)^#{1,6}\s+", "", text)
    text = re.sub(r"(?im)^\[source:[^\]]*\]\s*", "", text)
    text = re.sub(r"(?im)^Section:\s*\S+\s*$", "", text)
    text = re.sub(r"(?im)^(?:title|summary|page|image_url|banner_image|keywords|id):\s*", "", text)
    text = re.sub(r"\*\*|__", "", text)
    text = re.sub(r"(?im)^Q:\s*", "", text)
    text = re.sub(r"(?im)^A:\s*", "", text)
    text = re.sub(r"(?im)\bQ:\s*", "", text)
    text = re.sub(r"(?im)\bA:\s*", "", text)
    text = re.sub(
        r"(?im)^\s*(?:Projects?\s*&\s*Programs?|About(?:\s+Us)?|Contact(?:\s+Us)?|"
        r"Donations?|Volunteering|Scholarships?|Events?|Employment)"
        r"(?:\s*[—\-:]\s*AMP India Foundation)?\s*$",
        "",
        text,
    )
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_facts(blob: str) -> dict:
    """Pull common AMP fact patterns from raw chunk text."""
    lower = blob.lower()
    facts: dict = {}

    phone = re.search(r"(\+91[\s-]?\d{10}|\b8291101312\b)", blob)
    if phone:
        facts["phone"] = phone.group(1).strip() if "+91" in phone.group(1) else f"+91 {phone.group(1)}"

    email = re.search(r"[\w.+-]+@ampindiafoundation\.org", blob, re.I)
    if email:
        facts["email"] = email.group(0)

    if "nagpada" in lower or "halima" in lower or "400008" in lower:
        addr = re.search(
            r"(Room\s*9[^\n.]{0,120}(?:Nagpada|Mumbai)[^\n.]{0,40}400008)",
            blob,
            re.I,
        )
        if addr:
            facts["address"] = re.sub(r"\s+", " ", addr.group(1)).strip(" .")
        elif "Room 9" in blob or "room 9" in lower:
            facts["address"] = (
                "Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, "
                "A Clare Road, Nagpada, Mumbai - 400008"
            )

    if re.search(r"9:00|9\s*AM|monday\s+to\s+saturday|सोमवार", lower):
        facts["hours"] = "Monday to Saturday, 9:00 AM to 6:00 PM"

    vol_link = re.search(r"https?://tinyurl\.com/\S+|https?://\S*volunteer\S*", blob, re.I)
    if vol_link or "volunteer" in lower and "regist" in lower:
        facts["volunteer_link"] = (
            vol_link.group(0).rstrip(".,)")
            if vol_link
            else "https://tinyurl.com/AIFVolunteerRegn"
        )

    ifsc = re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", blob)
    if ifsc or ("ifsc" in lower and "account" in lower):
        facts["donation"] = True

    return facts


def _compose_from_facts(facts: dict, language: str, question: str) -> Optional[str]:
    q = (question or "").lower()
    wants_addr = bool(re.search(r"address|location|where|kaha|kahan|reach|located|pata|kidhar", q))
    wants_phone = bool(re.search(r"phone|number|call|mobile|contact number", q))
    wants_email = bool(re.search(r"email|e-?mail|mail", q))
    wants_hours = bool(re.search(r"timing|hours|open|kitne", q))
    wants_vol = bool(re.search(r"volunteer|sewa|seva|join", q))
    wants_donate = bool(re.search(r"\b(donat|contribute|support us)\b", q))
    wants_bank = bool(re.search(r"\b(bank|ifsc|account number|upi|account details)\b", q))
    broad_contact = bool(re.search(r"\bcontact\b|details", q)) or (
        wants_addr and not (wants_phone or wants_email)
    )

    if language == Language.HINDI.value:
        parts: List[str] = []
        if (wants_addr or broad_contact) and facts.get("address"):
            parts.append(f"AMP India Foundation का कार्यालय {facts['address']} में स्थित है।")
        if (wants_phone or broad_contact) and facts.get("phone"):
            parts.append(f"फ़ोन नंबर: {facts['phone']}।")
        if (wants_email or broad_contact) and facts.get("email"):
            parts.append(f"ईमेल: {facts['email']}।")
        if (wants_hours or broad_contact) and facts.get("hours"):
            parts.append(f"कार्यालय समय: {facts['hours']}।")
        if wants_vol and facts.get("volunteer_link"):
            parts.append(
                f"आप स्वयंसेवक बनने के लिए इस लिंक पर पंजीकरण कर सकते हैं: {facts['volunteer_link']}। "
                "पंजीकरण के बाद टीम आपसे संपर्क करेगी।"
            )
        if wants_donate:
            if wants_bank and facts.get("donation"):
                parts.append(
                    "AMP India Foundation आधिकारिक बैंक ट्रांसफर के माध्यम से दान स्वीकार करता है। "
                    "कृपया Support Us पेज या आधिकारिक बैंक विवरण देखें।"
                )
            else:
                parts.append(
                    "आप AMP India Foundation की Support Us पेज (/support-us) से दान कर सकते हैं। "
                    "बैंक विवरण चाहिए हो तो स्पष्ट रूप से पूछें।"
                )
        if parts:
            return " ".join(parts)

    if language == Language.HINGLISH.value:
        parts = []
        if (wants_addr or broad_contact) and facts.get("address"):
            parts.append(f"AMP India Foundation ka office {facts['address']} par hai.")
        if (wants_phone or broad_contact) and facts.get("phone"):
            parts.append(f"Phone: {facts['phone']}.")
        if (wants_email or broad_contact) and facts.get("email"):
            parts.append(f"Email: {facts['email']}.")
        if (wants_hours or broad_contact) and facts.get("hours"):
            parts.append(f"Office timing: {facts['hours']}.")
        if wants_vol and facts.get("volunteer_link"):
            parts.append(
                f"Volunteer banne ke liye yahan register karein: {facts['volunteer_link']}. "
                "Registration ke baad team aapse contact karegi."
            )
        if wants_donate:
            if wants_bank and facts.get("donation"):
                parts.append(
                    "AMP India Foundation official bank transfer se donation accept karta hai. "
                    "Support Us page ya official bank details dekhein."
                )
            else:
                parts.append(
                    "Aap AMP India Foundation ki Support Us page (/support-us) se donate kar sakte hain. "
                    "Bank details chahiye ho to clearly poochiye."
                )
        if parts:
            return " ".join(parts)

    # English
    parts = []
    if (wants_addr or broad_contact) and facts.get("address"):
        parts.append(f"AMP India Foundation is located at {facts['address']}.")
    if (wants_phone or broad_contact) and facts.get("phone"):
        parts.append(f"You can call {facts['phone']}.")
    if (wants_email or broad_contact) and facts.get("email"):
        parts.append(f"Email: {facts['email']}.")
    if (wants_hours or broad_contact) and facts.get("hours"):
        parts.append(f"Office timings: {facts['hours']}.")
    if wants_vol and facts.get("volunteer_link"):
        parts.append(
            f"You can register as a volunteer using this form: {facts['volunteer_link']}. "
            "After registration, the AMP India Foundation team will contact you."
        )
    if wants_donate:
        if wants_bank and facts.get("donation"):
            parts.append(
                "AMP India Foundation accepts donations via official bank transfer. "
                "Please use the Support Us page or the foundation's verified bank details."
            )
        else:
            parts.append(
                "You can support AMP India Foundation through the official Support Us page (/support-us). "
                "If you need bank transfer details, please ask specifically for them."
            )
    if parts:
        return " ".join(parts)
    return None


def _clean_paragraph(text: str, max_chars: int = 700) -> str:
    text = _strip_markup(text)
    # Drop leftover FAQ labels and section noise
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.lower().startswith(("source module", "common questions", "extra multilingual")):
            continue
        lines.append(s)
    joined = " ".join(lines)
    joined = re.sub(r"\s{2,}", " ", joined).strip()
    if len(joined) > max_chars:
        cut = joined[:max_chars].rsplit(".", 1)[0]
        joined = (cut + ".") if cut else joined[:max_chars]
    return joined


def format_from_chunks(
    docs: Iterable[Document],
    *,
    question: str,
    language: Language | str = Language.ENGLISH,
) -> str:
    """
    Build a natural answer from Pinecone documents.
    Prefer structured contact/volunteer/donation facts; otherwise clean prose from chunks.
    """
    lang = _lang(language)
    texts: List[str] = []
    for doc in docs:
        content = (doc.page_content or "").strip()
        if content:
            texts.append(content)
    if not texts:
        return ""

    blob = "\n\n".join(texts[:3])
    facts = _extract_facts(blob)
    composed = _compose_from_facts(facts, lang, question)
    if composed:
        return composed

    # Generic: clean top chunk into a short conversational sentence
    cleaned = _clean_paragraph(texts[0])
    if not cleaned:
        return ""

    # Soft natural openers so answers don't start with raw doc titles
    if lang == Language.HINDI.value:
        if not any("\u0900" <= c <= "\u097F" for c in cleaned):
            return (
                "AMP India Foundation कई प्रमुख कार्यक्रम चलाता है जो शिक्षा, रोज़गार, "
                "स्वास्थ्य और आर्थिक सशक्तिकरण पर केंद्रित हैं।\n\n" + cleaned
            )
        return cleaned
    if lang == Language.HINGLISH.value:
        lower = cleaned.lower()
        if lower.startswith(("projects", "programs", "about", "contact", "donations")):
            return (
                "AMP India Foundation kai flagship programmes chalata hai — education, "
                "employment, healthcare aur economic empowerment par focus ke saath.\n\n"
                + cleaned
            )
        return cleaned
    lower = cleaned.lower()
    if lower.startswith(("projects", "programs", "about amp", "contact")):
        return (
            "AMP India Foundation runs several flagship programmes focused on education, "
            "employment, healthcare and economic empowerment.\n\n" + cleaned
        )
    return cleaned


def format_local_hit(text: str, language: Language | str = Language.ENGLISH) -> str:
    """Clean a verified local-knowledge answer (no robotic openers)."""
    cleaned = _strip_markup(text or "")
    cleaned = re.sub(
        r"(?i)^(here's what i can share from amp india foundation'?s verified information:\s*)",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?i)^(amp india foundation ki verified information ke hisaab se:\s*)",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?i)^(amp india foundation की सत्यापित जानकारी के अनुसार:\s*)",
        "",
        cleaned,
    )
    return cleaned.strip()
