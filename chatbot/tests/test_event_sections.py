"""Event section routing / retrieval tests — upcoming vs past vs featured."""

from __future__ import annotations

import unittest

from app.services.document_service import chunk_text
from app.services.intent_router import (
    Intent,
    SECTION_FEATURED,
    SECTION_PAST,
    SECTION_UPCOMING,
    route_intent,
)
from app.services.rag_service import _filter_docs_by_section, _rerank
from app.services.types import Document


SAMPLE_EVENTS = """# AMP India Foundation — Events (CMS)
# schema: event_sections_v2

## Upcoming event: National Mega Job Fair
Section: upcoming_events
Description: Bridging skilled youth with employers.
Venue: Mumbai
Date: 12 Aug 2026
Category: Employment

## Featured event: Career Guidance Summit
Section: featured_event
Description: Mentorship and career counselling.
Venue: Nagpada
Date: 05 Sep 2026
Category: Career

## Home event: Employability Training Programme
Section: upcoming_events
Description: Soft skills and placement prep.
Venue: Mumbai
Date: 24 Jul 2026
Category: Training
"""

SAMPLE_PAST = """# AMP India Foundation — Past Events (CMS)
# schema: event_sections_v2

## Past event: National Job Fair 2025
Section: past_events
Description: A large-scale placement drive.
Category: Employment
Date: 2025
Venue: Mumbai

## Past event: Medical Relief Camp
Section: past_events
Description: Free health check-ups.
Category: Medical Camp
Date: 2025
Venue: Hyderabad
"""


class EventIntentTests(unittest.TestCase):
    def test_upcoming_intents(self):
        cases = [
            "What are upcoming events?",
            "upcoming events",
            "future events",
            "next event",
            "coming events",
            "what events are happening",
            "events this month",
            "events this year",
            "What employment events are coming?",
        ]
        for msg in cases:
            with self.subTest(msg=msg):
                route = route_intent(msg)
                self.assertEqual(route.intent, Intent.UPCOMING_EVENTS, msg)
                self.assertEqual(route.section_filter, SECTION_UPCOMING, msg)
                self.assertNotIn("cms_gallery", route.source_filter or [])

    def test_past_intents(self):
        cases = [
            "Past events",
            "previous events",
            "old events",
            "last events",
            "What happened in 2025?",
        ]
        for msg in cases:
            with self.subTest(msg=msg):
                route = route_intent(msg)
                self.assertEqual(route.intent, Intent.PAST_EVENTS, msg)
                self.assertEqual(route.section_filter, SECTION_PAST, msg)

    def test_featured_intent(self):
        for msg in ("Featured event", "Tell me about featured events"):
            with self.subTest(msg=msg):
                route = route_intent(msg)
                self.assertEqual(route.intent, Intent.FEATURED_EVENT, msg)
                self.assertEqual(route.section_filter, SECTION_FEATURED, msg)

    def test_medical_camps_upcoming(self):
        route = route_intent("Medical camps")
        self.assertEqual(route.intent, Intent.UPCOMING_EVENTS)
        self.assertEqual(route.section_filter, SECTION_UPCOMING)


class EventChunkingTests(unittest.TestCase):
    def test_one_vector_per_event_with_section(self):
        docs = chunk_text(SAMPLE_EVENTS, source="cms_events", category="cms_events")
        self.assertGreaterEqual(len(docs), 3)
        sections = {d.metadata.get("section") for d in docs}
        self.assertIn(SECTION_UPCOMING, sections)
        self.assertIn(SECTION_FEATURED, sections)
        # Each chunk is a single event heading
        for d in docs:
            self.assertIn("## ", d.page_content)
            self.assertEqual(d.metadata.get("doc_type"), "event")
            self.assertTrue(d.metadata.get("section"))

    def test_past_gallery_sections(self):
        docs = chunk_text(SAMPLE_PAST, source="cms_gallery", category="cms_gallery")
        self.assertGreaterEqual(len(docs), 2)
        for d in docs:
            self.assertEqual(d.metadata.get("section"), SECTION_PAST)


class EventRerankFilterTests(unittest.TestCase):
    def _docs(self):
        return [
            Document(
                page_content="## Past event: National Job Fair 2025\nDescription: Old drive",
                metadata={"source": "cms_gallery", "section": SECTION_PAST, "score": 0.90},
            ),
            Document(
                page_content="## Upcoming event: Free Medical Camp\nDescription: Screening",
                metadata={"source": "cms_events", "section": SECTION_UPCOMING, "score": 0.75},
            ),
            Document(
                page_content="## Featured event: Career Summit\nDescription: Mentorship",
                metadata={"source": "cms_events", "section": SECTION_FEATURED, "score": 0.70},
            ),
        ]

    def test_upcoming_filter_excludes_past(self):
        filtered = _filter_docs_by_section(self._docs(), SECTION_UPCOMING)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].metadata["section"], SECTION_UPCOMING)

    def test_past_filter_excludes_upcoming(self):
        filtered = _filter_docs_by_section(self._docs(), SECTION_PAST)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].metadata["section"], SECTION_PAST)

    def test_rerank_boosts_upcoming(self):
        ranked = _rerank(
            "What are upcoming events?",
            self._docs(),
            top_k=3,
            section_filter=SECTION_UPCOMING,
        )
        ranked = _filter_docs_by_section(ranked, SECTION_UPCOMING)
        self.assertTrue(ranked)
        self.assertEqual(ranked[0].metadata["section"], SECTION_UPCOMING)


if __name__ == "__main__":
    unittest.main()
