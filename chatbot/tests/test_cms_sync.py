"""Unit tests for incremental CMS / source ingest helpers."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app.services.document_service import (
    _content_hash,
    chunk_text,
    ingest_sources_batch,
)
from app.services.language_service import Language, detect_language, resolve_session_language
from app.services.query_rewrite import rewrite_query
from app.services.intent_router import Intent, route_intent
from app.services.response_formatter import format_user_response
from app.services.types import Document


class TestLanguageSwitches(unittest.TestCase):
    def test_hindi_switch(self):
        self.assertEqual(detect_language("Hindi me baat karo"), Language.HINDI)
        self.assertEqual(detect_language("Hindi akshar me"), Language.HINDI)

    def test_english_switch(self):
        self.assertEqual(detect_language("English please"), Language.ENGLISH)

    def test_session_remembers_hindi(self):
        detected = detect_language("Hindi me baat karo")
        lang = resolve_session_language(detected, "Hindi me baat karo", None)
        self.assertEqual(lang, Language.HINDI)
        follow = resolve_session_language(
            detect_language("Timings?", session_language="hi"),
            "Timings?",
            "hi",
        )
        self.assertEqual(follow, Language.HINDI)


class TestQueryRewriteCoverage(unittest.TestCase):
    def test_pata_and_reach(self):
        for q in ("pata", "Office address", "How to reach", "Nagpada", "Mumbai office"):
            route = route_intent(q if len(q) > 3 else f"{q} batao")
            # short tokens go through short_map / contact patterns
            rewritten = rewrite_query(q, intent=Intent.CONTACT)
            self.assertIn("contact", rewritten.search_query.lower(), q)

    def test_volunteer_serve(self):
        rewritten = rewrite_query("I want to serve / community work", intent=Intent.VOLUNTEERING)
        self.assertIn("volunteer", rewritten.search_query.lower())

    def test_fees_scholarship(self):
        rewritten = rewrite_query("Need help with fees / education", intent=Intent.SCHOLARSHIPS)
        self.assertTrue(
            "scholarship" in rewritten.search_query.lower()
            or "education" in rewritten.search_query.lower()
        )


class TestResponseNaturalization(unittest.TestCase):
    def test_strips_qa_dump(self):
        raw = "Q: What is phone?\nA: +91 8291101312\n\nYou can call +91 8291101312."
        out = format_user_response(raw)
        self.assertNotIn("Q:", out)
        self.assertIn("8291101312", out)


class TestIncrementalIngest(unittest.TestCase):
    def test_chunk_and_batch_skip_unchanged(self):
        text = "AMP India Foundation CMS event: Job Fair in Mumbai Nagpada."
        docs = chunk_text(text, source="cms_events", category="cms_events")
        self.assertGreaterEqual(len(docs), 1)

        digest = _content_hash(text)
        with patch("app.services.document_service.rag_service") as rag, patch(
            "app.services.document_service.clear_retrieval_cache"
        ), patch("app.services.document_service._save_hashes"), patch(
            "app.services.document_service._load_hashes"
        ):
            rag.delete_by_source.return_value = 1
            rag.upsert_documents.return_value = len(docs)

            from app.services import document_service as ds

            ds._SOURCE_HASHES.clear()
            first = ds.ingest_text("cms_events", text, skip_unchanged=True)
            self.assertEqual(first[2], "indexed")
            ds._SOURCE_HASHES["cms_events"] = digest
            second = ds.ingest_text("cms_events", text, skip_unchanged=True)
            self.assertEqual(second[2], "skipped_duplicate")

            result = ingest_sources_batch(
                [{"source": "cms_events", "text": text}],
                skip_unchanged=True,
                delete_missing_prefix="cms_",
                delete_sources=["backend_events", "events"],
            )
            self.assertIn("cms_events", result["sources"])
            self.assertGreaterEqual(result["deleted"], 2)


if __name__ == "__main__":
    unittest.main()
