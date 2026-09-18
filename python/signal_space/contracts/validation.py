"""Closed boundary validation for the versioned research schemas."""

from __future__ import annotations

import json
import math
from copy import deepcopy
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


def validate_config(value: Any) -> dict[str, Any]:
    """Validate and return a closed, normalized experiment configuration."""
    config = _object(
        value,
        "config",
        {"schema_version", "experiment_id", "model_id", "parameters", "units", "seeds", "resources", "analysis", "report"},
        {"fixture_controls"},
    )
    expected = {
        "schema_version": "research-experiment-v1",
        "experiment_id": "fixture.synthetic.v1",
        "model_id": "fixture.deterministic-recurrence.v1",
    }
    for key, required in expected.items():
        if config[key] != required:
            raise ContractError(f"{key} must be {required!r}")

    parameters = _object(
        config["parameters"], "parameters",
        {"steps", "checkpoint_interval", "initial_value", "gain", "forcing"},
        {"step_delay_ms"},
    )
    _integer(parameters["steps"], "parameters.steps", 2, 1_000_000)
    _integer(parameters["checkpoint_interval"], "parameters.checkpoint_interval", 1, 1_000_000)
    if parameters["checkpoint_interval"] > parameters["steps"]:
        raise ContractError("parameters.checkpoint_interval cannot exceed parameters.steps")
    _number(parameters["initial_value"], "parameters.initial_value")
    _number(parameters["gain"], "parameters.gain", -2, 2)
    _number(parameters["forcing"], "parameters.forcing")
    if "step_delay_ms" in parameters:
        _number(parameters["step_delay_ms"], "parameters.step_delay_ms", 0, 100)

    units = _object(config["units"], "units", {"step", "value"})
    if units != {"step": "index", "value": "dimensionless"}:
        raise ContractError("units must declare step='index' and value='dimensionless'")

    seeds = _object(config["seeds"], "seeds", {"root"})
    _integer(seeds["root"], "seeds.root", 0, 2**32 - 1)

    resources = _object(config["resources"], "resources", {"max_cpu_seconds", "max_memory_mb", "max_output_mb", "max_wall_seconds"})
    _integer(resources["max_cpu_seconds"], "resources.max_cpu_seconds", 1, 300)
    _integer(resources["max_memory_mb"], "resources.max_memory_mb", 64, 2048)
    _integer(resources["max_output_mb"], "resources.max_output_mb", 1, 256)
    _number(resources["max_wall_seconds"], "resources.max_wall_seconds", 0.1, 600)

    analysis = _object(config["analysis"], "analysis", {"max_abs_error", "require_complete"})
    _number(analysis["max_abs_error"], "analysis.max_abs_error", 0)
    if not isinstance(analysis["require_complete"], bool):
        raise ContractError("analysis.require_complete must be boolean")

    report = _object(config["report"], "report", {"title"})
    if not isinstance(report["title"], str) or not 1 <= len(report["title"]) <= 200:
        raise ContractError("report.title must contain 1 to 200 characters")

    if "fixture_controls" in config:
        controls = _object(config["fixture_controls"], "fixture_controls", set(), {"interrupt_at_step", "fail_at_step"})
        for key, raw in controls.items():
            if raw is not None:
                _integer(raw, f"fixture_controls.{key}", 1, parameters["steps"])

    normalized = deepcopy(config)
    normalized["parameters"].setdefault("step_delay_ms", 0.0)
    normalized.setdefault("fixture_controls", {"interrupt_at_step": None, "fail_at_step": None})
    normalized["fixture_controls"].setdefault("interrupt_at_step", None)
    normalized["fixture_controls"].setdefault("fail_at_step", None)
    return normalized


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
        "code_identity", "seed_algorithm", "seed_ledger", "attempts", "analyses", "reports", "artifacts",
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
