"""
UI-driven character limits for CMS content fields.

Mirrors cms/utils/fieldLimits.js — keep both in sync when adjusting limits.
Limits are based on public frontend layout (line clamps, card sizes, hero type).
Existing DB rows are never truncated; limits are enforced only on create/update.
"""

from __future__ import annotations

# URL / image capacity matches DB String(500)
URL_MAX = 500
IMAGE_URL_MAX = 500

FIELD_LIMITS: dict[str, dict[str, int]] = {
    "hero-banners": {
        "title": 48,
        "title_accent": 24,
        "subtitle": 280,
        "primary_btn_text": 22,
        "primary_btn_link": URL_MAX,
        "secondary_btn_text": 22,
        "secondary_btn_link": URL_MAX,
        "image_url": IMAGE_URL_MAX,
    },
    "home-projects": {
        "title": 55,
        "image_url": IMAGE_URL_MAX,
    },
    "home-gallery": {
        "alt_text": 160,
        "title": 80,
        "description": 280,
        "image_url": IMAGE_URL_MAX,
    },
    "home-events": {
        "title": 80,
        "description": 280,
        "venue": 50,
        "event_date": 32,
        "speaker": 40,
        "registration_link": URL_MAX,
        "button_text": 22,
        "image_url": IMAGE_URL_MAX,
    },
    "testimonials": {
        "name": 40,
        "designation": 100,
        "organisation": 50,
        "location": 40,
        "message": 500,
        "profile_image": IMAGE_URL_MAX,
    },
    "featured-events": {
        "title": 70,
        "description": 240,
        "venue": 50,
        "event_date": 32,
        "event_time": 28,
        "banner_image": IMAGE_URL_MAX,
    },
    "upcoming-events": {
        "title": 80,
        "description": 200,
        "venue": 50,
        "event_date": 32,
        "image_url": IMAGE_URL_MAX,
    },
    "past-events": {
        # Past Events card body — fuller CMS copy (~3–4 lines on card)
        "title": 60,
        "description": 380,
        "event_date": 32,
        "venue": 50,
        "image_url": IMAGE_URL_MAX,
    },
    # Legacy slug alias
    "gallery-items": {
        "title": 60,
        "description": 380,
        "event_date": 32,
        "venue": 50,
        "image_url": IMAGE_URL_MAX,
    },
    "navbar-items": {
        "label": 40,
        "href": URL_MAX,
        "item_type": 20,
        "item_key": 40,
        "parent_key": 40,
    },
    "footer-links": {
        "label": 40,
        "href": URL_MAX,
    },
    "footer-focus": {
        "title": 80,
        "href": URL_MAX,
        "date_label": 32,
    },
}

# Human-readable labels for API error messages
FIELD_LABELS: dict[str, str] = {
    "image_url": "Image",
    "banner_image": "Banner image",
    "profile_image": "Profile image",
    "title": "Title",
    "title_accent": "Title accent",
    "subtitle": "Subtitle",
    "description": "Description",
    "primary_btn_text": "Primary button text",
    "primary_btn_link": "Primary button link",
    "secondary_btn_text": "Secondary button text",
    "secondary_btn_link": "Secondary button link",
    "button_text": "Button text",
    "button_link": "Button link",
    "venue": "Venue",
    "event_date": "Event date",
    "event_time": "Event time",
    "speaker": "Speaker",
    "registration_link": "Registration link",
    "name": "Name",
    "designation": "Designation",
    "organisation": "Organisation",
    "location": "Location",
    "message": "Message",
    "category": "Category",
    "year": "Year",
    "alt_text": "Alt text",
    "label": "Label",
    "href": "Link",
    "item_type": "Item type",
    "item_key": "Dropdown key",
    "parent_key": "Parent dropdown",
    "date_label": "Date label",
}

# Fields that must be non-empty on create/update when present in the resource
REQUIRED_FIELDS: dict[str, list[str]] = {
    "home-projects": ["image_url", "title"],
    "home-gallery": ["image_url", "alt_text", "title", "description"],
    "past-events": ["image_url", "title", "description"],
    "gallery-items": ["image_url", "title", "description"],
    "navbar-items": ["label", "href", "item_type"],
    "footer-links": ["label", "href"],
    "footer-focus": ["title", "href", "date_label"],
}


def validate_content_lengths(resource: str, payload: dict) -> dict[str, str]:
    """
    Validate string field lengths for a CMS resource payload.

    Returns a dict of field → error message. Empty dict means valid.
    Non-string / missing values are skipped (required checks live elsewhere).
    """
    limits = FIELD_LIMITS.get(resource) or {}
    errors: dict[str, str] = {}

    for field, max_len in limits.items():
        if field not in payload:
            continue
        value = payload.get(field)
        if value is None:
            continue
        if not isinstance(value, str):
            # Numbers etc. — ignore for length checks
            continue
        if len(value) > max_len:
            label = FIELD_LABELS.get(field, field.replace("_", " ").title())
            if resource in ("past-events", "gallery-items") and field == "description":
                label = "Past Event Description"
            errors[field] = f"{label} must be at most {max_len} characters."

    return errors


def validate_required_fields(resource: str, payload: dict, *, partial: bool = False) -> dict[str, str]:
    """
    Validate required string fields for a CMS resource.

    When partial=True (typical PUT), only fields present in the payload are checked.
    When partial=False (typical POST), all required fields must be present and non-empty.
    """
    required = REQUIRED_FIELDS.get(resource) or []
    errors: dict[str, str] = {}

    for field in required:
        if partial and field not in payload:
            continue
        value = payload.get(field)
        text = "" if value is None else str(value).strip()
        if not text:
            label = FIELD_LABELS.get(field, field.replace("_", " ").title())
            if resource in ("past-events", "gallery-items") and field == "description":
                label = "Past Event Description"
            errors[field] = f"{label} is required."

    return errors


def _validate_navbar_item_rules(payload: dict, *, partial: bool = False) -> dict[str, str]:
    errors: dict[str, str] = {}
    item_type = payload.get("item_type")
    if item_type is not None:
        item_type = str(item_type).strip().lower()
        if item_type not in ("link", "dropdown"):
            errors["item_type"] = "Item type must be link or dropdown."
        elif item_type == "dropdown":
            key = str(payload.get("item_key") or "").strip()
            if not key and not (partial and "item_key" not in payload):
                errors["item_key"] = "Dropdown key is required for dropdown parents (e.g. projects)."
    return errors


def validate_content_payload(resource: str, payload: dict, *, partial: bool = False) -> dict[str, str]:
    """Run required + length validation. Returns field → error map."""
    errors = validate_required_fields(resource, payload, partial=partial)
    errors.update(validate_content_lengths(resource, payload))
    if resource == "navbar-items":
        errors.update(_validate_navbar_item_rules(payload, partial=partial))
    return errors
