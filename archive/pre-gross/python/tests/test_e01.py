"""Small analytic/integration controls. These never execute the research preset."""

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.integrate import simpson
from scipy.linalg import eigvals
from signal_space.contracts.e01 import ROOT, validate
from signal_space.contracts.validation import ContractError
from signal_space.experiments.charged_worker import execute
from signal_space.models.charged_scalar import tail
from signal_space.numerics.charged_radial import solve_profile, observables
from signal_space.numerics.charged_spectrum import generator, spectrum
from signal_space.runtime.runner import ResearchRuntime
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event
from signal_space.analysis.charged import branch_segments, breakup_thresholds


def fixture():
    return read_json(ROOT / "fixtures/research/e01-smoke.json")


class E01NumericalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = solve_profile(0.94, 30, 120, 1e-10, 6000, 4097)

    def test_normalized_gaussian_against_exact_integrals(self):
        a, w, omega = 0.63, 1.7, 0.93
        r = np.linspace(0, 24, 4097)
        f = a * np.exp(-r * r / (2 * w * w))
        fp = -r * f / (w * w)
        profile = {
            "r": r.tolist(),
            "f": f.tolist(),
            "fp": fp.tolist(),
            "omega": omega,
            "radius": 24,
        }
        got = observables(profile)
        integral = a * a * math.pi**1.5 * w**3
        expected = (
            (1 + omega**2) * integral
            + 3 * integral / (2 * w * w)
            - integral**2 / (2**1.5 * math.pi**1.5 * w**3)
            + integral**3 / (3**1.5 * math.pi**3 * w**6)
        ) / 0.01
        self.assertAlmostEqual(got["E"] / expected, 1, places=11)
        self.assertAlmostEqual(got["Q"] / (2 * omega * integral / 0.01), 1, places=11)
        self.assertAlmostEqual(got["radius"], math.sqrt(1.5) * w, places=11)
        self.assertGreater(got["field_residual"], 1e-4)  # Not stationary.

    def test_tail_integrals_and_robin_are_spherical(self):
        radius, fr, omega = 8.0, 0.001, 0.93
        k = math.sqrt(1 - omega**2)
        r = np.linspace(radius, radius + 40 / k, 20001)
        f = fr * radius / r * np.exp(-k * (r - radius))
        fp = -(k + 1 / r) * f
        got = tail(radius, fr, omega)
        self.assertAlmostEqual(got["i"] / simpson(r * r * f * f, x=r), 1, places=9)
        self.assertAlmostEqual(got["t"] / simpson(r * r * fp * fp, x=r), 1, places=9)
        self.assertAlmostEqual(got["r4"] / simpson(r**4 * f * f, x=r), 1, places=9)
        self.assertAlmostEqual(fp[0] + (k + 1 / radius) * fr, 0)
        self.assertNotEqual(fp[0] + k * fr, 0)

    def test_nontrivial_profile_independent_residual_and_virial(self):
        p = self.profile
        o = observables(p)
        self.assertEqual(p["status"], "accepted")
        self.assertGreater(p["f"][0], 0.1)
        self.assertLess(o["field_residual"], 1e-7)
        self.assertLess(o["virial_defect"], 1e-5)
        self.assertLess(o["energy_identity_defect"], 1e-5)
        r = np.asarray(p["r"])
        h = r[1] - r[0]
        f = np.asarray(p["f"])
        expected = ((1 - 0.94**2) * f[0] - 2 * f[0] ** 3 + 3 * f[0] ** 5) / 6
        self.assertAlmostEqual((f[1] - f[0]) / h**2, expected, places=6)
        perturbed = copy.deepcopy(p)
        perturbed["f"][100] += 0.001
        self.assertGreater(observables(perturbed)["field_residual"], 0.1)

    def test_exact_vacuum_rejected(self):
        zero = copy.deepcopy(self.profile)
        zero["f"] = [0.0] * len(zero["r"])
        zero["fp"] = [0.0] * len(zero["r"])
        p = solve_profile(0.94, 30, 60, 1e-7, 1000, 129, seed=zero)
        self.assertEqual(p["status"], "rejected-vacuum")

    def test_vacuum_full_generator_has_analytic_exp_sigma_signs(self):
        n, radius, omega = 12, 10.0, 0.94
        a, _, _, _ = generator(np.zeros(n), omega, radius, 0)
        actual = np.sort(eigvals(a).imag)
        spacing = radius / (n + 1)
        eigen = (
            4 * np.sin(np.arange(1, n + 1) * np.pi / (2 * (n + 1))) ** 2 / spacing**2
        )
        expected = np.sort(
            np.array(
                [
                    sign * (np.sqrt(1 + p2) + shift * omega)
                    for p2 in eigen
                    for sign in (-1, 1)
                    for shift in (-1, 1)
                ]
            )
        )
        np.testing.assert_allclose(actual, expected, atol=1e-12)
        self.assertLess(np.max(abs(eigvals(a).real)), 1e-12)

    def test_spectrum_original_equation_charge_constraint_and_refinement(self):
        coarse = spectrum(self.profile, 16, 2)
        fine = spectrum(self.profile, 32, 2)
        self.assertLess(
            fine["background_relative_error"], coarse["background_relative_error"]
        )
        for result in (coarse, fine):
            self.assertEqual([x["ell"] for x in result["sectors"]], [0, 1, 2])
            self.assertLess(result["background_residual"], 1e-10)
            for sector in result["sectors"]:
                self.assertLess(sector["max_residual"], 1e-7)
                self.assertLess(sector["max_charge_defect"], 1e-7)
            self.assertLess(result["sectors"][0]["symmetry_splitting"], 1e-7)
        # No test asserts a desired stability conclusion.

    def test_breakup_search_does_not_join_disconnected_branches(self):
        def point(name, q, e, parent=None, branch="a"):
            return {
                "id": name,
                "file": name,
                "parent": parent,
                "branch": branch,
                "lane": "base",
                "observables": {"Q": q, "E": e},
                "errors": {"E": 0.01, "Q": 0.01},
            }

        a = point("a", 2, 1.8)
        b = point("b", 4, 3.5, "a")
        other = point("other", 10, 1.0, branch="b")
        self.assertEqual(len(branch_segments([a, b, other])), 1)
        target = point("target", 6, 8)
        rows, covered = breakup_thresholds([target], [a, b], 65, 2)
        self.assertTrue(covered)
        best = min(x["threshold"] for x in rows)
        self.assertLess(best, 6)
        self.assertTrue(any(x["channel"] == "discrete-two-plus-free" for x in rows))
        rows, covered = breakup_thresholds([target], [a, other], 65, 2)
        self.assertFalse(covered)
        self.assertTrue(any(row["channel"] == "free-charge" for row in rows))
        self.assertTrue(any(row["channel"] == "discrete-one-plus-free" for row in rows))
        self.assertFalse(any("resolved-fragment" in row["channel"] for row in rows))


class E01RuntimeTest(unittest.TestCase):
    def test_closed_config_units_domains_and_opt_in(self):
        c = fixture()
        self.assertEqual(validate(c), c)
        for path, value in [
            ("omega_start", 1.0),
            ("omega_seed", 0.8),
            ("epsilon", 0.2),
            ("solver_tolerance", float("nan")),
            ("nodes", True),
            ("research_run", 1),
            ("max_points", 100),
        ]:
            changed = copy.deepcopy(c)
            changed["parameters"][path] = value
            with self.subTest(path=path), self.assertRaises(ContractError):
                validate(changed)
        changed = copy.deepcopy(c)
        changed["units"]["charge"] = "none"
        with self.assertRaises(ContractError):
            validate(changed)
        changed = copy.deepcopy(c)
        changed["parameters"]["hidden_force"] = 1
        with self.assertRaises(ContractError):
            validate(changed)
        self.assertTrue(
            ResearchRuntime().estimate(
                read_json(ROOT / "fixtures/research/e01-research.json")
            )["accepted"]
        )

    def test_headless_saved_data_reanalysis_report_and_verify(self):
        rt = ResearchRuntime()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = rt.run(fixture(), workspace)
            self.assertEqual(result["state"], "completed")
            with patch(
                "signal_space.numerics.charged_radial.solve_profile",
                side_effect=AssertionError("solver forbidden during analysis/report"),
            ):
                analysis = rt.analyze(workspace, result["run_id"])
                self.assertEqual(analysis["summary"]["outcome"], "unresolved")
                self.assertEqual(analysis["summary"]["points"], 3)
                self.assertEqual(analysis["summary"]["pending"], 0)
                report = rt.report(workspace, result["run_id"])
                self.assertTrue(rt.verify(workspace, result["run_id"])["valid"])
            report_path = Path(result["path"]) / report["path"]
            self.assertTrue(
                (report_path / "report.pdf").read_bytes().startswith(b"%PDF")
            )
            self.assertEqual(
                len(list((report_path / "figures").glob("*.figure.json"))), 5
            )
            self.assertIn("unresolved", (report_path / "report.md").read_text())
            exploration = read_json(report_path / "plot-data/exploration.json")
            self.assertEqual(exploration["selection"]["outcome"], "unresolved")
            self.assertEqual(len(exploration["views"]), 8)
            self.assertEqual(len(exploration["tables"]["branch"]), 3)
            self.assertEqual(len(exploration["tables"]["profiles"]), 3 * 1025)
            raw = read_json(Path(result["path"]) / analysis["raw_source"])
            for row in exploration["tables"]["branch"]:
                source = next(x for x in raw["records"] if x["id"] == row["id"])
                parent = next((x for x in raw["records"] if x["file"] == source["parent"]), None)
                self.assertEqual(row["parent_id"], parent["id"] if parent else None)
            events = [json.loads(line) for line in (Path(result["path"]) / "attempts/attempt-0001/events.jsonl").read_text().splitlines()]
            progress = [e["payload"] for e in events if e["type"] == "point-completed"]
            self.assertEqual(len(progress), 3)
            self.assertTrue(all(p["provisional"] for p in progress))
            for point in progress:
                saved = next(r for r in exploration["tables"]["branch"] if r["id"] == point["point_id"])
                self.assertEqual(point["observables"]["E"], saved["E"])
                self.assertLess(len(json.dumps(point)), 1500)
                self.assertNotIn("profile", point)

    def test_checkpoint_resumes_same_pending_continuation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def request(name, parent=None, resume=None):
                attempt = root / name
                attempt.mkdir()
                data = {
                    "attempt_path": str(attempt),
                    "attempt_id": name,
                    "config": fixture(),
                    "config_hash": "a" * 64,
                    "code_identity_hash": "b" * 64,
                    "seed_ledger": {
                        "initialization": 1,
                        "perturbations": 2,
                        "sampling": 3,
                        "analysis": 4,
                    },
                    "parent_attempt_id": parent,
                    "prior_attempt_path": str(root / parent) if parent else None,
                    "resume_checkpoint": resume,
                }
                path = root / f"{name}.json"
                write_json(path, data)
                return path

            first = request("attempt-1")

            def cancel_after_point(path, event, stage, payload):
                append_event(path, event, stage, payload)
                if event == "point-completed":
                    (root / "attempt-1/cancel.request").touch()

            with patch(
                "signal_space.experiments.charged_worker.append_event",
                side_effect=cancel_after_point,
            ):
                self.assertEqual(execute(first), 130)
            cp = read_json(sorted((root / "attempt-1/checkpoints").glob("*.json"))[-1])
            old = (root / "attempt-1/raw/branch.json").read_bytes()
            self.assertEqual(execute(request("attempt-2", "attempt-1", cp)), 0)
            self.assertEqual(execute(request("control")), 0)
            resumed = read_json(root / "attempt-2/raw/branch.json")
            control = read_json(root / "control/raw/branch.json")
            self.assertEqual(resumed, control)
            for row in resumed["records"]:
                self.assertEqual(
                    read_json(root / "attempt-2/raw" / row["file"]),
                    read_json(root / "control/raw" / row["file"]),
                )
            self.assertEqual((root / "attempt-1/raw/branch.json").read_bytes(), old)

    def test_small_refinement_fixture_keeps_incomplete_budget_visible(self):
        # Tiny mechanics control with refinement enabled, not the research preset.
        c = fixture()
        c["parameters"].update(
            research_run=True, refinements=True, max_points=3, spectral_nodes=12
        )
        with tempfile.TemporaryDirectory() as directory:
            rt = ResearchRuntime()
            w = Path(directory)
            result = rt.run(c, w)
            self.assertEqual(result["state"], "completed")
            a = rt.analyze(w, result["run_id"])
            self.assertGreater(a["summary"]["pending"], 0)
            self.assertEqual(a["classification"], "unresolved")
            data = read_json(
                Path(result["path"]) / "attempts/attempt-0001/raw/branch.json"
            )
            self.assertTrue(any(x["kind"] == "volume" for x in data["records"]))
            self.assertTrue(rt.verify(w, result["run_id"])["valid"])


if __name__ == "__main__":
    unittest.main()
