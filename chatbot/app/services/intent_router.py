"""Intent router — classify messages before RAG / Gemini / FAQ cache."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set, Tuple

from app.services.prompt_service import (
    GENERAL_KNOWLEDGE_FALLBACK,
    IDENTITY_RESPONSE,
    OUT_OF_SCOPE_RESPONSE,
)
from app.services.text_normalize import apply_spell_fixes


class Intent(str, Enum):
    GREETING = "greeting"
    SMALL_TALK = "small_talk"
    GOODBYE = "goodbye"
    GENERAL_KNOWLEDGE = "general_knowledge"
    CONTACT = "contact"
    DONATIONS = "donations"
    SCHOLARSHIPS = "scholarships"
    EVENTS = "events"
    UPCOMING_EVENTS = "upcoming_events"
    PAST_EVENTS = "past_events"
    FEATURED_EVENT = "featured_event"
    PROJECTS = "projects"
    EDUCATION = "education"
    ECONOMIC_EMPOWERMENT = "economic_empowerment"
    FORM_CLARIFY = "form_clarify"
    VOLUNTEERING = "volunteering"
    EMPLOYMENT = "employment"
    MEDICAL = "medical"
    MENTORSHIP = "mentorship"
    TRAINING = "training"
    AMP_KNOWLEDGE = "amp_knowledge"
    UNKNOWN = "unknown"
    INJECTION = "injection"
    OUT_OF_SCOPE = "out_of_scope"
    GIBBERISH = "gibberish"
    LOCATION_STATEMENT = "location_statement"
    LINK_CLARIFY = "link_clarify"
    CASUAL_CHAT = "casual_chat"
    ASSISTANT_IDENTITY = "assistant_identity"
    CLARIFICATION_NEEDED = "clarification_needed"
    SECURITY_REQUEST = "security_request"


RAG_INTENTS = {
    Intent.CONTACT,
    Intent.DONATIONS,
    Intent.SCHOLARSHIPS,
    Intent.EVENTS,
    Intent.UPCOMING_EVENTS,
    Intent.PAST_EVENTS,
    Intent.FEATURED_EVENT,
    Intent.PROJECTS,
    Intent.EDUCATION,
    Intent.ECONOMIC_EMPOWERMENT,
    Intent.VOLUNTEERING,
    Intent.EMPLOYMENT,
    Intent.MEDICAL,
    Intent.MENTORSHIP,
    Intent.TRAINING,
    Intent.AMP_KNOWLEDGE,
}

# section metadata values written at ingest time
SECTION_UPCOMING = "upcoming_events"
SECTION_FEATURED = "featured_event"
SECTION_PAST = "past_events"

SOURCE_FILTER = {
    Intent.CONTACT: ["cms_footer", "website_about"],
    Intent.DONATIONS: ["website_support"],
    Intent.SCHOLARSHIPS: ["website_projects", "website_about"],
    Intent.EVENTS: [
        "cms_events",
        "cms_gallery",
    ],
    Intent.UPCOMING_EVENTS: [
        "cms_events",
    ],
    Intent.FEATURED_EVENT: [
        "cms_events",
    ],
    Intent.PAST_EVENTS: [
        "cms_gallery",
        "cms_events",
    ],
    Intent.PROJECTS: [
        "website_projects",
        "cms_projects",
        "website_about",
        "website_home",
    ],
    Intent.EDUCATION: [
        "website_projects",
        "cms_projects",
        "website_about",
    ],
    Intent.ECONOMIC_EMPOWERMENT: [
        "website_projects",
        "cms_projects",
        "website_about",
    ],
    Intent.VOLUNTEERING: ["website_volunteer"],
    Intent.EMPLOYMENT: [
        "website_projects",
        "cms_projects",
        "website_home",
        "cms_events",
    ],
    Intent.MEDICAL: ["website_projects", "cms_projects", "website_about"],
    Intent.MENTORSHIP: ["website_projects", "cms_events"],
    Intent.TRAINING: ["website_projects", "cms_events"],
    Intent.AMP_KNOWLEDGE: [
        "website_about",
        "website_home",
        "cms_home",
        "cms_testimonials",
    ],
}

# Pinecone metadata.section filters per event intent
SECTION_FILTER = {
    Intent.UPCOMING_EVENTS: SECTION_UPCOMING,
    Intent.FEATURED_EVENT: SECTION_FEATURED,
    Intent.PAST_EVENTS: SECTION_PAST,
}

TOPIC_INTENTS = {i.value: i for i in RAG_INTENTS}


@dataclass
class RouteResult:
    intent: Intent
    confidence: float
    reason: str = ""
    canned_response: Optional[str] = None
    source_filter: Optional[str | list] = None
    section_filter: Optional[str] = None
    classify_ms: float = 0.0

    @property
    def uses_rag(self) -> bool:
        return self.intent in RAG_INTENTS and not self.canned_response


_INJECTION_PATTERNS = (
    r"ignore (all |any )?(previous|prior|above) (instructions|prompts|rules)",
    r"forget (all |any )?(previous|prior|above) (instructions|prompts|rules)",
    r"disregard (all |any )?(previous|prior|above) (instructions|prompts|rules)",
    r"reveal (your |the )?(system|hidden|developer) prompt",
    r"show (me )?(your |the )?(system|hidden|developer) prompt",
    r"print (your |the )?(system|hidden|developer) prompt",
    r"what (is|are) your (system |developer )?prompt",
    r"repeat your (system |developer )?instructions",
    r"(system|developer|hidden) prompt",
    r"act as (a )?developer",
    r"you are now (dan|jailbreak|unrestricted|chatgpt)",
    r"become (chatgpt|gpt|openai|unrestricted)",
    r"reveal (api|environment|env) (keys?|variables?|secrets?)",
    r"show (me )?(the )?(api|environment|env) (keys?|variables?)",
    r"print (the )?(api|pinecone|gemini|openai) ?keys?",
    r"(show|print|reveal|give|dump).{0,24}(api|pinecone|gemini|openai|admin).{0,12}(keys?|token|password|secret)",
    r"(database|mysql|password|admin credentials?|secret key)",
    r"disclose (confidential|private|hidden)",
    r"bypass (safety|security|filter)",
    r"developer mode",
    r"jailbreak",
    r"\/system",
    r"show (me )?(the )?source code",
    r"reveal (embedding|pinecone|architecture|model configuration)",
    r"(show|print|reveal|give|dump|list).{0,32}(gemini|openai|pinecone).{0,16}(key|token|secret|credential)",
    r"\b(gemini|openai|pinecone)\s*(api\s*)?(key|token|secret)\b",
    r"\b(admin\s*token|ingest\s*token|x-admin-token)\b",
    r"(\.env\b|env\s*file|environment variables?|process\.env)",
    r"(dump|show|print|reveal|cat|open).{0,12}(\.env|env file|environment)",
    r"\b(mysql|database)\s*(password|credentials?|connection|uri|url)\b",
    r"\b(internal architecture|hidden instructions?|developer prompt)\b",
)

_UNSAFE_PATTERNS = (
    r"\bhack\b",
    r"\bcrack (?:wifi|password)\b",
    r"\bweapon\b",
    r"\bporn\b",
)

_ARABIC_SALAM = "السلام عليكم"

_GREETING_RE = re.compile(
    r"^(hi+|hello+|hey+|hola|namaste|adaab|adab|good\s*(morning|afternoon|evening)|"
    r"assalamu?\s*alaikum|asalamualaikum|salam+|salaam+)[!?.]*$",
    re.I,
)

_GOODBYE_RE = re.compile(
    r"^(?:(?:ok|okay|thanks|thank\s*you|thankyou|thx|ty|shukriya)\s+)?"
    r"(?:bye+|goodbye|good\s*bye|see\s*you(?:\s*soon)?|take\s*care|ttyl|cya|"
    r"khuda\s*hafiz|allah\s*hafiz|allahafiz|fi\s*amanillah)[!?.]*$",
    re.I,
)

_IDENTITY_RE = re.compile(
    r"^(who are you|what are you|what(?:'s| is) your name|your name|"
    r"aap kaun ho|tum kaun ho|tu kaun hai|tu kon hai|tum kon ho|"
    r"tu kaun ho|aap kon ho|tum kon hai)\??$",
    re.I,
)

_MODEL_ASK_RE = re.compile(
    r"\b(what model|which model|what llm|are you (?:chatgpt|gpt|gemini|openai)|"
    r"what (?:ai|engine|technology) (?:are you|do you use)|tell me your model)\b",
    re.I,
)

_NEED_HELP_RE = re.compile(
    r"\b(mai gareeb|main gareeb|i am poor|i'?m poor|gareeb hu|garib hu|"
    r"mujhe madad|mujhko madad|need help|i need help|madad chahiye|help chahiye|"
    r"paise chahiye|paisa chahiye|money chahiye|"
    r"financial(?:ly)? (?:help|support)|"
    r"need money|need (?:scholarship|education|medical|mentor|counselling|counseling)|"
    r"can you help me financially)\b",
    re.I,
)

_REACH_RE = re.compile(
    r"\b(how (?:do i |to )?reach|reach (?:aif|amp|office)|directions?|"
    r"kaise pahunchun|kaise pahuche|where is (?:aif|amp))\b",
    re.I,
)

_THANKS_RE = re.compile(
    r"^(thanks|thank\s*you|thankyou|thx|ty|shukriya|shukria|dhanyavad|dhanyavaad|"
    r"jazakallah|jazak\s*allah|jazakallah\s*khair|jazak\s*allah\s*khair)[!?.]*$",
    re.I,
)

# Employment signals must beat volunteer (never classify job fair as volunteer)
_EMPLOYMENT_BLOCK = re.compile(
    r"\b("
    r"job\s*fair|career\s*fair|naukri\s*mela|rozgar\s*mela|"
    r"employment(?:\s+assistance|\s+help)?|placement|need\s+placement|recruitment|hiring|"
    r"jobs?|career\s*support|resume|cv|interview(?:\s+preparation)?|"
    r"employment\s+drive|on-?spot\s+hiring|"
    r"participate.{0,40}(?:job|fair|placement|hiring)|"
    r"job\s*fair\s*kab|naukri|rozgar|jop\s*fair|"
    r"mujhe\s+(?:job|naukri)|(?:job|naukri)\s+chahiye|"
    r"job\s+ke\s+liye|naukri\s+ke\s+liye|kaise\s+madad.+?(?:job|naukri)|"
    r"naukri\s+ke\s+liye\s+madad|"
    r"i need (?:a\s+)?(?:job|work)|need work|looking for (?:a\s+)?(?:job|work)|"
    r"find (?:a\s+)?(?:job|work)|help me find (?:a\s+)?(?:job|work)|"
    r"want (?:a\s+)?(?:job|work)|career (?:help|opportunity)"
    r")\b|"
    r"(नौकरी|रोजगार|जॉब\s*फेयर|प्लेसमेंट|भर्ती)",
    re.I,
)

_TRUST_BLOCK = re.compile(
    r"\b("
    r"trustworthy|trust\b|genuine|legit|reliable|scam|fraud|"
    r"are you (?:real|genuine|trustworthy)|is (?:aif|amp|amp india) (?:real|genuine|trustworthy)|"
    r"amp genuine|aif genuine|scam to nahi|bharosa"
    r")\b",
    re.I,
)

_HOURS_BLOCK = re.compile(
    r"\b("
    r"kitne\s*baje|kab\s*khulta|kab\s*khulte|open\s*rehta|open\s*hai|"
    r"office\s*(?:timing|timings|hours)|working\s*hours|office\s*time"
    r")\b",
    re.I,
)

_ABOUT_SHORT_RE = re.compile(
    r"^(aif|amp|amp india|amp india foundation)\s*"
    r"(kya hai|kya hain|kya karta hai|ke bare me|ke baare me|batao|bataye)?\s*[?.!]*$",
    re.I,
)

_VOLUNTEER_BLOCK = re.compile(
    r"\b("
    r"volunteer(?:ing)?|volnteer|volunter|voluntear|"
    r"join\s+as\s+(?:a\s+)?volunteer|become\s+(?:a\s+)?volunteer|"
    r"community\s+service|support\s+as\s+(?:a\s+)?volunteer|"
    r"volunteer\s+(?:registration|reg|form)|"
    r"volunteer\s+kaise|volunteer\s+bane|volunteer\s+banu"
    r")\b|"
    r"(स्वयंसेवक|वॉलंटियर)",
    re.I,
)

_TOPIC_PATTERNS: Tuple[Tuple[Intent, Tuple[str, ...], float], ...] = (
    # Specific event intents before generic EVENTS / CONTACT.
    (
        Intent.ECONOMIC_EMPOWERMENT,
        (
            r"\b(economic\s+empowerment|livelihood|financial\s+inclusion|"
            r"entrepreneurship|self[-\s]?reliance|women\s+(?:and\s+)?youth\s+empowerment)\b|"
            r"(आर्थिक\s*सशक्तिकरण)",
        ),
        0.98,
    ),
    (
        Intent.EDUCATION,
        (
            r"\b(education(?:\s+(?:project|page|programme|program|support))?|"
            r"padhai|ace academy|national talent|nts|"
            r"skill development(?:\s+and)?\s+livelihood)\b|"
            r"(शिक्षा)",
        ),
        0.97,
    ),
    (
        Intent.FEATURED_EVENT,
        (
            r"\b(featured events?|feature event|highlighted events?|spotlight events?)\b|"
            r"(फीचर्ड\s*इवेंट)",
        ),
        0.99,
    ),
    (
        Intent.PAST_EVENTS,
        (
            r"\b(past events?|previous events?|old events?|last events?|"
            r"events? (?:in|from|of)\s*20\d{2}|what happened in 20\d{2}|"
            r"completed events?|earlier events?)\b|"
            r"(पिछले\s*इवेंट|पुराने\s*इवेंट)",
        ),
        0.99,
    ),
    (
        Intent.UPCOMING_EVENTS,
        (
            r"\b(upcoming events?|future events?|next events?|coming events?|"
            r"events? (?:this|next)\s+(?:month|week|year)|"
            r"what events? (?:are )?(?:happening|coming|scheduled)|"
            r"events? (?:kab|coming|upcoming)|"
            r"employment events? (?:coming|upcoming)|"
            r"(?:coming|upcoming).{0,20}(?:job\s*fair|employment|medical\s*camp))\b|"
            r"(आगामी\s*इवेंट|आने\s*वाले\s*इवेंट)",
        ),
        0.99,
    ),
    (
        Intent.EVENTS,
        (
            r"\b(current events?|"
            r"event|events|evenet|evnet|evnts|workshop|medical camp|career guidance|employment drive|"
            r"events? (?:batao|kya)|events? list)\b|"
            r"(इवेंट|कार्यक्रम)",
        ),
        0.97,
    ),
    (
        Intent.DONATIONS,
        (
            r"\b(donat(?:e|ion|ions)|donaton|donetion|contribute|contribution|bank details|account number|"
            r"ifsc|upi|support us|donation kaise|donate kaise|funding)\b|"
            r"(दान|डोनेशन)",
        ),
        0.95,
    ),
    (
        Intent.SCHOLARSHIPS,
        (
            r"\b(scholarship|scholarships|scholorship|scholership|scolarship|"
            r"financial aid|education support|student funding|"
            r"scholarship ke liye)\b|"
            r"(छात्रवृत्ति|स्कॉलरशिप)",
        ),
        0.95,
    ),
    (
        Intent.EMPLOYMENT,
        (
            r"\b(job\s*fair|jop\s*fair|jobfare|career\s*fair|naukri\s*mela|"
            r"employment|employement|emplyment|emploment|placement|jobs?|"
            r"recruitment|hiring|resume|cv\b|interview|career support|"
            r"employment assistance|need (?:a )?job|get (?:a )?job|"
            r"looking for (?:a )?job|how (?:can|do) i (?:get|find) (?:a )?job)\b|"
            r"(नौकरी|रोजगार|जॉब)",
        ),
        0.97,
    ),
    (
        Intent.MEDICAL,
        (
            # Camps are handled as UPCOMING_EVENTS earlier; this is healthcare support.
            r"\b(medical(?:\s+relief|\s+support|\s+aid|\s+help)?|health(?:care)?|"
            r"hospital|treatment|clinic|critical illness|ilaj|ilaij|"
            r"health screening|doctor|health support)\b|"
            r"(मेडिकल|स्वास्थ्य|अस्पताल|इलाज)",
        ),
        0.93,
    ),
    (
        Intent.MENTORSHIP,
        (
            r"\b(mentor|mentorship|guidance|career guidance|centres? of excellence)\b|"
            r"(मेंटर|मार्गदर्शन)",
        ),
        0.92,
    ),
    (
        Intent.TRAINING,
        (
            r"\b(training|skill development|courses?|vocational|employability training)\b|"
            r"(ट्रेनिंग|प्रशिक्षण|स्किल)",
        ),
        0.92,
    ),
        (
            Intent.CONTACT,
            (
            r"\b(contact|phone|mobile|call|email|e-?mail|mail|address|office|helpline|"
            r"telephone|timing|timings|location|where are you|where is (?:aif|amp|your)|"
            r"phone number|contact number|office timing|office address|office hours|"
            r"working hours|reach (?:aif|amp|office)|how (?:do i |to )?reach|"
            r"aif ka address|amp ka address|aif ka location|aif ka number|amp ka number|"
            r"kitne baje|open rehta|"
            r"adres|locaton|ofis|kaha ho|kahan ho|"
            r"(?:office|aif|amp).{0,16}(?:kaha|kahan)|(?:kaha|kahan).{0,12}(?:office|aif|amp)"
            r")\b|"
            r"(संपर्क|फ़ोन|फोन|ईमेल|पता|ऑफिस|समय)",
            ),
            0.96,
        ),
    (
        Intent.PROJECTS,
        (
            r"\b(project|projects|programs?|services?|what (?:do you|does (?:amp|aif)) (?:provide|offer|do)|"
            r"initiatives?|focus areas|flagship|ace academy|national talent|nts|"
            r"kya (?:karta|karte) (?:hai|ho)|what u guys do|what you guys do|"
            r"what do you guys do)\b|"
            r"(प्रोजेक्ट|परियोजना|सेवा)",
        ),
        0.9,
    ),
    (
        Intent.VOLUNTEERING,
        (
            r"\b(volunteer(?:ing)?|volnteer|volunter|voluntear|"
            r"join as (?:a )?volunteer|become (?:a )?volunteer|"
            r"community service|support as (?:a )?volunteer|volunteer kaise|"
            r"volunteer bane)\b|"
            r"(स्वयंसेवक|वॉलंटियर)",
        ),
        0.94,
    ),
)

_AMP_ABOUT_RE = re.compile(
    r"\b(amp(?:\s+india)?(?:\s+foundation)?|aif)\b|"
    r"\b(mission|vision|purpose|history|founded|about (?:the )?foundation|"
    r"what (?:is|does) (?:amp|aif)|why (?:was )?(?:aif|amp)|"
    r"tell me about (?:it|amp|aif|them)|"
    r"head of (?:aif|amp)|(?:amp|aif)\s+leadership|"
    r"(?:chairman|director|president|founder) of (?:amp|aif))\b|"
    r"(मिशन|विजन|परिचय)",
    re.I,
)

_GENERAL_ENTITY_RE = re.compile(
    r"\b("
    r"chatgpt|gpt|openai|claude|gemini|llm|machine learning|artificial intelligence|\bai\b|"
    r"python|javascript|java|react|nodejs|docker|kubernetes|programming|"
    r"bitcoin|crypto|ethereum|blockchain|stock market|"
    r"weather|climate|planet|planets|solar system|universe|"
    r"sky|ocean|photosynthesis|gravity|einstein|newton|shakespeare|"
    r"joke|riddle|poem|recipe|movie|football|cricket|bollywood|"
    r"world\s*cup|fifa|olympics|ipl|premier league|nba|"
    r"capital of|france|paris|london|geography|"
    r"salman\s*khan|shahrukh|sharukh|aamir\s*khan|who is aiman|"
    r"iphone|android|windows|linux|google|facebook|instagram|twitter|youtube|"
    r"president of india|prime minister|math|calculate|fibonacci|pasta|cook"
    r")\b|"
    r"\b\d+\s*[\+\-\*/]\s*\d+\b",
    re.I,
)

_AMP_DOMAIN_RE = re.compile(
    r"\b("
    r"amp|aif|foundation|scholarship|volunteer|donat|event|job\s*fair|"
    r"employment|naukri|office|contact|address|phone|email|medical|"
    r"healthcare|project|program|education|empowerment|livelihood|"
    r"cheque|upi|ifsc|80g|form|registration|etp|mentorship|training"
    r")\b",
    re.I,
)

_FORM_UNSPECIFIC_RE = re.compile(
    r"\b("
    r"(?:link\s+of\s+)?forms?|registration\s+link|application\s+form|"
    r"apply\s+link|google\s+form|sign\s*up\s+link"
    r")\b",
    re.I,
)

_LINK_ONLY_RE = re.compile(
    r"^(?:please\s+|pls\s+|plz\s+)?(?:give|send|share|provide)\s+(?:me\s+)?(?:the\s+)?link|"
    r"^(?:link\s+(?:do|chahiye|bhejo|bhej|dena)|link\??)$",
    re.I,
)

_PERSONAL_OOD_RE = re.compile(
    r"\b("
    r"biwi|shohar|shaadi|shadi|boyfriend|girlfriend|dating|marriage|"
    r"pyaar|pyar|rishta|wife|husband|gf|bf|"
    r"mujhe\s+(?:biwi|shohar|gf|bf|girlfriend|boyfriend)"
    r")\b",
    re.I,
)

_LOCATION_STATEMENT_RE = re.compile(
    r"\b(?:mai|main|me)\s+(?P<place>[a-zA-Z\u0900-\u097F]{3,})\s+"
    r"(?:se|me|mein)\s*(?:hu|hun|hoon|hai|rehta|rehati|rahta|rahti)?\b|"
    r"\bi(?:'m|\s+am)\s+from\s+(?P<place2>[a-zA-Z]{3,})\b|"
    r"\bi\s+live\s+in\s+(?P<place3>[a-zA-Z]{3,})\b|"
    r"\bi(?:'m|\s+am)\s+(?:based|living)\s+in\s+(?P<place4>[a-zA-Z]{3,})\b|"
    r"\bi\s+belong\s+to\s+(?P<place5>[a-zA-Z]{3,})\b",
    re.I,
)

_INCLUSIVE_RE = re.compile(
    r"\b("
    r"can\s+hindus?\s+join|hindus?\s+can\s+join|is\s+(?:aif|amp)\s+only\s+for\s+muslims?|"
    r"only\s+for\s+muslims?|only\s+muslims?|"
    r"can\s+girls?\s+apply|can\s+women\s+apply|can\s+ladki|"
    r"who\s+can\s+(?:participate|join|apply|volunteer)|"
    r"can\s+anyone|anyone\s+(?:can\s+)?apply|"
    r"open\s+to\s+all|any\s+religion|all\s+religions?|"
    r"non[-\s]?muslims?|christians?\s+can|sikhs?\s+can|"
    r"discriminat|kisike\s+liye|sirf\s+muslim"
    r")\b",
    re.I,
)

_CASUAL_HOW_RE = re.compile(
    r"\b("
    r"tu\s+kais[ae]\s+hai(?:\s+re)?|tum\s+kais[ae]\s+ho|tu\s+kaise\s+ho|"
    r"kais[ae]\s+hai\s+re|kaisa\s+hai(?:\s+re)?|"
    r"how\s+are\s+you|aap\s+kaise\s+(?:ho|hai|hain)"
    r")\b",
    re.I,
)

_GENERAL_QUESTION_RE = re.compile(
    r"^(what(?:'s| is| are| was| were)|who(?:'s| is| are| was| were)|"
    r"how (?:many|much|does|do|did|is|are)|why (?:is|are|do|does)|"
    r"when (?:is|was|did)|where (?:is|are|was)|tell me (?:a |about )|"
    r"explain|define|"
    r"क्या है|क्यों|कौन है)\b",
    re.I,
)

_FOLLOWUP_RE = re.compile(
    r"\b(last date|deadline|eligibility|eligible|documents?|fees?|apply|application|"
    r"required|process|kab|kaise|kya|more|details?|aur batao|"
    r"when|where|conducted|date|dates|venue|hua|hui|"
    r"what about|and (?:the )?|timings?|hours?|phone|email|address|"
    r"cheque|check|dd\b|upi|ifsc|80g|receipt|tax|exemption|offline|"
    r"bank|account|"
    r"can (?:my|she|he|they)|daughter|son|child|beta|beti)\b",
    re.I,
)

_PLACE_EVENT_RE = re.compile(
    r"\b(kupwara|kashmir|kolkata|srinagar|nanded|mumbai|hyderabad|delhi|pune|"
    r"ballari|ahmedabad|agra)\b",
    re.I,
)
_JOB_FAIR_RE = re.compile(r"\b(job\s*fair|mega\s*job\s*fair|naukri\s*mela|rozgar\s*mela)\b", re.I)
_WHAT_YOU_DO_RE = re.compile(
    r"\b(what\s+(?:u|you|do you)\s+guys\s+do|what\s+do\s+you\s+do|"
    r"what\s+we\s+do|kya\s+karte\s+ho|kya\s+karta\s+hai)\b",
    re.I,
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _compact(text: str) -> str:
    return re.sub(r"[^\w\s\u0600-\u06FF\u0900-\u097F]", "", text, flags=re.UNICODE).strip()


def _tokens(text: str) -> Set[str]:
    return set(re.findall(r"[a-z0-9]+", text))


def detect_injection(message: str) -> bool:
    text = normalize(message)
    return any(re.search(pattern, text, re.I) for pattern in _INJECTION_PATTERNS)


def _match_topic(text: str) -> Optional[Tuple[Intent, float, str]]:
    best: Optional[Tuple[Intent, float, str]] = None
    for intent, patterns, base_conf in _TOPIC_PATTERNS:
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if not match:
                continue
            span = len(match.group(0))
            conf = min(0.99, base_conf + min(span, 24) / 400.0)
            if best is None or conf > best[1]:
                best = (intent, conf, f"topic:{intent.value}")
    return best


def route_intent(
    message: str,
    has_session_topic: bool = False,
    session_topic: Optional[str] = None,
) -> RouteResult:
    """Classify a user message. Runs locally — no Gemini / Pinecone."""
    t0 = time.perf_counter()
    raw = (message or "").strip()
    text = normalize(apply_spell_fixes(message))
    compact = _compact(text)
    fixed_raw = apply_spell_fixes(raw)
    if _ARABIC_SALAM in raw:
        compact = _ARABIC_SALAM

    def finish(
        intent: Intent,
        confidence: float,
        reason: str,
        canned: Optional[str] = None,
    ) -> RouteResult:
        # Prefer SourcePlan ordering (CMS → markdown → backend → FAQ).
        try:
            from app.services.source_planner import plan_sources

            plan = plan_sources(intent)
            sources = plan.sources or SOURCE_FILTER.get(intent)
            section = plan.section if plan.section is not None else SECTION_FILTER.get(intent)
        except Exception:
            sources = SOURCE_FILTER.get(intent)
            section = SECTION_FILTER.get(intent)
        return RouteResult(
            intent=intent,
            confidence=round(confidence, 3),
            reason=reason,
            canned_response=canned,
            source_filter=sources,
            section_filter=section,
            classify_ms=(time.perf_counter() - t0) * 1000,
        )

    if not text and _ARABIC_SALAM not in raw:
        return finish(Intent.UNKNOWN, 0.0, "empty")

    # Priority: Greeting / small-talk → Security → Domain RAG
    from app.services.conversation_service import classify_conversation

    conversation = classify_conversation(raw) or classify_conversation(fixed_raw)
    if conversation:
        intent, reply_key, conf = conversation
        return finish(intent, conf, f"conversation:{reply_key}", f"__CONV__:{reply_key}")

    if _GOODBYE_RE.match(text) or _GOODBYE_RE.match(compact):
        return finish(Intent.GOODBYE, 0.99, "goodbye", "__CONV__:goodbye")

    if _IDENTITY_RE.match(text) or _IDENTITY_RE.match(compact):
        return finish(Intent.ASSISTANT_IDENTITY, 0.99, "identity", "__IDENTITY__")

    if _MODEL_ASK_RE.search(text) or _MODEL_ASK_RE.search(raw):
        return finish(Intent.SMALL_TALK, 0.99, "model_ask", "__MODEL__")

    if compact in {"ok", "okay", "help"}:
        return finish(Intent.SMALL_TALK, 0.99, "small_talk", f"__SMALL__:{compact}")

    from app.services.query_normalize import looks_gibberish

    if looks_gibberish(raw) or looks_gibberish(text):
        from app.services.prompt_service import GIBBERISH_RESPONSE, t as _t

        return finish(Intent.GIBBERISH, 0.99, "gibberish", _t(GIBBERISH_RESPONSE))

    if _PERSONAL_OOD_RE.search(text) or _PERSONAL_OOD_RE.search(raw):
        from app.services.prompt_service import DOMAIN_ONLY_RESPONSE, t as _t

        return finish(
            Intent.GENERAL_KNOWLEDGE,
            0.97,
            "personal_out_of_domain",
            _t(DOMAIN_ONLY_RESPONSE),
        )

    if _CASUAL_HOW_RE.search(text) or _CASUAL_HOW_RE.search(raw):
        return finish(Intent.CASUAL_CHAT, 0.97, "casual_how_are_you", "__CONV__:how_are_you")

    loc = _LOCATION_STATEMENT_RE.search(text) or _LOCATION_STATEMENT_RE.search(raw)
    if loc:
        gd = loc.groupdict()
        place = (
            gd.get("place")
            or gd.get("place2")
            or gd.get("place3")
            or gd.get("place4")
            or gd.get("place5")
            or ""
        ).strip()
        if place.lower() not in {
            "job",
            "naukri",
            "madad",
            "help",
            "volunteer",
            "donate",
            "the",
            "this",
        }:
            from app.services.prompt_service import location_statement_reply
            from app.services.language_service import detect_language as _detect_lang

            return finish(
                Intent.LOCATION_STATEMENT,
                0.96,
                "location_statement",
                location_statement_reply(place, _detect_lang(raw or text)),
            )

    if _INCLUSIVE_RE.search(text) or _INCLUSIVE_RE.search(raw):
        from app.services.builtin_answers import inclusive_reply
        from app.services.language_service import detect_language as _detect_lang

        return finish(
            Intent.AMP_KNOWLEDGE,
            0.97,
            "inclusivity",
            inclusive_reply(_detect_lang(raw or text)),
        )

    if _LINK_ONLY_RE.search(text) or _LINK_ONLY_RE.search(compact):
        from app.services.prompt_service import LINK_CLARIFY_RESPONSE, t as _t

        return finish(
            Intent.LINK_CLARIFY,
            0.92,
            "link_clarify",
            _t(LINK_CLARIFY_RESPONSE),
        )

    if detect_injection(text):
        from app.services.prompt_service import INJECTION_RESPONSE, t as _t

        return finish(
            Intent.INJECTION,
            0.99,
            "security_request",
            _t(INJECTION_RESPONSE),
        )

    if any(re.search(p, text, re.I) for p in _UNSAFE_PATTERNS):
        from app.services.prompt_service import DOMAIN_ONLY_RESPONSE, t as _t

        return finish(Intent.OUT_OF_SCOPE, 0.95, "unsafe", _t(DOMAIN_ONLY_RESPONSE))

    from app.services.goal_intent import detect_goal_intent

    goal = detect_goal_intent(text, raw) or detect_goal_intent(fixed_raw, raw)
    if goal:
        g_intent, g_conf, g_reason = goal
        return finish(g_intent, g_conf, g_reason)

    # Specific need-help with a clear programme keyword → RAG for that topic.
    # Generic "paise/madad/help chahiye" is handled above as empathetic conversation.
    if _NEED_HELP_RE.search(text) or _NEED_HELP_RE.search(raw):
        if re.search(r"\b(job|naukri|employment|placement)\b", text, re.I):
            return finish(Intent.EMPLOYMENT, 0.96, "need_help_employment")
        if re.search(r"\b(scholarship|education|padhai)\b", text, re.I):
            return finish(Intent.SCHOLARSHIPS, 0.96, "need_help_scholarship")
        if re.search(r"\b(medical|health|ilaj|ilaij)\b", text, re.I):
            return finish(Intent.MEDICAL, 0.96, "need_help_medical")
        if re.search(r"\b(mentor|counsell|counsel)\b", text, re.I):
            return finish(Intent.MENTORSHIP, 0.96, "need_help_mentor")
        return finish(
            Intent.SMALL_TALK,
            0.94,
            "need_help_empathy",
            "__CONV__:need_help",
        )

    if _REACH_RE.search(text) or _REACH_RE.search(raw):
        return finish(Intent.CONTACT, 0.97, "reach_office")

    # Event subtype intents BEFORE employment/volunteer — so
    # "employment events coming" / "medical camps" map to event sections.
    if re.search(
        r"\b(featured events?|feature event|highlighted events?)\b",
        text,
        re.I,
    ):
        return finish(Intent.FEATURED_EVENT, 0.99, "featured_event_priority")
    if re.search(
        r"\b(past events?|previous events?|old events?|last events?|"
        r"what happened in\s*20\d{2}|events?\s+(?:in|from|of)\s*20\d{2})\b",
        text,
        re.I,
    ):
        return finish(Intent.PAST_EVENTS, 0.99, "past_events_priority")
    if re.search(
        r"\b(upcoming events?|future events?|next events?|coming events?|"
        r"what events? (?:are )?(?:happening|coming|scheduled)|"
        r"events? (?:this|next)\s+(?:month|week|year)|"
        r"(?:employment|job)\s+events?\s+(?:are\s+)?(?:coming|upcoming)|"
        r"(?:coming|upcoming).{0,24}(?:event|job\s*fair|medical\s*camp)|"
        r"events?\s+(?:are\s+)?coming)\b",
        text,
        re.I,
    ):
        return finish(Intent.UPCOMING_EVENTS, 0.99, "upcoming_events_priority")
    # Medical camps / job fairs without "past" → upcoming event section
    if re.search(r"\b(medical\s*camps?|health\s*screening)\b", text, re.I) and not re.search(
        r"\b(past|previous|old|last|20\d{2})\b", text, re.I
    ):
        return finish(Intent.UPCOMING_EVENTS, 0.97, "medical_camp_upcoming")

    if _WHAT_YOU_DO_RE.search(text) or _WHAT_YOU_DO_RE.search(fixed_raw):
        return finish(Intent.AMP_KNOWLEDGE, 0.97, "what_you_do")

    # Programme pages beat events / general-knowledge "tell me about …"
    if re.search(
        r"\b(economic\s+empowerment|financial\s+inclusion|livelihood)\b",
        text,
        re.I,
    ) or (
        re.search(r"\bempowerment\b", text, re.I)
        and not re.search(r"\b(event|events|job\s*fair|camp)\b", text, re.I)
    ):
        return finish(Intent.ECONOMIC_EMPOWERMENT, 0.98, "economic_empowerment_priority")
    if re.search(r"\beducation\b|\bpadhai\b|\bशिक्षा\b", text, re.I) and not re.search(
        r"\b(scholarship|scholorship|event|events|job\s*fair|camp|workshop)\b",
        text,
        re.I,
    ):
        return finish(Intent.EDUCATION, 0.98, "education_project_priority")

    # Named job fairs (Kupwara / Kashmir) are CMS events, not generic employment.
    if _JOB_FAIR_RE.search(text) and _PLACE_EVENT_RE.search(text):
        if re.search(r"\b(past|previous|old|last|conducted|hua|was)\b", text, re.I):
            return finish(Intent.PAST_EVENTS, 0.98, "named_job_fair_past")
        return finish(Intent.EVENTS, 0.98, "named_job_fair")

    # --- Hard priority: employment vs volunteer ---
    emp = _EMPLOYMENT_BLOCK.search(text) or _EMPLOYMENT_BLOCK.search(fixed_raw)
    vol = _VOLUNTEER_BLOCK.search(text) or _VOLUNTEER_BLOCK.search(fixed_raw)
    if emp and not vol:
        return finish(Intent.EMPLOYMENT, 0.98, "employment_priority")
    if emp and vol:
        return finish(Intent.EMPLOYMENT, 0.96, "employment_over_volunteer")
    if vol:
        return finish(Intent.VOLUNTEERING, 0.97, "volunteer_priority")

    if _FORM_UNSPECIFIC_RE.search(text) or _FORM_UNSPECIFIC_RE.search(fixed_raw):
        if re.search(r"\b(scholarship|scholorship)\b", text, re.I):
            return finish(Intent.SCHOLARSHIPS, 0.96, "form_scholarship")
        if re.search(r"\b(event|job\s*fair|camp)\b", text, re.I):
            return finish(Intent.EVENTS, 0.96, "form_event")
        if re.search(r"\b(employment|naukri|etp|job)\b", text, re.I):
            return finish(Intent.EMPLOYMENT, 0.96, "form_employment")
        from app.services.prompt_service import FORM_CLARIFY_RESPONSE, t as _t

        return finish(
            Intent.FORM_CLARIFY,
            0.9,
            "form_clarify",
            _t(FORM_CLARIFY_RESPONSE),
        )

    # Explicit mentorship beats generic "career guidance" event phrase
    if re.search(r"\bmentorship?\b", text, re.I) and not re.search(
        r"\b(event|events|summit|camp|workshop|fair)\b", text, re.I
    ):
        return finish(Intent.MENTORSHIP, 0.96, "mentorship_priority")

    if _HOURS_BLOCK.search(text) or _HOURS_BLOCK.search(raw):
        return finish(Intent.CONTACT, 0.97, "office_hours")

    if _TRUST_BLOCK.search(text) or _TRUST_BLOCK.search(raw):
        return finish(Intent.AMP_KNOWLEDGE, 0.96, "trust_credibility")

    if _ABOUT_SHORT_RE.match(text) or _ABOUT_SHORT_RE.match(compact):
        return finish(Intent.AMP_KNOWLEDGE, 0.97, "about_short")

    topic = _match_topic(text) or _match_topic(fixed_raw)
    if topic:
        intent, conf, reason = topic
        return finish(intent, conf, reason)

    if _AMP_ABOUT_RE.search(text) or _AMP_ABOUT_RE.search(raw):
        return finish(Intent.AMP_KNOWLEDGE, 0.9, "amp_about")

    # Ultra-short AMP / contact tokens (after typo normalization)
    if compact in {"aif", "amp", "about"}:
        return finish(Intent.AMP_KNOWLEDGE, 0.95, "short_about")
    if compact in {
        "address",
        "location",
        "email",
        "phone",
        "contact",
        "timing",
        "timings",
        "mail",
        "number",
        "adres",
        "office",
        "ofis",
    }:
        return finish(Intent.CONTACT, 0.95, "short_contact")
    if compact in {"job", "jobs", "naukri", "rozgar", "placement", "job fair"}:
        return finish(Intent.EMPLOYMENT, 0.95, "short_employment")
    if compact in {"volunteer", "volunteering"}:
        return finish(Intent.VOLUNTEERING, 0.95, "short_volunteer")
    if compact in {"scholarship", "scholarships"}:
        return finish(Intent.SCHOLARSHIPS, 0.95, "short_scholarship")
    if compact in {"donation", "donate", "donations"}:
        return finish(Intent.DONATIONS, 0.95, "short_donation")
    if compact in {"event", "events"}:
        return finish(Intent.UPCOMING_EVENTS, 0.95, "short_events_upcoming")
    if compact in {"upcoming", "upcoming events", "upcoming event"}:
        return finish(Intent.UPCOMING_EVENTS, 0.97, "short_upcoming")
    if compact in {"past events", "past event", "previous events"}:
        return finish(Intent.PAST_EVENTS, 0.97, "short_past")
    if compact in {"featured", "featured event", "featured events"}:
        return finish(Intent.FEATURED_EVENT, 0.97, "short_featured")

    tokens = _tokens(text)
    # Follow-ups inherit the last AMP topic only with follow-up language —
    # never because the message is merely short (that leaked Contact).
    if (has_session_topic or session_topic) and _FOLLOWUP_RE.search(text):
        topic_key = (session_topic or "").strip().lower()
        blocked = (
            _GENERAL_ENTITY_RE.search(text)
            or _PERSONAL_OOD_RE.search(text)
            or _LOCATION_STATEMENT_RE.search(text)
            or _CASUAL_HOW_RE.search(text)
        )
        contact_follow = bool(
            re.search(
                r"\b(phone|email|address|office|number|timing|timings|hours|contact)\b",
                text,
                re.I,
            )
        )
        if not blocked:
            if topic_key == "contact" and not contact_follow:
                pass
            elif topic_key in TOPIC_INTENTS:
                return finish(TOPIC_INTENTS[topic_key], 0.86, "session_followup")
            else:
                return finish(Intent.AMP_KNOWLEDGE, 0.8, "session_followup")

    if _GENERAL_ENTITY_RE.search(text):
        return finish(Intent.GENERAL_KNOWLEDGE, 0.95, "general_entity")

    if _GENERAL_QUESTION_RE.search(text) or _GENERAL_QUESTION_RE.search(raw):
        if _AMP_DOMAIN_RE.search(text):
            return finish(Intent.AMP_KNOWLEDGE, 0.82, "amp_general_question")
        return finish(Intent.GENERAL_KNOWLEDGE, 0.88, "general_question")

    if compact in {"education"}:
        return finish(Intent.EDUCATION, 0.96, "short_education")
    if compact in {"empowerment", "economic empowerment"}:
        return finish(Intent.ECONOMIC_EMPOWERMENT, 0.96, "short_empowerment")

    if len(tokens) <= 3:
        if not _AMP_DOMAIN_RE.search(text):
            return finish(Intent.GENERAL_KNOWLEDGE, 0.7, "short_out_of_domain")
        from app.services.prompt_service import CLARIFY_RESPONSE, t as _t

        return finish(
            Intent.CLARIFICATION_NEEDED,
            0.55,
            "clarification_needed",
            _t(CLARIFY_RESPONSE),
        )

    if not _AMP_DOMAIN_RE.search(text):
        return finish(Intent.GENERAL_KNOWLEDGE, 0.78, "unclassified_out_of_domain")

    from app.services.prompt_service import CLARIFY_RESPONSE, t as _t

    return finish(
        Intent.CLARIFICATION_NEEDED,
        0.5,
        "clarification_needed",
        _t(CLARIFY_RESPONSE),
    )


# Keep unused imports referenced for identity fallbacks in other modules
_ = (IDENTITY_RESPONSE, OUT_OF_SCOPE_RESPONSE)
