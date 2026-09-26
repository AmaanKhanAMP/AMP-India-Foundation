"""Singleton Navbar / Footer settings (logo, CTA, contact, copyright)."""

from __future__ import annotations

import re

from flask import jsonify, request

from extensions import db
from models.cms_models import FooterSettings, NavbarSettings, utcnow

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

NAVBAR_FIELDS = ["logo_url", "logo_alt", "logo_link"]
FOOTER_FIELDS = [
    "cta_heading",
    "cta_button_text",
    "cta_button_link",
    "about_heading",
    "about_text",
    "about_link_text",
    "about_link_href",
    "useful_links_heading",
    "recent_focus_heading",
    "contact_heading",
    "address_label",
    "address_text",
    "phone_label",
    "phone_text",
    "email_label",
    "email_text",
    "follow_heading",
    "facebook_url",
    "instagram_url",
    "copyright_text",
    "copyright_highlight",
]

FOOTER_DEFAULTS = {
    "cta_heading": "Join Our Mission to Empower Lives Through Education & Employment.",
    "cta_button_text": "BECOME A VOLUNTEER",
    "cta_button_link": "/volunteer",
    "about_heading": "ABOUT US",
    "about_text": (
        "AMP India Foundation is a non-profit organization dedicated to regularise "
        "and scale up socio-economic development welfare activities. We empower "
        "underprivileged youth through sustainable educational models, rigorous training, "
        "and professional mentorship."
    ),
    "about_link_text": "READ MORE →",
    "about_link_href": "/about",
    "useful_links_heading": "USEFUL LINKS",
    "recent_focus_heading": "RECENT FOCUS",
    "contact_heading": "GET IN TOUCH",
    "address_label": "📍 Address:",
    "address_text": "AMP India Foundation, Mumbai, Maharashtra, India.",
    "phone_label": "📞 Phone:",
    "phone_text": "+91 93200 60093",
    "email_label": "✉️ Email:",
    "email_text": "info@ampindia.org",
    "follow_heading": "FOLLOW US",
    "facebook_url": "https://www.facebook.com/ampindiafoundation/",
    "instagram_url": "https://www.instagram.com/ampindiafoundation/",
    "copyright_text": "Copyrights © 2026 All Rights Reserved. Powered by ",
    "copyright_highlight": "AMP India Foundation",
}

NAVBAR_LIMITS = {
    "logo_url": 500,
    "logo_alt": 120,
    "logo_link": 500,
}

FOOTER_LIMITS = {
    "cta_heading": 160,
    "cta_button_text": 40,
    "cta_button_link": 500,
    "about_heading": 40,
    "about_text": 600,
    "about_link_text": 40,
    "about_link_href": 500,
    "useful_links_heading": 40,
    "recent_focus_heading": 40,
    "contact_heading": 40,
    "address_label": 40,
    "address_text": 200,
    "phone_label": 40,
    "phone_text": 40,
    "email_label": 40,
    "email_text": 120,
    "follow_heading": 40,
    "facebook_url": 500,
    "instagram_url": 500,
    "copyright_text": 255,
    "copyright_highlight": 120,
}


def _ensure_navbar() -> NavbarSettings:
    row = NavbarSettings.query.order_by(NavbarSettings.id.asc()).first()
    if row:
        return row
    row = NavbarSettings(
        logo_url="/assets/logo.png",
        logo_alt="AMP Logo",
        logo_link="/",
        created_at=utcnow(),
        updated_at=utcnow(),
    )
    db.session.add(row)
    db.session.commit()
    return row


def _ensure_footer() -> FooterSettings:
    row = FooterSettings.query.order_by(FooterSettings.id.asc()).first()
    if row:
        return row
    row = FooterSettings(**FOOTER_DEFAULTS, created_at=utcnow(), updated_at=utcnow())
    db.session.add(row)
    db.session.commit()
    return row


def _validate_lengths(payload: dict, limits: dict) -> dict[str, str]:
    errors = {}
    for field, max_len in limits.items():
        if field not in payload:
            continue
        value = payload.get(field)
        if value is None:
            continue
        text = str(value)
        if len(text) > max_len:
            errors[field] = f"{field.replace('_', ' ').title()} must be at most {max_len} characters."
    return errors


def _validate_navbar(payload: dict) -> dict[str, str]:
    errors = _validate_lengths(payload, NAVBAR_LIMITS)
    for field in ("logo_url", "logo_alt", "logo_link"):
        if field in payload and not str(payload.get(field) or "").strip():
            errors[field] = f"{field.replace('_', ' ').title()} is required."
    return errors


def _validate_footer(payload: dict, *, partial: bool = False) -> dict[str, str]:
    errors = _validate_lengths(payload, FOOTER_LIMITS)
    required = FOOTER_FIELDS
    for field in required:
        if partial and field not in payload:
            continue
        if field not in payload and not partial:
            errors[field] = f"{field.replace('_', ' ').title()} is required."
            continue
        if field in payload and not str(payload.get(field) or "").strip():
            errors[field] = f"{field.replace('_', ' ').title()} is required."

    email = payload.get("email_text")
    if email is not None and str(email).strip() and not EMAIL_RE.match(str(email).strip()):
        errors["email_text"] = "Enter a valid email address."

    for url_field in ("facebook_url", "instagram_url", "cta_button_link", "about_link_href"):
        value = payload.get(url_field)
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        if not (
            text.startswith("/")
            or text.startswith("http://")
            or text.startswith("https://")
            or text.startswith("#")
            or text.startswith("mailto:")
            or text.startswith("tel:")
        ):
            errors[url_field] = "Enter a valid URL or site path (e.g. /about or https://…)."

    return errors


def get_navbar_settings():
    try:
        row = _ensure_navbar()
        return jsonify({"success": True, "data": row.to_dict()})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def _notify_chatbot(reason: str) -> None:
    try:
        from services.chatbot_sync import schedule_chatbot_sync

        schedule_chatbot_sync(reason=reason)
    except Exception:
        pass


def update_navbar_settings():
    payload = request.get_json(silent=True) or {}
    data = {k: payload.get(k) for k in NAVBAR_FIELDS if k in payload}
    if not data:
        return jsonify({"success": False, "message": "No valid fields provided."}), 400

    errors = _validate_navbar(data)
    if errors:
        return jsonify({"success": False, "message": "Validation failed.", "errors": errors}), 400

    try:
        row = _ensure_navbar()
        for key, value in data.items():
            setattr(row, key, str(value).strip())
        row.updated_at = utcnow()
        db.session.commit()
        _notify_chatbot("update:navbar_settings")
        return jsonify(
            {
                "success": True,
                "message": "Navbar settings saved.",
                "data": row.to_dict(),
            }
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def get_footer_settings():
    try:
        row = _ensure_footer()
        return jsonify({"success": True, "data": row.to_dict()})
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def update_footer_settings():
    payload = request.get_json(silent=True) or {}
    data = {k: payload.get(k) for k in FOOTER_FIELDS if k in payload}
    if not data:
        return jsonify({"success": False, "message": "No valid fields provided."}), 400

    # Require full set for PUT (settings form always sends all fields)
    missing = [f for f in FOOTER_FIELDS if f not in data]
    if missing:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": {f: "This field is required." for f in missing},
                }
            ),
            400,
        )

    errors = _validate_footer(data, partial=False)
    if errors:
        return jsonify({"success": False, "message": "Validation failed.", "errors": errors}), 400

    try:
        row = _ensure_footer()
        for key, value in data.items():
            setattr(row, key, str(value).strip() if value is not None else "")
        row.updated_at = utcnow()
        db.session.commit()
        _notify_chatbot("update:footer_settings")
        return jsonify(
            {
                "success": True,
                "message": "Footer settings saved.",
                "data": row.to_dict(),
            }
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500
