"""JWT auth helpers for CMS admin routes."""

from datetime import datetime, timezone
from functools import wraps

import bcrypt
import jwt
from flask import current_app, g, jsonify, request

from models.cms_models import AdminUser


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(admin: AdminUser, remember: bool = False) -> str:
    expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    if remember:
        from datetime import timedelta

        expires = timedelta(days=30)

    payload = {
        "sub": str(admin.id),
        "email": admin.email,
        "role": admin.role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + expires,
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authorization required."}), 401

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
            admin = AdminUser.query.get(int(payload["sub"]))
            if not admin or not admin.is_active:
                return jsonify({"success": False, "message": "Invalid or inactive admin."}), 401
            g.current_admin = admin
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired."}), 401
        except Exception:
            return jsonify({"success": False, "message": "Invalid token."}), 401

        return fn(*args, **kwargs)

    return wrapper
