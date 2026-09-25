"""Independent algebra, invalid-domain and saved-evidence controls for Test 1."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import numpy as np

from signal_space.contracts.validation import ContractError
from signal_space.experiments.operators import OperatorExperiment, ROOT
from signal_space.models.operators import observer, projector, norm
from signal_space.analysis.operators import analyze
from signal_space.runtime.io import read_json
from signal_space.runtime.runner import ResearchRuntime


class OperatorTests(unittest.TestCase):
    def setUp(self):
        self.config = read_json(ROOT / "fixtures/research/gross-test-01.json")

    def test_closed_schema_and_fixed_gates(self):
        for mutate in (
            lambda c: c.update(extra=True),
            lambda c: c["analysis"].update(max_residual=0.1),
            lambda c: c["parameters"].update(samples=True),
            lambda c: c["parameters"].update(near_angles=[0.1] * 9),
            lambda c: c["resources"].update(max_wall_seconds=float("nan")),
        ):
            candidate = deepcopy(self.config)
            mutate(candidate)
            with self.assertRaises(ContractError):
                OperatorExperiment().validate(candidate)

    def test_singular_observer_and_exact_boost(self):
        with self.assertRaises(ValueError):
            observer(np.diag([2, 0]))
        with self.assertRaises(ValueError):
            observer(np.diag([1, 1e-12]))
        with self.assertRaises(ValueError):
            projector(np.zeros(2))
        eta = 0.7
        s = np.diag(np.exp([eta / 2, -eta / 2]))
        z = np.array([1, 2j])
        transformed_t = np.diag(np.exp([eta, -eta]))
        self.assertAlmostEqual(norm(s @ z, transformed_t), 5)
        # The ordinary Euclidean norm is not a boost invariant.
        self.assertGreater(abs(np.vdot(s @ z, s @ z).real - 5), 0.1)

    def test_lifecycle_and_independent_corruption_detection(self):
        config = deepcopy(self.config)
        config["parameters"]["samples"] = 8  # infrastructure fixture, not full Test 1
        runtime = ResearchRuntime()
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run = runtime.run(config, workspace)
            self.assertEqual(run["state"], "completed")
            result = runtime.analyze(workspace, run["run_id"])
            self.assertEqual(result["classification"], "pass")
            runtime.verify(workspace, run["run_id"])
            # Copy saved evidence into a deliberately corrupt test-only directory;
            # never alter the canonical fixture package.
            import shutil
            import csv
            copied = workspace / "corrupt-control"
            shutil.copytree(Path(run["path"]), copied)
            raw = next(copied.glob("attempts/*/raw/measurements.csv"))
            with raw.open(newline="") as f:
                rows = list(csv.DictReader(f))
            rows[0]["observer_norm"] = str(float(rows[0]["observer_norm"]) + 1)
            with raw.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            corrupted = analyze(copied, workspace / "corrupt-analysis", config)
            self.assertEqual(OperatorExperiment().classify(corrupted["checks"], config), "fail")


if __name__ == "__main__":
    unittest.main()
