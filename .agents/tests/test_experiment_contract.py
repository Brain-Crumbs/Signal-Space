"""Contract gates with real fixture and tamper scenarios."""

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("experiment_contract", ROOT / ".agents/scripts/experiment_contract.py")
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class ExperimentContractTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / ".agents/examples/synthetic-plan.json").read_text())

    def test_locked_fixture(self):
        contract.validate_plan(self.plan)

    def test_preregistered_threshold_cannot_change_silently(self):
        changed = copy.deepcopy(self.plan)
        changed["criteria"][0]["pass_if"] = "any error"
        with self.assertRaisesRegex(ValueError, "plan lock differs"):
            contract.validate_plan(changed)

    def test_visual_cannot_reference_unknown_control(self):
        changed = copy.deepcopy(self.plan)
        changed["visualization_plan"][0]["controls"] = ["unperformed"]
        changed["locked_sha256"] = contract.digest(contract.canonical_plan(changed))
        with self.assertRaisesRegex(ValueError, "unknown control"):
            contract.validate_plan(changed)

    def test_runner_detects_changed_registered_config(self):
        contract.validate_plan(self.plan)
        self.assertEqual(contract.verify_runtime_config(self.plan, ROOT).name, "synthetic.json")
        changed = copy.deepcopy(self.plan)
        changed["runtime_config_sha256"] = "0" * 64
        changed["locked_sha256"] = contract.digest(contract.canonical_plan(changed))
        with self.assertRaisesRegex(ValueError, "differs from locked"):
            contract.verify_runtime_config(changed, ROOT)

    def test_unsafe_paths_rejected(self):
        for path in ("../raw.csv", "/tmp/result.csv", "results//x.csv", "results/./x.csv", "results\\x.csv"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                contract.relative_path(path)

    def test_registered_fixture_exports_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "runs"
            output = Path(temporary) / "export"
            env = {**os.environ, "PYTHONPATH": str(ROOT / "python")}

            def runtime(*args):
                result = subprocess.run([sys.executable, "-m", "signal_space", "--workspace", str(workspace), *args],
                                        cwd=ROOT, env=env, capture_output=True, text=True, check=True)
                return json.loads(result.stdout)

            prepared = subprocess.run([sys.executable, str(ROOT / ".agents/scripts/run_plan.py"),
                                       "--plan", str(ROOT / ".agents/examples/synthetic-plan.json"),
                                       "--repo-root", str(ROOT), "--workspace", str(workspace), "--execute"],
                                      cwd=ROOT, capture_output=True, text=True, check=True)
            run = json.loads(prepared.stdout.splitlines()[-1])["result"]
            runtime("analyze", "--run-id", run["run_id"])
            runtime("report", "--run-id", run["run_id"])
            self.assertTrue(runtime("verify", "--run-id", run["run_id"])["valid"])
            subprocess.run([sys.executable, str(ROOT / ".agents/scripts/package_experiment.py"),
                            "--run", run["path"], "--plan", str(ROOT / ".agents/examples/synthetic-plan.json"),
                            "--interpretations", str(ROOT / ".agents/examples/synthetic-interpretations.json"),
                            "--mentor", str(ROOT / ".agents/examples/synthetic-mentor.md"),
                            "--output", str(output)], cwd=ROOT, check=True, capture_output=True)
            contract.validate_bundle(output)
            plot = output / "results/data/plot-data/recurrence.csv"
            plot.write_text(plot.read_text() + "0,corrupted\n")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                contract.validate_bundle(output)


if __name__ == "__main__":
    unittest.main()
