"""Extract a conversation focus (event/place/project) for follow-up questions."""

from __future__ import annotations

import re
from typing import Optional

_PLACES = (
    "kupwara",
    "kashmir",
    "kolkata",
    "srinagar",
    "nanded",
    "mumbai",
    "hyderabad",
    "delhi",
    "pune",
    "ballari",
    "ahmedabad",
    "agra",
)

_PROJECTS = (
    "education",
    "employment training",
    "etp",
    "mentorship",
    "medical relief",
    "economic empowerment",
    "career guidance",
    "scholarship",
)

_PLACE_RE = re.compile(r"\b(" + "|".join(_PLACES) + r")\b", re.I)
_PROJECT_RE = re.compile(r"\b(" + "|".join(re.escape(p) for p in _PROJECTS) + r")\b", re.I)
_EVENT_RE = re.compile(
    r"\b(job fair|mega job fair|medical camp|etp|employability training)\b",
    re.I,
)


def extract_focus(message: str, previous: Optional[str] = None) -> Optional[str]:
    text = (message or "").strip()
    if not text:
        return previous
    place = _PLACE_RE.search(text)
    event = _EVENT_RE.search(text)
    project = _PROJECT_RE.search(text)
    parts = []
    if place:
        parts.append(place.group(1))
    if event:
        parts.append(event.group(1))
    elif project:
        parts.append(project.group(1))
    if parts:
        return " ".join(parts)
    return previous
