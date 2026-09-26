"""Email helpers for auth flows.

SMTP is optional. When not configured, reset links are logged to the Flask console
so local development works without a mail provider.
"""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

logger = logging.getLogger(__name__)


def smtp_configured() -> bool:
    cfg = current_app.config
    return bool(cfg.get("SMTP_HOST") and cfg.get("SMTP_FROM") and cfg.get("SMTP_USER"))


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True on success."""
    if not smtp_configured():
        logger.warning("SMTP not configured — email not sent to %s", to_email)
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = current_app.config["SMTP_FROM"]
    msg["To"] = to_email
    msg.set_content(body)

    host = current_app.config["SMTP_HOST"]
    port = int(current_app.config.get("SMTP_PORT") or 587)
    user = current_app.config["SMTP_USER"]
    password = current_app.config.get("SMTP_PASSWORD") or ""
    use_tls = bool(current_app.config.get("SMTP_USE_TLS", True))

    with smtplib.SMTP(host, port, timeout=20) as server:
        if use_tls:
            server.starttls()
        server.login(user, password)
        server.send_message(msg)
    return True


def send_password_reset_email(to_email: str, reset_url: str) -> None:
    subject = "Reset your AIF CMS password"
    body = (
        "You requested a password reset for the AIF Content Studio.\n\n"
        f"Open this link to set a new password (valid for 1 hour):\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email.\n"
    )
    sent = send_email(to_email, subject, body)
    if not sent:
        # Development fallback — always log the reset URL
        print("\n========== PASSWORD RESET (DEV) ==========")
        print(f"To: {to_email}")
        print(f"Reset URL: {reset_url}")
        print("==========================================\n")
        logger.info("Password reset URL for %s: %s", to_email, reset_url)


def send_email_change_confirmation(to_email: str, confirm_url: str) -> None:
    """Confirm a pending admin email change (used when verification is enabled)."""
    subject = "Confirm your new AIF CMS email"
    body = (
        "You requested to change the email for your AIF Content Studio account.\n\n"
        f"Open this link to confirm the new address:\n{confirm_url}\n\n"
        "If you did not request this, you can ignore this email — your "
        "current email will remain unchanged.\n"
    )
    sent = send_email(to_email, subject, body)
    if not sent:
        print("\n========== EMAIL CHANGE CONFIRM (DEV) ==========")
        print(f"To: {to_email}")
        print(f"Confirm URL: {confirm_url}")
        print("================================================\n")
        logger.info("Email-change confirm URL for %s: %s", to_email, confirm_url)
