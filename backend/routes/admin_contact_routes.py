"""Admin contact message management."""

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from extensions import db
from models.contact_message import ContactMessage
from utils.auth import admin_required

admin_contact_bp = Blueprint("admin_contact", __name__)


@admin_contact_bp.get("/messages")
@admin_required
def list_messages():
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
    search = (request.args.get("search") or "").strip()
    status = (request.args.get("status") or "").strip()

    query = ContactMessage.query
    if status:
        query = query.filter(ContactMessage.status == status)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                ContactMessage.first_name.ilike(like),
                ContactMessage.last_name.ilike(like),
                ContactMessage.email.ilike(like),
                ContactMessage.phone.ilike(like),
                ContactMessage.message.ilike(like),
            )
        )

    pagination = query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return (
        jsonify(
            {
                "success": True,
                "data": [m.to_dict() for m in pagination.items],
                "pagination": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                },
            }
        ),
        200,
    )


@admin_contact_bp.get("/messages/<int:message_id>")
@admin_required
def get_message(message_id):
    msg = ContactMessage.query.get(message_id)
    if not msg:
        return jsonify({"success": False, "message": "Not found."}), 404
    return jsonify({"success": True, "data": msg.to_dict()}), 200


@admin_contact_bp.patch("/messages/<int:message_id>/read")
@admin_required
def mark_read(message_id):
    msg = ContactMessage.query.get(message_id)
    if not msg:
        return jsonify({"success": False, "message": "Not found."}), 404
    msg.status = "Read"
    db.session.commit()
    return jsonify({"success": True, "data": msg.to_dict()}), 200


@admin_contact_bp.patch("/messages/<int:message_id>/important")
@admin_required
def toggle_important(message_id):
    msg = ContactMessage.query.get(message_id)
    if not msg:
        return jsonify({"success": False, "message": "Not found."}), 404
    data = request.get_json(silent=True) or {}
    if "is_important" in data:
        msg.is_important = bool(data["is_important"])
    else:
        msg.is_important = not bool(msg.is_important)
    db.session.commit()
    return jsonify({"success": True, "data": msg.to_dict()}), 200


@admin_contact_bp.delete("/messages/<int:message_id>")
@admin_required
def delete_message(message_id):
    msg = ContactMessage.query.get(message_id)
    if not msg:
        return jsonify({"success": False, "message": "Not found."}), 404
    db.session.delete(msg)
    db.session.commit()
    return jsonify({"success": True, "message": "Deleted."}), 200


@admin_contact_bp.post("/messages/bulk-delete")
@admin_required
def bulk_delete():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    if not ids:
        return jsonify({"success": False, "message": "ids required."}), 400
    ContactMessage.query.filter(ContactMessage.id.in_([int(i) for i in ids])).delete(
        synchronize_session=False
    )
    db.session.commit()
    return jsonify({"success": True, "message": "Deleted."}), 200
