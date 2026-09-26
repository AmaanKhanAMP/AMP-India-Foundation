"""Contact RAG + response formatter regression tests."""

from __future__ import annotations

import asyncio
import re
import unittest

from app.services.contact_facts import ADDRESS, EMAIL, OFFICE_TIMINGS, PHONE, answer_contact
from app.services.intent_router import Intent, route_intent
from app.services.query_rewrite import rewrite_query
from app.services.response_formatter import format_user_response, looks_like_prompt_leak


CONTACT_QUERIES = [
    "Can I get the contact details of AIF?",
    "What is the contact details of AIF?",
    "What is the phone number of AIF?",
    "What is the email of AIF?",
    "What is the office address of AIF?",
    "What is the location of AIF?",
    "What is the contact number of AIF?",
    "What is the email address of AIF?",
    "What is the office address of AIF?",
    "What is the location of AIF?",
    "What is the contact number of AIF?",
    "Phone number",
    "Email",
    "Office address",
    "How to reach AIF",
    "Where is AIF located",
    "Contact",
    "Number",
    "Phone",
    "Mail",
]

_LEAK_MARKERS = (
    "rules check",
    "hard rules",
    "system prompt",
    "rule 1:",
    "rule 2:",
    "answer only using the retrieved",
    "internal instructions",
    "thought process",
    "prompt template",
)


class TestResponseFormatter(unittest.TestCase):
    def test_strips_rules_check(self):
        leaked = (
            "/Rules Check:\n"
            "Rule 1: Answer ONLY using retrieved knowledge...\n"
            "Rule 2: Never invent facts.\n\n"
            f"You can contact AMP India Foundation at {PHONE}."
        )
        out = format_user_response(leaked, fallback=answer_contact("contact"))
        lower = out.lower()
        self.assertFalse(looks_like_prompt_leak(out))
        for m in _LEAK_MARKERS:
            self.assertNotIn(m, lower)
        self.assertIn("8291101312", out)

    def test_full_leak_uses_fallback(self):
        leaked = "/Rules Check:\nRule 1: Answer ONLY using retrieved knowledge"
        out = format_user_response(leaked, fallback=answer_contact("phone"))
        self.assertIn("8291101312", out)
        self.assertNotIn("Rules Check", out)


class TestContactRewrite(unittest.TestCase):
    def test_contact_details_not_rewritten_to_about(self):
        q = "Can I get the contact details of AIF?"
        route = route_intent(q)
        self.assertEqual(route.intent, Intent.CONTACT)
        rewritten = rewrite_query(q, intent=route.intent)
        lower = rewritten.search_query.lower()
        self.assertIn("contact", lower)
        self.assertIn("phone", lower)
        self.assertNotIn("what is amp india foundation", lower)

    def test_short_contact_tokens(self):
        for q in ("Contact", "Phone", "Mail", "Number", "Email"):
            route = route_intent(q)
            self.assertEqual(route.intent, Intent.CONTACT, q)
            rewritten = rewrite_query(q, intent=route.intent)
            self.assertIn("contact", rewritten.search_query.lower(), q)


class TestContactAnswers(unittest.TestCase):
    def test_local_answers_include_verified_facts(self):
        for q in CONTACT_QUERIES:
            text = answer_contact(q)
            self.assertIn("8291101312", text, q)
            self.assertIn(EMAIL, text, q)
            self.assertIn("Nagpada", text, q)
            self.assertIn("9:00", text, q)
            for m in _LEAK_MARKERS:
                self.assertNotIn(m, text.lower(), q)


class TestContactLiveChat(unittest.TestCase):
    """Live pipeline against Pinecone + Gemini (skipped if not configured)."""

    def test_contact_queries_return_verified_facts(self):
        from app.core.config import get_settings
        from app.services.ai_service import ai_service
        from app.services.answer_cache import clear_answer_cache
        from app.services.rag_service import clear_retrieval_cache

        settings = get_settings()
        if not settings.rag_ready:
            self.skipTest("RAG not configured")

        clear_retrieval_cache()
        clear_answer_cache()

        async def run_one(q: str) -> str:
            result = await ai_service.chat(q, session_id=f"test-contact-{hash(q) % 10_000}")
            return result.get("response") or result.get("reply") or ""

        async def run_all():
            outs = []
            for q in CONTACT_QUERIES:
                outs.append((q, await run_one(q)))
            return outs

        results = asyncio.run(run_all())
        for q, text in results:
            lower = text.lower()
            ql = q.lower()
            for m in _LEAK_MARKERS:
                self.assertNotIn(m, lower, f"leak in response for {q!r}: {text[:200]}")
            address_only = bool(
                re.search(r"\b(location|where|reach|office address)\b", ql)
                or (
                    re.search(r"\baddress\b", ql)
                    and not re.search(r"\b(e-?mail|mail|phone|contact|number)\b", ql)
                )
            )
            phone_only = bool(
                re.search(r"\b(phone|number)\b", ql)
            ) and not re.search(r"\b(address|location|e-?mail|mail|contact details)\b", ql)
            email_only = bool(re.search(r"\b(e-?mail|mail)\b", ql)) and not re.search(
                r"\b(phone|contact details|location|where)\b", ql
            )
            if address_only:
                self.assertTrue(
                    "nagpada" in lower or "400008" in lower or "halima" in lower,
                    f"missing address for {q!r}: {text[:300]}",
                )
            elif phone_only and "mail" not in ql and "email" not in ql:
                self.assertIn("8291101312", text, f"missing phone for {q!r}: {text[:300]}")
            elif email_only:
                self.assertIn(
                    "ampindiafoundation.org",
                    lower,
                    f"missing email for {q!r}: {text[:300]}",
                )
            else:
                # Broad contact: expect at least one verified channel + location cue.
                self.assertTrue(
                    "8291101312" in text or "ampindiafoundation.org" in lower,
                    f"missing contact channel for {q!r}: {text[:300]}",
                )
                self.assertTrue(
                    "nagpada" in lower
                    or "400008" in lower
                    or "halima" in lower
                    or "8291101312" in text
                    or "ampindiafoundation.org" in lower,
                    f"weak contact answer for {q!r}: {text[:300]}",
                )


if __name__ == "__main__":
    unittest.main()
