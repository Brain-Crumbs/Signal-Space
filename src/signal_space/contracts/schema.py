"""Closed schema subset shared by registered GROSS configurations."""
import math
from signal_space.contracts.validation import ContractError

def check(value, spec, path="config"):
    kind = spec.get("type")
    if kind == "object":
        if not isinstance(value, dict):
            raise ContractError(f"{path} must be an object")
        if not set(spec["required"]).issubset(value) or set(value) - set(spec["properties"]):
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
    if "enum" in spec and value not in spec["enum"]:
        raise ContractError(f'{path} must be one of {spec["enum"]!r}')

