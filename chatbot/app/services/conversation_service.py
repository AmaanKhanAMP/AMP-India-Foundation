"""Canned conversational replies — never FAQ / RAG / Gemini."""

from __future__ import annotations

import re
from typing import Optional, Tuple

from app.services.intent_router import Intent
from app.services.language_service import Language
from app.services.text_normalize import normalize_for_match


def _norm(text: str) -> str:
    return normalize_for_match(text)


# Exact / near-exact greeting forms (after normalize)
_GREETING_EXACT = {
    "hi",
    "hii",
    "hiii",
    "hello",
    "helloo",
    "hey",
    "heyy",
    "hola",
    "yo",
    "namaste",
    "namaskar",
    "नमस्ते",
    "नमस्कार",
    "हैलो",
    "hello ji",
    "hi ji",
    "hey ji",
    "hi bro",
    "hello bro",
    "hey bro",
    "hi there",
    "hello there",
    "good morning",
    "good afternoon",
    "good evening",
    "salaam",
    "salam",
    "assalam",
    "assalamualaikum",
    "assalamu alaikum",
    "asalamualaikum",
    "assalamu alaykum",
    "salam alaikum",
    "salaam alaikum",
    "as-salamu alaykum",
    "assalamualaikum wr wb",
    "adaab",
    "adab",
    "what's up",
    "whats up",
    "whatsup",
    "sup",
    "kya haal hai",
    "kya haal hain",
    "السلام عليكم",
}

_GREETING_RE = re.compile(
    r"^(hi+|hii+|hello+|hey+|yo|namaste|namaskar|नमस्ते|नमस्कार|हैलो|"
    r"(?:hello|hi|hey)\s+(?:ji|bro|there)|"
    r"good\s+(?:morning|afternoon|evening)|"
    r"ass?alamu?\s*a?lai?kum|asalamualaikum|assalam|salam+|salaam+|"
    r"salam\s+alaikum|salaam\s+alaikum|"
    r"adaab|adab|what'?s\s*up|whatsup|sup|"
    r"kya\s+haal\s+hai(?:n)?)$",
    re.I,
)

_SALAM_RE = re.compile(
    r"(السلام عليكم|ass?alamu?\s*a?lai?kum|asalamualaikum|salam\s+alaikum|"
    r"salaam\s+alaikum|^\s*assalam\s*$|^\s*salam+\s*$|^\s*salaam+\s*$)",
    re.I,
)

_HELP_MENU_EN = (
    "I can help you with:\n\n"
    "• Education\n"
    "• Employment\n"
    "• Scholarships\n"
    "• Healthcare\n"
    "• Economic Empowerment\n"
    "• Events\n"
    "• Volunteering\n"
    "• Donations"
)

_THANKS_EXACT = {
    "thanks",
    "thank you",
    "thankyou",
    "thx",
    "ty",
    "shukriya",
    "shukria",
    "dhanyavad",
    "dhanyavaad",
    "jazakallah",
    "jazak allah",
    "jazakallah khair",
    "jazak allah khair",
    "शुक्रिया",
    "धन्यवाद",
}

# Short Islamic phrases that are conversational (not domain RAG)
_ISLAMIC_PHRASE_EXACT = {
    "ameen",
    "amin",
    "aameen",
    "mashallah",
    "masha allah",
    "ma sha allah",
    "inshallah",
    "inshaallah",
    "in sha allah",
    "alhamdulillah",
    "alhamdulilah",
    "subhanallah",
}

_GOODBYE_EXACT = {
    "bye",
    "byee",
    "byeee",
    "goodbye",
    "good bye",
    "see you",
    "see you soon",
    "take care",
    "ttyl",
    "cya",
    "khuda hafiz",
    "allah hafiz",
    "allahafiz",
    "fi amanillah",
    "fiamanillah",
    "good night",
    "goodnight",
    "ok bye",
    "okay bye",
    "thanks bye",
    "thank you bye",
    "thx bye",
    "शुभ रात्रि",
}

_GOODBYE_RE = re.compile(
    r"^(?:(?:ok|okay|thanks|thank\s*you|thankyou|thx|ty|shukriya)\s+)?"
    r"(?:"
    r"bye+|goodbye|good\s*bye|see\s*you(?:\s*soon)?|take\s*care|ttyl|cya|"
    r"khuda\s*hafiz|allah\s*hafiz|allahafiz|fi\s*amanillah|"
    r"good\s*night|goodnight"
    r")"
    r"(?:\s+(?:bye+|thanks|thank\s*you))?$",
    re.I,
)

_SMALL_TALK_EXACT = {
    "how are you",
    "how are you doing",
    "how r you",
    "how're you",
    "how's your day",
    "how is your day",
    "kaise ho",
    "kaise ho aap",
    "kaise hai",
    "kaise hai aap",
    "kaise hain aap",
    "aap kaise ho",
    "aap kaise hain",
    "aap kaise hai",
    "kya haal hai",
    "kya haal hain",
    "sab theek",
    "sab theek hai",
    "sab thik",
    "aur batao",
    "aur batao na",
    "aur kya chal raha hai",
    "kya chal raha hai",
    "kaisa chal raha hai",
    "kaisi chal rahi hai",
    "how do you do",
    "whats going on",
    "what's going on",
    "kya kar rahe ho",
    "kya kar rahi ho",
    "kya kar raha hai",
    "kya kar rahe ho aap",
    "bore ho",
    "bored ho",
    "bored",
    "tum kaun ho",
    "aap kaun ho",
    "tu kaun hai",
    "tu kon hai",
    "tum kon ho",
    "tu kaun ho",
    "who are you",
    "what are you",
    "tu kaisa hai",
    "tu kaisa hai re",
    "tu kaise hai",
    "tu kaise ho",
}

# Personal / casual chitchat — never Pinecone / Gemini
_CASUAL_RE = re.compile(
    r"(?:"
    r"\bkya\s+kar\s+rahe\s+ho\b|\bkya\s+kar\s+rahi\s+ho\b|\bkya\s+kar\s+raha\s+hai\b|"
    r"\bbore\s*ho\b|\bbored\b|"
    r"\bkaise\s+ho\b|\bkaise\s+hai(?:\s+aap)?\b|"
    r"\btu\s+kais[ae]\s+hai(?:\s+re)?\b|\btu\s+kaise\s+ho\b|"
    r"\btum\s+kaun\s+ho\b|\baap\s+kaun\s+ho\b|\btu\s+kaun\s+hai\b|\btu\s+kon\s+hai\b|"
    r"\btujhse\b|\btumse\s+door\b|\bdoor\s+mai\b|\bdoor\s+main\b|"
    r"\bwajah\s+ke\s+liye\b|"
    r"\bkya\s+scene\b|\bfree\s+ho\b|\bbusy\s+ho\b|"
    r"\bmiss\s+you\b|\bi\s+love\s+you\b|\blove\s+you\b"
    r")",
    re.I,
)

_AMP_DOMAIN_RE = re.compile(
    r"\b("
    r"amp|aif|scholarship|volunteer|donat|event|job\s*fair|employment|"
    r"naukri|office|contact|address|phone|email|medical|healthcare|"
    r"project|program|foundation"
    r")\b",
    re.I,
)

_NEED_HELP_EMPATHY_RE = re.compile(
    r"\b("
    r"paise\s+chahiye|paisa\s+chahiye|money\s+chahiye|"
    r"madad\s+chahiye|help\s+chahiye|mujhe\s+madad|mujhko\s+madad|"
    r"need\s+help|i\s+need\s+help|help\s+me|"
    r"financial(?:ly)?\s+(?:help|support)|need\s+money|"
    r"gareeb\s+hu|garib\s+hu|mai\s+gareeb|main\s+gareeb|i\s+am\s+poor|i'?m\s+poor"
    r")\b",
    re.I,
)


def _goodbye_key(text: str) -> str:
    if "fi" in text and "amanillah" in text.replace(" ", ""):
        return "fi_amanillah"
    if "allah" in text and "hafiz" in text:
        return "allah_hafiz"
    if "khuda" in text and "hafiz" in text:
        return "khuda_hafiz"
    if "night" in text:
        return "good_night"
    return "goodbye"


def classify_conversation(message: str) -> Optional[Tuple[Intent, str, float]]:
    """
    Return (intent, reply_key, confidence) for conversational messages.
    reply_key is used by reply_for().
    """
    raw = (message or "").strip()
    text = _norm(raw)
    if not text:
        return None

    # Islamic greetings (spelling-tolerant)
    if "السلام عليكم" in raw or _SALAM_RE.search(raw) or _SALAM_RE.search(text):
        return Intent.GREETING, "salam", 0.99

    if text in _ISLAMIC_PHRASE_EXACT:
        if "ameen" in text or text in {"amin", "aameen"}:
            return Intent.SMALL_TALK, "ameen", 0.99
        if "mashallah" in text or "masha" in text:
            return Intent.SMALL_TALK, "mashallah", 0.99
        if "inshallah" in text or "insha" in text:
            return Intent.SMALL_TALK, "inshallah", 0.99
        if "alhamdulillah" in text or "alhamdulilah" in text:
            return Intent.SMALL_TALK, "alhamdulillah", 0.99
        if "subhanallah" in text:
            return Intent.SMALL_TALK, "subhanallah", 0.99

    # Goodbye before thanks so "thanks bye" / "ok bye" never hit RAG
    if text in _GOODBYE_EXACT or _GOODBYE_RE.match(text):
        return Intent.GOODBYE, _goodbye_key(text), 0.99

    if text in _THANKS_EXACT or re.fullmatch(
        r"(thanks|thank\s*you|shukriya|jazak\s*allah(?:\s*khair)?)", text, re.I
    ):
        key = "jazakallah" if "jazak" in text else "thanks"
        return Intent.SMALL_TALK, key, 0.99

    # Empathetic help requests — warm guidance, no Pinecone
    if _NEED_HELP_EMPATHY_RE.search(text) and not re.search(
        r"\b(scholarship|job|jobs|work|naukri|rozgar|volunteer|donat|event|medical|ilaj|employment|placement)\b",
        text,
        re.I,
    ):
        return Intent.SMALL_TALK, "need_help", 0.98

    if text in _SMALL_TALK_EXACT or re.fullmatch(
        r"(how are you(?: doing)?|how'?s your day|kaise (?:ho|hai)(?: aap)?|"
        r"aap kaise (?:ho|hai|hain)|kya haal hai(?:n)?|sab theek(?: hai)?|"
        r"aur batao(?: na)?|aur kya chal raha hai|kaisa chal raha hai|"
        r"kya kar rahe ho(?: aap)?|kya kar rahi ho|bore\s*ho|bored|"
        r"tum kaun ho|aap kaun ho|tu kaun hai|tu kon hai|who are you|what are you|"
        r"tu kaisa hai(?: re)?|tu kaise hai|tu kaise ho)",
        text,
        re.I,
    ):
        if "kaun" in text or "kon" in text or text in {"who are you", "what are you"}:
            return Intent.ASSISTANT_IDENTITY, "who_are_you", 0.99
        if "bore" in text:
            return Intent.SMALL_TALK, "bore", 0.99
        if "kar rahe" in text or "kar rahi" in text or "kar raha" in text:
            return Intent.SMALL_TALK, "kya_kar_rahe", 0.99
        if "aur batao" in text or "chal raha" in text:
            return Intent.SMALL_TALK, "aur_batao", 0.99
        if "sab theek" in text:
            return Intent.SMALL_TALK, "sab_theek", 0.99
        return Intent.SMALL_TALK, "how_are_you", 0.99

    # Broader casual / personal chitchat (no AMP domain terms)
    if _CASUAL_RE.search(text) and not _AMP_DOMAIN_RE.search(text):
        if "kaun" in text or "kon" in text:
            return Intent.ASSISTANT_IDENTITY, "who_are_you", 0.97
        if "bore" in text:
            return Intent.SMALL_TALK, "bore", 0.97
        if "kar rahe" in text or "kar rahi" in text:
            return Intent.SMALL_TALK, "kya_kar_rahe", 0.97
        if "tujhse" in text or "door" in text or "wajah" in text or "love" in text or "miss" in text:
            return Intent.SMALL_TALK, "casual", 0.96
        return Intent.SMALL_TALK, "how_are_you", 0.96

    if text in _GREETING_EXACT or _GREETING_RE.match(text):
        if "morning" in text:
            return Intent.GREETING, "good_morning", 0.99
        if "afternoon" in text:
            return Intent.GREETING, "good_afternoon", 0.99
        if "evening" in text:
            return Intent.GREETING, "good_evening", 0.99
        if "namaste" in text or "namaskar" in text or text in {"नमस्ते", "नमस्कार"}:
            return Intent.GREETING, "namaste", 0.99
        if "adaab" in text or "adab" in text:
            return Intent.GREETING, "adaab", 0.99
        if ("what" in text and "up" in text) or text in {"yo", "sup", "whatsup"}:
            return Intent.GREETING, "whats_up", 0.99
        if "kya haal" in text:
            return Intent.GREETING, "kya_haal", 0.99
        return Intent.GREETING, "hello", 0.99

    return None


def reply_for(key: str, language: Language) -> str:
    """Localized canned replies for conversational intents."""
    lang = language.value if isinstance(language, Language) else str(language or "en")

    replies = {
        "hello": {
            "en": (
                "Hello!\n\n"
                "Welcome to AMP India Foundation.\n\n"
                "How may I assist you today?\n\n"
                f"{_HELP_MENU_EN}"
            ),
            "hi": (
                "नमस्ते!\n\n"
                "AMP India Foundation में आपका स्वागत है।\n\n"
                "मैं आपकी कैसे मदद कर सकता हूँ?\n\n"
                "• शिक्षा\n• रोज़गार\n• छात्रवृत्ति\n• स्वास्थ्य\n"
                "• आर्थिक सशक्तिकरण\n• इवेंट्स\n• स्वयंसेवा\n• दान"
            ),
            "hinglish": (
                "Hello!\n\n"
                "AMP India Foundation me aapka swagat hai.\n\n"
                "Main aapki kaise madad kar sakta hoon?\n\n"
                f"{_HELP_MENU_EN}"
            ),
        },
        "good_morning": {
            "en": (
                "Good morning!\n\nWelcome to AMP India Foundation.\n"
                f"How may I assist you today?\n\n{_HELP_MENU_EN}"
            ),
            "hi": "सुप्रभात!\n\nAMP India Foundation में आपका स्वागत है। मैं आपकी कैसे मदद कर सकता हूँ?",
            "hinglish": "Good morning!\n\nAMP India Foundation me aapka swagat hai. Main aapki kaise madad kar sakta hoon?",
        },
        "good_afternoon": {
            "en": (
                "Good afternoon!\n\nWelcome to AMP India Foundation.\n"
                f"How may I assist you today?\n\n{_HELP_MENU_EN}"
            ),
            "hi": "नमस्कार!\n\nAMP India Foundation में आपका स्वागत है। मैं आपकी कैसे मदद कर सकता हूँ?",
            "hinglish": "Good afternoon!\n\nAMP India Foundation me aapka swagat hai. Main aapki kaise madad kar sakta hoon?",
        },
        "good_evening": {
            "en": (
                "Good evening!\n\nWelcome to AMP India Foundation.\n"
                f"How may I assist you today?\n\n{_HELP_MENU_EN}"
            ),
            "hi": "शुभ संध्या!\n\nAMP India Foundation में आपका स्वागत है। मैं आपकी कैसे मदद कर सकता हूँ?",
            "hinglish": "Good evening!\n\nAMP India Foundation me aapka swagat hai. Main aapki kaise madad kar sakta hoon?",
        },
        "salam": {
            "en": (
                "Wa Alaikum Assalam wa Rahmatullahi wa Barakatuh 🌿\n\n"
                "Welcome to AMP India Foundation.\n\n"
                "How may I assist you today?\n\n"
                f"{_HELP_MENU_EN}"
            ),
            "hi": (
                "वअलाइकुम अस्सलाम व रहमतुल्लाह 🌿\n\n"
                "AMP India Foundation में आपका स्वागत है।\n\n"
                "मैं आपकी किस तरह मदद कर सकता हूँ?\n\n"
                "• शिक्षा\n• रोज़गार\n• छात्रवृत्ति\n• स्वास्थ्य\n"
                "• आर्थिक सशक्तिकरण\n• इवेंट्स\n• स्वयंसेवा\n• दान"
            ),
            "hinglish": (
                "Wa Alaikum Assalam wa Rahmatullahi wa Barakatuh 🌿\n\n"
                "AMP India Foundation me aapka swagat hai.\n\n"
                "Main aapki kaise madad kar sakta hoon?\n\n"
                f"{_HELP_MENU_EN}"
            ),
        },
        "namaste": {
            "en": (
                "Namaste!\n\nWelcome to AMP India Foundation.\n\n"
                f"How may I assist you today?\n\n{_HELP_MENU_EN}"
            ),
            "hi": (
                "नमस्ते!\n\nAMP India Foundation में आपका स्वागत है।\n\n"
                "मैं आपकी कैसे मदद कर सकता हूँ?"
            ),
            "hinglish": (
                "Namaste!\n\nAMP India Foundation me aapka swagat hai.\n\n"
                "Main aapki kaise madad kar sakta hoon?"
            ),
        },
        "adaab": {
            "en": "Adaab!\n\nWelcome to AMP India Foundation. How may I assist you?",
            "hi": "आदाब!\n\nAMP India Foundation में आपका स्वागत है। मैं आपकी कैसे मदद कर सकता हूँ?",
            "hinglish": "Adaab!\n\nAMP India Foundation me aapka swagat hai. Main aapki kaise madad kar sakta hoon?",
        },
        "whats_up": {
            "en": "Hey! 👋\n\nI'm here to help with AMP India Foundation — scholarships, events, donations, volunteering, and more.",
            "hi": "नमस्ते! 👋\n\nमैं AMP India Foundation — छात्रवृत्ति, कार्यक्रम, दान, स्वयंसेवा में मदद के लिए यहाँ हूँ।",
            "hinglish": "Hey! 👋\n\nMain AMP India Foundation — scholarships, events, donations, volunteering me madad ke liye yahan hoon.",
        },
        "kya_haal": {
            "en": (
                "Main bilkul theek hoon, shukriya! 😊\n\n"
                "Aap kaise hain?\n\n"
                "Main AMP India Foundation se related scholarships, events, donations, "
                "volunteering aur projects ke baare me madad kar sakta hoon."
            ),
            "hi": (
                "मैं बिल्कुल ठीक हूँ, शुक्रिया! 😊\n\n"
                "आप कैसे हैं?\n\n"
                "मैं AMP India Foundation की छात्रवृत्ति, कार्यक्रम, दान, स्वयंसेवा और प्रोजेक्ट्स में मदद कर सकता हूँ।"
            ),
            "hinglish": (
                "Main bilkul theek hoon, shukriya! 😊\n\n"
                "Aap kaise hain?\n\n"
                "Main AMP India Foundation se related scholarships, events, donations, "
                "volunteering aur projects ke baare me madad kar sakta hoon."
            ),
        },
        "how_are_you": {
            "en": (
                "I'm doing well, thank you! 😊\n\n"
                "I can help with AMP India Foundation programs, events, scholarships, and volunteering."
            ),
            "hi": (
                "मैं ठीक हूँ, शुक्रिया! 😊\n\n"
                "मैं AMP India Foundation के कार्यक्रम, इवेंट्स, छात्रवृत्ति और स्वयंसेवा में मदद कर सकता हूँ।"
            ),
            "hinglish": (
                "Main theek hoon, shukriya 😊. Main AMP India Foundation se related programs, "
                "events, scholarships aur volunteering ke baare mein madad kar sakta hoon."
            ),
        },
        "who_are_you": {
            "en": (
                "I am the AMP India Foundation assistant. I can help with AIF programs, projects, "
                "events, volunteering, scholarships, healthcare initiatives, employment support, and donations."
            ),
            "hi": (
                "मैं AMP India Foundation का सहायक हूँ। मैं AIF के कार्यक्रमों, परियोजनाओं, इवेंट्स, "
                "स्वयंसेवा, छात्रवृत्ति, स्वास्थ्य पहल, रोज़गार सहायता और दान में मदद कर सकता हूँ।"
            ),
            "hinglish": (
                "Main AMP India Foundation assistant hoon. Main AIF ke programs, projects, events, "
                "volunteering, scholarships, healthcare initiatives, employment support aur donations "
                "me madad kar sakta hoon."
            ),
        },
        "kya_kar_rahe": {
            "en": (
                "I'm here and ready to help with AMP India Foundation questions. 😊\n\n"
                "What would you like to know?"
            ),
            "hi": (
                "मैं यहीं हूँ और AMP India Foundation से जुड़े सवालों में मदद के लिए तैयार हूँ। 😊\n\n"
                "आप क्या जानना चाहेंगे?"
            ),
            "hinglish": (
                "Main yahan hoon aur AMP India Foundation ke sawalon me madad ke liye ready hoon. 😊\n\n"
                "Aap kya jaanna chahenge?"
            ),
        },
        "bore": {
            "en": (
                "No boredom here — I'm happy to chat about AMP India Foundation. 😊\n\n"
                "Ask me about scholarships, jobs, events, volunteering, or donations."
            ),
            "hi": (
                "बिल्कुल नहीं! मैं AMP India Foundation के बारे में बात करने के लिए तैयार हूँ। 😊\n\n"
                "छात्रवृत्ति, नौकरी, इवेंट्स, स्वयंसेवा या दान पूछ सकते हैं।"
            ),
            "hinglish": (
                "Bilkul nahi! Main AMP India Foundation ke baare me baat karne ke liye ready hoon. 😊\n\n"
                "Scholarships, jobs, events, volunteering ya donations pooch sakte hain."
            ),
        },
        "casual": {
            "en": (
                "That's kind of you to share. I'm here as the AMP India Foundation assistant.\n\n"
                "If you need help with scholarships, employment, healthcare, volunteering, or donations — just ask."
            ),
            "hi": (
                "आपकी बात सुनकर अच्छा लगा। मैं AMP India Foundation का सहायक हूँ।\n\n"
                "अगर छात्रवृत्ति, रोज़गार, स्वास्थ्य, स्वयंसेवा या दान में मदद चाहिए तो बताएं।"
            ),
            "hinglish": (
                "Aapki baat sunkar accha laga. Main AMP India Foundation ka assistant hoon.\n\n"
                "Agar scholarships, employment, healthcare, volunteering ya donations me madad chahiye to batayiye."
            ),
        },
        "need_help": {
            "en": (
                "I'm sorry you're going through a difficult time — you're not alone.\n\n"
                "AMP India Foundation supports people through programmes in:\n\n"
                "• Education & scholarships\n"
                "• Employment & job fairs\n"
                "• Healthcare\n"
                "• Economic empowerment\n\n"
                "Tell me which area you need help with, or share your concern, and I'll guide you to the right support.\n\n"
                "You can also reach the foundation via the Contact page or Support Us page."
            ),
            "hi": (
                "मुझे खेद है कि आप मुश्किल समय से गुज़र रहे हैं — आप अकेले नहीं हैं।\n\n"
                "AMP India Foundation इन क्षेत्रों में मदद करता है:\n\n"
                "• शिक्षा और छात्रवृत्ति\n"
                "• रोज़गार और जॉब फेयर\n"
                "• स्वास्थ्य सेवा\n"
                "• आर्थिक सशक्तिकरण\n\n"
                "बताएं आपको किस तरह की मदद चाहिए, मैं सही दिशा में मार्गदर्शन करूँगा।\n\n"
                "आप Contact पेज या Support Us पेज से भी संपर्क कर सकते हैं।"
            ),
            "hinglish": (
                "Mujhe afsos hai ki aap mushkil waqt se guzar rahe hain — aap akele nahi hain.\n\n"
                "AMP India Foundation in areas me madad karta hai:\n\n"
                "• Education aur scholarships\n"
                "• Employment aur job fairs\n"
                "• Healthcare\n"
                "• Economic empowerment\n\n"
                "Bataiye aapko kis tarah ki madad chahiye, main sahi programme ki taraf guide karunga.\n\n"
                "Aap Contact page ya Support Us page se bhi contact kar sakte hain."
            ),
        },
        "aur_batao": {
            "en": (
                "All good here! 😄\n\n"
                "What would you like to know about AMP India Foundation?"
            ),
            "hi": (
                "सब बढ़िया! 😄\n\n"
                "आप AMP India Foundation के बारे में क्या जानना चाहेंगे?"
            ),
            "hinglish": (
                "Sab badhiya! 😄\n\n"
                "Aap AMP India Foundation ke baare me kya jaana chahenge?"
            ),
        },
        "sab_theek": {
            "en": "Glad to hear that! 😊\n\nHow can I help with AMP India Foundation today?",
            "hi": "सुनकर अच्छा लगा! 😊\n\nआज AMP India Foundation के बारे में मैं कैसे मदद कर सकता हूँ?",
            "hinglish": "Sunkar accha laga! 😊\n\nAaj AMP India Foundation ke baare me main kaise madad kar sakta hoon?",
        },
        "thanks": {
            "en": (
                "You're very welcome!\n\n"
                "If you have another question about AMP India Foundation, feel free to ask."
            ),
            "hi": (
                "आपका स्वागत है!\n\n"
                "AMP India Foundation के बारे में और प्रश्न हों तो पूछें।"
            ),
            "hinglish": (
                "Shukriya! Aapka swagat hai!\n\n"
                "AMP India Foundation ke baare me aur sawal hon to poochiye."
            ),
        },
        "jazakallah": {
            "en": (
                "Wa iyyakum! You're most welcome.\n\n"
                "If you need anything else about AMP India Foundation, I'm here to help."
            ),
            "hi": (
                "व इय्याकुम! आपका स्वागत है।\n\n"
                "AMP India Foundation के बारे में और मदद चाहिए तो पूछें।"
            ),
            "hinglish": (
                "Wa iyyakum! Aapka swagat hai.\n\n"
                "AMP India Foundation ke baare me aur madad chahiye to poochiye."
            ),
        },
        "ameen": {
            "en": "Ameen. 🤲\n\nHow else may I help you with AMP India Foundation today?",
            "hi": "आमीन। 🤲\n\nAMP India Foundation के बारे में और कैसे मदद करूँ?",
            "hinglish": "Ameen. 🤲\n\nAMP India Foundation ke baare me aur kaise madad karun?",
        },
        "mashallah": {
            "en": "Mashallah! 🌟\n\nI'm glad. How can I help with AMP India Foundation?",
            "hi": "माशाअल्लाह! 🌟\n\nAMP India Foundation में मैं कैसे मदद कर सकता हूँ?",
            "hinglish": "Mashallah! 🌟\n\nAMP India Foundation me main kaise madad kar sakta hoon?",
        },
        "inshallah": {
            "en": "Inshallah. 🤲\n\nI'm here whenever you need AMP India Foundation information.",
            "hi": "इंशाअल्लाह। 🤲\n\nजब चाहें AMP India Foundation की जानकारी पूछ सकते हैं।",
            "hinglish": "Inshallah. 🤲\n\nJab chahiye AMP India Foundation ki information pooch sakte hain.",
        },
        "alhamdulillah": {
            "en": "Alhamdulillah! 😊\n\nHow may I assist you with AMP India Foundation?",
            "hi": "अलहम्दुलिल्लाह! 😊\n\nAMP India Foundation में कैसे मदद करूँ?",
            "hinglish": "Alhamdulillah! 😊\n\nAMP India Foundation me kaise madad karun?",
        },
        "subhanallah": {
            "en": "Subhanallah.\n\nHow can I help with AMP India Foundation today?",
            "hi": "सुभानअल्लाह।\n\nआज AMP India Foundation में कैसे मदद करूँ?",
            "hinglish": "Subhanallah.\n\nAaj AMP India Foundation me kaise madad karun?",
        },
        "goodbye": {
            "en": (
                "Goodbye!\n\n"
                "Thank you for visiting AMP India Foundation. Feel free to come back anytime."
            ),
            "hi": (
                "अलविदा!\n\n"
                "AMP India Foundation आने के लिए धन्यवाद। कभी भी वापस आइए।"
            ),
            "hinglish": (
                "Alvida!\n\n"
                "AMP India Foundation visit karne ke liye shukriya. Kabhi bhi wapas aaiye."
            ),
        },
        "allah_hafiz": {
            "en": (
                "Allah Hafiz!\n\n"
                "Thank you for visiting AMP India Foundation. Take care."
            ),
            "hi": (
                "अल्लाह हाफ़िज़!\n\n"
                "AMP India Foundation आने के लिए धन्यवाद। अपना ख्याल रखें।"
            ),
            "hinglish": (
                "Allah Hafiz!\n\n"
                "AMP India Foundation visit karne ke liye shukriya. Apna khayal rakhein."
            ),
        },
        "khuda_hafiz": {
            "en": (
                "Khuda Hafiz!\n\n"
                "Thank you for visiting AMP India Foundation. Take care."
            ),
            "hi": (
                "ख़ुदा हाफ़िज़!\n\n"
                "AMP India Foundation आने के लिए धन्यवाद। अपना ख्याल रखें।"
            ),
            "hinglish": (
                "Khuda Hafiz!\n\n"
                "AMP India Foundation visit karne ke liye shukriya. Apna khayal rakhein."
            ),
        },
        "fi_amanillah": {
            "en": (
                "Fi Amanillah!\n\n"
                "Thank you for visiting AMP India Foundation. Take care, and come back anytime."
            ),
            "hi": (
                "फी अमानिल्लाह!\n\n"
                "AMP India Foundation आने के लिए धन्यवाद। अपना ख्याल रखें।"
            ),
            "hinglish": (
                "Fi Amanillah!\n\n"
                "AMP India Foundation visit karne ke liye shukriya. Apna khayal rakhein."
            ),
        },
        "good_night": {
            "en": (
                "Good night! 🌙\n\n"
                "Take care and have a wonderful rest.\n\n"
                "If you ever have a question about AMP India Foundation, I'm always here."
            ),
            "hi": (
                "शुभ रात्रि! 🌙\n\n"
                " अपना ख्याल रखें और अच्छी नींद लें।\n\n"
                "AMP India Foundation के बारे में कभी कोई सवाल हो तो मैं हमेशा यहाँ हूँ।"
            ),
            "hinglish": (
                "Good night! 🌙\n\n"
                "Take care and have a wonderful rest.\n\n"
                "Agar kabhi AMP India Foundation ke baare me koi sawal ho, main hamesha yahan hoon."
            ),
        },
    }

    bucket = replies.get(key) or replies["hello"]
    return bucket.get(lang) or bucket.get("en") or list(bucket.values())[0]
