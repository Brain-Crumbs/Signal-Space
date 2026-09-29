"""Closed boundary validation for the versioned research schemas."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """A recoverable boundary validation failure."""

    code = "INVALID_CONFIG"


def _reject_constant(value: str) -> None:
    raise ContractError(f"non-finite JSON number {value} is not allowed")


def load_json(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(), parse_constant=_reject_constant)
    except ContractError:
        raise
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"could not read JSON: {error}") from error


def _object(value: Any, path: str, required: set[str], optional: set[str] = set()) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{path} must be an object")
    keys = set(value)
    missing = required - keys
    unknown = keys - required - optional
    if missing:
        raise ContractError(f"{path} is missing: {', '.join(sorted(missing))}")
    if unknown:
        raise ContractError(f"{path} has unknown fields: {', '.join(sorted(unknown))}")
    return value


def _number(value: Any, path: str, minimum: float | None = None, maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"{path} must be a finite number")
    result = float(value)
    if minimum is not None and result < minimum:
        raise ContractError(f"{path} must be >= {minimum}")
    if maximum is not None and result > maximum:
        raise ContractError(f"{path} must be <= {maximum}")
    return result


def _integer(value: Any, path: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ContractError(f"{path} must be an integer from {minimum} to {maximum}")
    return value


def validate_event(value: Any) -> None:
    event = _object(value, "event", {"schema_version", "sequence", "timestamp", "type", "stage", "payload"})
    if event["schema_version"] != "research-event-v1":
        raise ContractError("event schema_version is unsupported")
    _integer(event["sequence"], "event.sequence", 1, 2**63 - 1)
    if event["stage"] not in {"prepare", "run", "analyze", "report", "runtime"}:
        raise ContractError("event.stage is invalid")
    if not isinstance(event["timestamp"], str) or not isinstance(event["type"], str) or not isinstance(event["payload"], dict):
        raise ContractError("event timestamp/type/payload have invalid types")


def validate_manifest(value: Any) -> None:
    required = {
        "schema_version", "package_version", "experiment_id", "experiment_version", "model_id", "run_id",
        "created_at", "updated_at", "technical_state", "scientific_classification", "config_hash", "config_path",
        "code_identity", "execution_identity", "seed_algorithm", "seed_ledger", "attempts", "analyses", "reports", "artifacts",
        "acceptance_criteria", "completeness", "known_gaps", "checksum_algorithm", "checksum_path",
    }
    manifest = _object(value, "manifest", required, {"parent_run_id"})
    if manifest["schema_version"] != "research-run-manifest-v1" or manifest["package_version"] != 1:
        raise ContractError("manifest schema/package version is unsupported")
    if manifest["technical_state"] not in {"draft", "validated", "prepared", "running", "completed", "cancelled", "interrupted", "failed", "analyzed", "archived"}:
        raise ContractError("manifest technical_state is invalid")
    if manifest["scientific_classification"] not in {"pass", "fail", "unresolved", "not-evaluated"}:
        raise ContractError("manifest scientific_classification is invalid")
    for name in ("attempts", "analyses", "reports", "artifacts", "acceptance_criteria", "known_gaps"):
        if not isinstance(manifest[name], list):
            raise ContractError(f"manifest.{name} must be an array")

    _validate_code_identity(manifest["code_identity"], "manifest.code_identity")
    _validate_execution_identity(
        manifest["execution_identity"], "manifest.execution_identity"
    )
    ledger = _object(
        manifest["seed_ledger"],
        "manifest.seed_ledger",
        {"initialization", "perturbations", "sampling", "analysis"},
    )
    for name, item in ledger.items():
        _integer(item, f"manifest.seed_ledger.{name}", 0, 2**64 - 1)

    attempt_fields = {
        "attempt_id", "parent_attempt_id", "state", "path", "created_at",
        "updated_at", "exit_code", "checkpoint", "failure",
    }
    for index, raw in enumerate(manifest["attempts"]):
        path = f"manifest.attempts[{index}]"
        attempt = _object(raw, path, attempt_fields)
        if attempt["state"] not in {"prepared", "running", "completed", "cancelled", "interrupted", "failed"}:
            raise ContractError(f"{path}.state is invalid")
        for name in ("attempt_id", "path", "created_at", "updated_at"):
            _require_string(attempt[name], f"{path}.{name}")
        if attempt["parent_attempt_id"] is not None:
            _require_string(attempt["parent_attempt_id"], f"{path}.parent_attempt_id")
        if attempt["exit_code"] is not None and (isinstance(attempt["exit_code"], bool) or not isinstance(attempt["exit_code"], int)):
            raise ContractError(f"{path}.exit_code must be an integer or null")
        if attempt["checkpoint"] is not None:
            checkpoint = _object(attempt["checkpoint"], f"{path}.checkpoint", {"path", "sha256", "step"})
            _require_string(checkpoint["path"], f"{path}.checkpoint.path")
            _require_hash(checkpoint["sha256"], f"{path}.checkpoint.sha256")
            _integer(checkpoint["step"], f"{path}.checkpoint.step", 0, 2**63 - 1)
        if attempt["failure"] is not None:
            failure = _object(attempt["failure"], f"{path}.failure", {"code", "recoverable", "message"})
            _require_string(failure["code"], f"{path}.failure.code")
            if not isinstance(failure["recoverable"], bool):
                raise ContractError(f"{path}.failure.recoverable must be boolean")
            if failure["message"] is not None:
                _require_string(failure["message"], f"{path}.failure.message")

    analysis_fields = {
        "schema_version", "analysis_id", "path", "created_at", "input_artifacts",
        "raw_source", "parameters", "code_identity", "classification", "summary", "supersedes",
    }
    for index, raw in enumerate(manifest["analyses"]):
        path = f"manifest.analyses[{index}]"
        analysis = _object(raw, path, analysis_fields)
        if analysis["schema_version"] != "research-analysis-v1":
            raise ContractError(f"{path}.schema_version is unsupported")
        for name in ("analysis_id", "path", "created_at", "raw_source"):
            _require_string(analysis[name], f"{path}.{name}", allow_empty=name == "raw_source")
        if not isinstance(analysis["input_artifacts"], dict) or not isinstance(analysis["parameters"], dict) or not isinstance(analysis["summary"], dict):
            raise ContractError(f"{path} object fields are invalid")
        for artifact_path, digest in analysis["input_artifacts"].items():
            _require_string(artifact_path, f"{path}.input_artifacts key")
            _require_hash(digest, f"{path}.input_artifacts[{artifact_path!r}]")
        _validate_code_identity(analysis["code_identity"], f"{path}.code_identity")
        if analysis["classification"] not in {"pass", "fail", "unresolved", "not-evaluated"}:
            raise ContractError(f"{path}.classification is invalid")
        if analysis["supersedes"] is not None:
            _require_string(analysis["supersedes"], f"{path}.supersedes")

    report_fields = {
        "schema_version", "report_id", "analysis_id", "path", "created_at",
        "required_inputs", "outputs", "render_provenance",
    }
    for index, raw in enumerate(manifest["reports"]):
        path = f"manifest.reports[{index}]"
        report = _object(raw, path, report_fields)
        if report["schema_version"] != "research-report-v1":
            raise ContractError(f"{path}.schema_version is unsupported")
        for name in ("report_id", "analysis_id", "path", "created_at"):
            _require_string(report[name], f"{path}.{name}")
        if not isinstance(report["required_inputs"], list) or not all(isinstance(item, str) for item in report["required_inputs"]):
            raise ContractError(f"{path}.required_inputs must be a string array")
        if not isinstance(report["outputs"], dict):
            raise ContractError(f"{path}.outputs must be an object")
        provenance = _object(report["render_provenance"], f"{path}.render_provenance", {"code_identity", "execution_identity"})
        _validate_code_identity(provenance["code_identity"], f"{path}.render_provenance.code_identity")
        _validate_execution_identity(provenance["execution_identity"], f"{path}.render_provenance.execution_identity")

    artifact_fields = {"id", "kind", "path", "sha256", "size", "media_type"}
    for index, raw in enumerate(manifest["artifacts"]):
        path = f"manifest.artifacts[{index}]"
        artifact = _object(raw, path, artifact_fields, {"source_ids"})
        for name in ("id", "kind", "path", "media_type"):
            _require_string(artifact[name], f"{path}.{name}")
        _require_hash(artifact["sha256"], f"{path}.sha256")
        _integer(artifact["size"], f"{path}.size", 0, 2**63 - 1)
        if "source_ids" in artifact and (not isinstance(artifact["source_ids"], list) or not all(isinstance(item, str) for item in artifact["source_ids"])):
            raise ContractError(f"{path}.source_ids must be a string array")

    for index, raw in enumerate(manifest["acceptance_criteria"]):
        path = f"manifest.acceptance_criteria[{index}]"
        criterion = _object(raw, path, {"id", "description", "evidence"})
        _require_string(criterion["id"], f"{path}.id")
        _require_string(criterion["description"], f"{path}.description")
        if criterion["evidence"] is not None:
            _require_string(criterion["evidence"], f"{path}.evidence")
    completeness = _object(manifest["completeness"], "manifest.completeness", {"config", "provenance", "attempts_terminal", "analysis", "report"})
    if not all(isinstance(item, bool) for item in completeness.values()):
        raise ContractError("manifest.completeness values must be boolean")


def _require_string(value: Any, path: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise ContractError(f"{path} must be a string")
    return value


def _require_hash(value: Any, path: str) -> str:
    text = _require_string(value, path)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ContractError(f"{path} must be a SHA-256 digest")
    return text


def _validate_code_identity(value: Any, path: str) -> None:
    identity = _object(value, path, {"revision", "tree_state", "dirty_patch_hash", "runtime_version"})
    for name in ("revision", "runtime_version"):
        _require_string(identity[name], f"{path}.{name}")
    if identity["tree_state"] not in {"clean", "dirty", "unknown"}:
        raise ContractError(f"{path}.tree_state is invalid")
    _require_hash(identity["dirty_patch_hash"], f"{path}.dirty_patch_hash")


def _validate_execution_identity(value: Any, path: str) -> None:
    identity = _object(value, path, {"environment", "dependencies"})
    environment = _object(identity["environment"], f"{path}.environment", {"python", "implementation", "os", "architecture", "numeric_libraries", "accelerator"}, {"execution_policy"})
    for name in ("python", "implementation", "os", "architecture", "accelerator"):
        _require_string(environment[name], f"{path}.environment.{name}")
    if "execution_policy" in environment:
        policy = _object(environment["execution_policy"], f"{path}.execution_policy", {"threads", "case_jobs"})
        for name, value in policy.items():
            _integer(value, f"{path}.execution_policy.{name}", 1, 65536)
    libraries = _object(environment["numeric_libraries"], f"{path}.environment.numeric_libraries", {"numpy", "matplotlib"}, {"scipy", "numba", "llvmlite"})
    for name in libraries:
        _require_string(libraries[name], f"{path}.environment.numeric_libraries.{name}")
    dependencies = _object(identity["dependencies"], f"{path}.dependencies", {"path", "sha256"})
    _require_string(dependencies["path"], f"{path}.dependencies.path")
    _require_hash(dependencies["sha256"], f"{path}.dependencies.sha256")
