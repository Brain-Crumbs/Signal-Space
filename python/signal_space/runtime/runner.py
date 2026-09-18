from __future__ import annotations

import os
import signal
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

from signal_space.experiments.registry import get_experiment, list_experiments
from signal_space.runtime.errors import CheckpointMismatch, IntegrityError, InvalidState, ResourceRejected, RunNotFound
from signal_space.runtime.events import append_event
from signal_space.runtime.io import canonical_bytes, now, read_json, sha256_bytes, sha256_file, write_json
from signal_space.runtime.package import (
    RunPackage,
    code_identity,
    execution_identity,
)
from signal_space.runtime.verify import verify_package


class ResearchRuntime:
    def list(self) -> list[dict[str, object]]:
        return list_experiments()

    def schema(self, experiment_id: str) -> dict[str, Any]:
        return get_experiment(experiment_id).schema()

    def list_runs(self, workspace: Path) -> list[dict[str, Any]]:
        manifests: list[dict[str, Any]] = []
        if workspace.exists():
            for path in workspace.glob("*/run-*/manifest.json"):
                package = RunPackage(path.parent)
                try:
                    self._reconcile_orphaned_attempts(package)
                    manifests.append(package.manifest)
                except (OSError, ValueError, KeyError, TypeError) as error:
                    relative = path.relative_to(workspace).as_posix()
                    raise IntegrityError(
                        f"unreadable run manifest: {relative}: {error}"
                    ) from error
        return sorted(
            manifests,
            key=lambda value: str(value.get("updated_at", "")),
            reverse=True,
        )

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
        created = self.create_run(value, workspace)
        return self.execute(workspace, created["run_id"])

    def create_run(self, value: Any, workspace: Path) -> dict[str, Any]:
        config = self.validate(value)
        estimate = self.estimate(config)
        if not estimate["accepted"]:
            raise ResourceRejected("resource estimate exceeds: " + ", ".join(estimate["rejected_limits"]))
        plugin = get_experiment(config["experiment_id"])
        package = RunPackage.create(workspace, config, plugin.version)
        return {
            "run_id": package.manifest["run_id"],
            "state": "validated",
            "path": str(package.path),
        }

    def execute(self, workspace: Path, run_id: str) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        manifest = package.manifest
        if manifest["attempts"]:
            raise InvalidState("initial execution has already been created")
        config = read_json(package.path / "resolved-config.json")
        plugin = get_experiment(manifest["experiment_id"])
        return self._attempt(package, plugin, config, None)

    def resume(
        self,
        workspace: Path,
        run_id: str,
        on_started: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        self._reconcile_orphaned_attempts(package)
        manifest = package.manifest
        parent = manifest["attempts"][-1] if manifest["attempts"] else None
        if manifest["technical_state"] == "archived" or not parent or parent["state"] not in {"cancelled", "interrupted", "failed"} or not parent.get("checkpoint"):
            raise InvalidState("latest attempt is not a resumable terminal attempt with a checkpoint")
        checkpoint_path = package.path / parent["checkpoint"]["path"]
        if not checkpoint_path.is_file() or sha256_file(checkpoint_path) != parent["checkpoint"]["sha256"]:
            raise CheckpointMismatch("checkpoint bytes do not match the recorded hash")
        checkpoint = read_json(checkpoint_path)
        code_hash = sha256_bytes(canonical_bytes(manifest["code_identity"]))
        if checkpoint.get("config_hash") != manifest["config_hash"] or checkpoint.get("code_identity_hash") != code_hash:
            raise CheckpointMismatch("checkpoint config/code identity is incompatible")
        if sha256_bytes(canonical_bytes(code_identity())) != code_hash:
            raise CheckpointMismatch("current code identity differs from the checkpoint producer")
        if execution_identity() != manifest["execution_identity"]:
            raise CheckpointMismatch("current execution environment differs from the checkpoint producer")
        package.verify_immutable()
        config = read_json(package.path / "resolved-config.json")
        plugin = get_experiment(manifest["experiment_id"])
        return self._attempt(
            package,
            plugin,
            config,
            {"checkpoint": checkpoint, "parent": parent},
            on_started,
        )

    def _attempt(
        self,
        package: RunPackage,
        plugin: Any,
        config: dict[str, Any],
        resume: dict[str, Any] | None,
        on_started: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        with package.locked():
            manifest = package.manifest
            package.verify_immutable()
            if any(item["state"] in {"prepared", "running"} for item in manifest["attempts"]):
                raise InvalidState("run already has an active attempt")
            if resume is None and manifest["attempts"]:
                raise InvalidState("initial execution has already been created")
            if resume is not None and manifest["attempts"][-1]["attempt_id"] != resume["parent"]["attempt_id"]:
                raise InvalidState("resume parent is no longer the latest attempt")
            number = len(manifest["attempts"]) + 1
            while True:
                attempt_id = f"attempt-{number:04d}"
                relative = f"attempts/{attempt_id}"
                attempt_path = package.path / relative
                try:
                    attempt_path.mkdir(parents=True, exist_ok=False)
                    break
                except FileExistsError:
                    number += 1
            parent = resume["parent"] if resume else None
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
                manifest["scientific_classification"] = "not-evaluated"
                manifest["completeness"].update({"attempts_terminal": False, "analysis": False, "report": False})
                for criterion in manifest["acceptance_criteria"]:
                    criterion["evidence"] = None
            package.update(add)
            try:
                plugin.prepare(config, package.path, attempt_path, resume["checkpoint"] if resume else None)
            except Exception as error:
                return self._setup_failure(package, attempt, "PREPARATION_FAILED", error)

        manifest = package.manifest

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
            "prior_attempt_path": str((package.path / parent["path"]).resolve()) if parent else None,
        }
        request_path = attempt_path / "request.json"
        write_json(request_path, request, canonical=True)
        log_path = attempt_path / "logs/worker.log"
        log_path.parent.mkdir(parents=True)
        append_event(events, "attempt-running", "runtime", {"limits": config["resources"]})
        attempt["state"] = "running"
        attempt["updated_at"] = now()
        environment = os.environ.copy()
        python_root = str(Path(__file__).resolve().parents[2])
        environment["PYTHONPATH"] = python_root + (os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else "")
        with log_path.open("wb") as log:
            try:
                process = subprocess.Popen(
                    [sys.executable, "-m", "signal_space.runtime.worker", "--request", str(request_path)],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    env=environment,
                    start_new_session=os.name == "posix",
                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                    if os.name == "nt"
                    else 0,
                )
            except Exception as error:
                return self._setup_failure(package, attempt, "WORKER_START_FAILED", error)
            attempt["worker_pid"] = process.pid
            write_json(attempt_path / "attempt.json", attempt)
            self._update_attempt(package, attempt, "running")
            if on_started is not None:
                on_started(
                    {
                        "run_id": manifest["run_id"],
                        "attempt_id": attempt_id,
                        "state": "running",
                    }
                )
            terminal_error: str | None = None
            try:
                reason, exit_code = _monitor_process(
                    process, attempt_path, config["resources"]
                )
                if reason == "cancel":
                    append_event(events, "cancellation-timeout", "runtime", {"grace_seconds": 2})
                    _terminate_process(process, cooperative_seconds=0)
                    exit_code = 130
                elif reason == "wall":
                    (attempt_path / "cancel.request").touch()
                    append_event(events, "wall-limit-exceeded", "runtime", {"limit_seconds": config["resources"]["max_wall_seconds"]})
                    _terminate_process(process)
                    exit_code = 124
                elif reason == "output":
                    (attempt_path / "cancel.request").touch()
                    append_event(events, "output-limit-exceeded", "runtime", {"bytes": _directory_size(attempt_path)})
                    _terminate_process(process)
                    exit_code = 125
            except KeyboardInterrupt:
                (attempt_path / "cancel.request").touch()
                append_event(events, "cancellation-requested", "runtime", {"source": "signal"})
                _terminate_process(process)
                exit_code = 130
            except BaseException as error:
                terminal_error = f"{type(error).__name__}: {error}"
                _terminate_process(process)
                exit_code = 1
            finally:
                if process.poll() is None:
                    _terminate_process(process, cooperative_seconds=0)
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
            "failure": None if state in {"completed", "cancelled"} else {"code": "PROCESS_INTERRUPTED" if state == "interrupted" else "OUTPUT_LIMIT_EXCEEDED" if exit_code == 125 else "WORKER_FAILED", "recoverable": bool(checkpoint_record), "message": terminal_error},
        })
        attempt.pop("worker_pid", None)
        (attempt_path / "cancel.request").unlink(missing_ok=True)
        write_json(attempt_path / "attempt.json", attempt)
        append_event(events, f"attempt-{state}", "runtime", {"exit_code": exit_code, "recoverable": bool(checkpoint_record)})
        self._update_attempt(package, attempt, state)
        result = {"run_id": manifest["run_id"], "attempt_id": attempt_id, "state": state, "exit_code": exit_code, "resumable": bool(checkpoint_record) and state != "completed", "path": str(package.path)}
        return result

    def _setup_failure(self, package: RunPackage, attempt: dict[str, Any], code: str, error: Exception) -> dict[str, Any]:
        attempt.update({"state": "failed", "updated_at": now(), "exit_code": 1,
                        "failure": {"code": code, "recoverable": False, "message": f"{type(error).__name__}: {error}"}})
        path = package.path / attempt["path"]
        write_json(path / "attempt.json", attempt)
        append_event(path / "events.jsonl", "attempt-failed", "runtime", attempt["failure"])
        self._update_attempt(package, attempt, "failed")
        return {"run_id": package.manifest["run_id"], "attempt_id": attempt["attempt_id"], "state": "failed", "exit_code": 1, "resumable": False, "path": str(package.path)}

    def _reconcile_orphaned_attempts(self, package: RunPackage) -> None:
        with package.locked():
            manifest = package.manifest
            for entry in list(manifest["attempts"]):
                if entry["state"] != "running":
                    continue
                attempt_path = package.path / entry["path"]
                detail = read_json(attempt_path / "attempt.json")
                pid = detail.get("worker_pid")
                if isinstance(pid, int) and _process_exists(pid):
                    continue
                checkpoints = sorted((attempt_path / "checkpoints").glob("checkpoint-*.json"))
                checkpoint_record = None
                if checkpoints:
                    checkpoint = checkpoints[-1]
                    checkpoint_record = {
                        "path": checkpoint.relative_to(package.path).as_posix(),
                        "sha256": sha256_file(checkpoint),
                        "step": read_json(checkpoint)["solver_state"]["step"],
                    }
                detail.update({
                    "state": "interrupted",
                    "updated_at": now(),
                    "exit_code": None,
                    "checkpoint": checkpoint_record,
                    "failure": {
                        "code": "ORPHANED_WORKER",
                        "recoverable": bool(checkpoint_record),
                        "message": "recorded worker process is no longer running",
                    },
                })
                detail.pop("worker_pid", None)
                write_json(attempt_path / "attempt.json", detail)
                append_event(attempt_path / "events.jsonl", "attempt-reconciled", "runtime", {"previous_state": "running", "worker_pid": pid, "recoverable": bool(checkpoint_record)})
                self._update_attempt(package, detail, "interrupted")

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
        package = self._package(workspace, run_id)
        self._reconcile_orphaned_attempts(package)
        return package.manifest

    def cancel(self, workspace: Path, run_id: str) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        with package.locked():
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
        with package.locked():
            package.verify_immutable()
            manifest = package.manifest
            if not manifest["attempts"]:
                raise InvalidState("run has no attempt output")
            if any(
                attempt["state"] in {"prepared", "running"}
                for attempt in manifest["attempts"]
            ):
                raise InvalidState("analysis requires terminal attempt output")
            config = read_json(package.path / "resolved-config.json")
            plugin = get_experiment(manifest["experiment_id"])
            analysis_id = f"analysis-{len(manifest['analyses']) + 1:04d}-{int(time.time_ns()) & 0xffffffff:08x}"
            relative = f"analyses/{analysis_id}"
            path = package.path / relative
            before = {artifact["path"]: artifact["sha256"] for artifact in manifest["artifacts"] if artifact["kind"] == "raw"}
            try:
                result = plugin.analyze(package.path, path, config)
                after = {
                    relative_path: sha256_file(package.path / relative_path)
                    for relative_path in before
                }
                if before != after:
                    raise RuntimeError("analysis mutated raw artifacts")
                classification = plugin.classify(result["checks"], config)
                raw_source = result["raw_source"]
                if raw_source not in before:
                    raise IntegrityError("analysis raw_source must name indexed raw evidence")
                check_ids = {check["id"] for check in result["checks"]["checks"]}
                required_ids = {criterion["id"] for criterion in manifest["acceptance_criteria"]}
                if not required_ids.issubset(check_ids):
                    raise IntegrityError("analysis omitted preregistered acceptance checks")
                if classification not in {"pass", "fail", "unresolved", "not-evaluated"}:
                    raise IntegrityError("invalid scientific classification")
                record = {
                    "schema_version": "research-analysis-v1",
                    "analysis_id": analysis_id,
                    "path": relative,
                    "created_at": now(),
                    "input_artifacts": before,
                    "raw_source": raw_source,
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
                return record
            except BaseException:
                if path.exists():
                    shutil.rmtree(path)
                raise

    def report(self, workspace: Path, run_id: str, analysis_id: str | None = None) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        with package.locked():
            package.verify_immutable()
            manifest = package.manifest
            analyses = [entry for entry in manifest["analyses"] if analysis_id is None or entry["analysis_id"] == analysis_id]
            if not analyses:
                raise InvalidState("requested analysis does not exist")
            analysis = analyses[-1]
            number = len(manifest["reports"]) + 1
            while True:
                report_id = f"report-{number:04d}"
                relative = f"reports/{report_id}"
                report_path = package.path / relative
                try:
                    report_path.mkdir(parents=True, exist_ok=False)
                    break
                except FileExistsError:
                    number += 1
            render_provenance = {
                "code_identity": code_identity(),
                "execution_identity": execution_identity(),
            }
            try:
                output = get_experiment(manifest["experiment_id"]).report(
                    package.path,
                    report_path,
                    manifest,
                    analysis,
                    render_provenance,
                )
                output = dict(output)
                required_inputs = output.pop("required_inputs")
                indexed_paths = {artifact["path"] for artifact in manifest["artifacts"]}
                if not isinstance(required_inputs, list) or not required_inputs or any(not isinstance(item, str) or item not in indexed_paths for item in required_inputs):
                    raise IntegrityError("report required_inputs must name indexed evidence")
                record = {
                    "schema_version": "research-report-v1",
                    "report_id": report_id,
                    "analysis_id": analysis["analysis_id"],
                    "path": relative,
                    "created_at": now(),
                    "required_inputs": required_inputs,
                    "outputs": output,
                    "render_provenance": render_provenance,
                }
                write_json(report_path / "report.json", record)

                def change(updated: dict[str, Any]) -> None:
                    updated["reports"].append(record)
                    updated["completeness"]["report"] = True
                package.update(change)
                return record
            except BaseException:
                shutil.rmtree(report_path)
                raise

    def verify(self, workspace: Path, run_id: str) -> dict[str, Any]:
        package = self._package(workspace, run_id)
        with package.locked():
            return verify_package(package.path)

    def _package(self, workspace: Path, run_id: str) -> RunPackage:
        matches = list(workspace.glob(f"*/{run_id}"))
        if len(matches) != 1 or not (matches[0] / "manifest.json").is_file():
            raise RunNotFound(f"run not found: {run_id}")
        return RunPackage(matches[0])


def _directory_size(path: Path) -> int:
    total = 0
    for candidate in path.rglob("*"):
        try:
            if candidate.is_file():
                total += candidate.stat().st_size
        except FileNotFoundError:
            continue
    return total


def _monitor_process(
    process: subprocess.Popen[bytes],
    attempt_path: Path,
    resources: dict[str, Any],
) -> tuple[str, int | None]:
    deadline = time.monotonic() + float(resources["max_wall_seconds"])
    output_limit = int(resources["max_output_mb"]) * 1024 * 1024
    cancellation_deadline = None
    while True:
        if (attempt_path / "cancel.request").exists():
            if cancellation_deadline is None:
                cancellation_deadline = time.monotonic() + 2
            elif time.monotonic() >= cancellation_deadline:
                return "cancel", process.poll()
        if _directory_size(attempt_path) > output_limit:
            return "output", None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return "wall", None
        try:
            exit_code = process.wait(timeout=min(0.05, remaining))
            if _directory_size(attempt_path) > output_limit:
                return "output", exit_code
            return "completed", exit_code
        except subprocess.TimeoutExpired:
            continue


def _terminate_process(
    process: subprocess.Popen[bytes], cooperative_seconds: float = 2.0
) -> int:
    if process.poll() is not None:
        return int(process.returncode)
    if cooperative_seconds > 0:
        try:
            return process.wait(timeout=cooperative_seconds)
        except subprocess.TimeoutExpired:
            pass
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        return process.wait(timeout=2)
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            completed = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=False,
                capture_output=True,
            )
            if completed.returncode != 0:
                process.kill()
    except OSError:
        process.kill()
    try:
        return process.wait(timeout=5)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"worker process {process.pid} could not be terminated") from error


def _process_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
