"""Generic CRUD helpers for CMS content resources (with soft delete / trash)."""

from flask import g, jsonify, request

from extensions import db
from models.cms_models import AdminUser, utcnow
from utils.content_registry import CONTENT_RESOURCES, get_model_meta, get_resource_meta
from utils.uploads import cleanup_item_media


def _notify_chatbot(reason: str) -> None:
    """Fire-and-forget: CMS change → export → chatbot Pinecone incremental upsert."""
    try:
        from services.chatbot_sync import schedule_chatbot_sync

        schedule_chatbot_sync(reason=reason)
    except Exception:
        # Never fail CMS saves because of sync issues
        pass


def _alive(query, model):
    """Exclude soft-deleted rows from normal CMS and public queries."""
    if hasattr(model, "is_deleted"):
        query = query.filter(model.is_deleted.is_(False))
    return query


def _apply_filters(query, model, published_only=False):
    query = _alive(query, model)
    if published_only:
        query = query.filter(model.status == "published")
    status = request.args.get("status")
    if status and not published_only:
        query = query.filter(model.status == status)
    search = request.args.get("search", "").strip()
    if search and hasattr(model, "title"):
        query = query.filter(model.title.ilike(f"%{search}%"))
    elif search and hasattr(model, "name"):
        query = query.filter(model.name.ilike(f"%{search}%"))
    return query


def _get_alive(model, item_id):
    item = model.query.get(item_id)
    if not item or getattr(item, "is_deleted", False):
        return None
    return item


def _get_trashed(model, item_id):
    item = model.query.get(item_id)
    if not item or not getattr(item, "is_deleted", False):
        return None
    return item


def list_items(model, published_only=False):
    try:
        query = _apply_filters(model.query, model, published_only=published_only)
        items = query.order_by(model.display_order.asc(), model.id.desc()).all()
        return (
            jsonify(
                {
                    "success": True,
                    "count": len(items),
                    "data": [item.to_dict() for item in items],
                }
            ),
            200,
        )
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


def get_item(model, item_id, published_only=False):
    item = _get_alive(model, item_id)
    if not item:
        return jsonify({"success": False, "message": "Not found."}), 404
    if published_only and item.status != "published":
        return jsonify({"success": False, "message": "Not found."}), 404
    return jsonify({"success": True, "data": item.to_dict()}), 200


def create_item(model, allowed_fields, resource=None):
    data = request.get_json(silent=True) or {}
    payload = {k: data.get(k) for k in allowed_fields if k in data}
    if "status" not in payload:
        payload["status"] = "draft"
    if "display_order" not in payload:
        max_order = (
            db.session.query(db.func.max(model.display_order))
            .filter(model.is_deleted.is_(False))
            .scalar()
            or 0
        )
        payload["display_order"] = max_order + 1

    if resource:
        from utils.content_field_limits import validate_content_payload

        length_errors = validate_content_payload(resource, payload, partial=False)
        if length_errors:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Please fix the highlighted fields.",
                        "errors": length_errors,
                    }
                ),
                400,
            )

    try:
        item = model(**payload)
        db.session.add(item)
        db.session.commit()
        _notify_chatbot(f"create:{model.__tablename__}")
        return jsonify({"success": True, "data": item.to_dict()}), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def update_item(model, item_id, allowed_fields, resource=None):
    item = _get_alive(model, item_id)
    if not item:
        return jsonify({"success": False, "message": "Not found."}), 404
    data = request.get_json(silent=True) or {}
    payload = {k: data[k] for k in allowed_fields if k in data}

    if resource:
        from utils.content_field_limits import validate_content_payload

        length_errors = validate_content_payload(resource, payload, partial=True)
        if length_errors:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Please fix the highlighted fields.",
                        "errors": length_errors,
                    }
                ),
                400,
            )

    for key, value in payload.items():
        setattr(item, key, value)
    try:
        db.session.commit()
        _notify_chatbot(f"update:{model.__tablename__}")
        return jsonify({"success": True, "data": item.to_dict()}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def delete_item(model, item_id):
    """Soft-delete: move item to Trash (does not remove the DB row)."""
    item = _get_alive(model, item_id)
    if not item:
        return jsonify({"success": False, "message": "Not found."}), 404
    admin = getattr(g, "current_admin", None)
    item.is_deleted = True
    item.deleted_at = utcnow()
    item.deleted_by = admin.id if admin else None
    try:
        db.session.commit()
        _notify_chatbot(f"delete:{model.__tablename__}")
        return jsonify({"success": True, "message": "Moved to Trash.", "data": item.to_dict()}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def restore_item(model, item_id):
    item = _get_trashed(model, item_id)
    if not item:
        return jsonify({"success": False, "message": "Not found in Trash."}), 404
    item.is_deleted = False
    item.deleted_at = None
    item.deleted_by = None
    try:
        db.session.commit()
        db.session.refresh(item)
        _notify_chatbot(f"restore:{model.__tablename__}")
        return jsonify({"success": True, "message": "Restored.", "data": item.to_dict()}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def permanent_delete_item(model, item_id):
    """Hard-delete from Trash and remove orphaned upload files."""
    item = _get_trashed(model, item_id)
    if not item:
        return jsonify({"success": False, "message": "Not found in Trash."}), 404
    meta = get_model_meta(model) or {}
    image_fields = meta.get("image_fields") or []
    try:
        cleanup_item_media(item, image_fields, exclude_self=True)
        db.session.delete(item)
        db.session.commit()
        _notify_chatbot(f"permanent_delete:{model.__tablename__}")
        return jsonify({"success": True, "message": "Permanently deleted."}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def duplicate_item(model, item_id, allowed_fields):
    item = _get_alive(model, item_id)
    if not item:
        return jsonify({"success": False, "message": "Not found."}), 404
    data = item.to_dict()
    payload = {k: data.get(k) for k in allowed_fields if k in data}
    payload["status"] = "draft"
    if "title" in payload and payload["title"]:
        payload["title"] = f"{payload['title']} (Copy)"
    max_order = (
        db.session.query(db.func.max(model.display_order))
        .filter(model.is_deleted.is_(False))
        .scalar()
        or 0
    )
    payload["display_order"] = max_order + 1
    try:
        clone = model(**payload)
        db.session.add(clone)
        db.session.commit()
        _notify_chatbot(f"duplicate:{model.__tablename__}")
        return jsonify({"success": True, "data": clone.to_dict()}), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def reorder_items(model):
    data = request.get_json(silent=True) or {}
    order = data.get("order") or data.get("ids") or []
    if not isinstance(order, list) or not order:
        return jsonify({"success": False, "message": "order array required."}), 400
    try:
        for index, item_id in enumerate(order):
            item = _get_alive(model, int(item_id))
            if item:
                item.display_order = index + 1
        db.session.commit()
        _notify_chatbot(f"reorder:{model.__tablename__}")
        return jsonify({"success": True, "message": "Order updated."}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def set_status(model, item_id, status):
    if status not in ("draft", "published", "archived"):
        return jsonify({"success": False, "message": "Invalid status."}), 400
    item = _get_alive(model, item_id)
    if not item:
        return jsonify({"success": False, "message": "Not found."}), 404
    item.status = status
    try:
        db.session.commit()
        db.session.refresh(item)
        _notify_chatbot(f"status:{model.__tablename__}:{status}")
        return jsonify({"success": True, "data": item.to_dict()}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def bulk_action(model):
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    action = data.get("action")
    if not ids or action not in ("delete", "publish", "unpublish"):
        return jsonify({"success": False, "message": "ids and action required."}), 400
    admin = getattr(g, "current_admin", None)
    try:
        items = (
            model.query.filter(model.id.in_([int(i) for i in ids]))
            .filter(model.is_deleted.is_(False))
            .all()
        )
        if action == "delete":
            now = utcnow()
            for item in items:
                item.is_deleted = True
                item.deleted_at = now
                item.deleted_by = admin.id if admin else None
        elif action == "publish":
            for item in items:
                item.status = "published"
        else:
            for item in items:
                item.status = "draft"
        db.session.commit()
        _notify_chatbot(f"bulk:{model.__tablename__}:{action}")
        return jsonify({"success": True, "message": f"Bulk {action} complete.", "count": len(items)}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


def _admin_name(admin_id):
    if not admin_id:
        return None
    admin = AdminUser.query.get(admin_id)
    return admin.name if admin else None


def _trash_row(entry, item):
    title_attr = entry["title_attr"]
    title = getattr(item, title_attr, None) or getattr(item, "title", None) or "Untitled"
    thumb = None
    for field in entry["image_fields"]:
        value = getattr(item, field, None)
        if value:
            thumb = value
            break
    return {
        "id": item.id,
        "resource": entry["resource"],
        "module": entry["module"],
        "title": title,
        "thumbnail": thumb,
        "status": item.status,
        "display_order": item.display_order,
        "deleted_at": item.deleted_at.isoformat() if item.deleted_at else None,
        "deleted_by": item.deleted_by,
        "deleted_by_name": _admin_name(item.deleted_by),
        "is_deleted": True,
    }


def list_trash():
    """Unified Trash across all registered content modules."""
    try:
        module_filter = (request.args.get("module") or request.args.get("resource") or "").strip()
        search = (request.args.get("search") or "").strip().lower()
        sort = (request.args.get("sort") or "deleted_at_desc").strip()

        rows = []
        for entry in CONTENT_RESOURCES:
            if module_filter and entry["resource"] != module_filter:
                continue
            model = entry["model"]
            for item in model.query.filter(model.is_deleted.is_(True)).all():
                rows.append(_trash_row(entry, item))

        if search:
            rows = [
                r
                for r in rows
                if search in (r["title"] or "").lower()
                or search in (r["module"] or "").lower()
                or search in (r.get("deleted_by_name") or "").lower()
            ]

        reverse = sort != "deleted_at_asc"
        rows.sort(key=lambda r: r["deleted_at"] or "", reverse=reverse)

        return jsonify({"success": True, "count": len(rows), "data": rows}), 200
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


def trash_count():
    total = 0
    for entry in CONTENT_RESOURCES:
        total += entry["model"].query.filter(entry["model"].is_deleted.is_(True)).count()
    return total


def restore_from_trash(resource, item_id):
    meta = get_resource_meta(resource)
    if not meta:
        return jsonify({"success": False, "message": "Unknown module."}), 404
    return restore_item(meta["model"], item_id)


def permanent_delete_from_trash(resource, item_id):
    meta = get_resource_meta(resource)
    if not meta:
        return jsonify({"success": False, "message": "Unknown module."}), 404
    return permanent_delete_item(meta["model"], item_id)
