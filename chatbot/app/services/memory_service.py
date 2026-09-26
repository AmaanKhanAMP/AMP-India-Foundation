"""In-memory session conversation store (TTL-based, not permanent)."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.core.config import get_settings


@dataclass
class SessionState:
    session_id: str
    messages: List[BaseMessage] = field(default_factory=list)
    last_topic: Optional[str] = None
    last_entity: Optional[str] = None
    last_language: Optional[str] = None
    updated_at: float = field(default_factory=time.time)


class MemoryService:
    """Active-session memory only — cleared on TTL expiry."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: Dict[str, SessionState] = {}

    def ensure_session(self, session_id: Optional[str]) -> str:
        sid = (session_id or "").strip() or str(uuid.uuid4())
        with self._lock:
            self._purge_locked()
            if sid not in self._sessions:
                self._sessions[sid] = SessionState(session_id=sid)
            else:
                self._sessions[sid].updated_at = time.time()
            return sid

    def get_history(self, session_id: str, limit: int = 8) -> List[BaseMessage]:
        with self._lock:
            self._purge_locked()
            state = self._sessions.get(session_id)
            if not state:
                return []
            return list(state.messages[-limit:])

    def history_as_chat(self, session_id: str, limit: int = 8) -> List[dict]:
        """Convert LangChain history messages to chat role/content dicts."""
        rows = []
        for msg in self.get_history(session_id, limit=limit):
            role = "assistant" if isinstance(msg, AIMessage) else "user"
            content = str(getattr(msg, "content", "") or "")
            if content:
                rows.append({"role": role, "content": content})
        return rows

    # Backward-compatible alias
    def history_as_openai(self, session_id: str, limit: int = 8) -> List[dict]:
        return self.history_as_chat(session_id, limit=limit)

    def add_turn(self, session_id: str, user: str, assistant: str) -> None:
        with self._lock:
            self._purge_locked()
            state = self._sessions.get(session_id) or SessionState(session_id=session_id)
            state.messages.append(HumanMessage(content=user))
            state.messages.append(AIMessage(content=assistant))
            if len(state.messages) > 16:
                state.messages = state.messages[-16:]
            state.updated_at = time.time()
            self._sessions[session_id] = state

    def set_topic(self, session_id: str, topic: Optional[str]) -> None:
        with self._lock:
            state = self._sessions.get(session_id)
            if state:
                state.last_topic = topic
                state.updated_at = time.time()

    def get_topic(self, session_id: str) -> Optional[str]:
        with self._lock:
            state = self._sessions.get(session_id)
            return state.last_topic if state else None

    def set_entity(self, session_id: str, entity: Optional[str]) -> None:
        with self._lock:
            state = self._sessions.get(session_id)
            if state and entity:
                state.last_entity = entity.strip()
                state.updated_at = time.time()

    def get_entity(self, session_id: str) -> Optional[str]:
        with self._lock:
            state = self._sessions.get(session_id)
            return state.last_entity if state else None

    def set_language(self, session_id: str, language: Optional[str]) -> None:
        with self._lock:
            state = self._sessions.get(session_id)
            if state:
                state.last_language = language
                state.updated_at = time.time()

    def get_language(self, session_id: str) -> Optional[str]:
        with self._lock:
            state = self._sessions.get(session_id)
            return state.last_language if state else None

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def stats(self) -> Tuple[int, int]:
        with self._lock:
            self._purge_locked()
            return len(self._sessions), sum(len(s.messages) for s in self._sessions.values())

    def _purge_locked(self) -> None:
        ttl = get_settings().session_ttl_minutes * 60
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now - s.updated_at > ttl]
        for sid in expired:
            del self._sessions[sid]


memory_service = MemoryService()
