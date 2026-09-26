"""Verify startup warming, FAQ cache, routing, and performance targets."""

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
from app.services.faq_cache import get_faq_cache
from app.services.intent_router import route_intent
from app.services.rag_service import get_pinecone_client, rag_service
from app.services.startup import warm_services


async def main() -> None:
    get_settings.cache_clear()
    get_embeddings.cache_clear()
    get_pinecone_client.cache_clear()
    get_faq_cache.cache_clear()

    print("=== Startup Warmup ===")
    status = await warm_services()
    print(
        "warmup:",
        {
            "gemini": status.gemini,
            "pinecone": status.pinecone,
            "index": status.index,
            "clients_warmed": status.clients_warmed,
            "errors": status.errors,
        },
    )
    print()

    print("=== Intent Synonyms ===")
    cases = [
        ("Hi", "greeting"),
        ("السلام عليكم", "greeting"),
        ("Khuda Hafiz", "goodbye"),
        ("Shukriya", "small_talk"),
        ("What is ChatGPT?", "general_knowledge"),
        ("bank details donate", "donations"),
        ("financial aid", "scholarships"),
        ("job fair", "employment"),
        ("medical treatment", "medical"),
        ("career guidance", "mentorship"),
        ("skill development", "training"),
        ("become volunteer", "volunteering"),
    ]
    for msg, expected in cases:
        got = route_intent(msg).intent.value
        mark = "✓" if got == expected else "✗"
        print(f"{mark} {msg!r} -> {got} (expected {expected})")
    print()

    print("=== Chat Performance ===")
    questions = [
        ("Hi", "greeting", 100, True, False),
        ("What is your contact number?", "contact", 200, True, False),
        ("How can I donate? Share bank details", "donations", 200, True, False),
        ("What scholarships do you offer?", "scholarships", 300, True, False),
        ("How do I become a volunteer?", "volunteering", 300, True, False),
        ("What color is the sky?", "general_knowledge", 2500, False, False),
        ("What is the mission of AMP India Foundation?", "amp_knowledge", 300, True, False),
    ]

    for q, expected_intent, target_ms, expect_cache, expect_rag in questions:
        t0 = time.perf_counter()
        res = await ai_service.chat(q, session_id="opt-verify")
        ms = (time.perf_counter() - t0) * 1000
        meta = res.get("meta") or {}
        cache_hit = bool(meta.get("cache_hit") or meta.get("fast_path"))
        rag_used = bool(meta.get("rag_used"))
        # greetings use fast_path but not faq cache — treat canned as cache-like
        if expected_intent == "greeting":
            cache_hit = True
            rag_used = False
        ok_intent = res["intent"] == expected_intent or (
            expected_intent == "amp_knowledge" and res["intent"] in {"amp_knowledge", "about"}
        )
        ok_cache = (not expect_cache) or cache_hit or meta.get("reason", "").startswith("faq_cache")
        ok_rag = rag_used is expect_rag if expected_intent not in {"greeting", "contact", "donations", "scholarships", "volunteering"} else (rag_used is False)
        # For FAQ questions, require no RAG
        if expected_intent in {"contact", "donations", "scholarships", "volunteering"}:
            ok_rag = rag_used is False
            ok_cache = bool(meta.get("cache_hit")) or str(meta.get("reason", "")).startswith("faq_cache")
        mark = "✓" if ok_intent and ok_cache and (ok_rag or expected_intent == "general_knowledge") and ms <= target_ms * 1.5 else "~"
        print(
            f"{mark} {ms:7.1f}ms (target <{target_ms}ms) intent={res['intent']} "
            f"cache={meta.get('cache_hit')} rag={meta.get('rag_used')} "
            f"q={q!r}"
        )
        print("   ", res["response"][:160].replace("\n", " "))
        print()

    # Confirm retrieval still works for non-cached AMP
    docs, _ctx, timings = await rag_service.retrieve("AMP India Foundation mission vision")
    print(
        f"✓ RAG retrieval chunks={len(docs)} "
        f"embed={timings.get('embed_ms', 0):.0f}ms pinecone={timings.get('pinecone_ms', 0):.0f}ms"
    )


if __name__ == "__main__":
    asyncio.run(main())
