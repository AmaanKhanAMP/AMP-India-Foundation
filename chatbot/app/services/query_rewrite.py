"""Intelligent query rewriting: normalize, spell-fix, expand synonyms, map intent."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from app.services.intent_router import Intent
from app.services.language_service import Language
from app.services.text_normalize import apply_spell_fixes


@dataclass
class RewrittenQuery:
    original: str
    search_query: str
    language: str
    intent_hint: Optional[str] = None
    normalized: str = ""
    synonyms: List[str] = field(default_factory=list)

# CONTACT / LOCATION first — must beat trailing "… aif" about patterns
_PHRASE_MAP = (
    # Programme pages first — never let events/job-fair rewrite steal education
    (
        r"\b(economic\s+empowerment|livelihood|financial\s+inclusion|entrepreneurship)\b",
        "AMP India Foundation Economic Empowerment project livelihood entrepreneurship "
        "financial independence /projects/empowerment website_projects cms_projects",
        ["economic empowerment", "livelihood", "website_projects"],
    ),
    (
        r"\b(education(?:\s+(?:project|page|programme|program))?|padhai)\b",
        "AMP India Foundation Education project skill development livelihood scholarships "
        "career guidance vocational training BPL /projects/education website_projects cms_projects",
        ["education", "website_projects", "scholarships"],
    ),
    (
        r"\b(upcoming events?|future events?|next events?|coming events?|"
        r"what events? (?:are )?(?:happening|coming)|events? this (?:month|year))\b",
        "AMP India Foundation upcoming events CMS upcoming_events section job fair medical camp workshop",
        ["upcoming_events", "cms_events", "events"],
    ),
    (
        r"\b(featured events?|feature event|highlighted events?)\b",
        "AMP India Foundation featured event CMS featured_event section",
        ["featured_event", "cms_events", "events"],
    ),
    (
        r"\b(past events?|previous events?|old events?|last events?|"
        r"what happened in|events? (?:in|from|of)\s*20\d{2})\b",
        "AMP India Foundation past events CMS past_events section completed programmes gallery",
        ["past_events", "cms_gallery", "events"],
    ),
    (
        r"\b(events?|workshop|medical camp|career guidance|employment drive)\b",
        "AMP India Foundation upcoming past events job fair medical camp workshop career guidance CMS events",
        ["events", "upcoming", "workshop", "job fair", "medical camp"],
    ),
    (
        r"\b(contact details?|contact (?:info|information)|get (?:the )?contact|"
        r"phone|mobile|telephone|number|call|helpline|email|e-?mail|mail|"
        r"address|location|office address|office location|office timings?|"
        r"working hours|office hours|timings?|kitne baje|pata|patt?a|"
        r"how (?:do i |to )?reach|reach (?:aif|amp|office)|where is (?:aif|amp|the office)|"
        r"aif kaha|amp kaha|office kaha|kaha hai|kahan hai|kaha ho|kahan ho|"
        r"nagpada|mumbai office|reach office)\b",
        "AMP India Foundation contact phone email office address working hours location Mumbai Nagpada",
        ["contact", "phone", "email", "address", "timings", "office"],
    ),
    (
        r"\b(how (?:do i |to )?reach|directions?|kaise pahunchun|kaise pahuche)\b",
        "AMP India Foundation office address location directions how to reach contact office Mumbai Nagpada",
        ["address", "location", "directions", "contact", "office"],
    ),
    (
        r"\b(mai gareeb|main gareeb|i am poor|i'?m poor|gareeb hu|garib hu|financial(?:ly)? (?:help|support|aid)|"
        r"need money|mujhe paise|paise chahiye|paisa chahiye|money chahiye|"
        r"can you help me financially)\b",
        "AMP India Foundation scholarships education employment healthcare support programmes for underprivileged families",
        ["scholarship", "education", "employment", "medical", "support"],
    ),
    (
        r"\b(mujhe madad|need help|i need help|help me|madad chahiye|help chahiye|support chahiye)\b",
        "AMP India Foundation help support programs scholarships employment medical volunteering donations contact",
        ["help", "support", "financial", "programs", "scholarship", "employment", "medical"],
    ),
    (
        r"\b(aif|amp|amp india|amp india foundation)\s+(kya hai|kya hain|kya karta hai|ke bare me|ke baare me|batao|bataye)\b|"
        r"\b(what is aif|what is amp|why (?:was )?(?:aif|amp)|about (?:aif|amp|the foundation)|"
        r"purpose of (?:aif|amp)|history of (?:aif|amp)|who founded)\b",
        "What is AMP India Foundation? About organization mission vision history purpose objectives and activities",
        ["about", "mission", "vision", "foundation", "purpose"],
    ),
    (
        r"\b(job|jobs|naukri|rozgar|placement|job fair|career|hire|hiring|employment|"
        r"resume|cv|interview|mock interview|need (?:a )?job|job chahiye|naukri chahiye)\b",
        "AMP India Foundation employment assistance job fair placement resume mock interview career guidance",
        ["employment", "placement", "career", "resume", "job fair"],
    ),
    (
        r"\b(volunteer|volunteering|volunteer (?:kaise|bane|banu|link|form|registration)|become volunteer|"
        r"join as volunteer|mentor registration|serve|community work|sewa|seva|"
        r"join (?:aif|amp|us)|how (?:to |do i )?join)\b",
        "How to volunteer with AMP India Foundation registration form link join as volunteer mentor community service",
        ["volunteer", "registration", "join", "mentor", "form"],
    ),
    (
        r"\b(donate|donation|contribute|support us|crowdfunding|"
        r"cheque|check|dd\b|upi|80g|tax exemption|receipt|offline donation)\b",
        "AMP India Foundation Support Us donation UPI AMPINDIA@KOTAK cheque DD bank IFSC "
        "receipt 80G tax website_support",
        ["donation", "support us", "upi", "cheque"],
    ),
    (
        r"\b(bank details?|account number|ifsc|upi)\b",
        "AMP India Foundation official bank transfer details IFSC Support Us donation contact",
        ["donation", "bank", "ifsc"],
    ),
    (
        r"\b(scholarship|scholarships|education (?:help|support)|student funding|apply karna|"
        r"fees|fee|study|padhai|padhaai|financial help|mai gareeb|main gareeb|"
        r"i am poor|i'?m poor|gareeb hu|garib hu|need help financially)\b",
        "AMP India Foundation scholarships education support eligibility how to apply financial help for students",
        ["scholarship", "education", "financial"],
    ),
    (
        r"\b(trust|trustworthy|genuine|legit|reliable|scam|fraud)\b",
        "Is AMP India Foundation trustworthy genuine registered non-profit credibility",
        ["trustworthy", "genuine", "registered"],
    ),
    (
        r"\b(mission|vision)\b",
        "AMP India Foundation mission and vision statement",
        ["mission", "vision"],
    ),
    (
        r"\b(medical camp|health screening)\b",
        "AMP India Foundation upcoming medical camp health screening events CMS upcoming_events",
        ["medical camp", "upcoming_events", "events"],
    ),
    (
        r"\b(medical|health|hospital|treatment|healthcare|critical illness|ilaj)\b",
        "AMP India Foundation healthcare medical support programmes critical illness assistance eligibility contact",
        ["medical", "healthcare", "programmes", "support"],
    ),
    (
        r"\b(training|skill|vocational|courses?)\b",
        "AMP India Foundation skill development vocational training employability",
        ["training", "skill"],
    ),
    (
        r"\b(mentor|mentorship|career guidance|counselling|counseling)\b",
        "AMP India Foundation mentorship career guidance counselling centres of excellence",
        ["mentorship", "guidance"],
    ),
    (
        r"\b(services?|what (?:do you|does (?:amp|aif)) (?:provide|offer|do)|kya karta hai)\b",
        "What services and programs does AMP India Foundation provide education employment medical scholarships",
        ["programs", "services"],
    ),
)

_INTENT_DEFAULTS = {
    Intent.CONTACT: (
        "AMP India Foundation contact phone number email office address working hours location Mumbai",
        ["contact", "phone", "email", "address", "timings"],
    ),
    Intent.DONATIONS: (
        "AMP India Foundation Support Us donation bank IFSC UPI AMPINDIA@KOTAK cheque receipt 80G",
        ["donation", "support us", "upi", "cheque", "bank"],
    ),
    Intent.SCHOLARSHIPS: (
        "AMP India Foundation scholarships education support eligibility apply",
        ["scholarship", "education"],
    ),
    Intent.EMPLOYMENT: (
        "AMP India Foundation Employment Assistance Cell placement resume interview career "
        "training /projects/employment website_projects",
        ["employment", "job", "placement", "resume"],
    ),
    Intent.EVENTS: (
        "AMP India Foundation upcoming events past events workshops job fair",
        ["events"],
    ),
    Intent.UPCOMING_EVENTS: (
        "AMP India Foundation upcoming events CMS upcoming_events job fair medical camp workshop",
        ["upcoming_events", "events"],
    ),
    Intent.FEATURED_EVENT: (
        "AMP India Foundation featured event CMS featured_event",
        ["featured_event", "events"],
    ),
    Intent.PAST_EVENTS: (
        "AMP India Foundation past events CMS past_events gallery completed programmes",
        ["past_events", "events"],
    ),
    Intent.PROJECTS: (
        "AMP India Foundation programs projects education employment medical economic empowerment",
        ["programs", "projects"],
    ),
    Intent.EDUCATION: (
        "AMP India Foundation Education project skill development scholarships career guidance "
        "vocational training /projects/education website_projects",
        ["education", "website_projects"],
    ),
    Intent.ECONOMIC_EMPOWERMENT: (
        "AMP India Foundation Economic Empowerment livelihood entrepreneurship financial inclusion "
        "/projects/empowerment website_projects",
        ["economic empowerment", "livelihood", "website_projects"],
    ),
    Intent.VOLUNTEERING: (
        "AMP India Foundation volunteer registration how to join form link",
        ["volunteer", "registration"],
    ),
    Intent.MEDICAL: (
        "AMP India Foundation Medical Relief healthcare project diagnostic camps clinics "
        "/projects/medical /projects/healthcare website_projects",
        ["medical", "healthcare", "website_projects"],
    ),
    Intent.MENTORSHIP: (
        "AMP India Foundation mentorship career guidance counselling",
        ["mentorship"],
    ),
    Intent.TRAINING: (
        "AMP India Foundation skill development vocational training",
        ["training", "skill"],
    ),
    Intent.AMP_KNOWLEDGE: (
        "AMP India Foundation about organization mission vision objectives services",
        ["about", "mission", "vision"],
    ),
}

_TOPIC_FOLLOWUP = {
    "contact": "AMP India Foundation office address phone email timings location",
    "volunteering": "AMP India Foundation volunteer registration form link where to register",
    "employment": "AMP India Foundation employment job fair placement resume support",
    "donations": "AMP India Foundation Support Us donation UPI cheque bank IFSC receipt",
    "scholarships": "AMP India Foundation scholarship eligibility application process",
    "events": "AMP India Foundation upcoming events dates venues",
    "medical": "AMP India Foundation medical relief healthcare project",
    "amp_knowledge": "AMP India Foundation about mission vision programs",
    "projects": "AMP India Foundation programs projects services",
    "education": "AMP India Foundation Education project scholarships vocational training",
    "economic_empowerment": "AMP India Foundation Economic Empowerment livelihood",
}


def _normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = text.replace("amp india foundation", "amp")
    text = apply_spell_fixes(text)
    text = re.sub(r"[^\w\s\u0900-\u097F]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def rewrite_query(
    message: str,
    *,
    language: Language | str = Language.ENGLISH,
    intent: Optional[Intent] = None,
    session_topic: Optional[str] = None,
    last_entity: Optional[str] = None,
) -> RewrittenQuery:
    original = (message or "").strip()
    text = _normalize(original)
    lang = language.value if isinstance(language, Language) else str(language or "en")

    if last_entity and (
        re.fullmatch(
            r"(they|them|it|this|that|us|unke|uska|uski|iske|tell me about it|aur|more|details?)",
            text,
        )
        or (
            re.search(
                r"\b(when|where|kab|kahan|date|conducted|hua|venue|apply|documents?|daughter|son)\b",
                text,
            )
            and len(text.split()) <= 10
        )
    ):
        search = f"AMP India Foundation {last_entity} {text}"
        return RewrittenQuery(original, search, lang, session_topic, text, [last_entity])

    if re.search(r"\b(kupwara|kashmir)\b", text) and re.search(
        r"\b(job\s*fair|mega\s*job\s*fair)\b", text
    ):
        search = (
            f"AMP India Foundation Kupwara Mega Job Fair cms_events "
            f"featured_event upcoming_events venue date Jammu Kashmir"
        )
        return RewrittenQuery(
            original,
            search,
            lang,
            intent.value if intent else "events",
            text,
            ["cms_events", "kupwara", "job fair"],
        )

    if intent in {
        Intent.EVENTS,
        Intent.UPCOMING_EVENTS,
        Intent.PAST_EVENTS,
        Intent.FEATURED_EVENT,
    } and intent in _INTENT_DEFAULTS:
        base, syn = _INTENT_DEFAULTS[intent]
        return RewrittenQuery(
            original,
            f"{base} {original}".strip(),
            lang,
            intent.value,
            text,
            list(syn),
        )

    if session_topic and re.fullmatch(
        r"(they|them|it|this|that|us|unke|uska|uski|iske|tell me about it|aur|more|details?|"
        r"where|where\?|kahan|kaha|link|form|registration|timings?|hours?|phone|email|address)",
        text,
    ):
        topic_key = session_topic.strip().lower()
        search = _TOPIC_FOLLOWUP.get(topic_key, f"AMP India Foundation {topic_key.replace('_', ' ')} details")
        return RewrittenQuery(original, search, lang, topic_key, text, [topic_key])

    # Intent-first for contact: never let trailing "aif" rewrite to about
    if intent == Intent.CONTACT:
        base, syn = _INTENT_DEFAULTS[Intent.CONTACT]
        english_bits = " ".join(re.findall(r"[a-zA-Z]{3,}", original))
        return RewrittenQuery(
            original,
            f"{base} {english_bits} {text}".strip(),
            lang,
            Intent.CONTACT.value,
            text,
            syn,
        )

    if intent in {
        Intent.EDUCATION,
        Intent.ECONOMIC_EMPOWERMENT,
        Intent.SCHOLARSHIPS,
        Intent.DONATIONS,
        Intent.MEDICAL,
        Intent.PROJECTS,
        Intent.EMPLOYMENT,
    } and intent in _INTENT_DEFAULTS:
        base, syn = _INTENT_DEFAULTS[intent]
        english_bits = " ".join(re.findall(r"[a-zA-Z]{3,}", original))
        return RewrittenQuery(
            original,
            f"{base} {english_bits} {text}".strip(),
            lang,
            intent.value,
            text,
            syn,
        )

    for pattern, expansion, synonyms in _PHRASE_MAP:
        if re.search(pattern, text, re.I):
            return RewrittenQuery(
                original,
                expansion,
                lang,
                intent.value if intent else None,
                text,
                list(synonyms),
            )

    # ONLY exact short tokens — never suffix match on long sentences ending with "aif"
    short_map = {
        "job": Intent.EMPLOYMENT,
        "jobs": Intent.EMPLOYMENT,
        "naukri": Intent.EMPLOYMENT,
        "rozgar": Intent.EMPLOYMENT,
        "address": Intent.CONTACT,
        "location": Intent.CONTACT,
        "email": Intent.CONTACT,
        "mail": Intent.CONTACT,
        "phone": Intent.CONTACT,
        "number": Intent.CONTACT,
        "contact": Intent.CONTACT,
        "timing": Intent.CONTACT,
        "timings": Intent.CONTACT,
        "office": Intent.CONTACT,
        "aif": Intent.AMP_KNOWLEDGE,
        "amp": Intent.AMP_KNOWLEDGE,
        "about": Intent.AMP_KNOWLEDGE,
        "volunteer": Intent.VOLUNTEERING,
        "donation": Intent.DONATIONS,
        "donate": Intent.DONATIONS,
        "scholarship": Intent.SCHOLARSHIPS,
    }
    if text in short_map:
        mapped = short_map[text]
        base, syn = _INTENT_DEFAULTS[mapped]
        return RewrittenQuery(original, base, lang, mapped.value, text, syn)

    if intent in _INTENT_DEFAULTS and (len(text.split()) <= 10 or lang in {"hi", "hinglish"}):
        base, syn = _INTENT_DEFAULTS[intent]
        english_bits = " ".join(re.findall(r"[a-zA-Z]{3,}", original))
        search = f"{base} {english_bits} {text}".strip()
        return RewrittenQuery(original, search, lang, intent.value, text, syn)

    search = original
    if intent in _INTENT_DEFAULTS and "amp" not in text and "aif" not in text:
        search = f"AMP India Foundation {original}"
    return RewrittenQuery(
        original,
        search,
        lang,
        intent.value if intent else None,
        text,
        [],
    )
