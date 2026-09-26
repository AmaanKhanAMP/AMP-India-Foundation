"""Website knowledge map — public pages → verified answer layers.

Website content reaches the chatbot via:
  CMS (MySQL) → Flask export → Pinecone (cms_*)
  Approved website snapshots → website_*
  chatbot/knowledge/* (non-dated programme copy only)
"""

from __future__ import annotations

from typing import Dict, List

WEBSITE_PAGE_SOURCES: Dict[str, List[str]] = {
    "/": ["cms_home", "website_about"],
    "/about": ["website_about", "cms_home"],
    "/what-we-do": ["website_about", "website_projects"],
    "/projects": ["website_projects", "cms_projects"],
    "/events": ["cms_events", "cms_gallery"],
    "/volunteer": ["website_volunteer", "volunteer"],
    "/support-us": ["website_support", "donations"],
    "/healthcare": ["website_projects"],
    "/education": ["website_projects", "scholarships"],
    "/employment": ["website_projects", "cms_events"],
    "/economic-empowerment": ["website_projects"],
    "/scholarships": ["scholarships", "website_projects"],
    "/gallery": ["cms_gallery", "cms_home_gallery"],
    "/testimonials": ["cms_testimonials"],
    "/contact": ["cms_footer"],
}


def layers_for_page(page: str | None) -> List[str]:
    if not page:
        return []
    key = (page or "/").split("?")[0].rstrip("/") or "/"
    return list(WEBSITE_PAGE_SOURCES.get(key) or WEBSITE_PAGE_SOURCES.get(page) or [])
