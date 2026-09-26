"""Shared Google GenAI (Gemini) client factory."""

from __future__ import annotations

from functools import lru_cache

from google import genai

from app.core.config import get_settings


@lru_cache
def get_gemini_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_configured:
        raise RuntimeError("Gemini API key is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)
