"""Emergency NGO knowledge — always available when CMS / Pinecone / Gemini fail.

This layer is intentionally hardcoded with verified AMP India Foundation facts.
It must never invent dates, bank numbers, or unpublished event details.

Kept separate from contact_facts.py (legacy helpers remain for rollback).
"""

from __future__ import annotations

import re
from typing import Optional

from app.services.contact_facts import ADDRESS, EMAIL, OFFICE_TIMINGS, PHONE
from app.services.intent_router import Intent
from app.services.language_service import Language

# Canonical volunteer registration (verified public link used across knowledge)
VOLUNTEER_REGISTRATION = "https://tinyurl.com/AIFVolunteerRegn"
SUPPORT_US_PATH = "/support-us"
WEBSITE = "https://ampindiafoundation.org"

FINAL_APOLOGY = {
    Language.ENGLISH.value: (
        "I'm sorry, I couldn't find verified information about that in the current "
        "AMP India Foundation knowledge base.\n\n"
        "Please contact us:\n"
        f"📞 {PHONE}\n"
        f"✉️ {EMAIL}"
    ),
    Language.HINDI.value: (
        "मुझे खेद है — वर्तमान AMP India Foundation ज्ञान आधार में इसके बारे में "
        "सत्यापित जानकारी नहीं मिली।\n\n"
        "कृपया संपर्क करें:\n"
        f"📞 {PHONE}\n"
        f"✉️ {EMAIL}"
    ),
    Language.HINGLISH.value: (
        "Maaf kijiye — current AMP India Foundation knowledge base me iske baare me "
        "verified information nahi mili.\n\n"
        "Please contact karein:\n"
        f"📞 {PHONE}\n"
        f"✉️ {EMAIL}"
    ),
}


def _pick(block: dict, language: Language | str) -> str:
    lang = language.value if isinstance(language, Language) else str(language or "en")
    return block.get(lang) or block.get(Language.ENGLISH.value) or ""


_ABOUT = {
    "en": (
        "AMP India Foundation (AIF) is a non-profit organisation working to empower "
        "communities through education, employment, healthcare, scholarships, and "
        "economic empowerment.\n\n"
        "Mission: Enable underprivileged youth and families with skills, opportunity, "
        "and support so they can build a dignified future.\n\n"
        "Vision: A society where every deserving individual has access to education, "
        "livelihood, and healthcare support.\n\n"
        "Core focus areas include Education, Employment & job fairs, Scholarships, "
        "Healthcare, Economic empowerment, volunteering, and community events.\n\n"
        f"Contact: {PHONE} | {EMAIL}\n"
        f"Office: {ADDRESS}\n"
        f"Timings: {OFFICE_TIMINGS}"
    ),
    "hi": (
        "AMP India Foundation (AIF) एक गैर-लाभकारी संस्था है जो शिक्षा, रोज़गार, "
        "स्वास्थ्य, छात्रवृत्ति और आर्थिक सशक्तिकरण के माध्यम से समुदायों को सशक्त बनाती है।\n\n"
        "मिशन: वंचित युवाओं और परिवारों को कौशल, अवसर और सहायता देना।\n\n"
        "विजन: एक ऐसा समाज जहाँ हर योग्य व्यक्ति को शिक्षा, आजीविका और स्वास्थ्य सहायता मिले।\n\n"
        f"संपर्क: {PHONE} | {EMAIL}\n"
        f"पता: {ADDRESS}\n"
        f"समय: {OFFICE_TIMINGS}"
    ),
    "hinglish": (
        "AMP India Foundation (AIF) ek non-profit organisation hai jo education, "
        "employment, healthcare, scholarships aur economic empowerment ke through "
        "communities ko empower karti hai.\n\n"
        "Mission: Underprivileged youth aur families ko skills, opportunity aur support dena.\n\n"
        "Vision: Har deserving individual ko education, livelihood aur healthcare access mile.\n\n"
        f"Contact: {PHONE} | {EMAIL}\n"
        f"Office: {ADDRESS}\n"
        f"Timings: {OFFICE_TIMINGS}"
    ),
}

_CONTACT = {
    "en": (
        f"You can contact AMP India Foundation at:\n\n"
        f"📞 Phone: {PHONE}\n"
        f"✉️ Email: {EMAIL}\n"
        f"📍 Address: {ADDRESS}\n"
        f"🕒 Office timings: {OFFICE_TIMINGS} (closed on Sundays)."
    ),
    "hi": (
        f"AMP India Foundation से संपर्क करें:\n\n"
        f"📞 फ़ोन: {PHONE}\n"
        f"✉️ ईमेल: {EMAIL}\n"
        f"📍 पता: {ADDRESS}\n"
        f"🕒 समय: {OFFICE_TIMINGS} (रविवार बंद)।"
    ),
    "hinglish": (
        f"AMP India Foundation se contact karein:\n\n"
        f"📞 Phone: {PHONE}\n"
        f"✉️ Email: {EMAIL}\n"
        f"📍 Address: {ADDRESS}\n"
        f"🕒 Timings: {OFFICE_TIMINGS} (Sunday band)."
    ),
}

_VOLUNTEER = {
    "en": (
        "You can volunteer with AMP India Foundation to support education, events, "
        "community outreach, and other programmes.\n\n"
        "Process:\n"
        "1. Share your interest and skills.\n"
        "2. Register using the official form.\n"
        "3. The team will follow up with next steps.\n\n"
        f"Registration link: {VOLUNTEER_REGISTRATION}\n\n"
        f"Questions? Call {PHONE} or email {EMAIL}."
    ),
    "hi": (
        "आप AMP India Foundation के साथ स्वयंसेवक बनकर शिक्षा, इवेंट्स और सामुदायिक "
        "कार्यक्रमों में सहयोग कर सकते हैं।\n\n"
        f"पंजीकरण लिंक: {VOLUNTEER_REGISTRATION}\n\n"
        f"सवाल हों तो {PHONE} या {EMAIL} पर संपर्क करें।"
    ),
    "hinglish": (
        "Aap AMP India Foundation ke saath volunteer ban kar education, events aur "
        "community programmes me madad kar sakte hain.\n\n"
        f"Registration link: {VOLUNTEER_REGISTRATION}\n\n"
        f"Sawal ho to {PHONE} ya {EMAIL} par contact karein."
    ),
}

_DONATION = {
    "en": (
        "Thank you for wanting to support AMP India Foundation.\n\n"
        "You can donate via the official Support Us page on the website "
        f"({SUPPORT_US_PATH}).\n\n"
        "For guidance on donation methods, please use the Support Us page or contact "
        f"the foundation at {PHONE} / {EMAIL}.\n\n"
        "Bank transfer details are shared only when you specifically ask for them "
        "and only from verified sources."
    ),
    "hi": (
        "AMP India Foundation का समर्थन करने के लिए धन्यवाद।\n\n"
        f"आधिकारिक Support Us पेज ({SUPPORT_US_PATH}) से दान कर सकते हैं।\n\n"
        f"मार्गदर्शन के लिए {PHONE} या {EMAIL} पर संपर्क करें।\n\n"
        "बैंक विवरण केवल स्पष्ट अनुरोध पर और सत्यापित स्रोत से ही साझा किए जाते हैं।"
    ),
    "hinglish": (
        "AMP India Foundation support karne ke liye shukriya.\n\n"
        f"Official Support Us page ({SUPPORT_US_PATH}) se donate kar sakte hain.\n\n"
        f"Guidance ke liye {PHONE} ya {EMAIL} par contact karein.\n\n"
        "Bank details sirf tab share kiye jate hain jab aap clearly poochein."
    ),
}

_EMPLOYMENT = {
    "en": (
        "AMP India Foundation supports employment through career guidance, resume "
        "and interview preparation, placement assistance, and job fairs / employment drives.\n\n"
        "Ask about upcoming job fairs or employment events for the latest schedule, "
        f"or contact {PHONE} / {EMAIL} for guidance."
    ),
    "hi": (
        "AMP India Foundation रोज़गार सहायता, करियर मार्गदर्शन, रिज़्यूमे/इंटरव्यू तैयारी, "
        "प्लेसमेंट और जॉब फेयर के माध्यम से मदद करता है।\n\n"
        f"नवीनतम जानकारी के लिए {PHONE} या {EMAIL} पर संपर्क करें।"
    ),
    "hinglish": (
        "AMP India Foundation employment support, career guidance, resume/interview "
        "preparation, placement aur job fairs ke through madad karti hai.\n\n"
        f"Latest schedule ke liye upcoming job fairs poochiye, ya {PHONE} / {EMAIL} par contact karein."
    ),
}

_SCHOLARSHIP = {
    "en": (
        "AMP India Foundation offers scholarship and education-support pathways for "
        "deserving students.\n\n"
        "Share whether you need eligibility, documents, or application guidance, and "
        f"we will help from verified information. You can also call {PHONE} or email {EMAIL}."
    ),
    "hi": (
        "AMP India Foundation योग्य छात्रों के लिए छात्रवृत्ति और शिक्षा सहायता प्रदान करता है।\n\n"
        f"पात्रता या आवेदन प्रक्रिया पूछें, या {PHONE} / {EMAIL} पर संपर्क करें।"
    ),
    "hinglish": (
        "AMP India Foundation deserving students ke liye scholarships aur education "
        "support pathways provide karti hai.\n\n"
        f"Eligibility ya application guidance poochiye, ya {PHONE} / {EMAIL} par contact karein."
    ),
}

_HEALTHCARE = {
    "en": (
        "AMP India Foundation supports healthcare through medical camps, health "
        "awareness, and assistance pathways for families in need.\n\n"
        "This is programme support — not a substitute for emergency medical care.\n\n"
        f"For guidance, contact {PHONE} or {EMAIL}, and ask about upcoming medical camps "
        "if you want scheduled event details."
    ),
    "hi": (
        "AMP India Foundation मेडिकल कैंप, स्वास्थ्य जागरूकता और जरूरतमंद परिवारों "
        "के लिए सहायता मार्गों के माध्यम से स्वास्थ्य क्षेत्र में काम करता है।\n\n"
        f"मार्गदर्शन के लिए {PHONE} या {EMAIL} पर संपर्क करें।"
    ),
    "hinglish": (
        "AMP India Foundation medical camps, health awareness aur needy families ke "
        "liye healthcare support pathways ke through kaam karti hai.\n\n"
        "Yeh emergency hospital care ka substitute nahi hai.\n\n"
        f"Guidance ke liye {PHONE} ya {EMAIL} par contact karein."
    ),
}

_EDUCATION = {
    "en": (
        "Education is a core focus of AMP India Foundation — including academic "
        "support, skill-building, scholarships, and related youth programmes.\n\n"
        f"Ask about scholarships, training, or mentorship, or contact {PHONE} / {EMAIL}."
    ),
    "hi": (
        "शिक्षा AMP India Foundation का मुख्य फोकस है — शैक्षणिक सहायता, कौशल विकास, "
        "छात्रवृत्ति और युवा कार्यक्रम।\n\n"
        f"विवरण के लिए {PHONE} या {EMAIL} पर संपर्क करें।"
    ),
    "hinglish": (
        "Education AMP India Foundation ka core focus hai — academic support, "
        "skill-building, scholarships aur youth programmes.\n\n"
        f"Details ke liye {PHONE} ya {EMAIL} par contact karein."
    ),
}

_ECONOMIC = {
    "en": (
        "AMP India Foundation works on economic empowerment so families can build "
        "stable livelihoods through skills, guidance, and community programmes.\n\n"
        f"For current opportunities, contact {PHONE} or {EMAIL}."
    ),
    "hi": (
        "AMP India Foundation आर्थिक सशक्तिकरण पर काम करता है ताकि परिवार स्थिर "
        "आजीविका बना सकें।\n\n"
        f"वर्तमान अवसरों के लिए {PHONE} या {EMAIL} पर संपर्क करें।"
    ),
    "hinglish": (
        "AMP India Foundation economic empowerment par kaam karti hai taaki families "
        "stable livelihood bana saken.\n\n"
        f"Current opportunities ke liye {PHONE} ya {EMAIL} par contact karein."
    ),
}

_EVENTS_GENERIC = {
    "en": (
        "AMP India Foundation hosts community events such as job fairs, medical camps, "
        "workshops, and career drives.\n\n"
        "Ask specifically for upcoming events, past events, or the featured event "
        "for the right list. For confirmation, contact "
        f"{PHONE} or {EMAIL}."
    ),
    "hi": (
        "AMP India Foundation जॉब फेयर, मेडिकल कैंप, कार्यशालाएँ और करियर ड्राइव जैसे "
        "इवेंट आयोजित करता है।\n\n"
        f"आगामी, पिछले या फीचर्ड इवेंट पूछें। पुष्टि के लिए {PHONE} या {EMAIL}।"
    ),
    "hinglish": (
        "AMP India Foundation job fairs, medical camps, workshops aur career drives "
        "jaise events host karti hai.\n\n"
        "Upcoming, past ya featured events clearly poochiye. Confirmation ke liye "
        f"{PHONE} ya {EMAIL}."
    ),
}


def lookup_emergency(
    question: str,
    *,
    intent: Optional[Intent] = None,
    language: Language | str = Language.ENGLISH,
) -> Optional[str]:
    """Return an emergency answer when higher layers fail. Never returns None for contact-like intents."""
    q = (question or "").lower()
    lang = language if isinstance(language, Language) else Language(str(language or "en"))

    # Prefer full builtin layer (includes bank details, employment, etc.)
    try:
        from app.services.builtin_answers import answer_builtin

        builtin = answer_builtin(question, intent=intent, language=lang)
        if builtin:
            return builtin
    except Exception:
        pass

    if intent == Intent.CONTACT:
        return _pick(_CONTACT, lang)

    if intent == Intent.VOLUNTEERING or re.search(r"\bvolunteer|स्वयंसेवक\b", q):
        return _pick(_VOLUNTEER, lang)

    if intent == Intent.DONATIONS or re.search(r"\b(donat|support us|contribute)\b", q):
        return _pick(_DONATION, lang)

    if intent == Intent.EMPLOYMENT or re.search(r"\b(job|employment|naukri|placement)\b", q):
        return _pick(_EMPLOYMENT, lang)

    if intent == Intent.SCHOLARSHIPS or re.search(r"\bscholarship|छात्रवृत्ति\b", q):
        return _pick(_SCHOLARSHIP, lang)

    if intent == Intent.MEDICAL or re.search(r"\b(medical|healthcare|health\s*camp|ilaj)\b", q):
        return _pick(_HEALTHCARE, lang)

    if intent in {
        Intent.UPCOMING_EVENTS,
        Intent.PAST_EVENTS,
        Intent.FEATURED_EVENT,
        Intent.EVENTS,
    } or re.search(r"\b(event|events|workshop|job\s*fair)\b", q):
        return _pick(_EVENTS_GENERIC, lang)

    if intent == Intent.AMP_KNOWLEDGE or re.search(
        r"\b(about|mission|vision|what is (?:aif|amp)|amp india)\b", q
    ):
        return _pick(_ABOUT, lang)

    if intent == Intent.PROJECTS or re.search(r"\b(project|program|education|economic)\b", q):
        if re.search(r"\beconomic|empowerment|livelihood\b", q) or intent == Intent.ECONOMIC_EMPOWERMENT:
            return _pick(_ECONOMIC, lang)
        if re.search(r"\beducation|padhai|ace|nts\b", q) or intent == Intent.EDUCATION:
            return _pick(_EDUCATION, lang)
        return _pick(_ABOUT, lang)

    if intent == Intent.TRAINING:
        return _pick(_EDUCATION, lang)

    if intent == Intent.MENTORSHIP:
        return _pick(_EMPLOYMENT, lang)

    return None


def final_apology(language: Language | str = Language.ENGLISH) -> str:
    return _pick(FINAL_APOLOGY, language)
