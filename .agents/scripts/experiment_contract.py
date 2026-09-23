#!/usr/bin/env python3
"""Validate locked design and reader export independently of the physics runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"
REQUIRED = {
    "README.md",
    "Experimental_Setup.pdf",
    "Experiment_Results.pdf",
    "Experiment_Analysis_and_Next.md",
    "plan.json",
    "figures/figure_index.json",
}


def check_schema(value: Any, schema: dict[str, Any], root: dict[str, Any], location: str = "$") -> None:
    if "$ref" in schema:
        pointer = schema["$ref"]
        if not pointer.startswith("#/"):
            raise ValueError(f"unsupported schema reference {pointer}")
        target = root
        for part in pointer[2:].split("/"):
            target = target[part]
        check_schema(value, target, root, location)
        return
    kind = schema.get("type")
    valid_type = {
        "object": lambda x: isinstance(x, dict),
        "array": lambda x: isinstance(x, list),
        "string": lambda x: isinstance(x, str),
        "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
        "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
        "boolean": lambda x: isinstance(x, bool),
    }
    if kind and not valid_type[kind](value):
        raise ValueError(f"{location}: expected {kind}")
    if "const" in schema and value != schema["const"]:
        raise ValueError(f"{location}: expected {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{location}: invalid value {value!r}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise ValueError(f"{location}: missing {key}")
        if len(value) < schema.get("minProperties", 0):
            raise ValueError(f"{location}: too few properties")
        for key, child in value.items():
            definition = schema.get("properties", {}).get(key, schema.get("additionalProperties", {}))
            if definition is False:
                raise ValueError(f"{location}: unexpected {key}")
            check_schema(child, definition, root, f"{location}.{key}")
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{location}: too few items")
        if schema.get("uniqueItems") and len(set(map(json.dumps, value))) != len(value):
            raise ValueError(f"{location}: duplicate items")
        for i, child in enumerate(value):
            check_schema(child, schema.get("items", {}), root, f"{location}[{i}]")
    elif isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or ("pattern" in schema and not re.fullmatch(schema["pattern"], value)):
            raise ValueError(f"{location}: invalid string")
    elif kind in ("number", "integer"):
        if value <= schema.get("exclusiveMinimum", float("-inf")) or value < schema.get("minimum", float("-inf")):
            raise ValueError(f"{location}: below minimum")


def read_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_plan(plan: dict[str, Any]) -> bytes:
    return json.dumps({key: val for key, val in plan.items() if key != "locked_sha256"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def unique_ids(rows: list[dict[str, Any]], key: str) -> set[str]:
    values = [row[key] for row in rows]
    if len(set(values)) != len(values):
        raise ValueError(f"duplicate {key}")
    return set(values)


def validate_plan(plan: dict[str, Any]) -> None:
    schema = read_schema("experiment-plan.schema.json")
    check_schema(plan, schema, schema)
    if plan["locked_sha256"] != digest(canonical_plan(plan)):
        raise ValueError("plan lock differs from plan contents; review and lock a new plan")
    hypothesis_ids = unique_ids(plan["hypotheses"], "id")
    control_ids = unique_ids(plan["controls"], "id")
    unique_ids(plan["criteria"], "id")
    unique_ids(plan["visualization_plan"], "figure_id")
    for figure in plan["visualization_plan"]:
        if set(figure["competing_signatures"]) - hypothesis_ids:
            raise ValueError(f"{figure['figure_id']}: signature references unknown hypothesis")
        if set(figure["controls"]) - control_ids:
            raise ValueError(f"{figure['figure_id']}: references unknown control")
    if not any(row["required"] and row["role"] == "evidentiary" for row in plan["visualization_plan"]):
        raise ValueError("at least one required evidentiary figure is needed")


def verify_runtime_config(plan: dict[str, Any], root: Path) -> Path:
    """Resolve the registered config only under the explicit repository root."""
    name = plan["runtime_config"]
    path = root.joinpath(*relative_path(name).parts)
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"missing or unsafe registered config: {name}")
    if digest(path.read_bytes()) != plan["runtime_config_sha256"]:
        raise ValueError("runtime configuration differs from locked SHA-256")
    config = json.loads(path.read_text(encoding="utf-8"))
    if (config["experiment_id"], config["model_id"]) != (plan["experiment_id"], plan["model_id"]):
        raise ValueError("runtime configuration identity differs from plan")
    for key, budget in plan["resources"].items():
        if config["resources"][key] > budget:
            raise ValueError(f"runtime configuration exceeds locked {key}")
    return path


def relative_path(name: str) -> PurePosixPath:
    candidate = PurePosixPath(name)
    if not name or candidate.is_absolute() or "\\" in name or any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError(f"invalid relative path: {name!r}")
    return candidate


def safe_file(base: Path, name: str) -> Path:
    path = base.joinpath(*relative_path(name).parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
        raise ValueError(f"missing or unsafe file: {name}")
    return path


def validate_bundle(base: Path) -> None:
    plan = json.loads(safe_file(base, "plan.json").read_text(encoding="utf-8"))
    validate_plan(plan)
    export = json.loads(safe_file(base, "export.json").read_text(encoding="utf-8"))
    schema = read_schema("export.schema.json")
    check_schema(export, schema, schema)
    source = export["source_run"]
    if source["experiment_id"] != plan["experiment_id"] or source["model_id"] != plan["model_id"]:
        raise ValueError("export source identity differs from locked plan")
    index = json.loads(safe_file(base, "figures/figure_index.json").read_text(encoding="utf-8"))
    schema = read_schema("figure-index.schema.json")
    check_schema(index, schema, schema)
    planned = {row["figure_id"]: row for row in plan["visualization_plan"]}
    delivered = unique_ids(index["figures"], "figure_id")
    missing = [key for key, row in planned.items() if row["required"] and key not in delivered]
    if missing:
        raise ValueError(f"missing required figures: {missing}")
    listed = set()
    for row in export["files"]:
        name = row["path"]
        if name == "export.json" or name in listed:
            raise ValueError(f"duplicate or self-indexed file: {name}")
        listed.add(name)
        if digest(safe_file(base, name).read_bytes()) != row["sha256"]:
            raise ValueError(f"checksum mismatch: {name}")
    if not REQUIRED <= listed:
        raise ValueError(f"missing required export files: {sorted(REQUIRED - listed)}")
    actual = {p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()}
    if actual != listed | {"export.json"}:
        raise ValueError(f"unindexed or missing files: {sorted(actual ^ (listed | {'export.json'}))}")
    for name in ("Experimental_Setup.pdf", "Experiment_Results.pdf"):
        if not safe_file(base, name).read_bytes().startswith(b"%PDF-"):
            raise ValueError(f"invalid PDF header: {name}")
    for name in listed:
        if name.endswith(".py") and not name.startswith("results/"):
            raise ValueError(f"Python source outside results/: {name}")
        if name.startswith("figures/") and name != "figures/figure_index.json":
            if not name.startswith(("figures/static/", "figures/animations/", "figures/interactive/")):
                raise ValueError(f"figure outside standard folders: {name}")
    for figure in index["figures"]:
        key = figure["figure_id"]
        if key not in planned or figure["question"] != planned[key]["question"] or figure["role"] != planned[key]["role"]:
            raise ValueError(f"unplanned or mismatched figure {key}")
        for name in figure["files"]:
            if name not in listed or not name.startswith("figures/"):
                raise ValueError(f"{key}: missing figure file {name}")
        for name in figure["source_data"]:
            if name not in listed or not name.startswith("results/"):
                raise ValueError(f"{key}: missing plot data {name}")
        spec_file = figure["spec_file"]
        if spec_file not in listed or not spec_file.startswith("results/"):
            raise ValueError(f"{key}: missing figure specification {spec_file}")
    if not any(name.startswith("results/") for name in listed):
        raise ValueError("no saved results or plot data")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("lock", "plan", "bundle", "scan"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "scan":
            for path in args.path.rglob("export.json"):
                validate_bundle(path.parent)
        elif args.action == "bundle":
            validate_bundle(args.path)
        else:
            plan = json.loads(args.path.read_text(encoding="utf-8"))
            if args.action == "lock":
                plan["locked_sha256"] = digest(canonical_plan(plan))
                validate_plan(plan)
                args.path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            else:
                validate_plan(plan)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"contract error: {error}", file=sys.stderr)
        return 1
    print(f"validated {args.action}: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
