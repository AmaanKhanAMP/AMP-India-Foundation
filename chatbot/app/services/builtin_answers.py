"""Layer-1 built-in verified answers for static AMP questions.

Used BEFORE Pinecone for common topics. Pinecone is reserved for dynamic CMS
content (events, gallery, testimonials, live projects).

Do not invent unpublished event dates here.
"""

from __future__ import annotations

import re
from typing import Optional, Set

from app.services.contact_facts import (
    ADDRESS,
    EMAIL,
    OFFICE_TIMINGS,
    PHONE,
    answer_contact,
    get_address,
    get_email,
    get_office_timings,
    get_phone,
)
from app.services.intent_router import Intent
from app.services.language_service import Language

# Verified donation account (from knowledge/donations.md + FAQ)
BANK_NAME = "Kotak Mahindra Bank"
ACCOUNT_NAME = "AMP India Foundation"
ACCOUNT_NUMBER = "3114476665"
ACCOUNT_TYPE = "Savings"
IFSC = "KKBK0001348"
VOLUNTEER_LINK = "https://tinyurl.com/AIFVolunteerRegn"
SUPPORT_US = "/support-us"

# Intents answered from built-in knowledge first (skip Pinecone)
STATIC_INTENTS: Set[Intent] = {
    Intent.CONTACT,
    Intent.DONATIONS,
    Intent.VOLUNTEERING,
}

# Intents that MUST use Pinecone / CMS
DYNAMIC_INTENTS: Set[Intent] = {
    Intent.UPCOMING_EVENTS,
    Intent.PAST_EVENTS,
    Intent.FEATURED_EVENT,
    Intent.EVENTS,
}


def wants_bank_details(question: str) -> bool:
    q = (question or "").lower()
    return bool(
        re.search(
            r"\b("
            r"bank\s*details?|bank\s*account|account\s*(?:number|no|details?)|"
            r"ifsc|neft|rtgs|transfer\s*details?|donation\s*account|"
            r"account\s*name|give\s*(?:me\s+)?bank|send\s*(?:me\s+)?bank"
            r")\b",
            q,
        )
    )


def wants_dynamic_cms(question: str) -> bool:
    """Force Pinecone when user asks for live/latest CMS listings."""
    q = (question or "").lower()
    return bool(
        re.search(
            r"\b("
            r"upcoming|past events?|featured|gallery|testimonial|"
            r"latest|this month|this year|cms|announcement|"
            r"what events|event list|job fair kab|medical camp kab"
            r")\b",
            q,
        )
    )


def _lang(language: Language | str) -> str:
    if isinstance(language, Language):
        return language.value
    return str(language or "en")


def _pick(block: dict, language: Language | str) -> str:
    lang = _lang(language)
    return block.get(lang) or block["en"]


_BANK = {
    "en": (
        "You can support AMP India Foundation through a direct bank transfer.\n\n"
        f"Bank Name: {BANK_NAME}\n"
        f"Account Name: {ACCOUNT_NAME}\n"
        f"Account Number: {ACCOUNT_NUMBER}\n"
        f"Account Type: {ACCOUNT_TYPE}\n"
        f"IFSC: {IFSC}\n\n"
        "If you would like, I can also explain how to donate via the Support Us page."
    ),
    "hi": (
        "आप सीधे बैंक ट्रांसफर से AMP India Foundation का समर्थन कर सकते हैं।\n\n"
        f"बैंक: {BANK_NAME}\n"
        f"खाता नाम: {ACCOUNT_NAME}\n"
        f"खाता संख्या: {ACCOUNT_NUMBER}\n"
        f"खाता प्रकार: {ACCOUNT_TYPE}\n"
        f"IFSC: {IFSC}\n\n"
        "चाहें तो Support Us पेज से ऑनलाइन दान का तरीका भी बता सकता हूँ।"
    ),
    "hinglish": (
        "Aap direct bank transfer se AMP India Foundation support kar sakte hain.\n\n"
        f"Bank Name: {BANK_NAME}\n"
        f"Account Name: {ACCOUNT_NAME}\n"
        f"Account Number: {ACCOUNT_NUMBER}\n"
        f"Account Type: {ACCOUNT_TYPE}\n"
        f"IFSC: {IFSC}\n\n"
        "Agar chaho to Support Us page se online donate kaise karein, woh bhi bata sakta hoon."
    ),
}

_UPI = {
    "en": (
        "Yes — you can donate via UPI.\n\n"
        "AMP UPI ID: AMPINDIA@KOTAK\n\n"
        "After donating, please send a confirmation email to info@ampindia.org."
    ),
    "hi": (
        "हाँ — आप UPI से दान कर सकते हैं।\n\n"
        "AMP UPI ID: AMPINDIA@KOTAK\n\n"
        "दान के बाद कृपया info@ampindia.org पर पुष्टि ईमेल भेजें।"
    ),
    "hinglish": (
        "Haan — aap UPI se donate kar sakte hain.\n\n"
        "AMP UPI ID: AMPINDIA@KOTAK\n\n"
        "Donate ke baad please info@ampindia.org par confirmation email bhejein."
    ),
}

_CHEQUE = {
    "en": (
        "Yes, cheque and demand draft (DD) donations are accepted.\n\n"
        "Cheque/DD in favour of: Association of Muslim Professionals\n\n"
        "Mail to:\n"
        "Association of Muslim Professionals\n"
        "Room 8, 1st Floor, Halima Manzil\n"
        "Mirza Ghalib Marg, Clare Road\n"
        "Nagpada, Mumbai – 400008\n\n"
        "This is an offline donation option listed on the Support Us page."
    ),
    "hi": (
        "हाँ, चेक और डिमांड ड्राफ्ट (DD) स्वीकार किए जाते हैं।\n\n"
        "चेक/DD: Association of Muslim Professionals के पक्ष में।\n\n"
        "पता: Room 8, 1st Floor, Halima Manzil, Mirza Ghalib Marg, Clare Road, "
        "Nagpada, Mumbai – 400008।"
    ),
    "hinglish": (
        "Haan, cheque aur DD accept kiye jaate hain.\n\n"
        "Cheque/DD in favour of: Association of Muslim Professionals\n\n"
        "Mail: Room 8, 1st Floor, Halima Manzil, Clare Road, Nagpada, Mumbai – 400008."
    ),
}

_RECEIPT = {
    "en": (
        "After your donation, please send a confirmation email to info@ampindia.org "
        "with your transfer reference so AMP India Foundation can acknowledge it "
        "and help with a donation receipt."
    ),
    "hi": (
        "दान के बाद कृपया info@ampindia.org पर ट्रांसफर संदर्भ के साथ पुष्टि ईमेल भेजें "
        "ताकि रसीद में मदद की जा सके।"
    ),
    "hinglish": (
        "Donation ke baad info@ampindia.org par transfer reference ke saath "
        "confirmation email bhejein taaki receipt me madad ho sake."
    ),
}

_TAX = {
    "en": (
        "AMP India Foundation is a Section 8 Company (non-profit) registered under "
        "the Companies Act, 2013 with the Ministry of Corporate Affairs.\n\n"
        "For current 80G / tax-exemption documentation, please email info@ampindia.org "
        "or use the Support Us page — I only share verified details from that page."
    ),
    "hi": (
        "AMP India Foundation कंपनी अधिनियम, 2013 के अंतर्गत पंजीकृत Section 8 "
        "(गैर-लाभकारी) कंपनी है। 80G दस्तावेज़ों के लिए info@ampindia.org पर लिखें।"
    ),
    "hinglish": (
        "AMP India Foundation Section 8 Company (non-profit) hai, Companies Act 2013 "
        "ke under registered. 80G documents ke liye info@ampindia.org par likhein."
    ),
}

_EDUCATION_PROJECT = {
    "en": (
        "AMP India Foundation's Education project focuses on skill development and "
        "livelihood support so BPL youth can continue learning and earn with dignity.\n\n"
        "Key initiatives include scholarships, career guidance, student mentorship, "
        "educational support, and Centres of Excellence. AIF also runs vocational "
        "training — such as mobile repairing, AC/refrigerator maintenance, water-filter "
        "repair, and motor-vehicle servicing — including NSDC-sponsored short-term "
        "skills programmes.\n\n"
        "More detail is on the Education project page: /projects/education"
    ),
    "hi": (
        "AMP India Foundation का शिक्षा प्रोजेक्ट कौशल विकास और आजीविका सहायता पर केंद्रित है "
        "ताकि BPL युवा पढ़ाई जारी रख सकें। छात्रवृत्ति, करियर मार्गदर्शन, मेंटरशिप और व्यावसायिक "
        "प्रशिक्षण शामिल हैं। विवरण: /projects/education।"
    ),
    "hinglish": (
        "AMP India Foundation ka Education project skill development aur livelihood "
        "support par focus karta hai — scholarships, career guidance, mentorship aur "
        "vocational training. Details: /projects/education."
    ),
}

_CONTACT = {
    "en": (
        f"You can reach AMP India Foundation at:\n\n"
        f"Phone: {PHONE}\n"
        f"Email: {EMAIL}\n"
        f"Address: {ADDRESS}\n"
        f"Office hours: {OFFICE_TIMINGS} (closed Sundays)."
    ),
    "hi": (
        f"AMP India Foundation से संपर्क करें:\n\n"
        f"फ़ोन: {PHONE}\n"
        f"ईमेल: {EMAIL}\n"
        f"पता: {ADDRESS}\n"
        f"समय: {OFFICE_TIMINGS} (रविवार बंद)।"
    ),
    "hinglish": (
        f"AMP India Foundation se contact karein:\n\n"
        f"Phone: {PHONE}\n"
        f"Email: {EMAIL}\n"
        f"Address: {ADDRESS}\n"
        f"Timings: {OFFICE_TIMINGS} (Sunday band)."
    ),
}

_LOCATION = {
    "en": (
        "AMP India Foundation is located at:\n\n"
        "Room 9, 1st Floor,\n"
        "Halima Manzil,\n"
        "Mirza Ghalib Marg,\n"
        "A Clare Road,\n"
        "Nagpada,\n"
        "Mumbai – 400008.\n\n"
        f"Office Hours:\n{OFFICE_TIMINGS}.\n\n"
        "Need directions? I'd be happy to help."
    ),
    "hi": (
        "AMP India Foundation का पता:\n\n"
        "Room 9, 1st Floor, Halima Manzil,\n"
        "Mirza Ghalib Marg, A Clare Road,\n"
        "Nagpada, Mumbai – 400008.\n\n"
        f"कार्यालय समय: {OFFICE_TIMINGS}.\n\n"
        "दिशा-निर्देश चाहिए हों तो बताएं।"
    ),
    "hinglish": (
        "AMP India Foundation yahan situated hai:\n\n"
        "Room 9, 1st Floor, Halima Manzil,\n"
        "Mirza Ghalib Marg, A Clare Road,\n"
        "Nagpada, Mumbai – 400008.\n\n"
        f"Office hours: {OFFICE_TIMINGS}.\n\n"
        "Directions chahiye to bataiye."
    ),
}

_DONATE = {
    "en": (
        "You can donate through the official Support Us page (/support-us), UPI, bank transfer, or cheque/DD.\n\n"
        "If you would like bank, UPI, or cheque details, just let me know."
    ),
    "hi": (
        "आप आधिकारिक Support Us पेज से या सीधे बैंक ट्रांसफर से दान कर सकते हैं।\n\n"
        "बैंक खाता विवरण चाहिए हो तो बताएं।"
    ),
    "hinglish": (
        "Aap official Support Us page se ya direct bank transfer se donate kar sakte hain.\n\n"
        "Bank account details chahiye ho to bas bataiye."
    ),
}

_VOLUNTEER = {
    "en": (
        "You can volunteer with AMP India Foundation by filling out the official "
        "volunteer registration form.\n\n"
        "After registering, the AIF team will contact you regarding suitable opportunities.\n\n"
        f"Registration link: {VOLUNTEER_LINK}\n\n"
        "Would you like help choosing an area to volunteer in?"
    ),
    "hi": (
        "आप आधिकारिक पंजीकरण फ़ॉर्म भरकर AMP India Foundation के साथ स्वयंसेवक बन सकते हैं।\n\n"
        "पंजीकरण के बाद टीम उपयुक्त अवसरों के बारे में संपर्क करेगी।\n\n"
        f"लिंक: {VOLUNTEER_LINK}"
    ),
    "hinglish": (
        "Aap official volunteer registration form bhar kar AMP India Foundation ke saath "
        "volunteer ban sakte hain.\n\n"
        "Register ke baad AIF team suitable opportunities ke baare me contact karegi.\n\n"
        f"Link: {VOLUNTEER_LINK}"
    ),
}

_EMPLOYMENT = {
    "en": (
        "You can receive employment support through AMP India Foundation's "
        "Employment Assistance Cell — including job fairs, placement drives, "
        "resume review, mock interviews, and career guidance.\n\n"
        "AMP does not run a permanent online job portal; these programmes connect "
        "candidates with employers."
    ),
    "hi": (
        "AMP India Foundation का Employment Assistance Cell रोज़गार सहायता देता है — "
        "जॉब फेयर, प्लेसमेंट ड्राइव, रिज़्यूमे समीक्षा, मॉक इंटरव्यू और करियर मार्गदर्शन।\n\n"
        "स्थायी ऑनलाइन जॉब पोर्टल नहीं है; ये कार्यक्रम उम्मीदवारों को नियोक्ताओं से जोड़ते हैं।"
    ),
    "hinglish": (
        "AMP India Foundation ka Employment Assistance Cell employment support deta hai — "
        "job fairs, placement drives, resume review, mock interviews aur career guidance.\n\n"
        "Permanent job portal nahi hai — ye programmes candidates ko employers se connect karte hain."
    ),
}

_HEALTHCARE = {
    "en": (
        "AMP India Foundation supports healthcare through medical camps, medical relief, "
        "health screenings, and assistance pathways for critical illness.\n\n"
        "The goal is to make basic healthcare support more accessible to underprivileged "
        "communities. Ask about upcoming medical camps if you need scheduled dates."
    ),
    "hi": (
        "AMP India Foundation मेडिकल कैंप, मेडिकल रिलीफ, स्वास्थ्य जांच और गंभीर बीमारी "
        "के सहायता मार्गों के माध्यम से स्वास्थ्य सेवा में सहयोग करता है।\n\n"
        "उद्देश्य वंचित समुदायों के लिए स्वास्थ्य सहायता अधिक सुलभ बनाना है।"
    ),
    "hinglish": (
        "AMP India Foundation medical camps, medical relief, health screenings aur "
        "critical illness support ke through healthcare me madad karti hai.\n\n"
        "Maqsad underprivileged communities ke liye healthcare support accessible banana hai."
    ),
}

_SCHOLARSHIP = {
    "en": (
        "AMP India Foundation supports deserving students through scholarship and "
        "education-assistance programmes.\n\n"
        "Share whether you need eligibility, documents, or application guidance, and "
        "I'll help from verified information."
    ),
    "hi": (
        "AMP India Foundation योग्य छात्रों के लिए छात्रवृत्ति और शिक्षा सहायता कार्यक्रम चलाता है।\n\n"
        "पात्रता, दस्तावेज़ या आवेदन प्रक्रिया बताएं — मैं सत्यापित जानकारी से मार्गदर्शन करूँगा।"
    ),
    "hinglish": (
        "AMP India Foundation deserving students ke liye scholarship aur education "
        "support programmes chalati hai.\n\n"
        "Eligibility, documents ya application process bataiye — main verified information se guide karunga."
    ),
}

_ABOUT = {
    "en": (
        "AMP India Foundation is a non-profit organisation dedicated to empowering "
        "underprivileged communities through education, employment assistance, "
        "scholarships, healthcare, economic empowerment, and community development. "
        "Its goal is to help individuals build sustainable and dignified lives."
    ),
    "hi": (
        "AMP India Foundation एक गैर-लाभकारी संस्था है जो शिक्षा, रोज़गार सहायता, "
        "छात्रवृत्ति, स्वास्थ्य सेवा, आर्थिक सशक्तिकरण और सामुदायिक विकास के माध्यम से "
        "वंचित समुदायों को सशक्त बनाती है — ताकि लोग सम्मानजनक जीवन बना सकें।"
    ),
    "hinglish": (
        "AMP India Foundation ek non-profit organisation hai jo education, employment "
        "assistance, scholarships, healthcare, economic empowerment aur community "
        "development ke through underprivileged communities ko empower karti hai — "
        "taaki log dignified aur sustainable life bana saken."
    ),
}

_MISSION = {
    "en": (
        "AMP India Foundation's mission is to create real opportunity through education, "
        "skills, employment support, healthcare, and community programmes so every "
        "deserving individual can build a dignified future."
    ),
    "hi": (
        "AMP India Foundation का मिशन शिक्षा, कौशल, रोज़गार सहायता, स्वास्थ्य और "
        "सामुदायिक कार्यक्रमों से वास्तविक अवसर बनाना है।"
    ),
    "hinglish": (
        "AMP India Foundation ka mission education, skills, employment support, "
        "healthcare aur community programmes se real opportunity banana hai."
    ),
}

_VISION = {
    "en": (
        "AMP India Foundation envisions empowered communities where education, "
        "livelihood, and healthcare support help people move toward self-reliance "
        "and dignity."
    ),
    "hi": (
        "AMP India Foundation की दृष्टि ऐसे सशक्त समुदाय हैं जहाँ शिक्षा, आजीविका और "
        "स्वास्थ्य सहायता से लोग आत्मनिर्भरता की ओर बढ़ें।"
    ),
    "hinglish": (
        "AMP India Foundation ka vision empowered communities hai jahan education, "
        "livelihood aur healthcare support se log self-reliance ki taraf badhein."
    ),
}

_GENUINE = {
    "en": (
        "Yes — AMP India Foundation (AIF) is a registered non-profit organisation "
        "working openly through education, employment, healthcare, scholarships, and "
        "community programmes. You can verify details via the official website or by "
        f"contacting the office at {PHONE}."
    ),
    "hi": (
        "हाँ — AMP India Foundation एक पंजीकृत गैर-लाभकारी संस्था है जो शिक्षा, रोज़गार, "
        f"स्वास्थ्य और सामुदायिक कार्यक्रमों के माध्यम से काम करती है। संपर्क: {PHONE}."
    ),
    "hinglish": (
        "Haan — AMP India Foundation registered non-profit organisation hai jo "
        "education, employment, healthcare aur community programmes ke through kaam "
        f"karti hai. Contact: {PHONE}."
    ),
}

_INCLUSIVE = {
    "en": (
        "AMP India Foundation is open to everyone. It is not limited to any one religion — "
        "Hindus, Muslims, Christians, Sikhs, and people of all faiths can participate. "
        "Girls and women can apply to programmes as per the relevant guidelines. "
        "Anyone who meets a programme's criteria is welcome.\n\n"
        "Tell me whether you want volunteering, scholarships, education, employment, "
        "healthcare, or another programme, and I'll guide you."
    ),
    "hi": (
        "AMP India Foundation सभी के लिए खुली है। यह किसी एक धर्म तक सीमित नहीं है — "
        "हिंदू, मुस्लिम, ईसाई, सिख और सभी पृष्ठभूमि के लोग भाग ले सकते हैं। "
        "लड़कियाँ और महिलाएँ भी कार्यक्रमों के दिशानिर्देशों के अनुसार आवेदन कर सकती हैं।\n\n"
        "बताएं आपको स्वयंसेवा, छात्रवृत्ति, शिक्षा, रोज़गार या स्वास्थ्य में से क्या चाहिए।"
    ),
    "hinglish": (
        "AMP India Foundation sabke liye open hai. Ye kisi ek religion tak limited nahi hai — "
        "Hindu, Muslim, Christian, Sikh aur har background ke log participate kar sakte hain. "
        "Girls aur women bhi programme guidelines ke hisaab se apply kar sakti hain.\n\n"
        "Bataiye volunteering, scholarships, education, employment ya healthcare me se kya chahiye."
    ),
}


def inclusive_reply(language: Language | str = Language.ENGLISH) -> str:
    return _pick(_INCLUSIVE, language)


_FEES = {
    "en": (
        "AMP India Foundation does not charge any fee to attend its job fairs unless "
        "specifically mentioned for a particular event."
    ),
    "hi": (
        "AMP India Foundation के जॉब फेयर में भाग लेने के लिए कोई शुल्क नहीं लिया जाता, "
        "जब तक किसी विशेष कार्यक्रम में स्पष्ट रूप से उल्लेख न हो।"
    ),
    "hinglish": (
        "AMP India Foundation ke job fairs attend karne ke liye koi fee nahi hoti, "
        "jab tak kisi particular event me clearly mention na ho."
    ),
}

_UNVERIFIED = {
    "en": (
        "I don't have verified information about that. For the most accurate "
        "information, please contact AMP India Foundation directly.\n\n"
        f"Phone: {PHONE}\nEmail: {EMAIL}"
    ),
    "hi": (
        "इसके बारे में मेरे पास सत्यापित जानकारी नहीं है। सटीक जानकारी के लिए कृपया "
        f"AMP India Foundation से सीधे संपर्क करें।\n\nफ़ोन: {PHONE}\nईमेल: {EMAIL}"
    ),
    "hinglish": (
        "Iske baare me mere paas verified information nahi hai. Accurate details ke liye "
        f"AMP India Foundation se seedha contact karein.\n\nPhone: {PHONE}\nEmail: {EMAIL}"
    ),
}

_DOCUMENTS = {
    "en": (
        "Required documents depend on the specific programme (scholarship, employment "
        "support, volunteering, or medical assistance). Share which programme you mean, "
        "and I'll guide you from verified information — or contact the office for the "
        f"current checklist at {PHONE}."
    ),
    "hi": (
        "आवश्यक दस्तावेज़ कार्यक्रम पर निर्भर करते हैं (छात्रवृत्ति, रोज़गार, स्वयंसेवा या "
        f"चिकित्सा सहायता)। बताएं किस कार्यक्रम के लिए चाहिए — या कार्यालय से संपर्क करें: {PHONE}."
    ),
    "hinglish": (
        "Required documents programme par depend karte hain (scholarship, employment, "
        f"volunteer ya medical). Bataiye kaunsa programme — ya office contact karein: {PHONE}."
    ),
}

_GET_HELP = {
    "en": (
        "I can help you with AMP India Foundation programmes — education and scholarships, "
        "employment and job fairs, volunteering, healthcare support, or donations.\n\n"
        "Tell me what you need, and I'll guide you to the right next step."
    ),
    "hi": (
        "मैं AMP India Foundation के कार्यक्रमों में मदद कर सकता हूँ — शिक्षा/छात्रवृत्ति, "
        "रोज़गार, स्वयंसेवा, स्वास्थ्य या दान। बताएं आपको क्या चाहिए।"
    ),
    "hinglish": (
        "Main AMP India Foundation programmes me madad kar sakta hoon — education/"
        "scholarship, employment, volunteer, healthcare ya donation. Bataiye kya chahiye."
    ),
}

_PROJECTS = {
    "en": (
        "AMP India Foundation runs programmes across:\n"
        "• Education\n"
        "• Employment & job fairs\n"
        "• Scholarships\n"
        "• Healthcare\n"
        "• Economic empowerment\n\n"
        "Ask about a specific area — for example scholarships, volunteering, or "
        "upcoming events — and I'll guide you."
    ),
    "hi": (
        "AMP India Foundation के मुख्य कार्यक्रम:\n"
        "• शिक्षा\n• रोज़गार\n• छात्रवृत्ति\n• स्वास्थ्य\n• आर्थिक सशक्तिकरण\n\n"
        "किसी एक क्षेत्र के बारे में पूछें — मैं मार्गदर्शन करूँगा।"
    ),
    "hinglish": (
        "AMP India Foundation ke main programmes:\n"
        "• Education\n• Employment\n• Scholarships\n• Healthcare\n• Economic empowerment\n\n"
        "Kisi specific area ke baare me poochiye — main guide karunga."
    ),
}

_TRAINING = {
    "en": (
        "AMP India Foundation offers skill-development and employability-oriented "
        "training linked to its education and employment programmes.\n\n"
        "Tell me whether you want career guidance, job-fair preparation, or "
        "education support, and I'll point you to the right path."
    ),
    "hi": (
        "AMP India Foundation कौशल विकास और रोज़गार-उन्मुख प्रशिक्षण सहायता देता है।\n\n"
        "करियर मार्गदर्शन, जॉब फेयर तैयारी या शिक्षा सहायता में से बताएं।"
    ),
    "hinglish": (
        "AMP India Foundation skill development aur employability training support deti hai.\n\n"
        "Career guidance, job-fair preparation ya education support — bataiye kya chahiye."
    ),
}

_MENTORSHIP = {
    "en": (
        "AMP India Foundation supports mentorship and career guidance so youth can "
        "make informed education and career choices.\n\n"
        f"For current mentorship opportunities, contact {PHONE} or {EMAIL}."
    ),
    "hi": (
        "AMP India Foundation मेंटरशिप और करियर मार्गदर्शन के माध्यम से युवाओं की मदद करता है।\n\n"
        f"वर्तमान अवसरों के लिए {PHONE} या {EMAIL} पर संपर्क करें।"
    ),
    "hinglish": (
        "AMP India Foundation mentorship aur career guidance ke through youth ki madad karti hai.\n\n"
        f"Current opportunities ke liye {PHONE} ya {EMAIL} par contact karein."
    ),
}

_ECONOMIC = {
    "en": (
        "Economic Empowerment is a core AMP India Foundation project. It cultivates "
        "entrepreneurial self-reliance through livelihood support, early capital guidance, "
        "small-enterprise tools, marketplace connections, financial awareness, and "
        "women-and-youth empowerment programmes.\n\n"
        "You can read more on the Economic Empowerment project page: /projects/empowerment"
    ),
    "hi": (
        "आर्थिक सशक्तिकरण AMP India Foundation का मुख्य फोकस है — कौशल और सामुदायिक "
        "सहायता से परिवारों को स्थिर आजीविका बनाने में मदद।"
    ),
    "hinglish": (
        "Economic empowerment AMP India Foundation ka core focus hai — skills aur "
        "community support se families ko stable livelihood banane me madad."
    ),
}


def _wants_assistance_contact(q: str) -> bool:
    return bool(
        re.search(
            r"\b("
            r"how (?:can|do) i (?:apply|register|join|get help|contact)|"
            r"help me|assist(?:ance)?|registration|apply|contact (?:me|us)|"
            r"madad|kaise (?:apply|register|join)|documents? needed|"
            r"what documents"
            r")\b",
            q,
        )
    )


def _with_optional_contact(text: str, q: str, language: Language | str) -> str:
    if not _wants_assistance_contact(q):
        return text
    if PHONE in text or EMAIL in text:
        return text
    if _lang(language) == "hi":
        return f"{text}\n\nसहायता के लिए: {PHONE} | {EMAIL}"
    if _lang(language) == "hinglish":
        return f"{text}\n\nMadad ke liye: {PHONE} | {EMAIL}"
    return f"{text}\n\nFor assistance: {PHONE} | {EMAIL}"


def answer_builtin(
    question: str,
    *,
    intent: Optional[Intent] = None,
    language: Language | str = Language.ENGLISH,
) -> Optional[str]:
    """Return a short natural answer for static topics, or None to continue pipeline."""
    from app.services.text_normalize import apply_spell_fixes

    q = apply_spell_fixes((question or "").lower())
    lang = language

    # --- Special FAQs (zero tokens) ---
    if re.search(
        r"\b(who (?:founded|founded|started|established)|founder of|"
        r"who (?:heads|leads|runs)|chairman|current head|ceo of)\b",
        q,
    ):
        return _pick(_UNVERIFIED, lang)

    if re.search(
        r"\b(genuine|trustworthy|legit|scam|fraud|real ngo|bharosa|trust\b)\b",
        q,
    ):
        return _pick(_GENUINE, lang)

    if re.search(
        r"\b(discriminat|religion|only (?:muslim|hindu)|anyone (?:can )?apply|"
        r"can women|can girls?|can hindus?|women volunteer|open to all|"
        r"who can (?:participate|join|apply)|kisike liye|sirf muslim)\b",
        q,
    ):
        return _pick(_INCLUSIVE, lang)

    if re.search(
        r"\b(fees?|fee|cost|price|payment|registration fee|job fair fee|"
        r"kitna (?:paisa|charge)|charges?)\b",
        q,
    ):
        return _pick(_FEES, lang)

    if re.search(r"\b(what documents|documents? needed|required documents|kya documents)\b", q):
        return _pick(_DOCUMENTS, lang)

    if re.search(
        r"\b(how can i get help|how do i get help|i need help|madad chahiye|"
        r"kaise madad|get help)\b",
        q,
    ) and not re.search(
        r"\b(job|scholarship|volunteer|donat|medical|healthcare|hospital)\b", q
    ):
        return _pick(_GET_HELP, lang)

    if re.search(r"\bmission\b", q) and not re.search(r"\bvision\b", q):
        return _pick(_MISSION, lang)
    if re.search(r"\bvision\b", q):
        return _pick(_VISION, lang)

    if re.search(r"\bupi\b", q) and (
        intent in {Intent.DONATIONS, None, Intent.UNKNOWN} or re.search(r"\b(donat|upi)\b", q)
    ):
        return _pick(_UPI, lang)
    if re.search(r"\b(cheque|check|demand\s*draft|\bdd\b|offline donation)\b", q):
        return _pick(_CHEQUE, lang)
    if re.search(r"\b(80g|tax exemption|tax benefit)\b", q):
        return _pick(_TAX, lang)
    if re.search(r"\b(receipt|acknowledg(?:e|ement)?|invoice)\b", q) and (
        intent == Intent.DONATIONS or re.search(r"\b(donat|support)\b", q)
    ):
        return _pick(_RECEIPT, lang)

    if wants_bank_details(q) or (
        intent == Intent.DONATIONS and re.search(r"\b(bank|ifsc|account)\b", q)
    ):
        return _pick(_BANK, lang)

    if intent == Intent.CONTACT or (
        intent is None
        and re.search(
            r"\b(contact|phone|email|helpline|timing|timings|hours|address|office timings?)\b",
            q,
        )
        and not re.search(
            r"\b(biwi|shohar|dating|education|empowerment|python|world cup|form)\b",
            q,
        )
    ):
        # Prefer channel-specific answers before address ("email address" ≠ office address).
        wants_email = bool(re.search(r"\b(e-?mail|mail)\b", q))
        wants_phone = bool(
            re.search(r"\b(phone|mobile|helpline|call|contact number|number)\b", q)
        ) and not wants_email
        wants_hours = bool(re.search(r"\b(timing|timings|hours|open|kitne baje)\b", q))
        wants_addr = bool(
            re.search(r"\b(location|where|reach|directions?|kaha|kahan|office address)\b", q)
            or (
                re.search(r"\baddress\b", q)
                and not wants_email
                and not re.search(r"\bemail\s+address\b", q)
            )
        )
        if wants_email and not (wants_addr or wants_phone or wants_hours):
            email = get_email()
            if _lang(lang) == "hi":
                return f"ईमेल: {email}"
            if _lang(lang) == "hinglish":
                return f"Email: {email}"
            return f"You can email AMP India Foundation at:\n{email}"
        if wants_phone and not (wants_addr or wants_hours):
            phone = get_phone()
            if _lang(lang) == "hi":
                return f"फ़ोन: {phone}"
            if _lang(lang) == "hinglish":
                return f"Phone: {phone}"
            return f"You can call AMP India Foundation at:\n{phone}"
        if wants_hours and not wants_addr:
            timings = get_office_timings()
            phone = get_phone()
            if _lang(lang) == "hi":
                return f"कार्यालय समय: {timings}। रविवार को बंद रहता है।\n\nफ़ोन: {phone}"
            if _lang(lang) == "hinglish":
                return f"Office timing: {timings}. Sunday band rehta hai.\n\nPhone: {phone}"
            return (
                f"Office hours: {timings}.\n"
                "Closed on Sundays.\n\n"
                f"Phone: {phone}"
            )
        if wants_addr and not wants_email and not wants_phone:
            return (
                "AMP India Foundation is located at:\n\n"
                f"{get_address()}"
            )
        return answer_contact(question)

    if intent == Intent.DONATIONS or re.search(
        r"\b(donat(?:e|ion|ions)?|support us|contribute)\b", q
    ):
        return _pick(_DONATE, lang)

    if intent == Intent.VOLUNTEERING or re.search(r"\bvolunteer|स्वयंसेवक\b", q):
        return _with_optional_contact(_pick(_VOLUNTEER, lang), q, lang)

    if intent == Intent.EMPLOYMENT or re.search(
        r"\b(job|jobs|employment|naukri|placement|career|resume|interview|work)\b", q
    ):
        if not re.search(r"\b(upcoming|event|fair kab|camp)\b", q):
            return _with_optional_contact(_pick(_EMPLOYMENT, lang), q, lang)

    if intent == Intent.MEDICAL or re.search(
        r"\b(healthcare|medical|health support|hospital|treatment|ilaj|doctor)\b", q
    ):
        if not re.search(r"\b(camp|upcoming|event)\b", q):
            return _with_optional_contact(_pick(_HEALTHCARE, lang), q, lang)

    if intent == Intent.SCHOLARSHIPS or re.search(r"\bscholarship|छात्रवृत्ति\b", q):
        return _with_optional_contact(_pick(_SCHOLARSHIP, lang), q, lang)

    if intent == Intent.AMP_KNOWLEDGE or re.search(
        r"\b(what is (?:aif|amp)|about (?:aif|amp)|tell me about (?:aif|amp|the foundation))\b",
        q,
    ):
        return _pick(_ABOUT, lang)

    if intent == Intent.EDUCATION or (
        re.search(r"\beducation\b", q)
        and not re.search(r"\b(scholarship|event|job\s*fair)\b", q)
    ):
        return _pick(_EDUCATION_PROJECT, lang)

    if intent == Intent.ECONOMIC_EMPOWERMENT or re.search(
        r"\beconomic|empowerment|livelihood\b", q
    ):
        return _pick(_ECONOMIC, lang)

    if intent == Intent.TRAINING:
        return _pick(_TRAINING, lang)

    if intent == Intent.MENTORSHIP:
        return _pick(_MENTORSHIP, lang)

    if intent == Intent.PROJECTS and not wants_dynamic_cms(q):
        return _pick(_PROJECTS, lang)

    return None


def should_use_builtin_first(intent: Intent, question: str) -> bool:
    if intent in DYNAMIC_INTENTS:
        return False
    if wants_dynamic_cms(question):
        return False
    if intent in STATIC_INTENTS:
        return True
    return False
