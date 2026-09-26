"""DEPRECATED for live chat path (kept for warmup / rollback).

Historically this module provided fast FAQ answers. Production chat now uses
Pinecone + local_fallback + emergency_knowledge instead.

Do NOT delete — AiService no longer calls lookup_faq(), but startup may still
warm the cache, and tests may import it.

Original: In-memory FAQ / fact cache — multilingual, no Gemini / Pinecone.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from app.services.intent_router import Intent
from app.services.language_service import Language


@dataclass(frozen=True)
class FaqEntry:
    intent: Intent
    keywords: Tuple[str, ...]
    answers: Dict[str, str]  # language.value -> answer
    followups: Dict[str, Tuple[str, ...]]
    priority: int = 0


@dataclass
class FaqHit:
    answer: str
    intent: Intent
    score: float
    lookup_ms: float
    key: str
    followups: Tuple[str, ...] = ()


def _a(en: str, hi: str, hinglish: str) -> Dict[str, str]:
    return {
        Language.ENGLISH.value: en,
        Language.HINDI.value: hi,
        Language.HINGLISH.value: hinglish,
    }


def _f(en: Tuple[str, ...], hi: Tuple[str, ...], hinglish: Tuple[str, ...]) -> Dict[str, Tuple[str, ...]]:
    return {
        Language.ENGLISH.value: en,
        Language.HINDI.value: hi,
        Language.HINGLISH.value: hinglish,
    }


CONTACT_PHONE = _a(
    "You can contact AMP India Foundation at **+91 8291101312**.\n\nOffice timings: Monday to Saturday, 9:00 AM to 6:00 PM.",
    "आप AMP India Foundation से **+91 8291101312** पर संपर्क कर सकते हैं।\n\nकार्यालय समय: सोमवार से शनिवार, सुबह 9:00 से शाम 6:00 बजे तक।",
    "Aap AMP India Foundation se **+91 8291101312** par contact kar sakte hain.\n\nOffice timing: Monday se Saturday, 9:00 AM se 6:00 PM.",
)
CONTACT_EMAIL = _a(
    "Email AMP India Foundation at **contact@ampindiafoundation.org**.\n\nWe typically reply within 24 hours.",
    "AMP India Foundation को **contact@ampindiafoundation.org** पर ईमेल करें।\n\nहम आमतौर पर 24 घंटे में उत्तर देते हैं।",
    "AMP India Foundation ko **contact@ampindiafoundation.org** par email karein.\n\nHum usually 24 hours me reply karte hain.",
)
CONTACT_ADDRESS = _a(
    "**Office address**\n\nRoom 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008.",
    "**कार्यालय पता**\n\nRoom 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008.",
    "**Office address**\n\nRoom 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008.",
)
CONTACT_TIMINGS = _a(
    "AMP India Foundation office timings are **Monday to Saturday, 9:00 AM to 6:00 PM**.",
    "AMP India Foundation का कार्यालय समय **सोमवार से शनिवार, सुबह 9:00 से शाम 6:00** है।",
    "AMP India Foundation ka office timing **Monday se Saturday, 9:00 AM se 6:00 PM** hai.",
)
CONTACT_FULL = _a(
    "**Contact AMP India Foundation**\n\n"
    "• Phone: +91 8291101312\n"
    "• Email: contact@ampindiafoundation.org\n"
    "• Timings: Monday to Saturday, 9:00 AM to 6:00 PM\n"
    "• Address: Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008",
    "**AMP India Foundation से संपर्क**\n\n"
    "• फ़ोन: +91 8291101312\n"
    "• ईमेल: contact@ampindiafoundation.org\n"
    "• समय: सोमवार से शनिवार, 9:00 AM – 6:00 PM\n"
    "• पता: Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008",
    "**AMP India Foundation contact**\n\n"
    "• Phone: +91 8291101312\n"
    "• Email: contact@ampindiafoundation.org\n"
    "• Timing: Monday se Saturday, 9:00 AM – 6:00 PM\n"
    "• Address: Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, A Clare Road, Nagpada, Mumbai - 400008",
)

DONATION = _a(
    "**Support AMP India Foundation** via direct bank transfer:\n\n"
    "• Bank: Kotak Mahindra\n"
    "• Account Name: AMP India Foundation\n"
    "• Account Number: 3114476665\n"
    "• Account Type: Savings\n"
    "• IFSC: KKBK0001348\n\n"
    "Visit the Support Us page for more details, or call +91 8291101312.",
    "**AMP India Foundation** का समर्थन बैंक ट्रांसफर से करें:\n\n"
    "• बैंक: Kotak Mahindra\n"
    "• खाता नाम: AMP India Foundation\n"
    "• खाता संख्या: 3114476665\n"
    "• प्रकार: Savings\n"
    "• IFSC: KKBK0001348\n\n"
    "अधिक जानकारी के लिए Support Us पेज देखें या +91 8291101312 पर कॉल करें।",
    "**AMP India Foundation** ko direct bank transfer se support kar sakte hain:\n\n"
    "• Bank: Kotak Mahindra\n"
    "• Account Name: AMP India Foundation\n"
    "• Account Number: 3114476665\n"
    "• Type: Savings\n"
    "• IFSC: KKBK0001348\n\n"
    "Zyada details ke liye Support Us page dekhein, ya +91 8291101312 par call karein.",
)

SCHOLARSHIP = _a(
    "**AMP Scholarship & Education Support**\n\n"
    "AMP India Foundation offers support for meritorious, underprivileged students:\n\n"
    "• AMP Higher Education Scholarship\n"
    "• Orphans' Basic Education Support\n"
    "• Self-Employment Assistance\n"
    "• Critical Illness & Medical Support\n\n"
    "Apply through AMP's online crowdfunding and welfare portals. Applications are verified on merit and economic need.",
    "**AMP छात्रवृत्ति और शिक्षा सहायता**\n\n"
    "मेधावी और वंचित छात्रों के लिए सहायता:\n\n"
    "• उच्च शिक्षा छात्रवृत्ति\n"
    "• अनाथ बच्चों की बुनियादी शिक्षा सहायता\n"
    "• स्वरोज़गार सहायता\n"
    "• गंभीर बीमारी और चिकित्सा सहायता\n\n"
    "ऑनलाइन पोर्टल के माध्यम से आवेदन करें। योग्यता और आर्थिक आवश्यकता के आधार पर सत्यापन होता है।",
    "**AMP Scholarship & Education Support**\n\n"
    "Meritorious aur underprivileged students ke liye:\n\n"
    "• Higher Education Scholarship\n"
    "• Orphans' Basic Education Support\n"
    "• Self-Employment Assistance\n"
    "• Critical Illness & Medical Support\n\n"
    "Online crowdfunding / welfare portal se apply karein. Merit aur economic need ke basis par verify hota hai.",
)

SCHOLARSHIP_APPLY = _a(
    "**How to apply**\n\n"
    "Deserving students can apply through AMP's designated online crowdfunding and welfare application portals. "
    "Submissions are verified based on merit and economic need.\n\n"
    "Need help? Call +91 8291101312 or email contact@ampindiafoundation.org.",
    "**आवेदन कैसे करें**\n\n"
    "पात्र छात्र AMP के ऑनलाइन क्राउडफंडिंग और कल्याण आवेदन पोर्टल के माध्यम से आवेदन कर सकते हैं। "
    "आवेदन योग्यता और आर्थिक आवश्यकता के आधार पर सत्यापित होते हैं।\n\n"
    "मदद चाहिए? +91 8291101312 पर कॉल करें।",
    "**Apply kaise karein**\n\n"
    "Eligible students AMP ke online crowdfunding aur welfare portals se apply kar sakte hain. "
    "Applications merit aur economic need ke basis par verify hote hain.\n\n"
    "Help chahiye? +91 8291101312 par call karein.",
)

VOLUNTEER = _a(
    "**Volunteer with AMP India Foundation**\n\n"
    "Register here: https://tinyurl.com/AIFVolunteerRegn\n\n"
    "Professionals and student mentors can offer career guidance, training, or field support. "
    "After registration, the team typically responds within a few working days.",
    "**AMP India Foundation के साथ स्वयंसेवक बनें**\n\n"
    "पंजीकरण: https://tinyurl.com/AIFVolunteerRegn\n\n"
    "पेशेवर और छात्र मेंटर करियर मार्गदर्शन, प्रशिक्षण या फील्ड सपोर्ट दे सकते हैं। "
    "पंजीकरण के बाद टीम कुछ कार्य दिवसों में संपर्क करती है।",
    "**Volunteer kaise banein**\n\n"
    "Register yahan karein: https://tinyurl.com/AIFVolunteerRegn\n\n"
    "Professionals aur student mentors career guidance, training ya field support de sakte hain. "
    "Registration ke baad team kuch working days me respond karti hai.",
)

EMPLOYMENT = _a(
    "**Employment & Job Fair Support**\n\n"
    "AMP India Foundation helps youth through job fairs, placement drives, resume clinics, "
    "mock interviews, and the AMP Employment Assistance Cell.\n\n"
    "**Upcoming highlights**\n"
    "• Career Guidance & Employment Drive 2026 — 15 March 2026, Mumbai\n"
    "• National Mega Job Fair & Placement Drive — 12 Aug 2026, Mumbai / Nagpada\n\n"
    "You can participate in these employment programs — this is separate from volunteering.",
    "**रोज़गार और जॉब फेयर सहायता**\n\n"
    "AMP India Foundation जॉब फेयर, प्लेसमेंट ड्राइव, रिज़्यूमे क्लिनिक, मॉक इंटरव्यू "
    "और Employment Assistance Cell के माध्यम से युवाओं की मदद करता है।\n\n"
    "**आगामी कार्यक्रम**\n"
    "• Career Guidance & Employment Drive 2026 — 15 मार्च 2026, मुंबई\n"
    "• National Mega Job Fair — 12 अगस्त 2026, मुंबई / नागपाड़ा\n\n"
    "आप इन रोज़गार कार्यक्रमों में भाग ले सकते हैं — यह स्वयंसेवा से अलग है।",
    "**Employment & Job Fair**\n\n"
    "AMP India Foundation job fairs, placement drives, resume clinics, mock interviews, "
    "aur Employment Assistance Cell ke through youth ki madad karta hai.\n\n"
    "**Upcoming**\n"
    "• Career Guidance & Employment Drive 2026 — 15 March 2026, Mumbai\n"
    "• National Mega Job Fair — 12 Aug 2026, Mumbai / Nagpada\n\n"
    "Aap in employment programs me participate kar sakte hain — ye volunteering se alag hai.",
)

MEDICAL = _a(
    "**Medical Programs**\n\n"
    "AMP India Foundation provides medical relief through diagnostic camps, free medicine clinics, "
    "emergency tertiary-care funding, and critical illness support.\n\n"
    "Upcoming: Free Medical Camp & Health Screening — 22 Aug 2026, Hyderabad.",
    "**चिकित्सा कार्यक्रम**\n\n"
    "AMP India Foundation डायग्नोस्टिक कैंप, मुफ्त दवा क्लिनिक, आपातकालीन चिकित्सा सहायता "
    "और गंभीर बीमारी सहायता प्रदान करता है।\n\n"
    "आगामी: मुफ्त मेडिकल कैंप — 22 अगस्त 2026, हैदराबाद।",
    "**Medical programs**\n\n"
    "AMP diagnostic camps, free medicine clinics, emergency care funding, "
    "aur critical illness support deta hai.\n\n"
    "Upcoming: Free Medical Camp — 22 Aug 2026, Hyderabad.",
)

MENTORSHIP = _a(
    "**Mentorship & Career Guidance**\n\n"
    "AMP offers mentorship through Centres of Excellence, ACE (Academy for Competitive Exams), "
    "and National Talent Search (NTS) for meritorious underprivileged students.",
    "**मेंटरशिप और करियर मार्गदर्शन**\n\n"
    "AMP Centres of Excellence, ACE और National Talent Search (NTS) के माध्यम से "
    "मेधावी वंचित छात्रों को मार्गदर्शन देता है।",
    "**Mentorship & career guidance**\n\n"
    "AMP Centres of Excellence, ACE, aur National Talent Search (NTS) ke through "
    "meritorious underprivileged students ko guidance deta hai.",
)

TRAINING = _a(
    "**Training & Skill Development**\n\n"
    "AMP runs vocational skill programs for BPL youth (e.g. mobile repair, AC/fridge servicing) "
    "with NSDC and CSR partnerships.\n\n"
    "Upcoming: Employability Training Programme (ETP) — 24 Jul 2026, Mumbai.",
    "**प्रशिक्षण और कौशल विकास**\n\n"
    "AMP बीपीएल युवाओं के लिए व्यावसायिक कौशल कार्यक्रम चलाता है।\n\n"
    "आगामी: Employability Training Programme — 24 जुलाई 2026, मुंबई।",
    "**Training & skill development**\n\n"
    "AMP BPL youth ke liye vocational skill programs chalata hai.\n\n"
    "Upcoming: Employability Training Programme — 24 Jul 2026, Mumbai.",
)

EVENTS = _a(
    "**Events**\n\n"
    "• Scholarship Awareness Workshop — 18 Jan 2026, Delhi NCR\n"
    "• Employability Training Programme — 24 Jul 2026, Mumbai\n"
    "• National Mega Job Fair — 12 Aug 2026, Mumbai\n"
    "• Free Medical Camp — 22 Aug 2026, Hyderabad\n"
    "• Career Guidance & Employment Drive — 15 March 2026, Mumbai",
    "**कार्यक्रम / इवेंट्स**\n\n"
    "• छात्रवृत्ति जागरूकता कार्यशाला — 18 जनवरी 2026, दिल्ली NCR\n"
    "• Employability Training — 24 जुलाई 2026, मुंबई\n"
    "• Mega Job Fair — 12 अगस्त 2026, मुंबई\n"
    "• मुफ्त मेडिकल कैंप — 22 अगस्त 2026, हैदराबाद\n"
    "• Employment Drive — 15 मार्च 2026, मुंबई",
    "**Events**\n\n"
    "• Scholarship Awareness Workshop — 18 Jan 2026, Delhi NCR\n"
    "• Employability Training — 24 Jul 2026, Mumbai\n"
    "• Mega Job Fair — 12 Aug 2026, Mumbai\n"
    "• Free Medical Camp — 22 Aug 2026, Hyderabad\n"
    "• Employment Drive — 15 March 2026, Mumbai",
)

PROJECTS = _a(
    "**Projects & Programs**\n\n"
    "AMP runs education, employment, medical, empowerment, mentorship, and training initiatives.\n\n"
    "Flagship: ACE, Employment Assistance Cell, National Talent Search (NTS), Higher Education Scholarships.",
    "**प्रोजेक्ट्स और कार्यक्रम**\n\n"
    "AMP शिक्षा, रोज़गार, चिकित्सा, सशक्तिकरण, मेंटरशिप और प्रशिक्षण पहल चलाता है।\n\n"
    "मुख्य: ACE, Employment Assistance Cell, NTS, उच्च शिक्षा छात्रवृत्तियाँ।",
    "**Projects & programs**\n\n"
    "AMP education, employment, medical, empowerment, mentorship aur training initiatives chalata hai.\n\n"
    "Flagship: ACE, Employment Assistance Cell, NTS, Higher Education Scholarships.",
)

MISSION = _a(
    "**Mission**\n\n"
    "AMP India Foundation is dedicated to promoting inclusive social progression by bridging "
    "structural development gaps for the under-served and needy all over India, entirely managed "
    "through professional volunteer resources.",
    "**मिशन**\n\n"
    "AMP India Foundation पूरे भारत में वंचित और जरूरतमंद समुदायों के लिए समावेशी सामाजिक प्रगति "
    "को बढ़ावा देने के लिए प्रतिबद्ध है, जो पेशेवर स्वयंसेवी संसाधनों द्वारा प्रबंधित है।",
    "**Mission**\n\n"
    "AMP India Foundation under-served aur needy communities ke liye inclusive social progression "
    "promote karta hai — professional volunteer resources ke through.",
)

VISION = _a(
    "**Vision**\n\n"
    "Trusted professional philanthropy that uplifts communities through education, employment, "
    "skill development, medical relief, and mentorship—without bias of caste, community, creed, or religion.",
    "**विजन**\n\n"
    "विश्वसनीय पेशेवर परोपकार जो शिक्षा, रोज़गार, कौशल विकास, चिकित्सा राहत और मेंटरशिप के माध्यम से "
    "समुदायों को ऊपर उठाए — जाति, समुदाय, पंथ या धर्म के भेदभाव के बिना।",
    "**Vision**\n\n"
    "Trusted professional philanthropy jo education, employment, skill development, medical relief "
    "aur mentorship ke through communities ko uplift kare — bina kisi bias ke.",
)

ABOUT = _a(
    "**About AMP India Foundation**\n\n"
    "A registered non-profit delivering structured social services for underprivileged communities across India.\n\n"
    + MISSION[Language.ENGLISH.value].replace("**Mission**\n\n", "**Mission:** ")
    + "\n\n"
    + VISION[Language.ENGLISH.value].replace("**Vision**\n\n", "**Vision:** "),
    "**AMP India Foundation के बारे में**\n\n"
    "भारत भर में वंचित समुदायों के लिए सामाजिक सेवाएँ प्रदान करने वाला पंजीकृत गैर-लाभ संगठन।\n\n"
    + MISSION[Language.HINDI.value],
    "**AMP India Foundation ke baare me**\n\n"
    "Registered non-profit jo underprivileged communities ke liye social services deta hai.\n\n"
    + MISSION[Language.HINGLISH.value],
)

LEADERSHIP_UNAVAILABLE = _a(
    "I couldn't find verified information regarding the current leadership of AMP India Foundation.",
    "AMP India Foundation के वर्तमान नेतृत्व के बारे में मुझे सत्यापित जानकारी नहीं मिली।",
    "AMP India Foundation ke current leadership ke baare me verified information nahi mili.",
)

FOLLOW_SCHOLARSHIP = _f(
    ("Eligibility", "Required documents", "Application process", "Last date"),
    ("पात्रता", "आवश्यक दस्तावेज़", "आवेदन प्रक्रिया", "अंतिम तिथि"),
    ("Eligibility", "Required documents", "Application process", "Last date"),
)
FOLLOW_EMPLOYMENT = _f(
    ("Job fair dates", "Resume support", "Interview preparation", "How to register"),
    ("जॉब फेयर तिथियाँ", "रिज़्यूमे सहायता", "इंटरव्यू तैयारी", "रजिस्ट्रेशन कैसे करें"),
    ("Job fair dates", "Resume support", "Interview preparation", "Register kaise karein"),
)
FOLLOW_VOLUNTEER = _f(
    ("Registration link", "Who can join", "What roles are available"),
    ("पंजीकरण लिंक", "कौन शामिल हो सकता है", "कौन सी भूमिकाएँ उपलब्ध हैं"),
    ("Registration link", "Kaun join kar sakta hai", "Kaunse roles available hain"),
)
FOLLOW_DONATION = _f(
    ("Bank details", "IFSC code", "Contact for donation help"),
    ("बैंक विवरण", "IFSC कोड", "दान सहायता संपर्क"),
    ("Bank details", "IFSC code", "Donation help contact"),
)
FOLLOW_CONTACT = _f(
    ("Email", "Office address", "Office timings"),
    ("ईमेल", "कार्यालय पता", "कार्यालय समय"),
    ("Email", "Office address", "Office timings"),
)
FOLLOW_EVENTS = _f(
    ("Upcoming events", "Past events", "Job fair details"),
    ("आगामी कार्यक्रम", "पिछले कार्यक्रम", "जॉब फेयर विवरण"),
    ("Upcoming events", "Past events", "Job fair details"),
)


def _entries() -> List[FaqEntry]:
    return [
        FaqEntry(Intent.CONTACT, ("phone", "mobile", "call", "number", "helpline", "contact number", "call ka number", "फ़ोन", "फोन"), CONTACT_PHONE, FOLLOW_CONTACT, 10),
        FaqEntry(Intent.CONTACT, ("email", "e-mail", "mail", "mail id", "email id", "ईमेल"), CONTACT_EMAIL, FOLLOW_CONTACT, 10),
        FaqEntry(Intent.CONTACT, ("address", "location", "where", "located", "aif ka address", "amp ka address", "aif ka location", "adres", "locaton", "पता"), CONTACT_ADDRESS, FOLLOW_CONTACT, 10),
        FaqEntry(Intent.CONTACT, ("timing", "timings", "hours", "open", "kitne baje", "open rehta", "office time", "working hours", "kab khulta", "ofis", "समय"), CONTACT_TIMINGS, FOLLOW_CONTACT, 12),
        FaqEntry(Intent.CONTACT, ("contact", "office", "reach", "संपर्क", "ऑफिस"), CONTACT_FULL, FOLLOW_CONTACT, 5),
        FaqEntry(
            Intent.DONATIONS,
            ("donate", "donation", "donations", "bank", "ifsc", "account", "upi", "support us", "contribute", "दान", "डोनेशन"),
            DONATION,
            FOLLOW_DONATION,
            10,
        ),
        FaqEntry(
            Intent.SCHOLARSHIPS,
            ("apply", "application", "how to apply", "eligibility", "deadline", "last date", "apply karna"),
            SCHOLARSHIP_APPLY,
            FOLLOW_SCHOLARSHIP,
            12,
        ),
        FaqEntry(
            Intent.SCHOLARSHIPS,
            ("scholarship", "scholarships", "financial aid", "education support", "student funding", "छात्रवृत्ति", "स्कॉलरशिप"),
            SCHOLARSHIP,
            FOLLOW_SCHOLARSHIP,
            8,
        ),
        FaqEntry(
            Intent.VOLUNTEERING,
            ("volunteer", "volunteering", "become volunteer", "community service", "स्वयंसेवक", "वॉलंटियर"),
            VOLUNTEER,
            FOLLOW_VOLUNTEER,
            10,
        ),
        FaqEntry(
            Intent.EMPLOYMENT,
            (
                "job fair",
                "employment",
                "placement",
                "jobs",
                "job",
                "career",
                "recruitment",
                "hiring",
                "resume",
                "interview",
                "naukri",
                "rozgar",
                "job chahiye",
                "mujhe job",
                "mujhe naukri",
                "job ke liye",
                "naukri ke liye",
                "नौकरी",
                "जॉब",
            ),
            EMPLOYMENT,
            FOLLOW_EMPLOYMENT,
            10,
        ),
        FaqEntry(Intent.MEDICAL, ("medical", "health", "hospital", "treatment", "healthcare", "मेडिकल", "स्वास्थ्य"), MEDICAL, FOLLOW_EVENTS, 10),
        FaqEntry(Intent.MENTORSHIP, ("mentor", "mentorship", "guidance", "career guidance", "मेंटर"), MENTORSHIP, FOLLOW_VOLUNTEER, 10),
        FaqEntry(Intent.TRAINING, ("training", "skill", "skills", "course", "courses", "vocational", "ट्रेनिंग"), TRAINING, FOLLOW_EMPLOYMENT, 10),
        FaqEntry(
            Intent.EVENTS,
            ("event", "events", "upcoming", "past events", "previous events", "old events", "current events", "workshop", "batao", "इवेंट"),
            EVENTS,
            FOLLOW_EVENTS,
            8,
        ),
        FaqEntry(
            Intent.PROJECTS,
            ("project", "projects", "program", "programs", "initiative", "initiatives", "focus areas", "प्रोजेक्ट"),
            PROJECTS,
            FOLLOW_EVENTS,
            8,
        ),
        FaqEntry(Intent.AMP_KNOWLEDGE, ("mission", "primary mission", "purpose", "मिशन"), MISSION, FOLLOW_EVENTS, 12),
        FaqEntry(Intent.AMP_KNOWLEDGE, ("vision", "विजन"), VISION, FOLLOW_EVENTS, 12),
        FaqEntry(
            Intent.AMP_KNOWLEDGE,
            (
                "trustworthy",
                "genuine",
                "trust",
                "scam",
                "fraud",
                "legit",
                "reliable",
                "amp genuine",
                "aif genuine",
                "bharosa",
            ),
            _a(
                "**Is AMP India Foundation trustworthy?**\n\n"
                "Yes. AMP India Foundation is a registered non-profit organisation focused on transparent, "
                "professional philanthropy. For official verification, call +91 8291101312 or email "
                "contact@ampindiafoundation.org.",
                "**क्या AMP India Foundation विश्वसनीय है?**\n\n"
                "हाँ। AMP India Foundation एक पंजीकृत गैर-लाभ संगठन है। सत्यापन के लिए +91 8291101312 पर कॉल करें "
                "या contact@ampindiafoundation.org पर ईमेल करें।",
                "**Kya AMP India Foundation trustworthy / genuine hai?**\n\n"
                "Haan. AMP India Foundation ek registered non-profit organisation hai. Verification ke liye "
                "+91 8291101312 par call karein ya contact@ampindiafoundation.org par email karein.",
            ),
            FOLLOW_CONTACT,
            14,
        ),
        FaqEntry(
            Intent.AMP_KNOWLEDGE,
            (
                "about amp",
                "what is amp",
                "what is aif",
                "who is amp",
                "about the foundation",
                "amp india foundation",
                "aif kya",
                "amp kya",
                "aif ke bare",
                "amp ke bare",
                "aif kya hai",
                "amp kya hai",
                "aif kya karta",
                "tell me about amp",
                "tell me about aif",
                "tell me about it",
                "aif",
                "amp",
                "परिचय",
            ),
            ABOUT,
            FOLLOW_EVENTS,
            10,
        ),
        FaqEntry(
            Intent.AMP_KNOWLEDGE,
            (
                "head of aif",
                "head of amp",
                "amp leadership",
                "aif leadership",
                "chairman of amp",
                "director of amp",
                "president of amp",
                "president of aif",
                "who is the head of",
            ),
            LEADERSHIP_UNAVAILABLE,
            FOLLOW_CONTACT,
            15,
        ),
    ]


class FaqCache:
    def __init__(self) -> None:
        self._entries = _entries()

    def lookup(
        self,
        message: str,
        intent: Optional[Intent] = None,
        language: Language = Language.ENGLISH,
    ) -> Optional[FaqHit]:
        t0 = time.perf_counter()
        text = re.sub(r"\s+", " ", (message or "").strip().lower())
        if not text:
            return None

        lang = language.value if isinstance(language, Language) else str(language)
        best: Optional[Tuple[float, FaqEntry, str]] = None

        for entry in self._entries:
            if intent and intent not in {Intent.AMP_KNOWLEDGE, Intent.UNKNOWN}:
                if entry.intent != intent:
                    continue
            hits = [kw for kw in entry.keywords if kw.lower() in text or kw in (message or "")]
            if not hits:
                continue
            score = (len(hits) * 2.0) + entry.priority + max(len(h) for h in hits) / 20.0
            if intent == entry.intent:
                score += 3.0
            if best is None or score > best[0]:
                best = (score, entry, hits[0])

        if best is None and intent in CACHEABLE_INTENTS:
            for entry in self._entries:
                if entry.intent == intent:
                    answer = entry.answers.get(lang) or entry.answers[Language.ENGLISH.value]
                    follow = entry.followups.get(lang) or entry.followups.get(Language.ENGLISH.value) or ()
                    return FaqHit(
                        answer=answer,
                        intent=entry.intent,
                        score=1.0,
                        lookup_ms=(time.perf_counter() - t0) * 1000,
                        key="intent_default",
                        followups=follow,
                    )
            return None

        if best is None:
            return None

        score, entry, key = best
        if score < 5.0 and intent not in CACHEABLE_INTENTS:
            return None

        answer = entry.answers.get(lang) or entry.answers[Language.ENGLISH.value]
        follow = entry.followups.get(lang) or entry.followups.get(Language.ENGLISH.value) or ()
        return FaqHit(
            answer=answer,
            intent=entry.intent,
            score=score,
            lookup_ms=(time.perf_counter() - t0) * 1000,
            key=key,
            followups=follow,
        )


CACHEABLE_INTENTS = {
    Intent.CONTACT,
    Intent.DONATIONS,
    Intent.SCHOLARSHIPS,
    Intent.VOLUNTEERING,
    Intent.EMPLOYMENT,
    Intent.MEDICAL,
    Intent.MENTORSHIP,
    Intent.TRAINING,
    Intent.EVENTS,
    Intent.PROJECTS,
    Intent.AMP_KNOWLEDGE,
}


@lru_cache
def get_faq_cache() -> FaqCache:
    return FaqCache()


def lookup_faq(
    message: str,
    intent: Optional[Intent] = None,
    language: Language = Language.ENGLISH,
) -> Optional[FaqHit]:
    return get_faq_cache().lookup(message, intent=intent, language=language)


def append_followups(answer: str, followups: Tuple[str, ...], language: Language) -> str:
    if not followups:
        return answer
    if language == Language.HINDI:
        header = "\n\nक्या आप यह भी जानना चाहेंगे:\n"
    elif language == Language.HINGLISH:
        header = "\n\nKya aap yeh bhi jaanna chahenge:\n"
    else:
        header = "\n\nWould you also like to know:\n"
    bullets = "".join(f"• {item}\n" for item in followups)
    return f"{answer.rstrip()}{header}{bullets}".rstrip()
