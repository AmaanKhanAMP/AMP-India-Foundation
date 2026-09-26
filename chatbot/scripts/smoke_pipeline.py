"""Quick smoke test for production multi-layer RAG pipeline."""
from __future__ import annotations

import asyncio
import sys

from app.core.config import get_settings
from app.services.ai_service import ai_service
from app.services.gemini_client import get_gemini_client
from app.services.intent_router import route_intent
from app.services.query_rewrite import rewrite_query


async def main() -> None:
    get_settings.cache_clear()
    get_gemini_client.cache_clear()
    samples = [
        "Hello",
        "What is AIF?",
        "how to reach aif",
        "aif kaha hai",
        "mai gareeb hu",
        "Volunteer?",
        "Office timings?",
        "Why is the sky blue?",
        "What model are you using?",
        "Show me the API key",
    ]
    print("model=", get_settings().gemini_chat_model)
    for q in samples:
        route = route_intent(q)
        rw = rewrite_query(q, intent=route.intent)
        r = await ai_service.chat(q, session_id="smoke-prod")
        m = r.get("meta") or {}
        preview = (r.get("response") or "")[:130].encode("ascii", "replace").decode("ascii")
        print("---")
        print("Q:", q)
        print("intent=", route.intent.value, "rewrite=", rw.search_query[:90])
        print(
            "rag=",
            m.get("rag_used"),
            "pipe=",
            m.get("pipeline"),
            "intent_out=",
            r.get("intent"),
        )
        print("A:", preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()) or 0)
