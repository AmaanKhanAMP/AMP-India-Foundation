"""Get / update website section visibility (show/hide entire sections)."""

from flask import jsonify, request

from extensions import db
from models.cms_models import SectionVisibility, utcnow
from utils.section_registry import (
    default_visible,
    is_known_section,
    section_label,
)


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes", "on"):
            return True
        if lowered in ("false", "0", "no", "off"):
            return False
    return None


def _get_or_create(section_name: str) -> SectionVisibility:
    row = SectionVisibility.query.filter_by(section_name=section_name).first()
    if row:
        return row
    row = SectionVisibility(
        section_name=section_name,
        is_visible=default_visible(section_name),
        created_at=utcnow(),
        updated_at=utcnow(),
    )
    db.session.add(row)
    db.session.commit()
    return row


def get_visibility(section_name: str):
    if not is_known_section(section_name):
        return jsonify({"success": False, "message": "Unknown section."}), 404
    try:
        row = _get_or_create(section_name)
        return jsonify(
            {
                "success": True,
                "data": {
                    **row.to_dict(),
                    "label": section_label(section_name),
                },
            }
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def update_visibility(section_name: str):
    if not is_known_section(section_name):
        return jsonify({"success": False, "message": "Unknown section."}), 404

    payload = request.get_json(silent=True) or {}
    if "is_visible" not in payload:
        return jsonify({"success": False, "message": "is_visible is required."}), 400

    parsed = _parse_bool(payload.get("is_visible"))
    if parsed is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "is_visible must be a boolean (true/false).",
                }
            ),
            400,
        )

    try:
        row = _get_or_create(section_name)
        row.is_visible = parsed
        row.updated_at = utcnow()
        db.session.commit()
        try:
            from services.chatbot_sync import schedule_chatbot_sync

            schedule_chatbot_sync(reason=f"visibility:{section_name}:{parsed}")
        except Exception:
            pass
        label = section_label(section_name)
        message = (
            f"{label} section is now visible."
            if parsed
            else f"{label} section hidden successfully."
        )
        return jsonify(
            {
                "success": True,
                "message": message,
                "data": {**row.to_dict(), "label": label},
            }
        )
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500
