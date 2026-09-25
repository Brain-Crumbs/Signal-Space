from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from signal_space.contracts.validation import ContractError, load_json
from signal_space.runtime.archive import archive_run
from signal_space.runtime.errors import ResearchRuntimeError
from signal_space.runtime.runner import ResearchRuntime
from signal_space.service.api import serve


def _emit(value: Any) -> None:
    print(json.dumps(value, sort_keys=True, allow_nan=False))


def _workspace(value: str) -> Path:
    return Path(value).resolve()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="signal-space-research")
    parser.add_argument("--workspace", default=".research-work", help="runtime package root")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    for name in ("validate", "estimate", "run"):
        command = sub.add_parser(name)
        command.add_argument("--config", required=True)
    sweep = sub.add_parser("sweep")
    sweep.add_argument("--config", required=True)
    sweep.add_argument("--axis", action="append", required=True, help="closed config path=v1,v2")
    for name in ("status", "cancel", "resume", "analyze", "report", "verify"):
        command = sub.add_parser(name)
        command.add_argument("--run-id", required=True)
        if name == "report": command.add_argument("--analysis-id")
    archive = sub.add_parser("archive")
    archive.add_argument("--run-id", required=True)
    archive.add_argument("--archive-root", default="research/experiments")
    archive.add_argument("--catalog", default="research/catalog.json")
    server = sub.add_parser("serve")
    server.add_argument("--origin", required=True)
    server.add_argument("--host", default="127.0.0.1")
    server.add_argument("--port", type=int, default=0)
    server.add_argument("--archive-root")
    server.add_argument("--catalog", default="research/catalog.json")
    return parser


def _coerce(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _set_closed(config: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    target: Any = config
    for part in parts[:-1]:
        if not isinstance(target, dict) or part not in target:
            raise ContractError(f"sweep axis uses unknown path: {path}")
        target = target[part]
    if not isinstance(target, dict) or parts[-1] not in target:
        raise ContractError(f"sweep axis uses unknown path: {path}")
    target[parts[-1]] = value


def _sweep(runtime: ResearchRuntime, config: dict[str, Any], axes: list[str], workspace: Path) -> dict[str, Any]:
    members = [config]
    declarations = []
    for axis in axes:
        if "=" not in axis: raise ContractError("sweep axis must be path=v1,v2")
        path, raw = axis.split("=", 1)
        values = [_coerce(item) for item in raw.split(",")]
        declarations.append({"path": path, "values": values})
        expanded = []
        for member in members:
            for value in values:
                copy = deepcopy(member)
                _set_closed(copy, path, value)
                expanded.append(copy)
        members = expanded
    results = []
    for member in members:
        try:
            run_result = runtime.run(member, workspace)
            results.append({"status": run_result["state"], "result": run_result})
        except Exception as error:
            results.append({"status": "failed", "error": {"code": getattr(error, "code", "SWEEP_MEMBER_FAILED"), "message": str(error)}})
    member_states = [entry["status"] for entry in results]
    if "failed" in member_states:
        state = "failed"
    elif "interrupted" in member_states:
        state = "interrupted"
    elif "cancelled" in member_states:
        state = "cancelled"
    else:
        state = "completed"
    sweep_record = {"schema_version": "research-sweep-v1", "state": state, "axes": declarations, "planned": len(members), "executed": len(results), "members": results}
    sweep_root = workspace / "sweeps"
    sweep_root.mkdir(parents=True, exist_ok=True)
    path = sweep_root / f"sweep-{len(list(sweep_root.glob('sweep-*.json'))) + 1:04d}.json"
    path.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")
    return {**sweep_record, "path": str(path)}


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    runtime = ResearchRuntime()
    workspace = _workspace(args.workspace)
    try:
        if args.command == "list": result = {"experiments": runtime.list()}
        elif args.command == "validate": result = {"config": runtime.validate(load_json(args.config))}
        elif args.command == "estimate": result = runtime.estimate(load_json(args.config))
        elif args.command == "run": result = runtime.run(load_json(args.config), workspace)
        elif args.command == "sweep": result = _sweep(runtime, load_json(args.config), args.axis, workspace)
        elif args.command == "status": result = runtime.status(workspace, args.run_id)
        elif args.command == "cancel": result = runtime.cancel(workspace, args.run_id)
        elif args.command == "resume": result = runtime.resume(workspace, args.run_id)
        elif args.command == "analyze": result = runtime.analyze(workspace, args.run_id)
        elif args.command == "report": result = runtime.report(workspace, args.run_id, args.analysis_id)
        elif args.command == "verify": result = runtime.verify(workspace, args.run_id)
        elif args.command == "archive":
            package = runtime._package(workspace, args.run_id)
            result = archive_run(package.path, Path(args.archive_root).resolve(), Path(args.catalog).resolve() if args.catalog else None)
        elif args.command == "serve":
            serve(
                workspace,
                args.origin,
                args.host,
                args.port,
                Path(args.archive_root).resolve() if args.archive_root else None,
                Path(args.catalog).resolve() if args.archive_root else None,
            )
            return 0
        else: raise AssertionError(args.command)
        _emit(result)
        if isinstance(result, dict) and result.get("state") in {"failed", "interrupted"}: return 1
        if isinstance(result, dict) and result.get("state") == "cancelled": return 130
        return 0
    except (ContractError, ResearchRuntimeError, ValueError, OSError) as error:
        code = getattr(error, "code", "INPUT_ERROR")
        print(json.dumps({"error": {"code": code, "message": str(error)}}, sort_keys=True), file=sys.stderr)
        return 2 if code in {"CHECKPOINT_MISMATCH", "CORRUPT_ARTIFACT", "INVALID_STATE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
