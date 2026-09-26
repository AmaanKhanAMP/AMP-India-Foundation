from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from flask import Blueprint, current_app, g, jsonify, request

from extensions import db
from models.cms_models import AdminUser, PasswordResetToken
from services.email_service import send_password_reset_email
# Future email-change confirmation: from services.email_service import send_email_change_confirmation
from utils.auth import admin_required, check_password, create_access_token, hash_password

auth_bp = Blueprint("auth", __name__)

RESET_TOKEN_HOURS = 1


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _normalize_email(value: str) -> str:
    return (value or "").strip().lower()


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember = bool(data.get("remember"))

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    admin = AdminUser.query.filter_by(email=email).first()
    if not admin or not check_password(password, admin.password_hash):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401
    if not admin.is_active:
        return jsonify({"success": False, "message": "Account is inactive."}), 403

    admin.last_login_at = datetime.now(timezone.utc)
    db.session.commit()

    token = create_access_token(admin, remember=remember)
    return (
        jsonify(
            {
                "success": True,
                "message": "Login successful.",
                "token": token,
                "admin": admin.to_dict(),
            }
        ),
        200,
    )


@auth_bp.post("/forgot-password")
def forgot_password():
    """Request a password reset link. Always returns a generic success message."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400

    admin = AdminUser.query.filter_by(email=email, is_active=True).first()
    if admin:
        # Invalidate previous unused tokens for this admin
        PasswordResetToken.query.filter_by(admin_id=admin.id, used_at=None).delete(
            synchronize_session=False
        )

        raw_token = secrets.token_urlsafe(32)
        record = PasswordResetToken(
            admin_id=admin.id,
            token_hash=_hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_HOURS),
        )
        db.session.add(record)
        db.session.commit()

        cms_url = current_app.config.get("CMS_URL", "http://localhost:3002")
        reset_url = f"{cms_url}/reset-password?token={raw_token}"
        try:
            send_password_reset_email(admin.email, reset_url)
        except Exception as exc:
            current_app.logger.exception("Failed to send reset email: %s", exc)
            # Still log for local recovery
            print("\n========== PASSWORD RESET (FALLBACK) ==========")
            print(f"To: {admin.email}")
            print(f"Reset URL: {reset_url}")
            print("===============================================\n")

    return (
        jsonify(
            {
                "success": True,
                "message": "If an account exists for that email, a reset link has been sent.",
            }
        ),
        200,
    )


@auth_bp.post("/reset-password")
def reset_password():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""

    if not token or not new_password:
        return jsonify({"success": False, "message": "Token and new password are required."}), 400
    if len(new_password) < 8:
        return jsonify({"success": False, "message": "New password must be at least 8 characters."}), 400

    record = PasswordResetToken.query.filter_by(token_hash=_hash_token(token)).first()
    now = datetime.now(timezone.utc)

    if not record or record.used_at is not None:
        return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400

    expires = record.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400

    admin = AdminUser.query.get(record.admin_id)
    if not admin or not admin.is_active:
        return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400

    admin.password_hash = hash_password(new_password)
    record.used_at = now
    # Invalidate any other unused tokens
    PasswordResetToken.query.filter(
        PasswordResetToken.admin_id == admin.id,
        PasswordResetToken.id != record.id,
        PasswordResetToken.used_at.is_(None),
    ).delete(synchronize_session=False)

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Password has been reset successfully."}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


@auth_bp.get("/me")
@admin_required
def me():
    return jsonify({"success": True, "admin": g.current_admin.to_dict()}), 200


@auth_bp.put("/profile")
@admin_required
def update_profile():
    """Update the logged-in admin profile.

    - Name can be updated without a password.
    - Email can be updated only after verifying current_password.
    """
    data = request.get_json(silent=True) or {}
    admin = g.current_admin

    if "name" in data and data["name"] is not None:
        name = str(data["name"]).strip()
        if not name:
            return jsonify({"success": False, "message": "Name is required."}), 400
        admin.name = name

    if "email" in data and data["email"] is not None:
        new_email = _normalize_email(data["email"])
        if not new_email:
            return jsonify({"success": False, "message": "Email is required."}), 400

        if new_email != _normalize_email(admin.email):
            current_password = data.get("current_password") or ""
            if not current_password:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Current password is required to change email.",
                        }
                    ),
                    400,
                )
            if not check_password(current_password, admin.password_hash):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Current password is incorrect.",
                        }
                    ),
                    401,
                )

            existing = AdminUser.query.filter(
                AdminUser.email == new_email, AdminUser.id != admin.id
            ).first()
            if existing:
                return jsonify({"success": False, "message": "Email already in use."}), 400

            admin.email = new_email

    try:
        db.session.commit()
        return jsonify({"success": True, "admin": admin.to_dict()}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


@auth_bp.put("/change-password")
@admin_required
def change_password():
    data = request.get_json(silent=True) or {}
    current = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if not current or not new_password:
        return jsonify({"success": False, "message": "Current and new password are required."}), 400
    if len(new_password) < 8:
        return jsonify({"success": False, "message": "New password must be at least 8 characters."}), 400

    admin = g.current_admin
    if not check_password(current, admin.password_hash):
        return jsonify({"success": False, "message": "Current password is incorrect."}), 400

    admin.password_hash = hash_password(new_password)
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Password updated successfully."}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500


@auth_bp.post("/logout")
@admin_required
def logout():
    # Stateless JWT — client discards token
    return jsonify({"success": True, "message": "Logged out."}), 200
