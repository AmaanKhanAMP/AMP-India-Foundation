"""UX / builtin / response composer regression tests."""

from __future__ import annotations

import asyncio
import unittest

from app.services.ai_service import AiService
from app.services.builtin_answers import (
    answer_builtin,
    should_use_builtin_first,
    wants_bank_details,
)
from app.services.intent_router import Intent, route_intent
from app.services.language_service import Language
from app.services.response_composer import clean_response, compose_final
from app.services.types import Document


class BuiltinFirstTests(unittest.TestCase):
    def test_bank_details_explicit(self):
        text = answer_builtin("Give me bank details", intent=Intent.DONATIONS, language=Language.ENGLISH)
        self.assertIsNotNone(text)
        self.assertIn("3114476665", text)
        self.assertIn("KKBK0001348", text)
        self.assertIn("Kotak", text)

    def test_donate_without_bank(self):
        text = answer_builtin("How can I donate?", intent=Intent.DONATIONS, language=Language.ENGLISH)
        self.assertIsNotNone(text)
        self.assertIn("Support Us", text)
        self.assertNotIn("3114476665", text)

    def test_employment_natural(self):
        text = answer_builtin("How can I get a job?", intent=Intent.EMPLOYMENT, language=Language.ENGLISH)
        self.assertIsNotNone(text)
        self.assertIn("job fairs", text.lower())
        self.assertNotIn("What jobs do you provide", text)

    def test_healthcare_natural(self):
        text = answer_builtin("What is healthcare?", intent=Intent.MEDICAL, language=Language.ENGLISH)
        self.assertIsNotNone(text)
        self.assertIn("medical camps", text.lower())
        self.assertNotIn("##", text)
        self.assertNotIn("Projects & Programs", text)

    def test_about_short(self):
        text = answer_builtin("What is AIF?", intent=Intent.AMP_KNOWLEDGE, language=Language.ENGLISH)
        self.assertIsNotNone(text)
        self.assertLess(len(text.split()), 120)

    def test_static_skips_pinecone_flag(self):
        self.assertTrue(should_use_builtin_first(Intent.CONTACT, "phone number"))
        self.assertFalse(should_use_builtin_first(Intent.EMPLOYMENT, "I need work"))
        self.assertFalse(should_use_builtin_first(Intent.UPCOMING_EVENTS, "upcoming events"))


class ComposerCleanerTests(unittest.TestCase):
    def test_strips_headings_and_faq(self):
        raw = (
            "# Projects & Programs — AMP India Foundation\n\n"
            "Q: What jobs do you provide?\n"
            "A: AMP does not run a portal.\n\n"
            "We help with job fairs and placement."
        )
        cleaned = clean_response(raw)
        self.assertNotIn("Projects & Programs", cleaned)
        self.assertNotIn("What jobs do you provide", cleaned)
        self.assertNotIn("Q:", cleaned)

    def test_compose_rejects_raw_dump(self):
        docs = [
            Document(
                page_content="## Projects & Programs\nQ: What jobs do you provide?\nA: None permanently.",
                metadata={"source": "faq", "score": 0.9},
            )
        ]
        out = compose_final(
            question="How can I get a job?",
            draft=docs[0].page_content,
            intent=Intent.EMPLOYMENT,
            language=Language.ENGLISH,
            docs=docs,
        )
        self.assertNotIn("What jobs do you provide", out)
        self.assertIn("Employment", out)

    def test_strips_source_names(self):
        cleaned = clean_response("See cms_events and backend_projects for more. Job fairs help youth.")
        self.assertNotIn("cms_events", cleaned)
        self.assertNotIn("backend_projects", cleaned)


class IntentSynonymTests(unittest.TestCase):
    def test_work_synonyms(self):
        for msg in ("job", "I need work", "employment", "career help"):
            self.assertEqual(route_intent(msg).intent, Intent.EMPLOYMENT, msg)

    def test_donate_synonyms(self):
        for msg in ("donate", "support us", "bank details", "IFSC code"):
            self.assertEqual(route_intent(msg).intent, Intent.DONATIONS, msg)

    def test_wants_bank(self):
        self.assertTrue(wants_bank_details("Give me bank details"))
        self.assertTrue(wants_bank_details("What is the IFSC?"))


class LiveBuiltinChatTests(unittest.IsolatedAsyncioTestCase):
    async def test_job_and_bank_via_chat(self):
        svc = AiService()
        job = await svc.chat("How can I get a job?", session_id="ux-job")
        self.assertEqual(job["intent"], "employment")
        self.assertNotIn("What jobs do you provide", job["response"])
        self.assertIn("job fair", job["response"].lower())
        self.assertNotEqual(job["meta"].get("response_source"), "BUILTIN_KNOWLEDGE")

        bank = await svc.chat("Give me bank details", session_id="ux-bank")
        self.assertEqual(bank["intent"], "donations")
        self.assertIn("3114476665", bank["response"])
        self.assertIn("KKBK0001348", bank["response"])


if __name__ == "__main__":
    unittest.main()
