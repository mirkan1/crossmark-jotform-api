import os
import time
import unittest

from crossmark_jotform_api.jotForm import JotForm


class TestJotFormStress(unittest.TestCase):
    """Stress/integration tests that hit the real JotForm API."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.api_key = os.getenv("JOTFORM_API_KEY")
        cls.form_id = os.getenv("JOTFORM_FORM_ID")

        if not cls.api_key or not cls.form_id:
            raise unittest.SkipTest(
                "Set JOTFORM_API_KEY and JOTFORM_FORM_ID to run stress tests."
            )

        cls.jotform = JotForm(cls.api_key, cls.form_id, timeout=90)

    def test_pull_all_submissions_from_real_form(self) -> None:
        """Fetch all submissions for the configured form and verify count."""
        form = self.jotform.get_form()
        self.assertIsNotNone(form, "Expected form metadata from JotForm API")

        content = form.get("content", {}) if form else {}
        total_submissions = int(content.get("count", 0))  # type: ignore[assignment]

        if total_submissions == 0:
            self.skipTest("Configured form has 0 submissions.")

        # Reset local cache so this test always exercises full pulling logic.
        self.jotform.submission_data = {}
        self.jotform.submission_ids = set()
        self.jotform.submission_count = 0
        self.jotform._reset_url_params()

        started_at = time.perf_counter()
        pulled = self.jotform._fetch_new_submissions(total_submissions)
        elapsed_seconds = time.perf_counter() - started_at

        actual_count = self.jotform.get_submission_count()

        self.assertTrue(pulled, "Expected _fetch_new_submissions to report an update")
        self.assertEqual(
            actual_count,
            total_submissions,
            (
                f"Submission count mismatch after stress pull: "
                f"expected={total_submissions}, actual={actual_count}, "
                f"elapsed={elapsed_seconds:.2f}s"
            ),
        )
