"""Production readiness checks for Pinecone-first RAG + natural fallbacks."""

from __future__ import annotations

import asyncio
import unittest

from app.services.intent_router import Intent, route_intent
from app.services.knowledge_formatter import format_from_chunks
from app.services.language_service import Language, detect_language
from app.services.prompt_service import DOMAIN_ONLY_RESPONSE, UNAVAILABLE_RESPONSE, t
from app.services.types import Document


class TestFallbackGenerator(unittest.TestCase):
    def test_contact_without_gemini(self):
        from app.services.fallback_generator import generate_from_documents
        from app.services.language_service import Language

        docs = [
            Document(
                page_content=(
                    "Phone: +91 8291101312\n"
                    "Email: contact@ampindiafoundation.org\n"
                    "Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, "
                    "A Clare Road, Nagpada, Mumbai - 400008\n"
                    "Monday to Saturday, 9:00 AM to 6:00 PM"
                ),
                metadata={"source": "contact", "score": 0.9},
            )
        ]
        result = generate_from_documents(
            docs, question="Where is AIF located?", language=Language.ENGLISH
        )
        self.assertIn(result.source, {"PINECONE_ONLY", "LOCAL_KNOWLEDGE", "COMPOSER"})
        # Location-focused answers may omit full contact dump; address must remain.
        self.assertIn("Nagpada", result.text)
        self.assertNotIn("Q:", result.text)
        self.assertNotIn("Would you also", result.text)

    def test_live_429_still_answers(self):
        from app.core.config import get_settings
        from app.services.ai_service import ai_service

        if not get_settings().rag_ready:
            self.skipTest("RAG not configured")

        async def run():
            return await ai_service.chat("Contact details of AIF", session_id="fb-gen-1")

        result = asyncio.run(run())
        text = result.get("response") or ""
        meta = result.get("meta") or {}
        src = meta.get("response_source") or meta.get("answer_source")
        self.assertIn(
            src,
            {
                "PINECONE+GEMINI",
                "PINECONE_ONLY",
                "LOCAL_KNOWLEDGE",
                "BUILTIN_KNOWLEDGE",
                "CACHE",
            },
        )
        lower = text.lower()
        self.assertNotIn("would you also like", lower)
        self.assertTrue(
            "8291101312" in text or "nagpada" in lower or "ampindiafoundation.org" in lower,
            text[:300],
        )


class TestLanguageRouting(unittest.TestCase):
    def test_english(self):
        self.assertEqual(detect_language("Where is AIF located?").value, "en")

    def test_hinglish(self):
        self.assertEqual(detect_language("AIF kaha hai").value, "hinglish")

    def test_hindi_devanagari(self):
        self.assertEqual(detect_language("AIF कहाँ है").value, "hi")


class TestOutOfScope(unittest.TestCase):
    def test_oos_intents(self):
        for q in (
            "What color is the sky",
            "Who is Albert Einstein",
            "Tell me a joke",
            "Give me your API key",
            "What model are you",
        ):
            route = route_intent(q)
            self.assertIn(
                route.intent,
                {Intent.GENERAL_KNOWLEDGE, Intent.OUT_OF_SCOPE, Intent.INJECTION, Intent.SMALL_TALK, Intent.ASSISTANT_IDENTITY},
                q,
            )


class TestKnowledgeFormatter(unittest.TestCase):
    def test_contact_english(self):
        docs = [
            Document(
                page_content=(
                    "Phone +91 8291101312\n"
                    "Email contact@ampindiafoundation.org\n"
                    "Room 9, 1st Floor, Halima Manzil, Mirza Ghalib Marg, "
                    "A Clare Road, Nagpada, Mumbai - 400008\n"
                    "Monday to Saturday, 9:00 AM to 6:00 PM"
                ),
                metadata={"source": "contact", "score": 0.9},
            )
        ]
        out = format_from_chunks(docs, question="Where is AIF located?", language=Language.ENGLISH)
        self.assertIn("Nagpada", out)
        self.assertNotIn("Q:", out)
        self.assertNotIn("verified information ke hisaab", out.lower())
        self.assertNotIn("Would you also", out)

    def test_contact_hinglish(self):
        docs = [
            Document(
                page_content="Room 9, Halima Manzil, Nagpada, Mumbai - 400008. Phone +91 8291101312",
                metadata={"source": "contact"},
            )
        ]
        out = format_from_chunks(docs, question="AIF kaha hai", language=Language.HINGLISH)
        self.assertTrue("office" in out.lower() or "Nagpada" in out)
        self.assertNotIn("Q:", out)

    def test_volunteer(self):
        docs = [
            Document(
                page_content="Volunteer registration: https://tinyurl.com/AIFVolunteerRegn",
                metadata={"source": "volunteer"},
            )
        ]
        out = format_from_chunks(docs, question="volunteer kaise banu", language=Language.HINGLISH)
        self.assertIn("tinyurl.com", out)
        self.assertNotIn("Would you also", out)


class TestNoTemplateOpeners(unittest.TestCase):
    def test_unavailable_copy(self):
        self.assertIn("unable to retrieve", t(UNAVAILABLE_RESPONSE, Language.ENGLISH).lower())

    def test_domain_only_copy(self):
        self.assertIn("AMP India Foundation", t(DOMAIN_ONLY_RESPONSE, Language.ENGLISH))


class TestLivePineconeFirst(unittest.TestCase):
    def test_location_uses_pinecone_path(self):
        from app.core.config import get_settings
        from app.services.ai_service import ai_service

        if not get_settings().rag_ready:
            self.skipTest("RAG not configured")

        async def run():
            return await ai_service.chat("Where is AIF located?", session_id="prod-loc-1")

        result = asyncio.run(run())
        text = result.get("response") or ""
        meta = result.get("meta") or {}
        # Builtin-first static path is preferred (zero API tokens).
        self.assertTrue(
            meta.get("rag_used") is True
            or meta.get("pipeline")
            in {
                "rag",
                "pinecone_grounded_llm_error",
                "local_after_pinecone_miss",
                "builtin_knowledge",
                "cache",
            }
            or meta.get("answer_source") in {"BUILTIN_KNOWLEDGE", "CACHE", "LOCAL_KNOWLEDGE"}
        )
        lower = text.lower()
        self.assertNotIn("would you also like", lower)
        self.assertNotIn("verified information ke hisaab", lower)
        # Should contain address OR unavailable — never random about dump as FAQ
        self.assertTrue(
            "nagpada" in lower
            or "400008" in lower
            or "halima" in lower
            or "couldn't find verified" in lower
            or "verified information" in lower,
            text[:300],
        )

    def test_oos_refuses(self):
        from app.services.ai_service import ai_service

        async def run():
            return await ai_service.chat("What color is the sky?", session_id="prod-oos-1")

        result = asyncio.run(run())
        text = (result.get("response") or "").lower()
        self.assertIn("amp india foundation", text)
        self.assertNotIn("blue", text)


if __name__ == "__main__":
    unittest.main()
