"""Gemini embedding helpers (used by Pinecone RAG)."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.services.gemini_client import get_gemini_client


def _extract_values(embedding_obj) -> List[float]:
    """Normalize SDK embedding object → list[float]."""
    if embedding_obj is None:
        return []
    if isinstance(embedding_obj, list):
        return [float(x) for x in embedding_obj]
    values = getattr(embedding_obj, "values", None)
    if values is not None:
        return [float(x) for x in values]
    nested = getattr(embedding_obj, "embedding", None)
    if nested is not None:
        return _extract_values(nested)
    return []


class EmbeddingService:
    """Gemini embeddings for ingest + query (Pinecone-compatible vectors)."""

    def _embed_config(self, task_type: str) -> types.EmbedContentConfig:
        settings = get_settings()
        return types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=settings.gemini_embedding_dimension,
        )

    def _embed_batch(self, texts: List[str], task_type: str) -> List[List[float]]:
        """Embed one or more texts; falls back to per-item calls if needed."""
        settings = get_settings()
        client = get_gemini_client()
        config = self._embed_config(task_type)

        # Prefer a single batch call; some SDK/API paths reject large batches.
        try:
            response = client.models.embed_content(
                model=settings.gemini_embedding_model,
                contents=texts if len(texts) > 1 else texts[0],
                config=config,
            )
            embeddings = getattr(response, "embeddings", None) or []
            vectors = [_extract_values(item) for item in embeddings]
            if len(vectors) == len(texts) and all(vectors):
                return vectors
            single = _extract_values(getattr(response, "embedding", None))
            if len(texts) == 1 and single:
                return [single]
        except Exception:
            pass

        vectors: List[List[float]] = []
        for text in texts:
            response = client.models.embed_content(
                model=settings.gemini_embedding_model,
                contents=text,
                config=config,
            )
            embeddings = getattr(response, "embeddings", None) or []
            if embeddings:
                vectors.append(_extract_values(embeddings[0]))
            else:
                vectors.append(_extract_values(getattr(response, "embedding", None)))
        return vectors

    @retry(wait=wait_exponential(multiplier=1, min=1, max=20), stop=stop_after_attempt(5))
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        # Batch in small groups to avoid payload / rate-limit issues
        batch_size = 16
        all_vectors: List[List[float]] = []
        for start in range(0, len(texts), batch_size):
            chunk = texts[start : start + batch_size]
            all_vectors.extend(self._embed_batch(chunk, "RETRIEVAL_DOCUMENT"))
        if len(all_vectors) != len(texts) or any(not v for v in all_vectors):
            raise RuntimeError("Embedding failed: incomplete vectors returned")
        expected = get_settings().gemini_embedding_dimension
        if any(len(v) != expected for v in all_vectors):
            raise RuntimeError(
                f"Embedding dimension mismatch: expected {expected}, "
                f"got {[len(v) for v in all_vectors[:3]]}"
            )
        return all_vectors

    @retry(wait=wait_exponential(multiplier=1, min=1, max=20), stop=stop_after_attempt(5))
    def embed_query(self, text: str) -> List[float]:
        vectors = self._embed_batch([text], "RETRIEVAL_QUERY")
        if not vectors or not vectors[0]:
            raise RuntimeError("Embedding failed: empty query vector")
        expected = get_settings().gemini_embedding_dimension
        if len(vectors[0]) != expected:
            raise RuntimeError(
                f"Query embedding dimension mismatch: expected {expected}, got {len(vectors[0])}"
            )
        return vectors[0]

    async def aembed_query(self, text: str) -> List[float]:
        return self.embed_query(text)

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embed_documents(texts)


@lru_cache
def get_embeddings() -> EmbeddingService:
    return EmbeddingService()


async def embed_query(text: str) -> List[float]:
    return await get_embeddings().aembed_query(text)


async def embed_documents(texts: List[str]) -> List[List[float]]:
    return await get_embeddings().aembed_documents(texts)
