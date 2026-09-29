"""Synthetic regressions for E01 review; no research scan or assumed result."""

from copy import deepcopy
import math
import unittest
from signal_space.analysis.charged import (
    breakup_thresholds,
    selection_checks,
    spectral_assessment,
)
from signal_space.contracts.e01 import ROOT, check, schema, validate
from signal_space.contracts.validation import ContractError
from signal_space.experiments.charged import CRITERIA, ChargedExperiment
from signal_space.runtime.io import read_json


def point(name, charge, energy, parent=None, branch="a"):
    return {
        "id": name,
        "file": name,
        "parent": parent,
        "branch": branch,
        "lane": "base",
        "observables": {"Q": charge, "E": energy},
        "errors": {"E": 1e-7, "Q": 1e-7},
    }


def spectrum(values, symmetry=None, ell=0):
    return {
        "background_relative_error": 1e-5,
        "sectors": [
            {
                "ell": ell,
                "sigma_real": [complex(v).real for v in values],
                "sigma_imag": [complex(v).imag for v in values],
                "symmetry_mode_index": symmetry,
                "max_residual": 1e-12,
                "max_charge_defect": 1e-12,
            }
        ],
    }


class E01ReviewTest(unittest.TestCase):
    def assess(self, base, mesh, volume):
        return spectral_assessment(
            base,
            {"spectral": mesh, "volume": volume},
            {"eigenpair_residual": 1e-7, "refinement_relative": 0.005},
        )

    def test_growth_uses_own_error_despite_unrelated_mode_drift(self):
        # Permuted refinement modes exercise matching by value, not array index.
        base = spectrum([0.001, -0.001, 0.2j])
        mesh = spectrum([0.204j, -0.001001, 0.001001])
        volume = spectrum([-0.001002, 0.202j, 0.001002])
        got = self.assess(base, mesh, volume)
        self.assertTrue(got["resolved_growth"])
        self.assertFalse(got["pass"])
        self.assertAlmostEqual(got["error"], 0.004)
        growing = next(x for x in got["modes"] if x["mode"] == 0)
        self.assertAlmostEqual(growing["error"], 0.000002)
        self.assertEqual(growing["axes"]["spectral"]["refined_mode"], 2)
        # A poorly resolved background cannot supply a scientific negative.
        mesh["background_relative_error"] = 0.1
        self.assertFalse(self.assess(base, mesh, volume)["resolved_growth"])

    def test_growing_high_mode_below_old_selection_cutoff_is_not_omitted(self):
        stable = [1j * n for n in range(1, 18)]
        base = spectrum(stable + [5e-9 + 20j])
        refined = spectrum(stable + [5.001e-9 + 20j])
        got = self.assess(base, refined, refined)
        self.assertTrue(got["resolved_growth"])
        self.assertFalse(got["pass"])

    def test_symmetry_splitting_uses_own_error(self):
        base = spectrum([0.001j, 0.2j], symmetry=0)
        mesh = spectrum([0.001001j, 0.204j], symmetry=0)
        got = self.assess(base, mesh, mesh)
        self.assertFalse(got["resolved_growth"])
        self.assertFalse(got["modes"][0]["symmetry_resolved"])
        self.assertFalse(got["pass"])

    def test_unmatched_refined_growth_remains_unresolved(self):
        base = spectrum([0j, 0.2j], symmetry=0)
        refined = spectrum([0j, 0.2j, 0.001], symmetry=0)
        got = self.assess(base, refined, refined)
        self.assertFalse(got["pass"])
        self.assertFalse(got["resolved_growth"])
        self.assertEqual(len(got["unmatched_growth"]), 2)
        self.assertTrue(self.assess(base, base, base)["pass"])

    def test_frequency_lower_bound_is_exclusive_for_all_three_fields(self):
        config = read_json(ROOT / "fixtures/research/e01-smoke.json")
        specs = schema()["properties"]["parameters"]["properties"]
        for field in ("omega_start", "omega_seed", "omega_end"):
            spec = specs[field]
            boundary = spec["exclusiveMinimum"]
            for value in (
                math.sqrt(3) / 2,
                math.nextafter(boundary, -math.inf),
                boundary,
            ):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ContractError):
                        check(value, spec, field)
                    changed = deepcopy(config)
                    changed["parameters"][field] = value
                    with self.assertRaisesRegex(ContractError, field):
                        validate(changed)
            check(math.nextafter(boundary, math.inf), spec, field)
        changed = deepcopy(config)
        changed["parameters"]["omega_start"] = math.nextafter(boundary, math.inf)
        changed["parameters"]["omega_seed"] = changed["parameters"]["omega_start"]
        validate(changed)

    def test_finite_single_emission_can_fail_with_free_and_two_body_passing(self):
        # A local slope .94 < m at the target does not rule out this finite jump.
        target = point("target", 10, 9)
        neighbor = point("neighbor", 10.1, 9.094, parent="target")
        remnant = point("remnant", 6, 4, branch="b")
        other = point("other", 7, 5, parent="remnant", branch="b")
        rows, covered = breakup_thresholds(
            [target], [target, neighbor, remnant, other], 1024, 2
        )
        self.assertTrue(covered)
        negative = [r for r in rows if r["margin"] < -3 * r["error"]]
        self.assertTrue(negative)
        self.assertTrue(all(r["channel"] == "discrete-one-plus-free" for r in negative))
        self.assertTrue(
            all(
                r["margin"] > 3 * r["error"]
                for r in rows
                if r["channel"] != "discrete-one-plus-free"
            )
        )
        self.assertTrue(any(r["threshold"] == 8 for r in negative))

    def test_single_fragment_excludes_only_identity_even_without_edges(self):
        target = point("target", 10, 9)
        nearby = point("nearby", 10 - 1e-4, 9 - 0.94e-4)
        alternate = point("alternate", 10, 8, branch="b")
        rows, covered = breakup_thresholds([target], [target, nearby, alternate], 32, 2)
        self.assertFalse(covered)
        single = [r for r in rows if r["channel"] == "discrete-one-plus-free"]
        self.assertEqual(len(single), 5)
        self.assertFalse(
            any(r["fragment_a"] == "target" and r["sign_a"] == 1 for r in single)
        )
        self.assertTrue(
            any(r["fragment_a"] == "target" and r["sign_a"] == -1 for r in single)
        )
        self.assertTrue(
            any(r["fragment_a"] == "alternate" and r["margin"] == -1 for r in single)
        )
        self.assertTrue(
            any(r["fragment_a"] == "nearby" and r["sign_a"] == 1 for r in single)
        )

    def test_single_fragment_checks_interior_kink_without_charge_grid_rounding(self):
        target = point("target", 10, 9)
        a = point("a", 8, 8.5)
        b = point("b", 12, 8.5, parent="a")
        rows, _ = breakup_thresholds([target], [a, b], 32, 2)
        interior = [
            r for r in rows if r["channel"] == "one-resolved-fragment-plus-free"
        ]
        self.assertEqual(len(interior), 1)
        self.assertEqual(interior[0]["margin"], -0.5)
        self.assertEqual(interior[0]["free_charge"], 0)
        b["parent"] = None
        disconnected, _ = breakup_thresholds([target], [a, b], 32, 2)
        self.assertFalse(
            any(r["channel"] == "one-resolved-fragment-plus-free" for r in disconnected)
        )

    def test_top_level_checks_preserve_mixed_failures_and_composite_verdict(self):
        def selection(name, failure=None, unresolved=None):
            return {
                "point": name,
                "criteria": {
                    key: {
                        "status": (
                            "fail"
                            if key == failure
                            else "unresolved" if key == unresolved else "pass"
                        )
                    }
                    for key in CRITERIA
                    if key not in ("coverage", "selection")
                },
            }

        cases = [
            (
                [selection("a", "binding"), selection("b", "spectrum")],
                True,
                "no-candidate",
                "fail",
            ),
            (
                [selection("a", "binding"), selection("b", unresolved="spectrum")],
                False,
                "unresolved",
                "unresolved",
            ),
            ([selection("a", "binding"), selection("b")], True, "candidate", "pass"),
        ]
        for points, coverage, outcome, expected in cases:
            with self.subTest(outcome=outcome):
                got = selection_checks(points, coverage, outcome)
                checks = {c["id"]: c for c in got["checks"]}
                self.assertEqual(checks["selection"]["status"], expected)
                self.assertEqual(ChargedExperiment().classify(got, {}), expected)
                self.assertEqual(checks["binding"]["status"], "fail")
                self.assertEqual(checks["binding"]["points_by_status"]["fail"], ["a"])
                if outcome == "no-candidate":
                    self.assertEqual(checks["spectrum"]["status"], "fail")
                    self.assertEqual(
                        checks["spectrum"]["points_by_status"]["fail"], ["b"]
                    )
        empty = selection_checks([], False, "unresolved")
        self.assertTrue(all(c["status"] == "unresolved" for c in empty["checks"]))


if __name__ == "__main__":
    unittest.main()
