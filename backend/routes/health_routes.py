from flask import Blueprint, jsonify
from sqlalchemy import text

from extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return (
            jsonify({"status": "success", "database": "Connected"}),
            200,
        )
    except Exception:
        return (
            jsonify(
                {
                    "status": "error",
                    "database": "Disconnected",
                }
            ),
            503,
        )
