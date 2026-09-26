"""Intent, gibberish, OOD, donation follow-ups, and form clarification."""

from __future__ import annotations

import unittest

from app.services.builtin_answers import answer_builtin
from app.services.intent_router import Intent, SOURCE_FILTER, route_intent
from app.services.language_service import Language
from app.services.prompt_service import DOMAIN_ONLY_RESPONSE, FORM_CLARIFY_RESPONSE, t
from app.services.query_normalize import looks_gibberish
from app.services.query_rewrite import rewrite_query


class EducationEmpowermentRoutingTests(unittest.TestCase):
    def test_education_not_events(self):
        for q in (
            "Tell me about education",
            "education",
            "Education programs?",
            "education project",
        ):
            route = route_intent(q)
            self.assertEqual(route.intent, Intent.EDUCATION, q)
            sources = list(route.source_filter or SOURCE_FILTER[Intent.EDUCATION])
            self.assertNotIn("cms_events", sources)
            self.assertNotIn("cms_gallery", sources)
            self.assertIn("website_projects", sources)

    def test_economic_not_events(self):
        for q in ("Tell me about economic empowerment", "economic empowerment"):
            route = route_intent(q)
            self.assertEqual(route.intent, Intent.ECONOMIC_EMPOWERMENT, q)
            sources = list(route.source_filter or [])
            self.assertNotIn("cms_events", sources)

    def test_education_overrides_event_session(self):
        route = route_intent(
            "Tell me about education",
            has_session_topic=True,
            session_topic="events",
        )
        self.assertEqual(route.intent, Intent.EDUCATION)

    def test_rewrite_education_avoids_job_fair(self):
        rw = rewrite_query(
            "Tell me about education",
            language=Language.ENGLISH,
            intent=Intent.EDUCATION,
        )
        self.assertIn("education", rw.search_query.lower())
        self.assertNotIn("job fair", rw.search_query.lower())


class GibberishAndOodTests(unittest.TestCase):
    def test_gibberish_samples(self):
        for msg in (
            "ajjsjsjsjsjwjjsm",
            "lalalallalalalala",
            "polallalaallalallalal",
            "asdasdasd",
            "qwerty",
            "nnnnnnnnnn",
        ):
            self.assertTrue(looks_gibberish(msg), msg)
            route = route_intent(msg)
            self.assertEqual(route.reason, "gibberish", msg)
            self.assertIn("rephrase", (route.canned_response or "").lower())
            self.assertNotEqual(route.intent, Intent.CONTACT)

    def test_out_of_domain(self):
        for q in (
            "Who won the World Cup?",
            "Capital of France?",
            "Who is Salman Khan?",
            "Who is Aiman?",
            "What is Python?",
        ):
            route = route_intent(q)
            self.assertEqual(route.intent, Intent.GENERAL_KNOWLEDGE, q)
            self.assertNotEqual(route.intent, Intent.CONTACT)

    def test_ood_copy(self):
        text = t(DOMAIN_ONLY_RESPONSE, Language.ENGLISH).lower()
        self.assertIn("specialize", text)
        self.assertNotIn("8291101312", text)


class DonationFollowupTests(unittest.TestCase):
    def test_cheque_intent_and_answer(self):
        route = route_intent(
            "Is cheque accepted?",
            has_session_topic=True,
            session_topic="donations",
        )
        self.assertEqual(route.intent, Intent.DONATIONS)
        text = answer_builtin("Is cheque accepted?", intent=Intent.DONATIONS)
        self.assertIsNotNone(text)
        self.assertIn("cheque", text.lower())
        self.assertIn("association of muslim professionals", text.lower())

    def test_upi(self):
        text = answer_builtin("UPI ID?", intent=Intent.DONATIONS)
        self.assertIn("ampindia@kotak", text.lower())

    def test_receipt_and_80g(self):
        rec = answer_builtin("Donation receipt?", intent=Intent.DONATIONS)
        self.assertIn("info@ampindia.org", rec.lower())
        tax = answer_builtin("80G certificate?", intent=Intent.DONATIONS)
        self.assertIn("section 8", tax.lower())
        self.assertNotIn("8291101312", tax)


class FormClarifyTests(unittest.TestCase):
    def test_unspecified_form(self):
        for q in ("Link of form", "Registration link", "Application form"):
            route = route_intent(q)
            self.assertEqual(route.intent, Intent.FORM_CLARIFY, q)
            self.assertIn("which form", (route.canned_response or "").lower())

    def test_volunteer_form_still_volunteer(self):
        self.assertEqual(route_intent("Volunteer form").intent, Intent.VOLUNTEERING)

    def test_form_copy(self):
        self.assertIn("volunteer", t(FORM_CLARIFY_RESPONSE, Language.ENGLISH).lower())


class ContactStillWorksTests(unittest.TestCase):
    def test_contact(self):
        self.assertEqual(route_intent("How can I contact AMP India Foundation?").intent, Intent.CONTACT)
        self.assertEqual(route_intent("aif ka number").intent, Intent.CONTACT)


class ContactLeakGuardTests(unittest.TestCase):
    def test_personal_ood_not_contact(self):
        for q in ("mujhe biwi chahiye", "mujhe shohar chahiye", "dating", "marriage advice"):
            route = route_intent(q, has_session_topic=True, session_topic="contact")
            self.assertNotEqual(route.intent, Intent.CONTACT, q)
            self.assertEqual(route.intent, Intent.GENERAL_KNOWLEDGE, q)

    def test_identity_and_casual(self):
        self.assertEqual(route_intent("tu kon hai").intent, Intent.ASSISTANT_IDENTITY)
        self.assertIn(
            route_intent("tu kaisa hai re").intent,
            {Intent.SMALL_TALK, Intent.CASUAL_CHAT},
        )

    def test_location_not_contact(self):
        for q in ("mai bihar se hu", "mai london me hu", "mai mumbai se hu"):
            route = route_intent(q, has_session_topic=True, session_topic="contact")
            self.assertEqual(route.intent, Intent.LOCATION_STATEMENT, q)
            self.assertNotIn("8291101312", (route.canned_response or ""))

    def test_gibberish_stretched(self):
        for q in ("hattttt", "bhagggg", "ahshhshbsbbsd", "nnnnnnnnnn"):
            route = route_intent(q)
            self.assertIn(route.intent, {Intent.GIBBERISH, Intent.UNKNOWN}, q)
            self.assertEqual(route.reason, "gibberish", q)
            self.assertNotEqual(route.intent, Intent.CONTACT)

    def test_give_me_link(self):
        route = route_intent("give me link")
        self.assertEqual(route.intent, Intent.LINK_CLARIFY)
        self.assertIn("which link", (route.canned_response or "").lower())

    def test_session_does_not_force_contact(self):
        route = route_intent("hattttt", has_session_topic=True, session_topic="contact")
        self.assertNotEqual(route.intent, Intent.CONTACT)


if __name__ == "__main__":
    unittest.main()
