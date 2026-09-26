"""Registered GROSS Test 2, separated from algebra-only and continuum models."""

from copy import deepcopy
from pathlib import Path

from signal_space.contracts.e01 import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {
    "coverage": "All 4 preparations, both lambdas, 12 events and all declared comparisons are saved",
    "conservation": "N, memory norm, J, event H, projector and complete-cut charge residuals below 1e-9 at both tolerances",
    "exact-reference": "Reciprocal and frozen numerical trajectories agree with independent closed solutions below 1e-9",
    "tolerance-refinement": "Halving rtol and atol changes the circuit state and overlap records by less than 1e-9",
    "rescheduling": "Permissible schedules agree on states and event overlap records below 1e-9",
    "local-frames": "Independent U(2) event frames with transformed wire transport agree below 1e-9",
    "causal-jacobian": "Outside-ancestor response below 1e-9; nonzero inside response above 1e-4 at both difference steps",
    "jacobian-refinement": "Halving the central-difference step changes the Jacobian by less than 1e-6",
    "shared-memory-order": "Reversing the shared-memory control changes its final projector by more than 1e-4 in each preparation",
    "frozen-memory": "Freezing driven memory exposes matrix-charge error above 1e-4; reciprocal memory responds above 1e-4",
}


class ReciprocalExperiment(ExperimentPlugin):
    experiment_id = "gross.reciprocal-events.v1"
    version = "1.0.0"
    model_id = "signal-space.ss-ops-1.v1"

    def describe(self):
        return {"experiment_id": self.experiment_id, "version": self.version, "model_id": self.model_id,
                "name": "Signal Space / GROSS Test 2: reciprocal events and rescheduling",
                "claims": "finite event-law audit only; no propagation metric or clock",
                "equations": ["Operator Program v0.2 sections 5 and 15.2"],
                "equation_sources": [{"label": "Reciprocal event protocol", "path": "docs/research/gross-test-02.md", "catalog_id": "gross-test-02"}],
                "capabilities": ["analysis", "report", "local-circuit", "causal-jacobian"],
                "unavailable_capabilities": ["checkpoint", "resume", "metric inference", "clock", "full spectrum"]}

    def schema(self):
        value = read_json(ROOT / "contracts/research/reciprocal.schema.json")
        value["default"] = read_json(ROOT / "fixtures/research/gross-test-02.json")
        return value

    def validate(self, config):
        check(config, self.schema())
        return deepcopy(config)

    def acceptance_criteria(self, config):
        return [{"id": k, "description": v, "evidence": None} for k, v in CRITERIA.items()]

    def known_gaps(self, config):
        return ["Finite acyclic circuit, not an emergent metric or autonomous clock.",
                "Flat wire transport; local U(2) covariance does not establish Lorentz covariance.",
                "Jacobian tested on one preparation at two lambdas; finite differences are not a global proof.",
                "No spatial grid or continuum boundary; circuit incidence is assumed. Complete-cut charge is not identified as energy-momentum.",
                "No checkpoint/resume; interrupted attempts require a new bounded run."]

    def estimate(self, config):
        return {"cpu_seconds": 75, "memory_mb": 256, "disk_mb": 12,
                "wall_seconds": 90, "wall_time_class": "short"}

    def prepare(self, config, run_path, attempt_path, resume):
        if resume:
            raise ValueError("Test 2 does not support resume")
        value = {"model": self.model_id, "method": "DOP853-circuit-v1", "parameters": config["parameters"],
                 "units": config["units"], "source": "docs/research/gross-test-02.md"}
        write_json(attempt_path / "preparation.json", value)
        return value

    def run(self, request_path):
        from signal_space.numerics.reciprocal import execute
        return execute(request_path)

    def analyze(self, run_path, analysis_path, config):
        from signal_space.analysis.reciprocal import analyze
        return analyze(run_path, analysis_path, config)

    def classify(self, checks, config):
        statuses = {c["id"]: c["status"] for c in checks["checks"]}
        if set(statuses) != set(CRITERIA) or statuses.get("coverage") != "pass":
            return "unresolved"
        return "pass" if all(v == "pass" for v in statuses.values()) else "fail"

    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.reciprocal import render_report
        return render_report(run_path, report_path, manifest, analysis, render_provenance)
