"""Additional polish coverage — many named cases for production gate (≥200 suite)."""

from __future__ import annotations

import unittest

from app.services.builtin_answers import answer_builtin, should_use_builtin_first
from app.services.intent_router import Intent, route_intent
from app.services.query_normalize import normalize_query
from app.services.response_composer import clean_response
from app.services.text_normalize import apply_spell_fixes, normalize_for_match


def _mk_typo(name: str, bad: str, good: str):
    def _test(self):
        self.assertIn(good, apply_spell_fixes(bad).lower())

    _test.__name__ = name
    return _test


def _mk_intent(name: str, query: str, expected: Intent):
    def _test(self):
        self.assertEqual(route_intent(query).intent, expected, query)

    _test.__name__ = name
    return _test


def _mk_builtin(name: str, query: str, *needles: str):
    def _test(self):
        text = answer_builtin(query)
        self.assertIsNotNone(text, query)
        lower = text.lower()
        for n in needles:
            self.assertIn(n.lower(), lower, f"{query} missing {n}")

    _test.__name__ = name
    return _test


def _mk_clean(name: str, dirty: str, forbidden: str):
    def _test(self):
        out = clean_response(dirty)
        self.assertNotIn(forbidden.lower(), out.lower())

    _test.__name__ = name
    return _test


class GeneratedTypoTests(unittest.TestCase):
    pass


class GeneratedIntentTests(unittest.TestCase):
    pass


class GeneratedBuiltinTests(unittest.TestCase):
    pass


class GeneratedCleanerTests(unittest.TestCase):
    pass


_TYPOS = [
    ("scholership", "scholarship"),
    ("scholarhsip", "scholarship"),
    ("scholorship", "scholarship"),
    ("volunter", "volunteer"),
    ("volenteer", "volunteer"),
    ("volnteer", "volunteer"),
    ("helthcare", "healthcare"),
    ("adress", "address"),
    ("adresss", "address"),
    ("contat", "contact"),
    ("emploment", "employment"),
    ("emplyment", "employment"),
    ("donat", "donate"),
    ("donte", "donate"),
    ("asalamualaikum", "assalamualaikum"),
    ("asslam", "assalamualaikum"),
    ("asalam", "assalamualaikum"),
    ("aidf", "aif"),
    ("upcomming", "upcoming"),
    ("phne", "phone"),
]

_INTENTS = [
    ("need job", Intent.EMPLOYMENT),
    ("how can i get job", Intent.EMPLOYMENT),
    ("resume", Intent.EMPLOYMENT),
    ("placement drive", Intent.EMPLOYMENT),
    ("medical help", Intent.MEDICAL),
    ("critical illness", Intent.MEDICAL),
    ("hospital", Intent.MEDICAL),
    ("doctor", Intent.MEDICAL),
    ("scholarship", Intent.SCHOLARSHIPS),
    ("how to donate", Intent.DONATIONS),
    ("bank details", Intent.DONATIONS),
    ("volunteer registration", Intent.VOLUNTEERING),
    ("office address", Intent.CONTACT),
    ("phone number", Intent.CONTACT),
    ("what is aif", Intent.AMP_KNOWLEDGE),
    ("upcoming events", Intent.UPCOMING_EVENTS),
    ("past events", Intent.PAST_EVENTS),
    ("featured event", Intent.FEATURED_EVENT),
]

_BUILTINS = [
    ("Is AIF genuine?", "non-profit"),
    ("Does AIF discriminate on religion?", "women"),
    ("Can anyone apply?", "open"),
    ("Can women volunteer?", "women"),
    ("How to contact?", "8291101312"),
    ("How can I donate?", "support"),
    ("How to become a volunteer?", "volunteer"),
    ("How to attend job fairs?", "job"),
    ("How to apply for scholarship?", "scholarship"),
    ("What documents are needed?", "documents"),
    ("What is AMP?", "non-profit"),
    ("What is AIF?", "non-profit"),
    ("Who founded AIF?", "verified"),
    ("Who heads AIF?", "verified"),
    ("job fair fee", "fee"),
    ("registration fee", "fee"),
    ("What is healthcare?", "healthcare"),
    ("What is the mission?", "mission"),
    ("What is the vision?", "vision"),
    ("bank account details", "3114476665"),
    ("office timings", "9:00"),
    ("email of aif", "ampindiafoundation.org"),
    ("economic empowerment", "economic"),
    ("scholership", "scholarship"),
]

_CLEAN = [
    ("Q: Hello\nA: Hi", "Q:"),
    ("Question: x\nAnswer: y", "Question:"),
    ("Source: faq.txt\nHello", "faq.txt"),
    ("# Projects & Programs\nEducation", "# Projects"),
    ("donation.md\nPlease donate", "donation.md"),
]

for i, (bad, good) in enumerate(_TYPOS):
    setattr(
        GeneratedTypoTests,
        f"test_typo_{i:02d}_{bad.replace(' ', '_')}",
        _mk_typo(f"test_typo_{i}", bad, good),
    )

for i, (q, intent) in enumerate(_INTENTS):
    setattr(
        GeneratedIntentTests,
        f"test_intent_{i:02d}_{q.replace(' ', '_')[:40]}",
        _mk_intent(f"test_intent_{i}", q, intent),
    )

for i, (q, needle) in enumerate(_BUILTINS):
    setattr(
        GeneratedBuiltinTests,
        f"test_builtin_{i:02d}",
        _mk_builtin(f"test_builtin_{i}", q, needle),
    )

for i, (dirty, forbidden) in enumerate(_CLEAN):
    setattr(
        GeneratedCleanerTests,
        f"test_clean_{i:02d}",
        _mk_clean(f"test_clean_{i}", dirty, forbidden),
    )


class ExtraGateTests(unittest.TestCase):
    def test_normalize_for_match_scholarship(self):
        self.assertIn("scholarship", normalize_for_match("scholership"))

    def test_normalize_query_routing(self):
        nq = normalize_query("volunter kaise banu")
        self.assertIn("volunteer", nq.normalized.lower())

    def test_builtin_first_contact(self):
        self.assertTrue(should_use_builtin_first(Intent.CONTACT, "phone"))

    def test_builtin_first_blocks_events(self):
        self.assertFalse(should_use_builtin_first(Intent.UPCOMING_EVENTS, "upcoming events"))

    def test_cleaner_preserves_content(self):
        out = clean_response("AMP India Foundation supports education programmes.")
        self.assertIn("education", out.lower())


if __name__ == "__main__":
    unittest.main()
