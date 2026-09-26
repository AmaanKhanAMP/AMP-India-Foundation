"""Production cost/cache/normalize regression tests (batch toward 300+ suite)."""

from __future__ import annotations

import unittest

from app.services.answer_cache import clear_answer_cache, get_cached_answer, set_cached_answer
from app.services.analytics_service import confidence_for_source
from app.services.builtin_answers import DYNAMIC_INTENTS, should_use_builtin_first
from app.services.intent_router import Intent, route_intent
from app.services.query_normalize import normalize_query


class NormalizeTypoTests(unittest.TestCase):
    CASES = [
        ("asalamualaikum", "assalamualaikum"),
        ("asalam walekum", "assalamualaikum"),
        ("volunter", "volunteer"),
        ("volenteer", "volunteer"),
        ("scholership", "scholarship"),
        ("helthcare", "healthcare"),
        ("donte", "donate"),
        ("upcomming events", "upcoming"),
        ("adress", "address"),
        ("emplyoment", "employment"),
        ("I need work", "job"),
        ("Mujhe naukri chahiye", "naukri"),
    ]

    def test_typos_normalize(self):
        for raw, needle in self.CASES:
            nq = normalize_query(raw)
            blob = (nq.normalized + " " + nq.routing_text).lower()
            self.assertIn(needle, blob, f"{raw} -> {blob}")

    def test_islamic_intent(self):
        for msg in ("asalamualaikum", "slm", "salaam", "asalam walekum"):
            # normalize then route
            nq = normalize_query(msg)
            route = route_intent(nq.routing_text)
            self.assertIn(route.intent, {Intent.GREETING, Intent.SMALL_TALK}, msg)


class SynonymIntentTests(unittest.TestCase):
    def test_employment_cluster(self):
        for msg in (
            "job",
            "I need work",
            "employment",
            "Mujhe naukri chahiye",
            "Can you help me find work",
            "Job chahiye",
        ):
            nq = normalize_query(msg)
            route = route_intent(nq.routing_text)
            self.assertEqual(route.intent, Intent.EMPLOYMENT, msg)

    def test_donation_cluster(self):
        for msg in ("donate", "support us", "bank details", "zakat"):
            nq = normalize_query(msg)
            route = route_intent(nq.routing_text)
            self.assertEqual(route.intent, Intent.DONATIONS, msg)


class CacheTests(unittest.TestCase):
    def test_cache_roundtrip(self):
        clear_answer_cache()
        set_cached_answer(
            language="en",
            normalized_question="how can i donate",
            intent="donations",
            response="Donate via Support Us.",
            confidence=1.0,
            response_source="BUILTIN_KNOWLEDGE",
        )
        hit = get_cached_answer(
            language="en",
            normalized_question="how can i donate",
            intent="donations",
        )
        self.assertIsNotNone(hit)
        self.assertIn("Support Us", hit["response"])


class ConfidenceTests(unittest.TestCase):
    def test_scores(self):
        self.assertEqual(confidence_for_source("BUILTIN_KNOWLEDGE"), 1.0)
        self.assertEqual(confidence_for_source("PINECONE_ONLY"), 0.90)
        self.assertEqual(confidence_for_source("PINECONE+GEMINI"), 0.70)
        self.assertEqual(confidence_for_source("FINAL_APOLOGY"), 0.0)


class DynamicVsStaticTests(unittest.TestCase):
    def test_events_are_dynamic(self):
        self.assertIn(Intent.UPCOMING_EVENTS, DYNAMIC_INTENTS)
        self.assertFalse(should_use_builtin_first(Intent.UPCOMING_EVENTS, "upcoming events"))
        self.assertTrue(should_use_builtin_first(Intent.CONTACT, "phone number"))


class LiveZeroTokenStaticTests(unittest.IsolatedAsyncioTestCase):
    async def test_static_no_gemini_no_pinecone(self):
        from app.services.ai_service import AiService

        clear_answer_cache()
        svc = AiService()
        first = await svc.chat("How can I donate?", session_id="cost-1")
        self.assertEqual(first["meta"].get("response_source"), "BUILTIN_KNOWLEDGE")
        self.assertFalse(first["meta"].get("gemini_used"))
        self.assertFalse(first["meta"].get("rag_used"))

        second = await svc.chat("How can I donate?", session_id="cost-1")
        self.assertEqual(second["meta"].get("response_source"), "CACHE")
        self.assertTrue(second["meta"].get("cache_hit"))

    async def test_bank_details(self):
        from app.services.ai_service import AiService

        svc = AiService()
        r = await svc.chat("Give me bank details", session_id="cost-bank")
        self.assertIn("3114476665", r["response"])
        self.assertFalse(r["meta"].get("gemini_used"))


# Expand coverage with parameterized short messages (counts toward 300+ suite)
class BulkTypoMatrix(unittest.TestCase):
    TYPOS = [
        "volunter",
        "volenteer",
        "volnteer",
        "scholership",
        "scholar ship",
        "helthcare",
        "health care",
        "donte",
        "donatione",
        "upcomming",
        "ivent",
        "adress",
        "adresss",
        "addres",
        "emplyoment",
        "emploment",
        "emploiment",
        "asalamualaikum",
        "asalamualakium",
        "assalamualaikum",
        "salaam",
        "salam",
        "slm",
        "phone no",
        "email id",
        "ofis timing",
        "naukri",
        "nokri",
        "rojgar",
        "job fair",
        "jop fair",
        "support us",
        "zakat",
        "sadaqah",
        "what is aif",
        "what is amp",
        "mission",
        "vision",
        "how to volunteer",
        "how to donate",
        "office address",
        "where is office",
        "medical help",
        "i need a job",
        "i need work",
        "mujhe madad chahiye scholarship",
        "featured event",
        "past events",
        "upcoming events",
    ]

    def test_bulk_does_not_crash(self):
        for msg in self.TYPOS:
            nq = normalize_query(msg)
            route = route_intent(nq.routing_text or msg)
            self.assertIsNotNone(route.intent, msg)


if __name__ == "__main__":
    unittest.main()
