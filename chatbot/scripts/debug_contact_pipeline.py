"""Debug contact RAG pipeline end-to-end (logs each stage)."""

from __future__ import annotations

import asyncio
import json

from app.core.config import get_settings
from app.services.ai_service import ai_service
from app.services.intent_router import route_intent
from app.services.language_service import detect_language
from app.services.query_rewrite import rewrite_query
from app.services.rag_service import clear_retrieval_cache, rag_service
from app.services.response_formatter import format_user_response


async def debug_contact(query: str = "Can I get the contact details of AIF?") -> None:
    settings = get_settings()
    print("=== CONTACT PIPELINE DEBUG ===")
    print(f"Original query: {query!r}")
    print(f"RAG ready: {settings.rag_ready} | top_k={settings.rag_top_k} | model={settings.gemini_chat_model}")

    language = detect_language(query)
    route = route_intent(query)
    rewritten = rewrite_query(query, language=language, intent=route.intent)
    print(f"Language: {language.value}")
    print(f"Intent: {route.intent.value} (filter={route.source_filter})")
    print(f"Rewritten query: {rewritten.search_query!r}")

    clear_retrieval_cache()
    docs, context, timings, relevant = await rag_service.retrieve_validated(
        rewritten.search_query,
        top_k=10,
        source_filter=route.source_filter,
        original_query=query,
    )
    print(f"Embed ms: {timings.get('embed_ms')} | Pinecone ms: {timings.get('pinecone_ms')}")
    print(f"Embedding dim: {timings.get('embedding_dim')} | relevant={relevant}")
    print(f"Top retrieved chunks ({len(docs)}):")
    for i, d in enumerate(docs[:10], 1):
        meta = d.metadata or {}
        print(
            f"  {i}. source={meta.get('source')} score={meta.get('score')} "
            f"rerank={meta.get('rerank_score')} id={meta.get('id')}"
        )
        print(f"     preview: {(d.page_content or '')[:180]!r}")

    print("\n--- Context selected for prompt ---")
    print(context[:1200])
    print("--- end context ---\n")

    result = await ai_service.chat(query, session_id="debug-contact-1")
    final = result.get("response") or ""
    print("Final response after formatting:")
    print(final)
    print("\nMeta:", json.dumps(result.get("meta") or {}, default=str)[:800])
    print("Leak-stripped sample:", format_user_response("/Rules Check:\nRule 1: foo\n\nHello")[:80])


if __name__ == "__main__":
    asyncio.run(debug_contact())
