"""Goal-based intent — reason about life situations, not keywords alone.

Examples:
- son/daughter + doctor/coaching/afford → scholarships / education
- lost my job → employment
- help society → volunteering (or donations if money)
- need medical help → healthcare
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

from app.services.intent_router import Intent

_FAMILY = r"(?:son|daughter|beta|beti|child|children|baccha|bacha|kids?|ladki|ladka)"
_STUDY = (
    r"(?:doctor|engineer|college|coaching|tuition|higher\s+education|"
    r"padhai|school|university|mbbs|neet|jee|study|studies|education)"
)
_AFFORD = (
    r"(?:cannot\s+afford|can'?t\s+afford|cant\s+afford|paise\s+nahi|"
    r"afford|gareeb|garib|fees|mehnga|mehanga|paisa\s+nahi)"
)


def detect_goal_intent(text: str, raw: str = "") -> Optional[Tuple[Intent, float, str]]:
    """Return (intent, confidence, reason) when the user describes a life goal."""
    blob = f"{text or ''} {raw or ''}".strip().lower()
    if not blob:
        return None

    # Scholarships / student support — before medical "doctor" keyword matching.
    coaching_or_afford = bool(
        re.search(r"\b(coaching|tuition|neet|jee|mbbs)\b", blob)
        or re.search(_AFFORD, blob)
    )
    family_study = bool(re.search(_FAMILY, blob) and re.search(_STUDY, blob))
    higher_ed = bool(
        re.search(_FAMILY, blob)
        and re.search(r"\b(higher\s+education|college|university|padhai|study)\b", blob)
    )
    if family_study or higher_ed or (
        coaching_or_afford and re.search(_STUDY, blob)
    ):
        if re.search(r"\b(job\s*fair|naukri|employment|volunteer|donat)\b", blob):
            pass
        else:
            return Intent.SCHOLARSHIPS, 0.94, "goal:education_scholarships"

    if re.search(
        r"\b("
        r"lost\s+(?:my\s+|the\s+)?job|laid\s+off|unemployed|"
        r"naukri\s+chali|nokri\s+nahi|job\s+chali\s+gayi|"
        r"i\s+lost\s+.{0,12}job"
        r")\b",
        blob,
    ):
        return Intent.EMPLOYMENT, 0.95, "goal:lost_job"

    if re.search(
        r"\b("
        r"need\s+medical|medical\s+help|hospital\s+bill|medical\s+bills?|"
        r"ilaj\s+ke\s+liye|ilaij|treatment\s+ke\s+liye|"
        r"operation\s+ke\s+(?:paise|liye)|critical\s+illness|"
        r"i\s+need\s+medical"
        r")\b",
        blob,
    ) and not re.search(r"\b(coaching|tuition|scholarship|college)\b", blob):
        return Intent.MEDICAL, 0.95, "goal:medical_help"

    donate_money = bool(
        re.search(r"\b(donat|paisa|paise|money|fund|cheque|upi|80g)\b", blob)
    )
    help_society = bool(
        re.search(
            r"(?:help|seva|serve).{0,28}(?:society|community|people|samaj|desh)|"
            r"give\s+back(?:\s+to)?|"
            r"want\s+to\s+(?:help|serve)\s+(?:society|people|community|others)|"
            r"contribute\s+(?:my\s+)?time|"
            r"samaj\s+(?:ki\s+)?madad|"
            r"help\s+society",
            blob,
        )
    )
    if help_society:
        if donate_money:
            return Intent.DONATIONS, 0.93, "goal:help_society_donate"
        return Intent.VOLUNTEERING, 0.93, "goal:help_society"

    if re.search(
        r"\b(?:want\s+to\s+)?support\s+(?:aif|amp|the\s+foundation|this\s+ngo)\b",
        blob,
    ) and not re.search(r"\bvolunteer\b", blob):
        return Intent.DONATIONS, 0.9, "goal:support_foundation"

    return None
