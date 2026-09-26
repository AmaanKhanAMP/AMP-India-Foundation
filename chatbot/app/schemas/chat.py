"""Pydantic request/response models for the chat API."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default=None, alias="sessionId", max_length=128)
    page: Optional[str] = Field(default=None, max_length=255)

    model_config = {"populate_by_name": True}

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError("Message cannot be empty.")
        return cleaned


class ChatResponse(BaseModel):
    success: bool = True
    response: str
    reply: Optional[str] = None  # alias for frontend compatibility
    session_id: str
    intent: Optional[str] = None
    category: Optional[str] = None
    confidence: Optional[float] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def sync_reply(self):
        if self.reply is None:
            self.reply = self.response
        return self


class HealthResponse(BaseModel):
    success: bool = True
    status: Literal["ok", "degraded"] = "ok"
    service: str = "aif-chatbot"


class StatusResponse(BaseModel):
    success: bool = True
    service: str
    version: str
    environment: str
    gemini_configured: bool
    pinecone_configured: bool
    rag_ready: bool
    embedding_model: str
    chat_model: str


class IngestResponse(BaseModel):
    success: bool
    indexed: int = 0
    deleted: int = 0
    message: str
    sources: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    response: Optional[str] = None
