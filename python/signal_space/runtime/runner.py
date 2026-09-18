from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from signal_space.experiments.registry import get_experiment, list_experiments
from signal_space.runtime.errors import CheckpointMismatch, InvalidState, ResourceRejected, RunNotFound
from signal_space.runtime.events import append_event
from signal_space.runtime.io import canonical_bytes, now, read_json, sha256_bytes, sha256_file, write_json
from signal_space.runtime.package import RunPackage, code_identity
from signal_space.runtime.verify import verify_package


class ResearchRuntime:
    def list(self) -> list[dict[str, object]]:
        return list_experiments()

    def validate(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict) or not isinstance(value.get("experiment_id"), str):
            raise ValueError("configuration must name a registered experiment_id")
        return get_experiment(value["experiment_id"]).validate(value)

    def estimate(self, value: Any) -> dict[str, Any]:
        config = self.validate(value)
        estimate = get_experiment(config["experiment_id"]).estimate(config)
        limits = config["resources"]
        rejected = []
        if estimate["memory_mb"] > limits["max_memory_mb"]: rejected.append("memory")
        if estimate["disk_mb"] > limits["max_output_mb"]: rejected.append("output")
        if estimate["wall_seconds"] > limits["max_wall_seconds"]: rejected.append("wall time")
        if estimate["cpu_seconds"] > limits["max_cpu_seconds"]: rejected.append("CPU")
        return {"estimate": estimate, "limits": limits, "accepted": not rejected, "rejected_limits": rejected}

    def run(self, value: Any, workspace: Path) -> dict[str, Any]:
        config = self.validate(value)
        estimate = self.estimate(config)
        if not estimate["accepted"]:
            raise ResourceRejected("resource estimate exceeds: " + ", ".join(estimate["rejected_limits"]))
        plugin = get_experiment(config["experiment_id"])
        package = RunPackage.create(workspace, config, plugin.version)
        return self._attempt(package, plugin, config, None)

    def resume(self, workspace: Path, run_id: str) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        manifest = package.manifest
        candidates = [entry for entry in manifest["attempts"] if entry["state"] in {"cancelled", "interrupted", "failed"} and entry.get("checkpoint")]
        if not candidates:
            raise InvalidState("no resumable terminal attempt with a checkpoint")
        parent = candidates[-1]
        checkpoint_path = package.path / parent["checkpoint"]["path"]
        if not checkpoint_path.is_file() or sha256_file(checkpoint_path) != parent["checkpoint"]["sha256"]:
            raise CheckpointMismatch("checkpoint bytes do not match the recorded hash")
        checkpoint = read_json(checkpoint_path)
        code_hash = sha256_bytes(canonical_bytes(manifest["code_identity"]))
        if checkpoint.get("config_hash") != manifest["config_hash"] or checkpoint.get("code_identity_hash") != code_hash:
            raise CheckpointMismatch("checkpoint config/code identity is incompatible")
        if sha256_bytes(canonical_bytes(code_identity())) != code_hash:
            raise CheckpointMismatch("current code identity differs from the checkpoint producer")
        config = read_json(package.path / "resolved-config.json")
        plugin = get_experiment(manifest["experiment_id"])
        return self._attempt(package, plugin, config, {"checkpoint": checkpoint, "parent": parent})

    def _attempt(self, package: RunPackage, plugin: Any, config: dict[str, Any], resume: dict[str, Any] | None) -> dict[str, Any]:
        manifest = package.manifest
        attempt_id = f"attempt-{len(manifest['attempts']) + 1:04d}"
        relative = f"attempts/{attempt_id}"
        attempt_path = package.path / relative
        attempt_path.mkdir(parents=True)
        parent = resume["parent"] if resume else None
        plugin.prepare(config, package.path, attempt_path, resume["checkpoint"] if resume else None)
        attempt = {
            "schema_version": "research-attempt-v1",
            "attempt_id": attempt_id,
            "parent_attempt_id": parent["attempt_id"] if parent else None,
            "state": "prepared",
            "path": relative,
            "created_at": now(),
            "updated_at": now(),
            "exit_code": None,
            "checkpoint": None,
            "failure": None,
        }
        write_json(attempt_path / "attempt.json", attempt)
        events = attempt_path / "events.jsonl"
        append_event(events, "attempt-prepared", "prepare", {"attempt_id": attempt_id, "parent_attempt_id": attempt["parent_attempt_id"]})

        def add(manifest: dict[str, Any]) -> None:
            manifest["attempts"].append({key: attempt[key] for key in ("attempt_id", "parent_attempt_id", "state", "path", "created_at", "updated_at", "exit_code", "checkpoint", "failure")})
            manifest["technical_state"] = "prepared"
        package.update(add)

        identity_hash = sha256_bytes(canonical_bytes(manifest["code_identity"]))
        request = {
            "config": config,
            "config_hash": manifest["config_hash"],
            "code_identity_hash": identity_hash,
            "seed_ledger": manifest["seed_ledger"],
            "attempt_id": attempt_id,
            "parent_attempt_id": attempt["parent_attempt_id"],
            "attempt_path": str(attempt_path.resolve()),
            "resume_checkpoint": resume["checkpoint"] if resume else None,
            "prior_raw": str((package.path / parent["path"] / "raw/series.csv").resolve()) if parent else None,
        }
        request_path = attempt_path / "request.json"
        write_json(request_path, request, canonical=True)
        log_path = attempt_path / "logs/worker.log"
        log_path.parent.mkdir(parents=True)
        append_event(events, "attempt-running", "runtime", {"limits": config["resources"]})
        attempt["state"] = "running"
        attempt["updated_at"] = now()
        write_json(attempt_path / "attempt.json", attempt)
        self._update_attempt(package, attempt, "running")
        environment = os.environ.copy()
        python_root = str(Path(__file__).resolve().parents[2])
        environment["PYTHONPATH"] = python_root + (os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else "")
        with log_path.open("wb") as log:
            process = subprocess.Popen(
                [sys.executable, "-m", "signal_space.runtime.worker", "--request", str(request_path)],
                stdout=log,
                stderr=subprocess.STDOUT,
                env=environment,
                start_new_session=True,
                preexec_fn=_resource_limiter(config["resources"]) if os.name == "posix" else None,
            )
            attempt["worker_pid"] = process.pid
            write_json(attempt_path / "attempt.json", attempt)
            try:
                exit_code = process.wait(timeout=float(config["resources"]["max_wall_seconds"]))
            except KeyboardInterrupt:
                (attempt_path / "cancel.request").touch()
                append_event(events, "cancellation-requested", "runtime", {"source": "signal"})
                try:
                    exit_code = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGTERM)
                    exit_code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                (attempt_path / "cancel.request").touch()
                append_event(events, "wall-limit-exceeded", "runtime", {"limit_seconds": config["resources"]["max_wall_seconds"]})
                os.killpg(process.pid, signal.SIGTERM)
                exit_code = process.wait(timeout=5)
                exit_code = 124

        size = sum(path.stat().st_size for path in attempt_path.rglob("*") if path.is_file())
        if size > int(config["resources"]["max_output_mb"]) * 1024 * 1024:
            exit_code = 125
            append_event(events, "output-limit-exceeded", "runtime", {"bytes": size})
        state = "completed" if exit_code == 0 else "cancelled" if exit_code == 130 else "interrupted" if exit_code in {77, 124, -signal.SIGTERM} else "failed"
        checkpoints = sorted((attempt_path / "checkpoints").glob("checkpoint-*.json"))
        checkpoint_record = None
        if checkpoints:
            checkpoint = checkpoints[-1]
            checkpoint_record = {"path": checkpoint.relative_to(package.path).as_posix(), "sha256": sha256_file(checkpoint), "step": read_json(checkpoint)["solver_state"]["step"]}
        attempt.update({
            "state": state,
            "updated_at": now(),
            "exit_code": exit_code,
            "checkpoint": checkpoint_record,
            "failure": None if state in {"completed", "cancelled"} else {"code": "PROCESS_INTERRUPTED" if state == "interrupted" else "WORKER_FAILED", "recoverable": bool(checkpoint_record)},
        })
        attempt.pop("worker_pid", None)
        (attempt_path / "cancel.request").unlink(missing_ok=True)
        write_json(attempt_path / "attempt.json", attempt)
        append_event(events, f"attempt-{state}", "runtime", {"exit_code": exit_code, "recoverable": bool(checkpoint_record)})
        self._update_attempt(package, attempt, state)
        result = {"run_id": manifest["run_id"], "attempt_id": attempt_id, "state": state, "exit_code": exit_code, "resumable": bool(checkpoint_record) and state != "completed", "path": str(package.path)}
        return result

    def _update_attempt(self, package: RunPackage, attempt: dict[str, Any], state: str) -> None:
        def change(manifest: dict[str, Any]) -> None:
            for index, entry in enumerate(manifest["attempts"]):
                if entry["attempt_id"] == attempt["attempt_id"]:
                    manifest["attempts"][index] = {key: attempt.get(key) for key in ("attempt_id", "parent_attempt_id", "state", "path", "created_at", "updated_at", "exit_code", "checkpoint", "failure")}
                    break
            manifest["technical_state"] = state
            manifest["completeness"]["attempts_terminal"] = state in {"completed", "cancelled", "interrupted", "failed"}
        package.update(change)

    def status(self, workspace: Path, run_id: str) -> dict[str, Any]:
        return self._package(workspace, run_id).manifest

    def cancel(self, workspace: Path, run_id: str) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        manifest = package.manifest
        running = [entry for entry in manifest["attempts"] if entry["state"] == "running"]
        if not running:
            raise InvalidState("run has no active attempt")
        attempt = running[-1]
        path = package.path / attempt["path"]
        (path / "cancel.request").touch()
        append_event(path / "events.jsonl", "cancellation-requested", "runtime", {"source": "command"})
        return {"run_id": run_id, "attempt_id": attempt["attempt_id"], "state": "cancellation-requested"}

    def analyze(self, workspace: Path, run_id: str) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        manifest = package.manifest
        if not manifest["attempts"]:
            raise InvalidState("run has no attempt output")
        config = read_json(package.path / "resolved-config.json")
        plugin = get_experiment(manifest["experiment_id"])
        analysis_id = f"analysis-{len(manifest['analyses']) + 1:04d}-{int(time.time_ns()) & 0xffffffff:08x}"
        relative = f"analyses/{analysis_id}"
        path = package.path / relative
        before = {artifact["path"]: artifact["sha256"] for artifact in manifest["artifacts"] if artifact["kind"] == "raw"}
        result = plugin.analyze(package.path, path, config)
        classification = plugin.classify(result["checks"], config)
        raw_candidates = sorted(artifact["path"] for artifact in manifest["artifacts"] if artifact["kind"] == "raw" and artifact["path"].endswith("series.csv"))
        record = {
            "schema_version": "research-analysis-v1",
            "analysis_id": analysis_id,
            "path": relative,
            "created_at": now(),
            "input_artifacts": before,
            "raw_source": raw_candidates[-1] if raw_candidates else "",
            "parameters": config["analysis"],
            "code_identity": code_identity(),
            "classification": classification,
            "summary": result["summary"],
            "supersedes": manifest["analyses"][-1]["analysis_id"] if manifest["analyses"] else None,
        }
        write_json(path / "analysis.json", record)

        def change(updated: dict[str, Any]) -> None:
            updated["analyses"].append(record)
            updated["scientific_classification"] = classification
            updated["technical_state"] = "analyzed"
            updated["completeness"]["analysis"] = True
            for criterion in updated["acceptance_criteria"]:
                criterion["evidence"] = f"{relative}/checks.json"
        package.update(change)
        after = {artifact["path"]: artifact["sha256"] for artifact in package.manifest["artifacts"] if artifact["kind"] == "raw"}
        if before != after:
            raise RuntimeError("analysis mutated raw artifacts")
        return record

    def report(self, workspace: Path, run_id: str, analysis_id: str | None = None) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        manifest = package.manifest
        analyses = [entry for entry in manifest["analyses"] if analysis_id is None or entry["analysis_id"] == analysis_id]
        if not analyses:
            raise InvalidState("requested analysis does not exist")
        analysis = analyses[-1]
        report_id = f"report-{len(manifest['reports']) + 1:04d}"
        relative = f"reports/{report_id}"
        output = get_experiment(manifest["experiment_id"]).report(package.path, package.path / relative, manifest, analysis)
        record = {
            "schema_version": "research-report-v1",
            "report_id": report_id,
            "analysis_id": analysis["analysis_id"],
            "path": relative,
            "created_at": now(),
            "required_inputs": [analysis["raw_source"], f"{analysis['path']}/derived/series.csv", f"{analysis['path']}/checks.json"],
            "outputs": output,
        }
        write_json(package.path / relative / "report.json", record)

        def change(updated: dict[str, Any]) -> None:
            updated["reports"].append(record)
            updated["completeness"]["report"] = True
        package.update(change)
        return record

    def verify(self, workspace: Path, run_id: str) -> dict[str, Any]:
        return verify_package(self._package(workspace, run_id).path)

    def _package(self, workspace: Path, run_id: str) -> RunPackage:
        matches = list(workspace.glob(f"*/{run_id}"))
        if len(matches) != 1 or not (matches[0] / "manifest.json").is_file():
            raise RunNotFound(f"run not found: {run_id}")
        return RunPackage(matches[0])


def _resource_limiter(resources: dict[str, Any]):
    def limit() -> None:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (int(resources["max_cpu_seconds"]), int(resources["max_cpu_seconds"])))
        bytes_limit = int(resources["max_memory_mb"]) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (bytes_limit, bytes_limit))
        file_limit = int(resources["max_output_mb"]) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
    return limit
