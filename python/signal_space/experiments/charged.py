"""Registered E01 plugin; all adapters call the same bounded worker."""

from signal_space.experiments.base import ExperimentPlugin
from signal_space.contracts.e01 import schema, validate, ROOT
from signal_space.runtime.io import read_json, write_json

CRITERIA = {
    "stationary": "Nodeless nonvacuum profile; independent field and virial residuals",
    "continuation": "Connected branch, frequency-step refinement and conditioned dE/dQ",
    "convergence": "Independent spacing, volume and solver-tolerance comparisons",
    "spectrum": "Charge-constrained coupled eigenpairs, symmetry modes and spectral refinement",
    "angular": "All declared angular sectors and a bound on remaining sectors",
    "binding": "Free-charge and computed fragmentation margins exceed 3 combined numerical errors",
    "selection": "At least one resolved candidate within the preregistered domain; fail only when every point has a resolved disqualifier",
    "coverage": "Preregistered seed/endpoint coverage and all pending work completed",
}


class ChargedExperiment(ExperimentPlugin):
    experiment_id = "e01-charged-branch"
    version = "1.0.0"
    model_id = "charged-scalar-3d-v1"

    def describe(self):
        return {
            "experiment_id": self.experiment_id,
            "version": self.version,
            "model_id": self.model_id,
            "name": "E01 · 3D charged recurrence branch and stability",
            "claims": "stationary / below tested thresholds / linear stability only when criterion-linked checks resolve",
            "equations": ["charged-recurrence-winding-hopf.md §§2–10,14–15,23"],
            "equation_sources": [
                {
                    "label": "E01 authoritative protocol",
                    "path": "docs/research/first-experiment.md",
                    "catalog_id": "e01-protocol",
                }
            ],
            "capabilities": [
                "radial-continuation",
                "constrained-spectra",
                "refinement",
                "checkpoint",
                "resume",
                "analysis",
                "report",
            ],
            "unavailable_capabilities": [
                "nonlinear stability",
                "global minimum proof",
                "Hopf binding",
                "particle identification",
            ],
        }

    def schema(self):
        value = schema()
        value["default"] = read_json(ROOT / "fixtures/research/e01-smoke.json")
        value["x-presets"] = [
            {"name": "Small validation fixture", "config": value["default"]},
            {
                "name": "Author research run (opt-in)",
                "config": read_json(ROOT / "fixtures/research/e01-research.json"),
            },
        ]
        return value

    def acceptance_criteria(self, config):
        return [
            {"id": key, "description": value, "evidence": None}
            for key, value in CRITERIA.items()
        ]

    def known_gaps(self, config):
        return [
            "Finite preregistered seed, frequency, angular and fragment coverage; no global or nonlinear stability claim.",
            "Failed continuation at a fold is retained as unresolved; no pseudo-arclength traversal is asserted.",
            (
                "Small fixture is not a research finding."
                if not config["parameters"]["research_run"]
                else "Research scan requires author interpretation of saved evidence."
            ),
        ]

    def validate(self, config):
        return validate(config)

    def estimate(self, config):
        p = config["parameters"]
        n = p["spectral_nodes"]
        sectors = p["ell_max"] + 1
        points = p["max_points"]
        factor = 10 if p["refinements"] else 1
        cpu = (
            max(1.0, points * factor * sectors * (n / 32) ** 3 * 0.06)
            + points**3 / 100000
        )
        disk = (
            points
            * factor
            * (p["sample_points"] * 130 + sectors * n * n * 256)
            / 1024**2
        )
        return {
            "cpu_seconds": round(cpu, 2),
            "memory_mb": int(256 + ((8 * n) ** 2 * 8 * 12) / 1024**2),
            "disk_mb": round(disk + points**3 * 0.0005, 2),
            "wall_seconds": round(cpu * 1.5, 2),
            "wall_time_class": (
                "research-opt-in" if p["research_run"] else "small-fixture"
            ),
        }

    def prepare(self, config, run_path, attempt_path, resume):
        from signal_space.models.charged_scalar import EQUATIONS, SOURCE

        plan = {
            "schema_version": "e01-preparation-v1",
            "source": SOURCE,
            "equations": EQUATIONS,
            "units": config["units"],
            "normalization": {
                "eta": 1,
                "lambda_4": 0.01,
                "zeta": 0.1,
                "neutral_field": 0,
            },
            "solver": "scipy solve_bvp singular-origin collocation, spherical Robin tail",
            "spectrum": "full dense eig; w=rU,z=rV; deltaQ null-space projection; exp(sigma*t)",
            "resume": resume is not None,
            "parameters": config["parameters"],
        }
        write_json(attempt_path / "preparation.json", plan)
        return plan

    def run(self, request_path):
        from signal_space.experiments.charged_worker import execute

        return execute(request_path)

    def analyze(self, run_path, analysis_path, config):
        from signal_space.analysis.charged import analyze

        return analyze(run_path, analysis_path, config)

    def classify(self, checks, config):
        return {
            "candidate": "pass",
            "no-candidate": "fail",
            "unresolved": "unresolved",
        }[checks["outcome"]]

    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.charged import render_report

        return render_report(
            run_path, report_path, manifest, analysis, render_provenance
        )
