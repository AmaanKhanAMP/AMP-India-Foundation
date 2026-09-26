"""Quick end-to-end verification of Pinecone retrieval + chat answers."""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.services.ai_service import ai_service
from app.services.embedding_service import get_embeddings
from app.services.rag_service import get_pinecone_client, rag_service


async def main() -> None:
    get_settings.cache_clear()
    get_embeddings.cache_clear()
    get_pinecone_client.cache_clear()
    settings = get_settings()

    print("=== RAG Verification ===")
    print("model:", settings.gemini_embedding_model, "dim:", settings.gemini_embedding_dimension)
    print("stats:", rag_service.index_stats())
    print()

    for q in [
        "What is the contact number of AMP?",
        "What scholarships does AMP offer?",
        "How can I volunteer?",
    ]:
        t0 = time.time()
        docs, _ctx, timings = await rag_service.retrieve(q)
        ms = (time.time() - t0) * 1000
        print(
            f"RETRIEVE {ms:.0f}ms chunks={len(docs)} "
            f"embed={timings.get('embed_ms', 0):.0f} pinecone={timings.get('pinecone_ms', 0):.0f} q={q!r}"
        )
        if docs:
            preview = docs[0].page_content[:140].replace("\n", " ")
            print("  top:", preview)

    print()
    questions = [
        "Hi",
        "What is the contact number of AMP India Foundation?",
        "Tell me about AMP scholarships",
        "What color is the sky?",
        "What is ChatGPT?",
        "What is the mission of AMP?",
    ]
    for q in questions:
        t0 = time.time()
        res = await ai_service.chat(q)
        ms = (time.time() - t0) * 1000
        reason = res["meta"].get("reason")
        timings = res["meta"].get("timings") or {}
        print(
            f"CHAT {ms:.0f}ms intent={res['intent']} reason={reason} "
            f"classify={timings.get('classify_ms', 0):.1f} "
            f"retrieve={timings.get('retrieve_ms', 0):.0f} "
            f"gemini={timings.get('gemini_ms', 0):.0f}"
        )
        print(" ", res["response"][:280].replace("\n", " "))
        print()


if __name__ == "__main__":
    asyncio.run(main())
