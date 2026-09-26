"""Production resilience: fallbacks, metrics, health probes."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app.services.analytics_service import record_exception, record_retrieval, snapshot
from app.services.ai_service import ai_service
from app.services.health_checks import run_health_checks


class MetricsTests(unittest.TestCase):
    def test_snapshot_includes_ops_fields(self):
        record_exception("test_kind")
        record_retrieval(hit=True, pinecone_ms=12.0)
        data = snapshot()
        self.assertIn("retrieval_success_rate", data)
        self.assertIn("pinecone_avg_latency_ms", data)
        self.assertIn("exception_count", data)
        self.assertIn("fallback_frequency", data)
        self.assertGreaterEqual(data["exception_count"], 1)


class RecoveryTests(unittest.TestCase):
    def test_crash_recovery_returns_contact(self):
        out = ai_service._recover_from_failure(
            "phone number",
            "audit-recover",
            None,
            RuntimeError("simulated"),
        )
        text = (out.get("response") or "").lower()
        self.assertNotIn("traceback", text)
        self.assertNotIn("runtimeerror", text)
        self.assertTrue("8291101312" in text or "contact" in text or "amp" in text)


class HealthCheckTests(unittest.TestCase):
    def test_cms_down_still_reports_chat_available(self):
        with patch("app.services.health_checks._pinecone", return_value={"vectors": 1}), patch(
            "app.services.health_checks._embeddings", return_value={"configured": True}
        ), patch(
            "app.services.health_checks._cms_and_database",
            side_effect=RuntimeError("cms_unavailable"),
        ):
            report = run_health_checks()
        self.assertTrue(report.get("chat_available"))
        self.assertEqual(report.get("status"), "degraded")
        self.assertFalse(report["checks"]["cms_api"]["ok"])


if __name__ == "__main__":
    unittest.main()
