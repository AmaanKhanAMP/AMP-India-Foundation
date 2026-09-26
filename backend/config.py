import os
import re
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _parse_csv_list(value: str) -> list[str]:
    """Split a comma-separated env value into trimmed non-empty strings."""
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _build_cors_origins() -> list:
    """
    Build Flask-CORS origins from env.

    CORS_ORIGINS — exact origins (comma-separated), e.g.
      http://localhost:3000,https://my-app.vercel.app

    CORS_ORIGIN_REGEXES — optional regex patterns (comma-separated), e.g.
      https://.*\\.vercel\\.app
    Useful for Vercel preview URLs without listing every deployment.
    Never use "*" here when sending credentials.
    """
    default_origins = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://127.0.0.1:3001,"
        "http://localhost:3002,http://127.0.0.1:3002,"
        "https://amp-aif.vercel.app"
    )
    origins: list = _parse_csv_list(os.getenv("CORS_ORIGINS", default_origins))

    # Reject wildcard when mixed with credentialed mode; keep list explicit.
    origins = [o for o in origins if o != "*"]

    for pattern in _parse_csv_list(os.getenv("CORS_ORIGIN_REGEXES", "")):
        try:
            origins.append(re.compile(pattern))
        except re.error:
            # Skip invalid patterns rather than crashing the app at boot
            continue

    return origins


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "aif_cms")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # Exact origins + optional regexes — see _build_cors_origins()
    CORS_ORIGINS = _build_cors_origins()

    # Auth is JWT in Authorization header (no cookie credentials on API calls)
    CORS_SUPPORTS_CREDENTIALS = os.getenv(
        "CORS_SUPPORTS_CREDENTIALS", "false"
    ).lower() in ("1", "true", "yes", "on")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    # Public CMS URL used in password-reset emails
    CMS_URL = os.getenv("CMS_URL", "http://localhost:3002").rstrip("/")

    # Optional SMTP (leave blank in local dev — reset URLs are logged to console)
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = os.getenv("SMTP_PORT", "587")
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

    # When True, email changes require confirming a link sent to the new address
    # (pending_email flow). Password re-auth is still required either way.
    EMAIL_CHANGE_REQUIRES_VERIFICATION = os.getenv(
        "EMAIL_CHANGE_REQUIRES_VERIFICATION", "false"
    ).lower() in ("1", "true", "yes")

    # Phase-3 chatbot sync (CMS Save → Pinecone incremental update)
    CHATBOT_URL = os.getenv("CHATBOT_URL", "http://127.0.0.1:8000").rstrip("/")
    CHATBOT_INGEST_TOKEN = os.getenv("CHATBOT_INGEST_TOKEN", "")
    CHATBOT_SYNC_ENABLED = os.getenv("CHATBOT_SYNC_ENABLED", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
