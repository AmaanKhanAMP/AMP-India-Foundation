"""Dashboard stats for CMS home."""

from pathlib import Path

from flask import Blueprint, current_app, jsonify

from controllers import content_controller as cc
from models.cms_models import (
    FeaturedEvent,
    FooterFocusItem,
    FooterLink,
    HeroBanner,
    HomeEvent,
    HomeGalleryItem,
    HomeProject,
    NavbarItem,
    PastEvent,
    Testimonial,
    UpcomingEvent,
)
from models.contact_message import ContactMessage
from utils.auth import admin_required
from utils.content_registry import CONTENT_RESOURCES

dashboard_bp = Blueprint("dashboard", __name__)

CONTENT_MODELS = [
    ("hero_banner", HeroBanner),
    ("home_project", HomeProject),
    ("home_gallery", HomeGalleryItem),
    ("home_event", HomeEvent),
    ("testimonial", Testimonial),
    ("featured_event", FeaturedEvent),
    ("upcoming_event", UpcomingEvent),
    ("past_event", PastEvent),
    ("navbar_item", NavbarItem),
    ("footer_link", FooterLink),
    ("footer_focus", FooterFocusItem),
]


def _alive_query(model):
    return model.query.filter(model.is_deleted.is_(False))


def _count_status(status):
    total = 0
    for _, model in CONTENT_MODELS:
        total += _alive_query(model).filter_by(status=status).count()
    return total


def _count_uploads():
    root = Path(current_app.config.get("UPLOAD_FOLDER", Path(current_app.root_path) / "uploads"))
    if not root.exists():
        return 0
    count = 0
    for path in root.rglob("*"):
        if path.is_file():
            count += 1
    return count


def _recent_updates(limit=8):
    rows = []
    for label, model in CONTENT_MODELS:
        for item in (
            _alive_query(model).order_by(model.updated_at.desc()).limit(limit).all()
        ):
            title = (
                getattr(item, "title", None)
                or getattr(item, "name", None)
                or getattr(item, "label", None)
                or getattr(item, "alt_text", None)
                or "Untitled"
            )
            rows.append(
                {
                    "type": label,
                    "id": item.id,
                    "title": title,
                    "status": item.status,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                }
            )
    rows.sort(key=lambda r: r["updated_at"] or "", reverse=True)
    return rows[:limit]


def _recent_messages(limit=5):
    return [
        m.to_dict()
        for m in ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(limit).all()
    ]


def _recent_images(limit=8):
    images = []
    for label, model in CONTENT_MODELS:
        image_attr = {
            FeaturedEvent: "banner_image",
            Testimonial: "profile_image",
        }.get(model, "image_url")
        for item in _alive_query(model).order_by(model.updated_at.desc()).limit(limit).all():
            url = getattr(item, image_attr, None)
            if url:
                images.append(
                    {
                        "type": label,
                        "id": item.id,
                        "title": getattr(item, "title", None) or getattr(item, "name", "Untitled"),
                        "url": url,
                        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                    }
                )
    images.sort(key=lambda r: r["updated_at"] or "", reverse=True)
    return images[:limit]


@dashboard_bp.get("/stats")
@admin_required
def stats():
    unread = ContactMessage.query.filter_by(status="New").count()
    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "hero_banners": _alive_query(HeroBanner).count(),
                    "home_projects": _alive_query(HomeProject).count(),
                    "home_gallery": _alive_query(HomeGalleryItem).count(),
                    "home_events": _alive_query(HomeEvent).count(),
                    "testimonials": _alive_query(Testimonial).count(),
                    "featured_events": _alive_query(FeaturedEvent).count(),
                    "upcoming_events": _alive_query(UpcomingEvent).count(),
                    "past_events": _alive_query(PastEvent).count(),
                    # Legacy key for older CMS dashboard builds
                    "gallery_items": _alive_query(PastEvent).count(),
                    "contact_messages": ContactMessage.query.count(),
                    "unread_messages": unread,
                    "published_items": _count_status("published"),
                    "draft_items": _count_status("draft"),
                    "trash_items": cc.trash_count(),
                    "total_uploads": _count_uploads(),
                    "recent_updates": _recent_updates(),
                    "recent_messages": _recent_messages(),
                    "recent_images": _recent_images(),
                    "modules": [r["resource"] for r in CONTENT_RESOURCES],
                },
            }
        ),
        200,
    )
