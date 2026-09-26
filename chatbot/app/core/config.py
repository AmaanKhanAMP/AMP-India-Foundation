"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AMP India Foundation AI Assistant"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    # Google Gemini
    gemini_api_key: str = ""
    # Default: gemini-2.5-flash. Optional faster model: gemini-2.5-flash-lite
    # Default alias tracks Google's current Flash generation — override via .env anytime
    gemini_chat_model: str = "gemini-flash-latest"
    gemini_general_model: str = ""  # empty → reuse gemini_chat_model
    # gemini-embedding-001 (replaces deprecated text-embedding-004)
    gemini_embedding_model: str = "gemini-embedding-001"
    # Matryoshka output size — Pinecone index must match this value
    gemini_embedding_dimension: int = 768
    gemini_timeout_seconds: int = 45
    gemini_max_retries: int = 2
    gemini_rag_temperature: float = 0.15
    gemini_general_temperature: float = 0.25
    gemini_rag_max_output_tokens: int = 1024
    gemini_general_max_output_tokens: int = 256

    pinecone_api_key: str = ""
    pinecone_index_name: str = "aif-chatbot"
    pinecone_namespace: str = "amp-foundation"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    rag_top_k: int = 10
    rag_score_threshold: float = 0.28
    chunk_size: int = 550
    chunk_overlap: int = 100

    rate_limit: str = "30/minute"
    max_message_length: int = 2000
    max_upload_mb: int = 10
    session_ttl_minutes: int = 60
    admin_ingest_token: str = "change-me"
    cms_api_url: str = "http://127.0.0.1:5000"

    # Prefer chatbot/knowledge; fall back handled by ingest if empty
    knowledge_dir: str = str((ROOT_DIR / "knowledge").resolve())
    documents_dir: str = str((ROOT_DIR / "documents").resolve())

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value):
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @field_validator("knowledge_dir", "documents_dir", mode="before")
    @classmethod
    def resolve_relative_dirs(cls, value):
        if not value:
            return value
        path = Path(str(value))
        if not path.is_absolute():
            path = (ROOT_DIR / path).resolve()
        return str(path)

    @property
    def gemini_configured(self) -> bool:
        key = (self.gemini_api_key or "").strip()
        if not key or len(key) < 20:
            return False
        # Reject common placeholders
        if key.upper() in {"YOUR_API_KEY", "CHANGE_ME", "PLACEHOLDER"}:
            return False
        if key.upper().startswith("YOUR_"):
            return False
        return True

    @property
    def pinecone_configured(self) -> bool:
        return bool(self.pinecone_api_key and len(self.pinecone_api_key) > 10)

    @property
    def rag_ready(self) -> bool:
        return self.gemini_configured and self.pinecone_configured

    @property
    def effective_general_model(self) -> str:
        """Model for general-knowledge answers (defaults to chat model)."""
        return (self.gemini_general_model or self.gemini_chat_model).strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()
