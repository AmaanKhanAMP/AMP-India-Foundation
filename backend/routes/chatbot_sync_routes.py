"""Admin routes to trigger chatbot / Pinecone knowledge sync."""

from flask import Blueprint, jsonify

from utils.auth import admin_required

chatbot_sync_bp = Blueprint("chatbot_sync", __name__)


@chatbot_sync_bp.post("/sync")
@admin_required
def sync_chatbot_now():
    """
    Force an immediate CMS + knowledge → chatbot Pinecone sync.
    Requires CHATBOT_URL and CHATBOT_INGEST_TOKEN in backend .env.
    """
    from services.chatbot_sync import run_chatbot_sync

    result = run_chatbot_sync(reason="admin_manual")
    status = 200 if result.get("success") else 502
    return jsonify(result), status


@chatbot_sync_bp.post("/rebuild")
@admin_required
def rebuild_chatbot_now():
    """Force CMS + website snapshots into Pinecone and drop legacy sources."""
    from services.chatbot_sync import run_chatbot_sync

    result = run_chatbot_sync(reason="rebuild_admin", force=True)
    status = 200 if result.get("success") else 502
    return jsonify(result), status


@chatbot_sync_bp.get("/status")
@admin_required
def sync_status():
    import os

    token = (os.getenv("CHATBOT_INGEST_TOKEN") or "").strip()
    configured = bool(token) and token not in {
        "change-me",
        "change-me-to-a-long-random-secret",
    }
    return jsonify(
        {
            "success": True,
            "chatbot_url": (os.getenv("CHATBOT_URL") or "http://127.0.0.1:8000").rstrip("/"),
            "sync_enabled": (os.getenv("CHATBOT_SYNC_ENABLED") or "true").lower()
            in {"1", "true", "yes", "on"},
            "token_configured": configured,
        }
    ), 200
