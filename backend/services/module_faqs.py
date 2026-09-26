"""Per-module FAQ bank for context-aware follow-up answers.

Kept in Python (not knowledge JSON) so the knowledge-file schema stays unchanged.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

from services.intent_detector import normalize_text, tokenize

# topic → list of {question, keywords, answer}
MODULE_FAQS: dict[str, list[dict[str, Any]]] = {
    "volunteer": [
        {
            "question": "Is volunteering free?",
            "keywords": [
                "free",
                "pay",
                "fee",
                "cost",
                "charge",
                "do i have to pay",
                "any fee",
                "payment",
            ],
            "answer": (
                "Yes — volunteering with AMP India Foundation is free. "
                "There is no registration fee to join as a volunteer."
            ),
        },
        {
            "question": "How do I register?",
            "keywords": [
                "register",
                "registration",
                "sign up",
                "signup",
                "join",
                "how do i register",
                "how to register",
            ],
            "answer": (
                "You can register as a volunteer through our secure portal: "
                "https://tinyurl.com/AIFVolunteerRegn — or visit the Volunteer "
                "page on the website and complete the registration form."
            ),
        },
        {
            "question": "Who can volunteer?",
            "keywords": [
                "who can volunteer",
                "who can apply",
                "eligibility",
                "eligible",
                "who",
            ],
            "answer": (
                "Professionals, student mentors, and individuals who want to "
                "contribute time or skills can volunteer. You can offer career "
                "guidance, training, or local field support based on your strengths."
            ),
        },
        {
            "question": "Is there any age limit?",
            "keywords": ["age", "age limit", "minimum age", "how old"],
            "answer": (
                "AMP welcomes volunteers across age groups, especially students "
                "and working professionals. Specific activity requirements may vary "
                "by program — the team will guide you after registration."
            ),
        },
        {
            "question": "Can students volunteer?",
            "keywords": ["student", "students", "college", "school"],
            "answer": (
                "Yes. Students are welcome to volunteer as mentors or field "
                "supporters and gain meaningful social-development experience."
            ),
        },
        {
            "question": "Will I receive a certificate?",
            "keywords": [
                "certificate",
                "certification",
                "letter",
                "proof",
                "experience letter",
            ],
            "answer": (
                "Volunteer recognition and certificates depend on the program and "
                "hours contributed. After you register, the volunteer coordination "
                "team can confirm certificate details for your role."
            ),
        },
    ],
    "job_fair": [
        {
            "question": "Is there any registration fee?",
            "keywords": [
                "fee",
                "pay",
                "cost",
                "charge",
                "free",
                "do i have to pay",
                "registration fee",
                "any fee",
            ],
            "answer": (
                "The National Mega Job Fair is free to attend unless otherwise "
                "mentioned in the event details."
            ),
        },
        {
            "question": "Who can attend?",
            "keywords": [
                "who can attend",
                "who can apply",
                "eligibility",
                "eligible",
                "who",
            ],
            "answer": (
                "Skilled and job-seeking youth, especially underprivileged "
                "candidates looking for placement opportunities, can attend the "
                "National Mega Job Fair & Placement Drive."
            ),
        },
        {
            "question": "What documents are required?",
            "keywords": [
                "document",
                "documents",
                "papers",
                "id",
                "resume",
                "cv",
                "required documents",
            ],
            "answer": (
                "Please carry a updated resume/CV, a valid photo ID, and any "
                "education or skill certificates relevant to the roles you are "
                "applying for."
            ),
        },
        {
            "question": "How do I register?",
            "keywords": [
                "register",
                "registration",
                "sign up",
                "how do i register",
                "how to register",
            ],
            "answer": (
                "Registration details are shared on the Events page for the "
                "National Mega Job Fair. Watch the event listing for the open "
                "registration link and on-spot registration guidance."
            ),
        },
        {
            "question": "Is placement guaranteed?",
            "keywords": [
                "guaranteed",
                "guarantee",
                "placement guaranteed",
                "sure job",
                "job guarantee",
            ],
            "answer": (
                "Placement is not guaranteed. The job fair connects candidates "
                "with employers through interviews and hiring drives; selection "
                "depends on employer requirements and candidate fit."
            ),
        },
    ],
    "events": [
        {
            "question": "Is there any registration fee?",
            "keywords": [
                "fee",
                "pay",
                "cost",
                "charge",
                "free",
                "do i have to pay",
                "registration fee",
                "any fee",
            ],
            "answer": (
                "Most AMP India Foundation events are free to attend unless the "
                "specific event details say otherwise."
            ),
        },
        {
            "question": "How do I register?",
            "keywords": ["register", "registration", "sign up", "how to register"],
            "answer": (
                "Use the registration link shown on the Events page for the "
                "specific event you want to join. Some programs also allow "
                "on-spot registration."
            ),
        },
        {
            "question": "Who can attend?",
            "keywords": ["who can attend", "who can apply", "eligibility", "who"],
            "answer": (
                "Eligibility depends on the event — for example job fairs target "
                "job seekers, while workshops may target students or community "
                "members. Check the event description for audience details."
            ),
        },
        {
            "question": "When is the event?",
            "keywords": ["when", "date", "deadline", "schedule", "timing", "time"],
            "answer": (
                "Event dates are listed on the Events page. If you tell me which "
                "event you mean (for example the Job Fair or Medical Camp), I can "
                "share that date."
            ),
        },
        {
            "question": "What documents are required?",
            "keywords": ["document", "documents", "resume", "id"],
            "answer": (
                "Document requirements vary by event. For job fairs, bring a "
                "resume and photo ID. For other programs, follow the checklist in "
                "the event details."
            ),
        },
    ],
    "scholarship": [
        {
            "question": "Eligibility",
            "keywords": [
                "eligibility",
                "eligible",
                "who can apply",
                "who",
                "criteria",
                "qualify",
            ],
            "answer": (
                "Scholarships and financial support are for deserving students, "
                "verified on merit and economic need. Programs also cover orphans' "
                "basic education support and related assistance."
            ),
        },
        {
            "question": "Required documents",
            "keywords": [
                "document",
                "documents",
                "papers",
                "required documents",
                "what documents",
            ],
            "answer": (
                "Typical submissions include identity proof, academic records, and "
                "income/need-related documents through the crowdfunding or welfare "
                "application portal. Exact requirements are shown in the application form."
            ),
        },
        {
            "question": "Last date / deadline",
            "keywords": [
                "deadline",
                "last date",
                "last date to apply",
                "when",
                "closing date",
            ],
            "answer": (
                "Application deadlines vary by scholarship cycle and portal. "
                "Please check the active scholarship or crowdfunding listing for "
                "the current last date, or contact AMP India Foundation for the "
                "latest timeline."
            ),
        },
        {
            "question": "Application process",
            "keywords": [
                "apply",
                "application",
                "process",
                "how to apply",
                "how do i apply",
                "registration",
                "register",
            ],
            "answer": (
                "Apply through AMP's designated online crowdfunding and welfare "
                "application portals. Submissions are transparently verified based "
                "on merit and economic need."
            ),
        },
        {
            "question": "Fee",
            "keywords": [
                "fee",
                "pay",
                "cost",
                "charge",
                "free",
                "do i have to pay",
                "any fee",
            ],
            "answer": (
                "There is no fee to apply for AMP scholarship or financial-support "
                "consideration through the official portals."
            ),
        },
        {
            "question": "Selection process",
            "keywords": [
                "selection",
                "selected",
                "how are students selected",
                "process",
                "verification",
            ],
            "answer": (
                "Applications are reviewed and verified against merit and economic "
                "need criteria before support is approved."
            ),
        },
    ],
    "donation": [
        {
            "question": "Payment methods",
            "keywords": [
                "payment",
                "pay",
                "method",
                "methods",
                "how to pay",
                "upi",
                "bank",
                "transfer",
                "how can i donate",
            ],
            "answer": (
                "You can donate via direct bank transfer to AMP India Foundation "
                "(Kotak Mahindra, A/C 3114476665, IFSC KKBK0001348, Savings). "
                "Direct clearing helps more of your contribution reach beneficiaries."
            ),
        },
        {
            "question": "Tax benefits",
            "keywords": ["tax", "80g", "exemption", "deduction", "tax benefit"],
            "answer": (
                "For current tax-benefit / 80G documentation details, please contact "
                "AMP India Foundation or check the Support Us page. I don't want to "
                "share unverified tax advice from an incomplete record."
            ),
        },
        {
            "question": "Receipt",
            "keywords": ["receipt", "acknowledgement", "acknowledgment", "invoice"],
            "answer": (
                "After a successful donation, you can request a receipt from AMP "
                "India Foundation using your transfer reference and contact details "
                "via the Contact or Support channels."
            ),
        },
        {
            "question": "Monthly donation",
            "keywords": [
                "monthly",
                "recurring",
                "every month",
                "subscription",
                "regular donation",
            ],
            "answer": (
                "You can support monthly by setting a recurring bank transfer to the "
                "AMP India Foundation account. For guided recurring options, contact "
                "the foundation team."
            ),
        },
    ],
}

# Alias topics that should reuse another FAQ set
TOPIC_ALIASES: dict[str, str] = {
    "employment": "job_fair",
    "volunteering": "volunteer",
    "scholarships": "scholarship",
    "donate": "donation",
    "event": "events",
}

_FOLLOWUP_RE = re.compile(
    r"^(?:"
    r"how(?:\s+so)?|why|where|when|who|what|"
    r"fee|fees|cost|costs|price|pay|payment|free|"
    r"register|registration|deadline|documents?|document|"
    r"eligibility|eligible|certificate|age|students?|"
    r"and\??|also\??|same\??"
    r")[\s\?\!\.]*$",
    re.IGNORECASE,
)

_FOLLOWUP_PHRASES = (
    "do i have to pay",
    "do we have to pay",
    "is it free",
    "is there any fee",
    "any fee",
    "any fees",
    "who can apply",
    "who can attend",
    "who can volunteer",
    "what documents",
    "required documents",
    "last date",
    "is placement guaranteed",
    "will i get a certificate",
    "can students volunteer",
    "age limit",
    "how do i register",
    "how to register",
    "how to apply",
    "tax benefit",
    "tax benefits",
    "monthly donation",
)


def resolve_faq_topic(topic: str | None) -> str | None:
    if not topic:
        return None
    key = topic.lower().strip()
    key = TOPIC_ALIASES.get(key, key)
    if key in MODULE_FAQS:
        return key
    return None


_TOPIC_SWITCH_TERMS = frozenset(
    {
        "scholarship",
        "scholarships",
        "volunteer",
        "volunteering",
        "donate",
        "donation",
        "donations",
        "event",
        "events",
        "project",
        "projects",
        "medical",
        "contact",
        "employment",
        "empowerment",
        "mentorship",
        "training",
        "job",
        "fair",
        "gallery",
        "mission",
        "vision",
    }
)


def is_followup_question(message: str) -> bool:
    """True for short / contextual follow-ups that inherit the prior topic."""
    text = normalize_text(message)
    if not text:
        return False

    tokens = tokenize(text)

    # A clear new topical question is NOT a follow-up
    switch_hits = [t for t in tokens if t in _TOPIC_SWITCH_TERMS]
    if switch_hits and len(tokens) >= 4:
        return False

    if text in set(_FOLLOWUP_PHRASES):
        return True
    for phrase in _FOLLOWUP_PHRASES:
        if phrase == text or text.startswith(phrase + " ") or text.endswith(" " + phrase):
            return True
        if phrase in text and len(tokens) <= 8 and not switch_hits:
            return True

    if _FOLLOWUP_RE.match(text):
        return True

    # Short clarification questions (≤ 6 tokens)
    if len(tokens) <= 6 and (
        text.endswith("?")
        or tokens[0]
        in {"how", "why", "where", "when", "who", "what", "is", "do", "can", "will", "any"}
    ):
        # Allow short topical clarifications like "scholarship fee?"
        return True

    return False


def search_module_faq(
    message: str,
    topic: str | None,
    entity: str | None = None,
) -> dict[str, Any] | None:
    """Return the best FAQ hit for a topic, or None."""
    faq_topic = resolve_faq_topic(topic)
    # Prefer job_fair FAQs when entity mentions job fair
    if entity and "job fair" in normalize_text(entity):
        faq_topic = "job_fair"
    if topic in {"events", "employment"} and entity and "job" in normalize_text(entity):
        faq_topic = "job_fair"

    if not faq_topic:
        return None

    items = MODULE_FAQS.get(faq_topic) or []
    if not items:
        return None

    msg = normalize_text(message)
    msg_tokens = set(tokenize(msg))
    best: dict[str, Any] | None = None
    best_score = 0.0

    for item in items:
        question = normalize_text(str(item.get("question") or ""))
        answer = str(item.get("answer") or "").strip()
        if not answer:
            continue

        score = SequenceMatcher(None, msg, question).ratio()
        for kw in item.get("keywords") or []:
            kw_n = normalize_text(str(kw))
            if not kw_n:
                continue
            if kw_n == msg or kw_n in msg:
                score = max(score, 0.9 if len(kw_n) > 3 else 0.84)
            kw_tokens = set(tokenize(kw_n))
            if kw_tokens and kw_tokens.issubset(msg_tokens):
                score = max(score, 0.86)

        q_tokens = set(tokenize(question))
        if q_tokens:
            overlap = len(msg_tokens & q_tokens) / max(len(q_tokens), 1)
            score = max(score, overlap * 0.88)

        if score > best_score:
            best_score = score
            best = {
                "topic": faq_topic,
                "question": item.get("question"),
                "answer": answer,
                "confidence": round(min(score, 0.98), 3),
            }

    if best and best_score >= 0.55:
        return best
    return None


def topic_fallback(topic: str | None) -> str:
    """Context-aware fallback when a follow-up cannot be answered."""
    key = resolve_faq_topic(topic) or (topic or "")
    mapping = {
        "volunteer": "I couldn't find that volunteering information yet.",
        "scholarship": "I couldn't find that scholarship information.",
        "events": "I couldn't find that event information.",
        "job_fair": "I couldn't find that job fair information yet.",
        "donation": "I couldn't find that donation information yet.",
        "medical": "I couldn't find that medical program information yet.",
        "education": "I couldn't find that education program information yet.",
        "projects": "I couldn't find that project information yet.",
        "contact": "I couldn't find that contact detail yet.",
        "about": "I couldn't find that information about the foundation yet.",
        "leadership": (
            "I couldn't find verified leadership information in my current "
            "knowledge base. Please visit the About Us page or contact AMP "
            "India Foundation."
        ),
    }
    return mapping.get(
        key,
        "I couldn't find that information yet. Please contact AMP India Foundation "
        "or ask another question.",
    )


LEADERSHIP_PATTERNS = (
    re.compile(r"\bwho (?:is|are) the (?:head|chairman|chairperson|founder|president|ceo|director|leader)\b", re.I),
    re.compile(r"\bwho founded\b", re.I),
    re.compile(r"\bwho (?:leads|lead|manages|managed|runs)\b", re.I),
    re.compile(r"\bhead of (?:aif|amp|the foundation|foundation)\b", re.I),
    re.compile(r"\b(?:chairman|chairperson|founder) of\b", re.I),
    re.compile(r"\bleadership\b", re.I),
)


def is_leadership_question(message: str) -> bool:
    text = normalize_text(message)
    return any(p.search(text) for p in LEADERSHIP_PATTERNS)


LEADERSHIP_NOT_FOUND = (
    "I couldn't find verified leadership information in my current knowledge base. "
    "Please visit the About Us page or contact AMP India Foundation."
)

IDENTITY_RESPONSE = (
    "Hello! I'm the AMP India Foundation AI Assistant. I'm here to help you with "
    "information about our scholarships, events, projects, volunteering, donations, "
    "and other foundation-related services."
)


def detect_entity(message: str, intent: str | None = None) -> str | None:
    """Best-effort entity extraction for events / programs."""
    text = normalize_text(message)
    if "job fair" in text or "placement drive" in text:
        return "National Mega Job Fair"
    if "medical camp" in text:
        return "Free Medical Camp & Health Screening"
    if "scholarship" in text and ("workshop" in text or "awareness" in text):
        return "Scholarship Awareness & Education Workshop"
    if "etp" in text or "employability training" in text:
        return "Employability Training Programme (ETP)"
    if intent in {"employment", "job_fair"}:
        return "National Mega Job Fair"
    return None
