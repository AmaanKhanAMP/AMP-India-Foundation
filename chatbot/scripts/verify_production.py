"""End-to-end production readiness verification."""

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
from app.services.language_service import detect_language
from app.services.memory_service import memory_service
from app.services.rag_service import get_pinecone_client


async def main() -> None:
    get_settings.cache_clear()
    get_embeddings.cache_clear()
    get_pinecone_client.cache_clear()
    get_faq_cache.cache_clear()

    print("=== Intent routing ===")
    cases = [
        ("Can I participate in job fair?", "employment"),
        ("Volunteer kaise bane?", "volunteering"),
        ("Job fair kab hai?", "employment"),
        ("Donation kaise kare?", "donations"),
        ("Mujhe scholarship ke liye apply karna hai.", "scholarships"),
        ("Past events batao", "events"),
        ("What is ChatGPT?", "general_knowledge"),
        ("Salam", "greeting"),
        ("Adaab", "greeting"),
    ]
    for msg, expected in cases:
        got = route_intent(msg).intent.value
        mark = "✓" if got == expected else "✗"
        print(f"{mark} {msg!r} -> {got}")

    print("\n=== Language detection ===")
    for msg, expected in [
        ("How can I volunteer?", "en"),
        ("मुझे नौकरी मेले की जानकारी चाहिए।", "hi"),
        ("Mujhe scholarship ke liye apply karna hai.", "hinglish"),
        ("Job fair kab hai?", "hinglish"),
    ]:
        got = detect_language(msg).value
        mark = "✓" if got == expected else "✗"
        print(f"{mark} {msg!r} -> {got}")

    print("\n=== Chat responses ===")
    checks = [
        ("Can I participate in job fair?", "employment", True, "Job Fair"),
        ("Volunteer kaise bane?", "volunteering", True, "tinyurl"),
        ("What is your contact number?", "contact", True, "+91"),
        ("Donation kaise kare?", "donations", True, "3114476665"),
        ("What scholarships do you offer?", "scholarships", True, "Scholarship"),
        ("What is the mission of AMP?", "amp_knowledge", True, "Mission"),
        ("Who is the head of AIF?", "amp_knowledge", True, "leadership"),
        ("Salam", "greeting", False, "Wa Alaikum"),
        ("Hello", "greeting", False, "Welcome"),
        ("Why is the sky blue?", "general_knowledge", False, "blue"),
    ]

    for q, intent, expect_cache, needle in checks:
        t0 = time.perf_counter()
        res = await ai_service.chat(q, session_id=f"prod-{intent}")
        ms = (time.perf_counter() - t0) * 1000
        meta = res.get("meta") or {}
        ok = res["intent"] == intent and needle.lower() in res["response"].lower()
        if expect_cache:
            ok = ok and bool(meta.get("cache_hit") or meta.get("fast_path"))
            ok = ok and not meta.get("rag_used")
        mark = "✓" if ok and ms < 500 else ("~" if ok else "✗")
        print(
            f"{mark} {ms:7.1f}ms intent={res['intent']} lang={meta.get('language')} "
            f"cache={meta.get('cache_hit')} rag={meta.get('rag_used')} | {q}"
        )
        print("   ", res["response"][:140].replace("\n", " "))

    print("\n=== Follow-up memory ===")
    sid = "prod-followup"
    memory_service.clear(sid)
    await ai_service.chat("Tell me about scholarships", session_id=sid)
    res = await ai_service.chat("What is the last date?", session_id=sid)
    ok = res["intent"] == "scholarships"
    print(("✓" if ok else "✗"), "last date follow-up ->", res["intent"], res["meta"].get("reason"))

    print("\n=== Hindi / Hinglish sample ===")
    for q in (
        "मुझे नौकरी मेले की जानकारी चाहिए।",
        "Mujhe scholarship ke liye apply karna hai.",
        "Volunteer kaise bane?",
    ):
        res = await ai_service.chat(q, session_id="prod-lang")
        print(f"- {q}")
        print(" ", res["response"][:180].replace("\n", " | "))
        print("  lang=", res["meta"].get("language"), "intent=", res["intent"])


if __name__ == "__main__":
    asyncio.run(main())
