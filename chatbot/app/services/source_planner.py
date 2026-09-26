"""Intent-aware source selection for retrieval (Phase A).

Builds an ordered SourcePlan used by RAG. Prefer CMS vectors, then static
markdown stems, then backend_* JSON — FAQ is last among Pinecone sources
so it does not drown CMS content.

DEPRECATED NOTE: Older callers may still pass flat SOURCE_FILTER lists;
plan_sources() is the preferred entry point going forward.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app.services.intent_router import (
    SECTION_FILTER,
    SOURCE_FILTER,
    Intent,
)


@dataclass
class SourcePlan:
    intent: str
    sources: List[str] = field(default_factory=list)
    section: Optional[str] = None
    cms_sources: List[str] = field(default_factory=list)
    markdown_sources: List[str] = field(default_factory=list)
    backend_sources: List[str] = field(default_factory=list)
    allow_faq: bool = True
    penalize_contact: bool = False
    penalize_crowdfunding: bool = False
    reason: str = ""


# Canonical groupings (stems as stored in Pinecone metadata.source)
_CMS = {
    "cms_events",
    "cms_gallery",
    "cms_footer",
    "cms_home",
    "cms_projects",
    "cms_home_gallery",
    "cms_testimonials",
    "cms_navbar",
    "cms_footer_links",
    "website_about",
    "website_projects",
    "website_support",
    "website_volunteer",
    "website_home",
}
_BACKEND = {
    "backend_events",
    "backend_contact",
    "backend_about",
    "backend_faq",
    "backend_projects",
    "backend_scholarships",
    "backend_volunteer",
    "backend_donations",
    "backend_navigation",
}
_MARKDOWN = {
    "contact",
    "faq",
    "events",
    "about_aif",
    "programs",
    "projects",
    "scholarships",
    "volunteer",
    "donations",
    "employment",
}


def _partition(sources: List[str]) -> tuple[List[str], List[str], List[str], List[str]]:
    cms, md, backend, other = [], [], [], []
    for s in sources:
        if s in _CMS or s.startswith("cms_") or s.startswith("website_"):
            cms.append(s)
        elif s in _BACKEND or s.startswith("backend_"):
            backend.append(s)
        elif s == "faq":
            other.append(s)  # faq last
        elif s in _MARKDOWN:
            md.append(s)
        else:
            other.append(s)
    return cms, md, backend, other


def _ordered(sources: List[str], *, faq_last: bool = True) -> List[str]:
    """Preserve caller priority; optionally push FAQ to the end."""
    if not faq_last:
        return list(dict.fromkeys(sources))
    faq = [s for s in sources if s == "faq"]
    rest = [s for s in sources if s != "faq"]
    return list(dict.fromkeys([*rest, *faq]))


def plan_sources(intent: Intent | str, *, section: Optional[str] = None) -> SourcePlan:
    """Build a retrieval plan for an intent. Backward-compatible flat `sources` list."""
    if isinstance(intent, str):
        try:
            intent_enum = Intent(intent)
        except ValueError:
            intent_enum = Intent.UNKNOWN
    else:
        intent_enum = intent

    base = list(SOURCE_FILTER.get(intent_enum) or [])
    sec = section if section is not None else SECTION_FILTER.get(intent_enum)

    # Intent-specific tuning (does not remove legacy SOURCE_FILTER entries)
    penalize_contact = intent_enum not in {Intent.CONTACT, Intent.UNKNOWN}
    penalize_crowd = intent_enum in {Intent.MEDICAL, Intent.EMPLOYMENT, Intent.SCHOLARSHIPS}
    allow_faq = intent_enum not in {
        Intent.UPCOMING_EVENTS,
        Intent.PAST_EVENTS,
        Intent.FEATURED_EVENT,
    }

    if intent_enum == Intent.MEDICAL:
        base = [
            "website_projects",
            "cms_projects",
            "website_about",
        ]
    elif intent_enum in {Intent.EDUCATION, Intent.ECONOMIC_EMPOWERMENT}:
        base = [
            "website_projects",
            "cms_projects",
            "website_about",
        ]
    elif intent_enum == Intent.DONATIONS:
        base = [
            "website_support",
        ]
    elif intent_enum == Intent.CONTACT:
        base = [
            "cms_footer",
            "website_about",
        ]
    elif intent_enum == Intent.AMP_KNOWLEDGE:
        base = [
            "website_about",
            "website_home",
            "cms_home",
            "cms_testimonials",
        ]

    if not allow_faq:
        base = [s for s in base if s != "faq"]

    ordered = _ordered(base, faq_last=True)
    cms, md, backend, _ = _partition(ordered)

    return SourcePlan(
        intent=intent_enum.value,
        sources=ordered,
        section=sec,
        cms_sources=cms,
        markdown_sources=md,
        backend_sources=backend,
        allow_faq=allow_faq,
        penalize_contact=penalize_contact,
        penalize_crowdfunding=penalize_crowd,
        reason=f"plan:{intent_enum.value}",
    )
