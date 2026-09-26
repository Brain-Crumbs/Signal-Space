#!/usr/bin/env python3
"""Run a reviewed experiment recipe and prepare downloadable evidence, without Git writes."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from experiment_contract import digest, validate_bundle, validate_plan, verify_runtime_config

ROOT = Path(__file__).resolve().parents[2]
# A new experiment requires a reviewed, locked plan and its report/assessment adapter.
RECIPES = {"gross-test-01": "docs/research/plans/gross-test-01.json",
           "gross-test-02": "docs/research/plans/gross-test-02.json",
           "gross-test-03": "docs/research/plans/gross-test-03.json",
           "gross-test-04": "docs/research/plans/gross-test-04.json"}
RECIPES["gross-test-07"] = "docs/research/plans/gross-test-07.json"
RECIPES["gross-test-07-order4"] = "docs/research/plans/gross-test-07-order4.json"
RECIPES["gross-test-07-transfer"] = "docs/research/plans/gross-test-07-transfer.json"
RECIPES["gross-test-05"] = "docs/research/plans/gross-test-05.json"
RECIPES["gross-test-06"] = "docs/research/plans/gross-test-06-v2.json"
for kind in ("longevity", "response"):
    RECIPES[f"gross-test-06-{kind}"] = f"docs/research/plans/gross-test-06-{kind}.json"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def assessment(manifest: dict, analysis: dict, checks: dict) -> str:
    """A conditional, evidence-derived assessment; not a human or AI review."""
    if manifest.get("experiment_id") == "gross.reception-transfer.v1":
        lines = ["# Test 7 discrete-transfer assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "Scientific review and visual inspection remain pending.", "",
                 "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "The full interval budget must resolve the second-to-fourth-order separation on both spectra.",
                  "The discrete inverse assumes known support and incoming preparation; no response coefficient is fitted.",
                  "Original Test 7 remains failed. Test 8 requires separate acceptance review.",
                  "Two-object recoil, invariance, gravity, angular stability and emergent spacetime remain untested."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.reception-order4.v1":
        lines = ["# Test 7 formal fourth-order follow-up", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "Original Test 7 failed and retains its original result. The inspected-history amplitude comparison is diagnostic.",
                 "The new held-out radial waveform uses saved upstream records, locked predictions and local markers.",
                 "", "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "A technical pass of this follow-up does not retroactively pass Test 7 or authorize Test 8.",
                  "Known-Z optical inversion is approximate; evaluate remaining spatial timing error before a two-object protocol.",
                  "No two-object recoil, coordinate invariance, gravity or emergent spacetime is tested."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.reception.v1":
        lines = ["# Test 7: surface-only reception assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "", "Scientific interpretation and visual review remain pending.", "",
                 "| Check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "Surface-only inversion and time-dependent Taylor predictions precede the held-out nonlinear receiver.",
                  "Local threshold markers define an interval; the quiet history at those times is a counterfactual reference.",
                  "Radial origin reflection supplies opposite propagation directions. No recoil or observer invariance is claimed.",
                  "Next: resolve any failed interval or numerical gate before Test 8. If accepted, register two surviving objects and conservation of exchanged momentum."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.router-propagation.v1":
        return router_assessment(manifest, analysis, checks)
    if manifest.get("experiment_id") == "gross.full-spectrum.v1":
        return floquet_assessment(manifest, analysis, checks)
    if manifest.get("experiment_id") == "gross.continuum-action.v1":
        lines = ["# Test 5 continuum action: automated assessment", "",
                 "Scientific interpretation and visual review remain pending.", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; bounded classification {analysis['classification']}.", "",
                 "| Check | Status | Value |", "| --- | --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} | {c.get('value')} |" for c in checks['checks']]
        lines += ["", "The common matter cone is selected by the action. Frozen local jets do not establish emergence, a bound clock, nonlinear Einstein evolution or constraint-satisfying initial data.",
                  "", "Next: Test 6 core profile and independently resolved bound clock eigenmode; require branch and finite-domain convergence before reception work."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.bound-clock.v1":
        lines = ["# Test 6 bound clock: automated assessment", "",
                 "Human scientific interpretation and visual review remain separate.", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; bounded classification {analysis['classification']}.", "",
                 "| Check | Status | Value |", "| --- | --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} | {c.get('value')} |" for c in checks['checks']]
        lines += ["", "This is a spherical flat decoupling calculation. An accepted radial lifetime does not establish nonspherical stability, gravity, reception or emergent geometry.",
                  "", "Next: if accepted, freeze the local clock calibration and preregister Test 7 incident neutral pulses and predicted local response before measuring reception; otherwise resolve the failing branch, mode or lifetime gate."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") in ("gross.clock-longevity.v1", "gross.clock-response.v1"):
        lines = ["# Test 6 prerequisite: automated assessment", "",
                 "Scientific interpretation and visual review remain pending.", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.", "",
                 "| Check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks["checks"]]
        lines += ["", "Frozen radial profiles; no nonspherical beam, recoil, gravity or emergent spacetime claim.",
                  "The concentric-shell response uses an ideal local clock probe. Historical energy diagnostics do not resolve tiny clock radiation.",
                  "Next: inspect numerical and tick-shift errors, then specify upstream-characteristic-only prediction and physical marker events before a two-object link."]
        return "\n".join(lines) + "\n"
    classification = manifest["scientific_classification"]
    reciprocal = manifest.get("experiment_id") == "gross.reciprocal-events.v1"
    next_step = (
        "Proceed to Test 3 exact-router dispersion with orthogonal, oblique and collinear triads, reversed order and full-zone inspection; keep physical memory modes for Test 4 and directional controls for Test 11."
        if classification == "pass" and reciprocal else
        "Proceed to the Test 2 reciprocal-event conservation derivation; Test 5's action audit is an independent branch."
        if classification == "pass" else
        "Resolve the failed, unresolved or unevaluated checks before using this run to support the next experiment."
    )
    lines = ["# Experiment analysis and next calculation", "",
             "Automated assessment from saved checks. Scientific interpretation and visual review remain pending.", "",
             f"Run: `{manifest['run_id']}`. Analysis: `{analysis['analysis_id']}`.",
             f"Scientific classification: **{classification}**.", "",
             "| Check | Status | Measured value |", "| --- | --- | --- |"]
    lines += [f"| {c['id']} | {c['status']} | {c.get('value', 'not reported')} |" for c in checks["checks"]]
    lines += ["", "Evidence: `results/tables/checks.json`, `results/tables/analysis.json`, and the exact plotted data in `results/data/plot-data/`.",
              "", "## Meaning and limits", "",
              ("The checks audit a finite reciprocal circuit, its conserved matrix ledger, permissible scheduling and causal Jacobian. Exact-solution and half-tolerance comparisons control integration error. Flat transport and U(2) covariance do not establish Lorentz covariance, mechanical recoil, a clock or an emergent metric. Spatial boundary and continuum convergence are not evaluated because no spatial mesh is supplied."
               if reciprocal else "The checks test algebra and its numerical implementation in the locked conditioning domain. They do not establish physical propagation, clock behavior, or emergent spacetime. Finite sampling does not replace an exact proof."),
              "", "## Next calculation", "", next_step, "",
              ("Competing signatures for the next calculation: long-wavelength dispersion follows the projector Gram matrix; collinear triads become degenerate; reversed order changes finite-band terms. Do not hide stationary memory modes or identify the circuit labels with measured spacetime."
               if reciprocal else "The next discrimination is whether the specified reciprocal update conserves its declared aggregate under permissible event rescheduling. Derive the invariant and ordering assumptions before coding that dynamics."),
              "", "Review every figure and its limitations before promoting the result to a research conclusion."]
    return "\n".join(lines) + "\n"


def router_assessment(manifest: dict, analysis: dict, checks: dict) -> str:
    status = manifest['scientific_classification']
    lines = ['# Router propagation: analysis and next calculation', '',
             'Automated assessment; scientific interpretation and visual review remain pending.', '',
             f"Run: {manifest['run_id']}. Analysis: {analysis['analysis_id']}. Classification: **{status}**.", '',
             '| Check | Status | Value |', '| --- | --- | --- |']
    lines += [f"| {r['id']} | {r['status']} | {r.get('value')} |" for r in checks['checks']]
    lines += ['', 'Evidence: results/tables/checks.json and results/data/plot-data/.', '',
              'This audits the homogeneous zero-wave linear router: supplied incidence, frozen background projectors, two wave bands. The Gram cone is predicted before execution; no metric fit is used. Collinear rank loss and order reversal are physical controls.', '',
              'Conservation means total wave amplitude norm. Periodic boxes check the explicit shifts; exact blocks have no PDE timestep or outgoing boundary. Group derivatives exclude band touchings, which remain in the saved spectrum. Extra full-zone nodes are detections, not a completeness or particle-species claim.', '',
              'No autonomous clock, invariant detector record, full-sector metric or emergent spacetime is established. Stationary physical memory modes are not removed from the full model. Finite-band directional asymmetry is not a leading identity drift.', '',
              ('Next: Test 4 complete zero-wave tangent spectrum, retaining stationary memory variations. A common-cone claim predicts all physical sectors; the known zero-wave obstruction instead predicts propagating waves plus physical stationary memory. A nonzero periodic background requires its own self-consistent full-circuit solution and a separately locked plan.'
               if status == 'pass' else 'Resolve the failed or incomplete checks before drawing a wave-cone conclusion; preserve this run and its thresholds.'), '',
              'Test 11 spectral diagnostics are preliminary here; operational drift tests still require an accepted clock and description-invariant local record.']
    return '\n'.join(lines) + '\n'


def floquet_assessment(manifest, analysis, checks):
    lines = ['# Full reciprocal spectrum: analysis and next calculation', '',
             'Automated assessment; visual and scientific review remain pending.', '',
             f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.", '',
             '| Check | Status | Value |', '| --- | --- | --- |']
    lines += [f"| {c['id']} | {c['status']} | {c.get('value')} |" for c in checks['checks']]
    lines += ['', 'Evidence: results/tables/checks.json and results/data/plot-data/summary.json.', '',
              'Twenty physical real tangent dimensions include twelve memory orientations. Only unobservable memory spinor phases are removed. Vacuum and equal-port backgrounds have physical stationary memories; the opposing-port background tests genuine backreaction. Failures of the strong cone criterion are scientific outcomes, not pipeline failures.', '',
              'The six-gate routing is an explicit additional incidence assumption, not a nonlinear extension proven equivalent to the Test 3 reduced stencil. Floquet growth and tangent norms are not kinetic energy or a nonlinear stability theorem. Degenerate eigenspaces have basis-dependent mode participation.', '',
              'Test 11: paired spectral sectors exhibit routing-derived drift. They are not invariant clock records; a common coordinate drift cannot eliminate a difference between port-sector drift vectors.', '',
              'Next: derive a non-collinear, unequal-port periodic background with active memory response, then preregister its complete tangent and stability tests. A shared-cone candidate must predict withheld memory and port sectors; the alternative requires a derived material response and autonomous clock, not a new label for unexplained modes. Generic backgrounds, clocks and emergent spacetime remain unresolved.']
    return '\n'.join(lines) + '\n'


class Pipeline:
    def __init__(self, repo: Path, output: Path, experiment: str):
        self.repo, self.output, self.experiment = repo.resolve(), output.resolve(), experiment
        if self.output.is_relative_to(self.repo):
            raise ValueError("output must be outside the checkout so generated files cannot dirty source provenance")
        self.output.mkdir(parents=True, exist_ok=False)
        self.evidence = self.output / "evidence"
        self.logs = self.evidence / "logs"
        self.logs.mkdir(parents=True)
        self.workspace = self.evidence / "runs"
        self.env = {**os.environ, "PYTHONPATH": str(self.repo / "python"),
                    "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "MPLBACKEND": "Agg"}
        self.status = {"experiment": experiment, "technical_status": "running",
                       "scientific_classification": "not-evaluated", "stage": "preflight"}

    def command(self, stage: str, args: list[str], timeout: int = 180) -> str:
        self.status["stage"] = stage
        write_json(self.evidence / "status.json", self.status)
        print(f"[{stage}]", flush=True)
        # Write directly to disk: even a timed-out command retains partial output.
        with (self.logs / f"{stage}.stdout.log").open("w") as stdout, (self.logs / f"{stage}.stderr.log").open("w") as stderr:
            result = subprocess.run(args, cwd=self.repo, env=self.env, stdout=stdout, stderr=stderr, timeout=timeout)
        if result.returncode:
            raise RuntimeError(f"{stage} exited {result.returncode}; see logs/{stage}.stderr.log and .stdout.log")
        return (self.logs / f"{stage}.stdout.log").read_text(encoding="utf-8")

    def runtime(self, stage: str, run_id: str) -> dict:
        return json.loads(self.command(stage, [sys.executable, "-m", "signal_space", "--workspace", str(self.workspace), stage, "--run-id", run_id]))

    def execute(self) -> None:
        if self.command("source-status", ["git", "status", "--porcelain"]).strip():
            raise ValueError("commit source changes before executing; a clean checkout is required")
        revision = self.command("source-revision", ["git", "rev-parse", "HEAD"]).strip()
        tree = self.command("source-tree", ["git", "rev-parse", "HEAD^{tree}"]).strip()
        self.status["source_commit"] = revision
        plan_path = self.repo / RECIPES[self.experiment]
        plan = json.loads(plan_path.read_text())
        validate_plan(plan)
        config = verify_runtime_config(plan, self.repo)
        shutil.copy2(plan_path, self.evidence / "plan.json")
        shutil.copy2(config, self.evidence / "config.json")
        # Portable source recovery even if a development branch is later removed.
        self.command("source-snapshot", ["git", "archive", "--format=tar.gz", "--output", str(self.evidence / "source.tar.gz"), revision])
        github = {key: self.env.get(key) for key in (
            "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_WORKFLOW_REF", "GITHUB_WORKFLOW_SHA",
            "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SERVER_URL", "RUNNER_OS", "RUNNER_ARCH")}
        write_json(self.evidence / "execution.json", {"source_commit": revision, "source_tree": tree,
                   "source_archive_sha256": digest((self.evidence / "source.tar.gz").read_bytes()),
                   "github": github, "plan_path": RECIPES[self.experiment], "plan_lock": plan["locked_sha256"]})
        output = self.command("run-plan", [sys.executable, str(self.repo / ".agents/scripts/run_plan.py"),
                              "--plan", str(plan_path), "--repo-root", str(self.repo),
                              "--workspace", str(self.workspace), "--execute"],
                              timeout=plan["resources"]["max_wall_seconds"] + 60)
        stages = [json.loads(line) for line in output.splitlines() if line.strip()]
        run = next(item["result"] for item in stages if item["stage"] == "run")
        if run["state"] != "completed":
            raise ValueError(f"solver did not complete: {run['state']}")
        run_id = run["run_id"]
        self.status["run_id"] = run_id
        run_path = Path(run["path"]).resolve()
        if not run_path.is_relative_to(self.workspace.resolve()):
            raise ValueError("runtime returned a path outside this attempt's workspace")
        analysis = self.runtime("analyze", run_id)
        self.status["scientific_classification"] = analysis["classification"]
        report = self.runtime("report", run_id)
        verified = self.runtime("verify", run_id)
        if not verified["valid"]:
            raise ValueError("canonical package verification failed")
        manifest = json.loads((run_path / "manifest.json").read_text())
        checks = json.loads((run_path / analysis["path"] / "checks.json").read_text())
        mentor = self.evidence / "automated-assessment.md"
        mentor.write_text(assessment(manifest, analysis, checks), encoding="utf-8")
        locator = f"research/experiments/{manifest['experiment_id']}/{run_id}"
        self.command("package", [sys.executable, str(self.repo / ".agents/scripts/package_experiment.py"),
                     "--run", str(run_path), "--plan", str(plan_path),
                     "--interpretations", str(run_path / report["path"] / "interpretations.json"),
                     "--mentor", str(mentor), "--source-dir", str(self.repo / "python/signal_space"),
                     "--source-locator", locator, "--output", str(self.output / "reader")])
        validate_bundle(self.output / "reader")
        self.status.update({"technical_status": "completed", "stage": "complete",
                            "analysis_id": analysis["analysis_id"], "report_id": report["report_id"],
                            "canonical_path": run_path.relative_to(self.evidence).as_posix(),
                            "repository_destination": locator, "checks": checks["checks"]})

    def run(self) -> int:
        started = time.monotonic()
        code = 0
        try:
            self.execute()
        except (Exception, KeyboardInterrupt) as error:
            code = 1
            self.status.update({"technical_status": "failed", "error": f"{type(error).__name__}: {error}"})
            print(self.status["error"], file=sys.stderr)
        finally:
            self.status["elapsed_seconds"] = round(time.monotonic() - started, 3)
            write_json(self.evidence / "status.json", self.status)
            text = self.summary()
            (self.evidence / "README.md").write_text(text, encoding="utf-8")
            if self.env.get("GITHUB_STEP_SUMMARY"):
                with Path(self.env["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as handle:
                    handle.write(text)
            # Outer ledger includes logs and metadata; canonical/reader ledgers stay untouched.
            files = [{"path": p.relative_to(self.evidence).as_posix(), "sha256": digest(p.read_bytes())}
                     for p in sorted(self.evidence.rglob("*")) if p.is_file() and p.name != "evidence-index.json"]
            write_json(self.evidence / "evidence-index.json", {"files": files})
        return code

    def summary(self) -> str:
        lines = [f"# Experiment: {self.experiment}", "",
                 f"Technical pipeline: **{self.status['technical_status']}**. Scientific classification: **{self.status['scientific_classification']}**.",
                 f"Last stage: `{self.status['stage']}`. Elapsed: {self.status['elapsed_seconds']} seconds.",
                 f"Source commit: `{self.status.get('source_commit', 'unavailable')}`.",
                 f"Run: `{self.status.get('run_id', 'not created or interrupted; inspect runs/')}`.", ""]
        if "error" in self.status:
            lines += [f"Failure: {self.status['error']}", "", "Partial evidence is diagnostic, not a completed reader export.", ""]
        if self.status.get("checks"):
            lines += ["| Check | Status | Value |", "| --- | --- | --- |"]
            lines += [f"| {c['id']} | {c['status']} | {c.get('value', '')} |" for c in self.status["checks"]]
        lines += ["", "Download the evidence and reader artifacts from this workflow run. Evidence contains `runs/`, source snapshot, plan, config, stage logs and `execution.json`. The reader export contains PDFs, figures, data and an automated assessment; human interpretation and visual review remain pending.",
                  "", "The reader's source locator names the intended repository destination if you choose to check in this run. Until then, the canonical bytes are under this evidence package's `runs/` directory. No results are automatically committed.",
                  "", "Artifacts expire under the chosen retention policy. Preserve selected results before expiry. See `docs/research/github-actions.md` in the source snapshot for verification and manual check-in instructions."]
        return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", choices=RECIPES, default="gross-test-01")
    parser.add_argument("--output", required=True, type=Path, help="new directory outside the checkout")
    args = parser.parse_args()
    try:
        return Pipeline(ROOT, args.output, args.experiment).run()
    except (OSError, ValueError) as error:
        print(f"experiment rejected: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
