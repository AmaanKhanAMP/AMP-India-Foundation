"""Human conversation, source-of-truth, and gibberish coverage."""

from __future__ import annotations

import unittest

from app.services.focus_entity import extract_focus
from app.services.intent_router import Intent, route_intent
from app.services.language_service import Language
from app.services.prompt_service import DOMAIN_ONLY_RESPONSE, GIBBERISH_RESPONSE, t
from app.services.query_normalize import looks_gibberish
from app.services.query_rewrite import rewrite_query


class GibberishTests(unittest.TestCase):
    def test_samples(self):
        for msg in ("asdasd", "qwerty", "111111", "djdjdjd"):
            self.assertTrue(looks_gibberish(msg), msg)
            route = route_intent(msg)
            self.assertEqual(route.reason, "gibberish")
            self.assertIn("rephrase", (route.canned_response or "").lower())

    def test_real_questions_not_gibberish(self):
        for msg in ("aif ka number", "scholarship info", "where office", "what u guys do"):
            self.assertFalse(looks_gibberish(msg), msg)


class NaturalIntentTests(unittest.TestCase):
    def test_phone_hinglish(self):
        self.assertEqual(route_intent("aif ka number").intent, Intent.CONTACT)

    def test_kashmir_job_fair(self):
        route = route_intent("job fair kashmir wala")
        self.assertIn(route.intent, {Intent.EVENTS, Intent.PAST_EVENTS, Intent.UPCOMING_EVENTS})

    def test_what_you_do(self):
        self.assertEqual(route_intent("what u guys do").intent, Intent.AMP_KNOWLEDGE)

    def test_volunteer_hinglish(self):
        self.assertEqual(route_intent("volunteer kaise kare").intent, Intent.VOLUNTEERING)

    def test_medical_help(self):
        self.assertEqual(route_intent("medical help available").intent, Intent.MEDICAL)

    def test_unrelated_copy(self):
        self.assertIn("specialize", t(DOMAIN_ONLY_RESPONSE, Language.ENGLISH).lower())
        self.assertIn("not sure I understood", t(GIBBERISH_RESPONSE, Language.ENGLISH))


class FollowupEntityTests(unittest.TestCase):
    def test_extract_kupwara(self):
        focus = extract_focus("Tell me about Kupwara Job Fair")
        self.assertIsNotNone(focus)
        self.assertIn("kupwara", focus.lower())

    def test_rewrite_binds_it(self):
        rw = rewrite_query(
            "When was it conducted?",
            language=Language.ENGLISH,
            intent=Intent.EVENTS,
            session_topic="events",
            last_entity="kupwara job fair",
        )
        self.assertIn("kupwara", rw.search_query.lower())

    def test_session_followup_intent(self):
        route = route_intent(
            "When was it conducted?",
            has_session_topic=True,
            session_topic="events",
        )
        self.assertEqual(route.intent, Intent.EVENTS)


class SourceFilterTests(unittest.TestCase):
    def test_no_legacy_markdown(self):
        from app.services.intent_router import SOURCE_FILTER

        banned = {
            "employment",
            "about_aif",
            "programs",
            "faq",
            "events",
            "donations",
            "scholarships",
            "contact",
            "volunteer",
        }
        for intent, sources in SOURCE_FILTER.items():
            if not isinstance(sources, list):
                continue
            for name in banned:
                self.assertNotIn(name, sources, f"{intent.value} still lists {name}")


class LooksUnclearHelperTests(unittest.TestCase):
    def test_helper_exists_and_spares_real_questions(self):
        from app.services.ai_service import _looks_unclear

        self.assertFalse(_looks_unclear("Contact details of AIF"))
        self.assertFalse(_looks_unclear("Upcoming events"))
        self.assertTrue(_looks_unclear("?"))


if __name__ == "__main__":
    unittest.main()
