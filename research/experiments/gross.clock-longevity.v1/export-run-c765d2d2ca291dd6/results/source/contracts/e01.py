"""Closed validation against the E01 JSON Schema (deliberately small subset)."""

from copy import deepcopy
import json
import math
from pathlib import Path
from signal_space.contracts.validation import ContractError

ROOT = Path(__file__).resolve().parents[3]


def schema():
    return json.loads((ROOT / "contracts/research/e01.schema.json").read_text())


def check(value, spec, path="config"):
    kind = spec.get("type")
    if kind == "object":
        if not isinstance(value, dict):
            raise ContractError(f"{path} must be an object")
        if set(value) != set(spec["required"]):
            raise ContractError(f"{path} has missing or unknown fields")
        for key, item in value.items():
            check(item, spec["properties"][key], f"{path}.{key}")
    elif kind == "array":
        if (
            not isinstance(value, list)
            or not spec["minItems"] <= len(value) <= spec["maxItems"]
        ):
            raise ContractError(f"{path} has invalid array length")
        for i, item in enumerate(value):
            check(item, spec["items"], f"{path}[{i}]")
    elif kind in ("number", "integer"):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ContractError(f"{path} must be finite numeric")
        if kind == "integer" and not isinstance(value, int):
            raise ContractError(f"{path} must be integer")
        if (
            value < spec.get("minimum", -math.inf)
            or value > spec.get("maximum", math.inf)
            or value <= spec.get("exclusiveMinimum", -math.inf)
        ):
            raise ContractError(f"{path} outside admissible range")
    elif kind == "boolean":
        if not isinstance(value, bool):
            raise ContractError(f"{path} must be boolean")
    elif kind == "string":
        if not isinstance(value, str) or not spec.get("minLength", 0) <= len(
            value
        ) <= spec.get("maxLength", 10000):
            raise ContractError(f"{path} invalid string")
    if "const" in spec and value != spec["const"]:
        raise ContractError(f'{path} must equal {spec["const"]!r}')


def validate(value):
    check(value, schema())
    p = value["parameters"]
    if not p["omega_start"] <= p["omega_seed"] <= p["omega_end"]:
        raise ContractError("seed must lie inside ascending frequency interval")
    if p["omega_start"] >= p["omega_end"]:
        raise ContractError("frequency interval must have nonzero width")
    if p["min_omega_step"] > p["omega_step"]:
        raise ContractError("minimum step exceeds initial step")
    if p["max_nodes"] < 2 * p["nodes"]:
        raise ContractError("max_nodes must accommodate independent doubled mesh")
    if p["sample_points"] % 2 != 1:
        raise ContractError("sample_points must be odd for Simpson quadrature")
    if not p["research_run"] and (
        p["max_points"] > 12
        or p["spectral_nodes"] > 24
        or p["ell_max"] > 2
        or p["refinements"]
    ):
        raise ContractError(
            "large scans/refinements require explicit parameters.research_run=true"
        )
    return deepcopy(value)
