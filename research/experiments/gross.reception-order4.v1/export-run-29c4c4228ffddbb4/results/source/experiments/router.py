"""Registered GROSS Test 3, separated from algebra-only and continuum models."""

from copy import deepcopy
from pathlib import Path

from signal_space.contracts.e01 import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {'coverage': 'Save all 3 triads, 2 orders, 26 signed directions, 4 radii, both zone and box sizes, rotation and derivative comparisons.', 'fourier-circuit': 'Stencil matrix agrees with independent matrix exponentials and real-space fields with FFT reference to <1e-10.', 'conservation': 'Matrix unitarity, det U=1 and total wave norm errors <1e-10.', 'continuum': 'Maximum |phase^2-q.G.q|/|q|^2 <0.02 at radius 0.02; each adjacent fine/coarse error envelope ratio <0.65 unless coarse error <=1e-10.', 'triad-rank': 'Gram matrix ranks [3,3,1] for orthogonal, oblique, collinear, with rank tolerance 1e-10.', 'order-control': 'Orthogonal trace matches the signed triple-sine formula to <1e-10; maximum order phase difference >1e-4 for each independent triad.', 'rotation': 'Common SU(2) conjugation agrees with rotated-projector stencil to <1e-10.', 'group-refinement': 'Central steps 1e-5 and 5e-6 agree with independent analytic quaternion derivative and each other to <1e-6 away from band touchings (vector norm >1e-6).', 'full-zone': 'Both 16^3/32^3 periodic-zone samples agree with quaternion reference to <1e-10; nested samples agree <1e-10; explicit node probes agree <1e-10; orthogonal grids detect >1 zero node and >=1 pi node.'}


class RouterExperiment(ExperimentPlugin):
    experiment_id = "gross.router-propagation.v1"
    version = "1.0.0"
    model_id = "signal-space.ss-ops-1.router-linear.v1"

    def describe(self):
        return {"experiment_id": self.experiment_id, "version": self.version, "model_id": self.model_id,
                "name": "Signal Space / GROSS Test 3: router propagation",
                "claims": "homogeneous linear wave-sector cone audit; no full-sector metric or clock",
                "equations": ["Operator Program v0.2 sections 5.5, 6 and 15.3"],
                "equation_sources": [{"label": "Router propagation protocol", "path": "docs/research/gross-test-03.md", "catalog_id": "gross-test-03"}],
                "capabilities": ["analysis", "report", "exact-fourier", "group-velocity"],
                "unavailable_capabilities": ["checkpoint", "resume", "metric inference", "clock", "full spectrum"]}

    def schema(self):
        value = read_json(ROOT / "contracts/research/router.schema.json")
        value["default"] = read_json(ROOT / "fixtures/research/gross-test-03.json")
        return value

    def validate(self, config):
        check(config, self.schema())
        return deepcopy(config)

    def acceptance_criteria(self, config):
        return [{"id": k, "description": v, "evidence": None} for k, v in CRITERIA.items()]

    def known_gaps(self, config):
        return ["Homogeneous zero-wave linear wave sector; physical memory modes not audited.",
                "Incidence, three routing directions and scale conversions are assumed.",
                "Finite full-zone sampling does not prove nodal completeness or particle identity.",
                "No bound clock, physical detector or local timing record.",
                "No checkpoint/resume; preserve interrupted attempts."]

    def estimate(self, config):
        return {"cpu_seconds": 30, "memory_mb": 256, "disk_mb": 12,
                "wall_seconds": 45, "wall_time_class": "short"}

    def prepare(self, config, run_path, attempt_path, resume):
        if resume:
            raise ValueError("Test 3 does not support resume")
        value = {"model": self.model_id, "method": "port-stencil-fourier-v1", "parameters": config["parameters"],
                 "units": config["units"], "source": "docs/research/gross-test-03.md"}
        write_json(attempt_path / "preparation.json", value)
        return value

    def run(self, request_path):
        from signal_space.numerics.router import execute
        return execute(request_path)

    def analyze(self, run_path, analysis_path, config):
        from signal_space.analysis.router import analyze
        return analyze(run_path, analysis_path, config)

    def classify(self, checks, config):
        statuses = {c["id"]: c["status"] for c in checks["checks"]}
        if set(statuses) != set(CRITERIA) or statuses.get("coverage") != "pass":
            return "unresolved"
        if any(v in {"unresolved", "not-evaluated"} for v in statuses.values()):
            return "unresolved"
        return "pass" if all(v == "pass" for v in statuses.values()) else "fail"

    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.router import render_report
        return render_report(run_path, report_path, manifest, analysis, render_provenance)
