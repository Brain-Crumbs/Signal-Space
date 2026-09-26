"""Registered bounded Test 1; independent of Candidate A/B evolution."""

from copy import deepcopy
from pathlib import Path

from signal_space.contracts.e01 import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {
    "coverage": "All seeded samples and declared controls are saved and independently checked",
    "identities": "All scale-normalized well-conditioned residuals are strictly below 1e-10",
    "positive-observer": "All valid observer forms and norms are positive",
    "tetrahedral": "Gram spectrum is (-1/3,-1/3,-1/3,1) within 1e-10",
    "weight-control": "Correct weights pass; deliberately omitted weights give error above 1e-3",
    "singular-domain": "Rank-one aggregate is rejected, near-collinear samples classified without regularization",
}


class OperatorExperiment(ExperimentPlugin):
    experiment_id = "gross.operator-identities.v1"
    version = "1.0.0"
    model_id = "signal-space.operator-constitution.v1"

    def describe(self):
        return {"experiment_id": self.experiment_id, "version": self.version, "model_id": self.model_id,
                "name": "Signal Space / GROSS Test 1: operator and observer identities",
                "claims": "algebra and implementation checks only",
                "equations": ["Operator Program v0.2 sections 2-4 and 15.1"],
                "equation_sources": [{"label": "Operator Test 1 protocol", "path": "docs/research/gross-test-01.md", "catalog_id": "gross-test-01"}],
                "capabilities": ["analysis", "report", "seeded-matrix-controls"],
                "unavailable_capabilities": ["checkpoint", "resume", "physical evolution", "spacetime emergence"]}

    def schema(self):
        value = read_json(ROOT / "contracts/research/operators.schema.json")
        value["default"] = read_json(ROOT / "fixtures/research/gross-test-01.json")
        return value

    def validate(self, config):
        check(config, self.schema())
        return deepcopy(config)

    def acceptance_criteria(self, config):
        return [{"id": k, "description": v, "evidence": None} for k, v in CRITERIA.items()]

    def known_gaps(self, config):
        return ["Finite seeded algebra screen, not a proof or a dynamics/geometry experiment.",
                "Condition number above 100 is outside the acceptance domain; near-singular controls remain explicit.",
                "No spatial boundary, timestep, conservation or detector record is evaluated; these require later tests.",
                "No checkpoint/resume for this short atomic matrix batch; interrupted attempts remain preserved."]

    def estimate(self, config):
        n = config["parameters"]["samples"]
        return {"cpu_seconds": max(1, n * 0.01), "memory_mb": 192,
                "disk_mb": 2 + n * 0.004, "wall_seconds": max(2, n * 0.015), "wall_time_class": "short"}

    def prepare(self, config, run_path, attempt_path, resume):
        if resume:
            raise ValueError("Test 1 does not support resume")
        value = {"model": self.model_id, "method": "direct-matrix-v1",
                 "parameters": config["parameters"], "units": config["units"],
                 "source": "docs/research/gross-test-01.md", "physical_evolution": False}
        write_json(attempt_path / "preparation.json", value)
        return value

    def run(self, request_path):
        from signal_space.numerics.operators import execute
        return execute(request_path)

    def analyze(self, run_path, analysis_path, config):
        from signal_space.analysis.operators import analyze
        return analyze(run_path, analysis_path, config)

    def classify(self, checks, config):
        statuses = {c["id"]: c["status"] for c in checks["checks"]}
        if statuses.get("coverage") != "pass":
            return "unresolved"
        return "pass" if all(v == "pass" for v in statuses.values()) else "fail"

    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.operators import render_report
        return render_report(run_path, report_path, manifest, analysis, render_provenance)
