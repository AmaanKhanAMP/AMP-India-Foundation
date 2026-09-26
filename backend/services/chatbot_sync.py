"""CMS / knowledge → chatbot Pinecone sync (Flask backend).

After CMS content changes, export published MySQL rows + approved website
snapshots and push incremental source updates to the FastAPI chatbot ingest API.

Legacy backend/knowledge JSON and dated markdown event lists are NOT synced.

Never blocks the CMS request for more than a few ms (background thread).
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_KNOWLEDGE_DIR = _BACKEND_ROOT / "knowledge"

_LOCK = threading.Lock()
_PENDING = False
_LAST_REASON = ""
_DEBOUNCE_SECONDS = 1.5
_TIMER: Optional[threading.Timer] = None

# Pinecone source ids that must never answer after the CMS/website rebuild
LEGACY_PINECONE_SOURCES = [
    "events",
    "faq",
    "contact",
    "employment",
    "about_aif",
    "programs",
    "projects",
    "scholarships",
    "donations",
    "volunteer",
    "backend_events",
    "backend_contact",
    "backend_about",
    "backend_projects",
    "backend_faq",
    "backend_scholarships",
    "backend_volunteer",
    "backend_donations",
    "backend_navigation",
]


def _chatbot_base_url() -> str:
    return (os.getenv("CHATBOT_URL") or "http://127.0.0.1:8000").rstrip("/")


def _ingest_token() -> str:
    return (os.getenv("CHATBOT_INGEST_TOKEN") or os.getenv("ADMIN_INGEST_TOKEN") or "").strip()


def _sync_enabled() -> bool:
    flag = (os.getenv("CHATBOT_SYNC_ENABLED") or "true").strip().lower()
    return flag in {"1", "true", "yes", "on"}


def _section_visible(section_name: str) -> bool:
    try:
        from models.cms_models import SectionVisibility

        row = SectionVisibility.query.filter_by(section_name=section_name).first()
        if row is None:
            return True
        return bool(row.is_visible)
    except Exception:
        return True


def _published_rows(model) -> List[Any]:
    query = model.query.filter(model.status == "published")
    if hasattr(model, "is_deleted"):
        query = query.filter(model.is_deleted.is_(False))
    if hasattr(model, "is_visible"):
        query = query.filter(model.is_visible.is_(True))
    if hasattr(model, "is_hidden"):
        query = query.filter(model.is_hidden.is_(False))
    return query.order_by(model.display_order.asc(), model.id.desc()).all()


def _line(label: str, value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return f"{label}: {text}"


def _export_cms_sources() -> Dict[str, str]:
    """Build source_name → plain-text documents from published CMS rows."""
    from models.cms_models import (
        FeaturedEvent,
        FooterLink,
        FooterSettings,
        HeroBanner,
        HomeEvent,
        HomeGalleryItem,
        HomeProject,
        NavbarItem,
        PastEvent,
        Testimonial,
        UpcomingEvent,
    )

    sources: Dict[str, str] = {}

    # Home / about-ish marketing content
    home_parts: List[str] = ["# AMP India Foundation — Website Home Content (CMS)"]
    for item in _published_rows(HeroBanner):
        d = item.to_dict()
        block = [
            "## Hero banner",
            _line("Title", d.get("title")),
            _line("Accent", d.get("title_accent")),
            _line("Subtitle", d.get("subtitle")),
            _line("Primary button", d.get("primary_btn_text")),
            _line("Primary link", d.get("primary_btn_link")),
        ]
        home_parts.append("\n".join(x for x in block if x))
    if len(home_parts) > 1:
        sources["cms_home"] = "\n\n".join(home_parts)

    # Projects (homepage carousel — title only; image is not useful for RAG text)
    project_parts: List[str] = ["# AMP India Foundation — Projects (CMS)"]
    for item in _published_rows(HomeProject):
        d = item.to_dict()
        project_parts.append(f"## Project: {d.get('title') or 'Untitled'}")
    if len(project_parts) > 1:
        sources["cms_projects"] = "\n\n".join(project_parts)

    # Homepage photo gallery captions
    home_gallery_parts: List[str] = ["# AMP India Foundation — Photo Gallery (CMS)"]
    for item in _published_rows(HomeGalleryItem):
        d = item.to_dict()
        block = [
            f"## Gallery item: {d.get('title') or 'Untitled'}",
            _line("Description", d.get("description")),
            _line("Alt text", d.get("alt_text")),
        ]
        home_gallery_parts.append("\n".join(x for x in block if x))
    if len(home_gallery_parts) > 1:
        sources["cms_home_gallery"] = "\n\n".join(home_gallery_parts)

    # Events — one block per event with explicit Section label for Pinecone metadata
    event_parts: List[str] = [
        "# AMP India Foundation — Events (CMS)",
        "# schema: event_sections_v2",
        "This document lists verified upcoming, featured, and homepage events.",
        "Do not confuse this with office contact or working hours.",
    ]
    upcoming_visible = _section_visible("upcoming_events")
    event_groups = [
        ("Home event", HomeEvent, "upcoming_events"),
        ("Featured event", FeaturedEvent, "featured_event"),
    ]
    if upcoming_visible:
        event_groups.append(("Upcoming event", UpcomingEvent, "upcoming_events"))
    for label, model, section in event_groups:
        for item in _published_rows(model):
            d = item.to_dict()
            block = [
                f"## {label}: {d.get('title') or 'Untitled'}",
                f"Section: {section}",
                _line("Description", d.get("description")),
                _line("Venue", d.get("venue")),
                _line("Date", d.get("event_date")),
                # Featured still uses event_time; home/upcoming do not.
                _line("Time", d.get("event_time")) if model is FeaturedEvent else None,
                _line("Speaker", d.get("speaker")),
            ]
            event_parts.append("\n".join(x for x in block if x))
    if len(event_parts) > 4:
        sources["cms_events"] = "\n\n".join(event_parts)

    # Past Events — each past event is its own section-tagged block
    gallery_parts: List[str] = [
        "# AMP India Foundation — Past Events (CMS)",
        "# schema: event_sections_v2",
    ]
    for item in _published_rows(PastEvent):
        d = item.to_dict()
        block = [
            f"## Past event: {d.get('title') or 'Untitled'}",
            "Section: past_events",
            _line("Description", d.get("description")),
            _line("Date", d.get("event_date") or d.get("year")),
            _line("Venue", d.get("venue") or d.get("location")),
        ]
        gallery_parts.append("\n".join(x for x in block if x))
    if len(gallery_parts) > 2:
        sources["cms_gallery"] = "\n\n".join(gallery_parts)

    # Testimonials
    testimonial_parts: List[str] = ["# AMP India Foundation — Testimonials (CMS)"]
    for item in _published_rows(Testimonial):
        d = item.to_dict()
        block = [
            f"## Testimonial: {d.get('name') or 'Anonymous'}",
            _line("Designation", d.get("designation")),
            _line("Organisation", d.get("organisation")),
            _line("Location", d.get("location")),
            _line("Message", d.get("message")),
            _line("Rating", d.get("rating")),
        ]
        testimonial_parts.append("\n".join(x for x in block if x))
    if len(testimonial_parts) > 1:
        sources["cms_testimonials"] = "\n\n".join(testimonial_parts)

    # Footer contact / about (singleton settings)
    try:
        footer = FooterSettings.query.order_by(FooterSettings.id.asc()).first()
    except Exception:
        footer = None
    if footer:
        d = footer.to_dict() if hasattr(footer, "to_dict") else {}
        if not d:
            d = {f: getattr(footer, f, None) for f in (
                "about_text", "address_text", "phone_text", "email_text",
                "facebook_url", "instagram_url", "cta_button_link",
            )}
        footer_parts = [
            "# AMP India Foundation — Footer / Contact (CMS)",
            _line("About", d.get("about_text")),
            _line("Address", d.get("address_text")),
            _line("Phone", d.get("phone_text")),
            _line("Email", d.get("email_text")),
            _line("Facebook", d.get("facebook_url")),
            _line("Instagram", d.get("instagram_url")),
            _line("Volunteer CTA link", d.get("cta_button_link")),
        ]
        sources["cms_footer"] = "\n".join(x for x in footer_parts if x)

    # Navbar + footer links (published)
    nav_parts: List[str] = ["# AMP India Foundation — Navigation (CMS)"]
    for item in _published_rows(NavbarItem):
        d = item.to_dict()
        nav_parts.append(
            " • ".join(
                x
                for x in (
                    _line("Label", d.get("label")),
                    _line("Link", d.get("href")),
                    _line("Type", d.get("item_type")),
                )
                if x
            )
        )
    if len(nav_parts) > 1:
        sources["cms_navbar"] = "\n".join(nav_parts)

    link_parts: List[str] = ["# AMP India Foundation — Footer Useful Links (CMS)"]
    for item in _published_rows(FooterLink):
        d = item.to_dict()
        link_parts.append(
            " • ".join(
                x
                for x in (_line("Label", d.get("label")), _line("Link", d.get("href")))
                if x
            )
        )
    if len(link_parts) > 1:
        sources["cms_footer_links"] = "\n".join(link_parts)

    return sources


def _json_to_text(data: Any, source: str) -> str:
    lines: List[str] = [f"# AMP India Foundation — {source}"]

    def walk(node: Any, prefix: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"keywords", "id", "page", "image_url", "banner_image"}:
                    continue
                if isinstance(value, (dict, list)):
                    walk(value, prefix=prefix)
                else:
                    walk(value, prefix=f"{prefix}{key}: ")
        elif isinstance(node, list):
            for item in node:
                walk(item, prefix=prefix)
        elif node is not None and str(node).strip():
            lines.append(f"{prefix}{node}".strip())

    walk(data)
    return "\n".join(lines)


# Map backend/knowledge JSON stems → Pinecone source ids (stable, non-colliding)
_KNOWLEDGE_SOURCE_MAP = {
    "about": "backend_about",
    "contact": "backend_contact",
    "faq": "backend_faq",
    "events": "backend_events",
    "projects": "backend_projects",
    "scholarships": "backend_scholarships",
    "volunteer": "backend_volunteer",
    "donation": "backend_donations",
    "navigation": "backend_navigation",
}


def _export_knowledge_json_sources() -> Dict[str, str]:
    sources: Dict[str, str] = {}
    if not _KNOWLEDGE_DIR.is_dir():
        return sources
    for path in sorted(_KNOWLEDGE_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("knowledge_json_read_failed file=%s err=%s", path.name, type(exc).__name__)
            continue
        source = _KNOWLEDGE_SOURCE_MAP.get(path.stem, f"backend_{path.stem}")
        sources[source] = _json_to_text(data, path.stem)
    return sources


def _live_facts_from_footer(sources: Dict[str, str]) -> Dict[str, str]:
    from models.cms_models import FooterSettings

    facts = {
        "phone": "+91 8291101312",
        "email": "contact@ampindiafoundation.org",
        "address": (
            "Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, "
            "A Clare Road, Nagpada, Mumbai - 400008"
        ),
        "office_timings": "Monday to Saturday, 9:00 AM to 6:00 PM",
    }
    try:
        footer = FooterSettings.query.order_by(FooterSettings.id.asc()).first()
    except Exception:
        footer = None
    if footer:
        facts["phone"] = (getattr(footer, "phone_text", None) or facts["phone"]).strip()
        facts["email"] = (getattr(footer, "email_text", None) or facts["email"]).strip()
        facts["address"] = (getattr(footer, "address_text", None) or facts["address"]).strip()
    return facts


def _export_live_dropins() -> Dict[str, str]:
    """Index any extra approved pages dropped into backend/knowledge/live/."""
    folder = _KNOWLEDGE_DIR / "live"
    out: Dict[str, str] = {}
    if not folder.is_dir():
        return out
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in {".md", ".txt", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            continue
        if text:
            out[f"website_live_{path.stem}"] = text
    return out


def build_sync_payload(*, force: bool = False) -> Dict[str, Any]:
    """Collect CMS + approved website snapshots for incremental Pinecone upsert."""
    from services.website_snapshots import export_website_sources

    sources: Dict[str, str] = {}
    sources.update(_export_cms_sources())
    sources.update(export_website_sources())
    live = _export_live_dropins()
    sources.update(live)
    live_facts = _live_facts_from_footer(sources)
    extra_prefixes: List[str] = []
    if (_KNOWLEDGE_DIR / "live").is_dir():
        extra_prefixes.append("website_live_")
    return {
        "reason": _LAST_REASON or "cms_sync",
        "sources": [{"source": k, "text": v, "category": k} for k, v in sources.items()],
        "delete_missing_cms": True,
        "cms_source_prefix": "cms_",
        "delete_sources": LEGACY_PINECONE_SOURCES,
        "extra_delete_prefixes": extra_prefixes,
        "live_facts": live_facts,
        "force": force,
    }


def _post_json(url: str, payload: Dict[str, Any], token: str, timeout: float = 120.0) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Admin-Token": token,
            "User-Agent": "aif-cms-sync/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}


def run_chatbot_sync(reason: str = "manual", *, force: bool = False) -> Dict[str, Any]:
    """Synchronously export + push to chatbot. Safe to call from a worker thread."""
    global _LAST_REASON
    _LAST_REASON = reason

    if not _sync_enabled():
        return {"success": False, "message": "CHATBOT_SYNC_ENABLED is false", "indexed": 0}

    token = _ingest_token()
    if not token or token in {"change-me", "change-me-to-a-long-random-secret"}:
        logger.warning("chatbot_sync_skipped reason=missing_or_placeholder_token")
        return {
            "success": False,
            "message": "CHATBOT_INGEST_TOKEN not configured",
            "indexed": 0,
        }

    payload = build_sync_payload(force=force or reason.startswith("rebuild"))
    url = f"{_chatbot_base_url()}/api/admin/ingest/cms-sync"
    try:
        result = _post_json(url, payload, token)
        logger.info(
            "chatbot_sync_ok reason=%s indexed=%s sources=%s",
            reason,
            result.get("indexed"),
            result.get("sources"),
        )
        return {"success": True, **result}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        logger.error("chatbot_sync_http status=%s detail=%s", exc.code, detail)
        return {"success": False, "message": f"HTTP {exc.code}", "detail": detail, "indexed": 0}
    except Exception as exc:
        logger.error("chatbot_sync_failed error=%s", type(exc).__name__)
        return {"success": False, "message": str(type(exc).__name__), "indexed": 0}


def _flush_pending() -> None:
    global _PENDING, _TIMER
    with _LOCK:
        _PENDING = False
        _TIMER = None
        reason = _LAST_REASON or "cms_update"
    # Need Flask app context for DB queries
    try:
        from app import app

        with app.app_context():
            run_chatbot_sync(reason=reason)
    except Exception as exc:
        logger.error("chatbot_sync_flush_failed error=%s", type(exc).__name__)


def schedule_chatbot_sync(reason: str = "cms_update") -> None:
    """Debounced background sync — call after successful CMS DB commits."""
    global _PENDING, _TIMER, _LAST_REASON

    if not _sync_enabled():
        return

    with _LOCK:
        _LAST_REASON = reason
        _PENDING = True
        if _TIMER is not None:
            try:
                _TIMER.cancel()
            except Exception:
                pass
        _TIMER = threading.Timer(_DEBOUNCE_SECONDS, _flush_pending)
        _TIMER.daemon = True
        _TIMER.start()
    logger.info("chatbot_sync_scheduled reason=%s debounce=%.1fs", reason, _DEBOUNCE_SECONDS)
