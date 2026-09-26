"""Shared lightweight types for the RAG pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Document:
    """Chunk stored / retrieved from Pinecone."""

    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
