from __future__ import annotations

from pathlib import Path
from typing import Any

from signal_space.analysis.synthetic import analyze_series
from signal_space.contracts.validation import validate_config
from signal_space.experiments.base import ExperimentPlugin
from signal_space.models.synthetic import EQUATION_REFERENCE, MODEL_ID
from signal_space.reporting.synthetic import render_report
from signal_space.runtime.io import write_json


class SyntheticExperiment(ExperimentPlugin):
    experiment_id = "fixture.synthetic.v1"
    version = "1.0.0"
    model_id = MODEL_ID

    def describe(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "version": self.version,
            "model_id": self.model_id,
            "name": "Deterministic synthetic lifecycle fixture",
            "claims": "none",
            "equations": [EQUATION_REFERENCE],
            "capabilities": ["checkpoint", "resume", "analysis", "report", "fault-injection"],
        }

    def validate(self, config: Any) -> dict[str, Any]:
        return validate_config(config)

    def estimate(self, config: dict[str, Any]) -> dict[str, Any]:
        steps = int(config["parameters"]["steps"])
        delay = float(config["parameters"]["step_delay_ms"]) / 1000
        bytes_estimate = 2048 + steps * 80
        wall = max(0.05, steps * (delay + 0.00002))
        return {
            "cpu_seconds": round(max(0.01, steps * 0.00002), 6),
            "memory_mb": 32,
            "disk_mb": round(bytes_estimate / 1024 / 1024, 6),
            "wall_seconds": round(wall, 6),
            "wall_time_class": "instant" if wall < 1 else "short" if wall < 60 else "bounded-long",
        }

    def prepare(self, config: dict[str, Any], run_path: Path, attempt_path: Path, resume: dict[str, Any] | None) -> dict[str, Any]:
        plan = {
            "schema_version": "research-preparation-v1",
            "domain": {"kind": "integer-index", "start": 0, "end": config["parameters"]["steps"], "unit": "index"},
            "initial_state": {"value": config["parameters"]["initial_value"], "unit": "dimensionless"},
            "solver": {"algorithm": "direct-recurrence-v1", "equation": EQUATION_REFERENCE},
            "resume": resume,
        }
        write_json(attempt_path / "preparation.json", plan)
        return plan

    def run(self, request_path: Path) -> int:
        from signal_space.experiments.synthetic_worker import execute

        return execute(request_path)

    def analyze(self, run_path: Path, analysis_path: Path, config: dict[str, Any]) -> dict[str, Any]:
        attempts = sorted((run_path / "attempts").glob("*/raw/series.csv"))
        if not attempts:
            raise ValueError("no raw series is available for analysis")
        return analyze_series(attempts[-1], analysis_path, config)

    def classify(self, checks: dict[str, Any], config: dict[str, Any]) -> str:
        statuses = {entry["id"]: entry["status"] for entry in checks["checks"]}
        if config["analysis"]["require_complete"] and statuses.get("fixture-complete") != "pass":
            return "unresolved"
        return "pass" if all(value == "pass" for value in statuses.values()) else "fail"

    def report(
        self,
        run_path: Path,
        report_path: Path,
        manifest: dict[str, Any],
        analysis: dict[str, Any],
        render_provenance: dict[str, Any],
    ) -> dict[str, Any]:
        return render_report(
            run_path, report_path, manifest, analysis, render_provenance
        )
