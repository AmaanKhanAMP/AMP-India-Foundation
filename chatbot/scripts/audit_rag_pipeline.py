"""RAG pipeline debug audit — prints every stage for a fixed query set.

Usage:
  python -m scripts.audit_rag_pipeline
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any, Dict, List

from app.core.config import get_settings
from app.services.ai_service import AiService, _to_gemini_contents
from app.services.intent_router import Intent, RAG_INTENTS, route_intent
from app.services.language_service import detect_language, resolve_session_language
from app.services.memory_service import memory_service
from app.services.prompt_service import build_rag_messages
from app.services.query_rewrite import rewrite_query
from app.services.rag_service import clear_retrieval_cache, rag_service
from app.services.response_formatter import format_user_response
from app.services.security_service import sanitize_message

QUERIES = [
    "AIF kaha hai",
    "address of aif",
    "where is aif located",
    "contact number",
    "volunteer kaise bane",
    "donation",
    "scholarship",
    "job",
    "AMP kya karta hai",
    "mujhe job chahiye",
    "mai gareeb hu",
    "how can I reach AIF",
]


def _preview(text: str, n: int = 250) -> str:
    return (text or "").replace("\n", " ")[:n]


async def audit_one(query: str) -> Dict[str, Any]:
    settings = get_settings()
    clean = sanitize_message(query)
    sid = memory_service.ensure_session(f"audit-{hash(query) % 100000}")
    session_lang = memory_service.get_language(sid)
    session_topic = memory_service.get_topic(sid)

    detected = detect_language(clean, session_language=session_lang)
    language = resolve_session_language(detected, clean, session_lang)
    route = route_intent(clean, has_session_topic=bool(session_topic), session_topic=session_topic)

    print("\n" + "=" * 72)
    print(f"ORIGINAL: {query!r}")
    print("=" * 72)
    print(f"Detected Language : {detected.value}")
    print(f"Session Language  : {language.value}")
    print(f"Detected Intent   : {route.intent.value} ({route.reason}) conf={route.confidence}")
    print(f"Source Filter     : {route.source_filter}")
    print(f"Uses RAG flag     : {route.uses_rag}")

    bypass = None
    if route.intent.value in {"greeting", "small_talk", "goodbye"}:
        bypass = "conversational_canned"
    elif route.intent in {Intent.INJECTION, Intent.OUT_OF_SCOPE, Intent.GENERAL_KNOWLEDGE}:
        bypass = f"refuse:{route.intent.value}"

    if bypass:
        print(f"*** PINECONE BYPASSED: {bypass} ***")
        result = await AiService().chat(clean, session_id=sid)
        print(f"Final Response    : {(result.get('response') or '')[:400]}")
        return {"query": query, "bypass": bypass, "response": result.get("response")}

    intent_for_rewrite = route.intent if route.intent in RAG_INTENTS else Intent.AMP_KNOWLEDGE
    rewritten = rewrite_query(
        clean, language=language, intent=intent_for_rewrite, session_topic=session_topic
    )
    print(f"Rewritten Query   : {rewritten.search_query!r}")
    print(f"Embedding Model   : {settings.gemini_embedding_model}")
    print(f"Embedding Dim     : {settings.gemini_embedding_dimension}")
    print(f"Namespace         : {settings.pinecone_namespace}")
    print(f"Top K             : {settings.rag_top_k}")
    print(f"Score Threshold   : {settings.rag_score_threshold}")

    clear_retrieval_cache()
    docs, context, timings, relevant = await rag_service.retrieve_validated(
        rewritten.search_query,
        top_k=10,
        source_filter=None if route.intent == Intent.UNKNOWN else route.source_filter,
        original_query=clean,
    )
    print(f"Embed ms / Pinecone ms : {timings.get('embed_ms'):.0f} / {timings.get('pinecone_ms'):.0f}")
    print(f"Embedding dim (runtime): {timings.get('embedding_dim')}")
    print(f"Relevant              : {relevant}")
    print(f"Chunks kept           : {len(docs)}")

    print("--- Retrieved / selected chunks ---")
    for i, d in enumerate(docs, 1):
        meta = d.metadata or {}
        print(
            f"  [{i}] score={meta.get('score')} rerank={meta.get('rerank_score')} "
            f"source={meta.get('source')} chunk={meta.get('chunk')} id={meta.get('id')}"
        )
        print(f"      meta keys: {sorted(k for k in meta.keys() if k not in {'text', 'page_content'})}")
        print(f"      preview: {_preview(d.page_content)}")

    sources = [str((d.metadata or {}).get("source") or "") for d in docs]
    about_heavy = sources.count("about_aif") >= 1 and not any(
        s in {"contact", "backend_contact"} for s in sources
    )
    if about_heavy and any(w in clean.lower() for w in ("kaha", "where", "address", "reach", "location")):
        print("*** WARNING: location/contact query retrieved ABOUT-heavy chunks ***")

    # Exact prompt that would be sent
    history = memory_service.history_as_chat(sid, limit=6)
    messages = build_rag_messages(context, clean, history, language=language.value)
    system_instruction, _contents = _to_gemini_contents(messages)
    user_content = messages[-1]["content"] if messages else ""
    print("--- Exact prompt (truncated) ---")
    print(f"SYSTEM ({len(system_instruction or '')} chars):\n{(system_instruction or '')[:500]}")
    print(f"USER ({len(user_content)} chars):\n{user_content[:900]}")
    print(f"Context in prompt? {'Room 9' in user_content or 'Nagpada' in user_content or '8291101312' in user_content or bool(context.strip())}")

    # Full chat path (includes Gemini + formatter + any post overrides)
    result = await AiService().chat(clean, session_id=sid)
    final = result.get("response") or ""
    meta = result.get("meta") or {}
    print("--- API path result ---")
    print(f"pipeline={meta.get('pipeline')} gemini_used={meta.get('gemini_used')} "
          f"fallback={meta.get('fallback')} chunks={meta.get('chunks')}")
    print(f"Raw-ish final ({len(final)} chars):\n{final[:600]}")
    print(f"Formatter only (same text): {format_user_response(final)[:200]!r}")

    return {
        "query": query,
        "language": language.value,
        "intent": route.intent.value,
        "reason": route.reason,
        "rewritten": rewritten.search_query,
        "filter": route.source_filter,
        "relevant": relevant,
        "sources": sources,
        "pipeline": meta.get("pipeline"),
        "gemini_used": meta.get("gemini_used"),
        "fallback": meta.get("fallback"),
        "response_preview": final[:300],
        "about_heavy_for_location": about_heavy,
    }


async def main() -> int:
    settings = get_settings()
    print("RAG ready:", settings.rag_ready)
    print("Index:", settings.pinecone_index_name, "ns:", settings.pinecone_namespace)
    if not settings.rag_ready:
        print("RAG not configured — abort")
        return 1

    rows: List[Dict[str, Any]] = []
    for q in QUERIES:
        try:
            rows.append(await audit_one(q))
        except Exception as exc:
            print(f"FAILED {q!r}: {type(exc).__name__}: {exc}")
            rows.append({"query": q, "error": str(type(exc).__name__)})

    print("\n" + "#" * 72)
    print("SUMMARY")
    print("#" * 72)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False)[:400])
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
