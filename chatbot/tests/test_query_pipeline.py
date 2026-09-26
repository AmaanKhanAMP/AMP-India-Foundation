"""Unit tests for intent routing, query rewrite, and FAQ multilingual coverage."""

from __future__ import annotations

import unittest

from app.services.faq_cache import lookup_faq
from app.services.intent_router import Intent, SOURCE_FILTER, route_intent
from app.services.language_service import Language, detect_language
from app.services.query_rewrite import rewrite_query


class IntentRouterTests(unittest.TestCase):
    def test_about_multilingual(self):
        cases = [
            "What is AMP India Foundation?",
            "What is AIF?",
            "AIF kya hai?",
            "AIF ke bare me batao",
            "aif?",
            "tell me about it",
        ]
        for msg in cases:
            with self.subTest(msg=msg):
                route = route_intent(msg)
                self.assertEqual(route.intent, Intent.AMP_KNOWLEDGE, msg)

    def test_employment_not_volunteer(self):
        for msg in (
            "What jobs do you provide?",
            "Mujhe job chahiye",
            "Job ke liye kya karna padega?",
            "How can I participate in job fairs?",
            "job?",
        ):
            with self.subTest(msg=msg):
                route = route_intent(msg)
                self.assertEqual(route.intent, Intent.EMPLOYMENT, msg)
                filt = route.source_filter
                if isinstance(filt, list):
                    self.assertIn("website_projects", filt)
                else:
                    self.assertEqual(filt, "website_projects")

    def test_contact_hours_address(self):
        for msg in (
            "Where is your office located?",
            "AIF ka address kya hai?",
            "kitne baje open rehta hai",
            "Office kitne baje khulta hai?",
            "address plz",
            "Email?",
        ):
            with self.subTest(msg=msg):
                route = route_intent(msg)
                self.assertEqual(route.intent, Intent.CONTACT, msg)

    def test_trust(self):
        for msg in ("Are you trustworthy?", "Is AIF genuine?", "AMP genuine hai kya?"):
            with self.subTest(msg=msg):
                self.assertEqual(route_intent(msg).intent, Intent.AMP_KNOWLEDGE)

    def test_events(self):
        for msg in ("Upcoming events?", "Events kab hote hai?", "Job fair dates?"):
            with self.subTest(msg=msg):
                intent = route_intent(msg).intent
                self.assertIn(
                    intent,
                    {
                        Intent.EVENTS,
                        Intent.UPCOMING_EVENTS,
                        Intent.PAST_EVENTS,
                        Intent.FEATURED_EVENT,
                        Intent.EMPLOYMENT,
                    },
                    msg,
                )

    def test_employment_source_filter(self):
        filt = SOURCE_FILTER[Intent.EMPLOYMENT]
        if isinstance(filt, list):
            self.assertIn("website_projects", filt)
            self.assertNotEqual(filt, ["events"])
        else:
            self.assertEqual(filt, "website_projects")
            self.assertNotEqual(filt, "events")


class QueryRewriteTests(unittest.TestCase):
    def test_hinglish_about(self):
        rw = rewrite_query("AIF kya hai", language=Language.HINGLISH, intent=Intent.AMP_KNOWLEDGE)
        self.assertIn("AMP India Foundation", rw.search_query)
        self.assertIn("mission", rw.search_query.lower())

    def test_hours(self):
        rw = rewrite_query("kitne baje open rehta hai", language=Language.HINGLISH)
        self.assertIn("working hours", rw.search_query.lower())

    def test_jobs(self):
        rw = rewrite_query("what jobs do they provide", language=Language.ENGLISH, intent=Intent.EMPLOYMENT)
        self.assertTrue(
            "employment" in rw.search_query.lower() or "job" in rw.search_query.lower()
        )

    def test_pronoun_followup(self):
        rw = rewrite_query(
            "tell me about it",
            language=Language.ENGLISH,
            session_topic="amp_knowledge",
        )
        self.assertIn("AMP India Foundation", rw.search_query)


class FaqCacheTests(unittest.TestCase):
    def test_aif_kya_hai(self):
        hit = lookup_faq("AIF kya hai?", intent=Intent.AMP_KNOWLEDGE, language=Language.HINGLISH)
        self.assertIsNotNone(hit)
        self.assertIn("AMP", hit.answer)

    def test_kitne_baje(self):
        hit = lookup_faq("kitne baje open rehta hai", intent=Intent.CONTACT, language=Language.HINGLISH)
        self.assertIsNotNone(hit)
        self.assertTrue("9" in hit.answer or "9:00" in hit.answer)

    def test_job_chahiye(self):
        hit = lookup_faq("Mujhe job chahiye", intent=Intent.EMPLOYMENT, language=Language.HINGLISH)
        self.assertIsNotNone(hit)
        self.assertTrue("job" in hit.answer.lower() or "employment" in hit.answer.lower())

    def test_trustworthy(self):
        hit = lookup_faq("Is AMP India Foundation trustworthy?", intent=Intent.AMP_KNOWLEDGE)
        self.assertIsNotNone(hit)
        self.assertIn("registered", hit.answer.lower())


class LanguageDetectTests(unittest.TestCase):
    def test_hinglish(self):
        lang = detect_language("AIF ke bare me batao")
        self.assertIn(lang, {Language.HINGLISH, Language.ENGLISH, Language.HINDI})


if __name__ == "__main__":
    unittest.main()
