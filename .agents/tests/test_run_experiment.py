"""Failure preservation and classification boundaries for the Actions adapter."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agents/scripts"))
from run_experiment import Pipeline, assessment


class RunExperimentTests(unittest.TestCase):
    def test_output_cannot_dirty_checkout_or_overwrite_prior_attempt(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            with self.assertRaisesRegex(ValueError, "outside the checkout"):
                Pipeline(repo, repo / "output", "gross-test-01")
            output = Path(temporary) / "output"
            Pipeline(repo, output, "gross-test-01")
            with self.assertRaises(FileExistsError):
                Pipeline(repo, output, "gross-test-01")

    def test_dirty_source_stops_before_solver_and_preserves_diagnostics(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}):
            repo = Path(temporary) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
            (repo / "uncommitted.py").write_text("uncommitted source")
            pipeline = Pipeline(repo, Path(temporary) / "output", "gross-test-01")
            self.assertEqual(pipeline.run(), 1)
            status = json.loads((pipeline.evidence / "status.json").read_text())
            self.assertEqual(status["scientific_classification"], "not-evaluated")
            self.assertEqual(status["technical_status"], "failed")
            self.assertIn("uncommitted.py", (pipeline.logs / "source-status.stdout.log").read_text())
            self.assertFalse(pipeline.workspace.exists())
            self.assertTrue((pipeline.evidence / "evidence-index.json").is_file())

    def test_failed_command_and_timeout_keep_partial_logs(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            pipeline = Pipeline(repo, Path(temporary) / "output", "gross-test-01")
            with self.assertRaisesRegex(RuntimeError, "exited 7"):
                pipeline.command("failure", [sys.executable, "-c", "import sys; print('partial'); print('problem', file=sys.stderr); sys.exit(7)"])
            self.assertIn("partial", (pipeline.logs / "failure.stdout.log").read_text())
            self.assertIn("problem", (pipeline.logs / "failure.stderr.log").read_text())
            with self.assertRaises(subprocess.TimeoutExpired):
                pipeline.command("timeout", [sys.executable, "-c", "import time; print('started', flush=True); time.sleep(5)"], timeout=1)
            self.assertIn("started", (pipeline.logs / "timeout.stdout.log").read_text())

    def test_scientific_failure_is_not_pipeline_failure_or_next_gate_permission(self):
        for classification in ("pass", "fail", "unresolved", "not-evaluated"):
            with self.subTest(classification=classification):
                text = assessment({"scientific_classification": classification, "run_id": "run-fixture"},
                                  {"analysis_id": "analysis-fixture"},
                                  {"checks": [{"id": "identities", "status": classification, "value": 1}]})
                self.assertIn(f"**{classification}**", text)
                self.assertIn("review remain pending", text)
                if classification == "pass":
                    self.assertIn("Proceed to the Test 2", text)
                else:
                    self.assertNotIn("Proceed to the Test 2", text)
                    self.assertIn("Resolve the failed", text)

    def test_completed_negative_result_remains_downloadable(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}):
            repo = Path(temporary) / "repo"
            repo.mkdir()
            pipeline = Pipeline(repo, Path(temporary) / "output", "gross-test-01")
            def completed_negative():
                pipeline.status.update({"technical_status": "completed", "scientific_classification": "fail", "stage": "complete"})
            with patch.object(pipeline, "execute", side_effect=completed_negative):
                self.assertEqual(pipeline.run(), 0)
            self.assertIn("**fail**", (pipeline.evidence / "README.md").read_text())


if __name__ == "__main__":
    unittest.main()
