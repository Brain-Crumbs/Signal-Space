#!/usr/bin/env python3
"""Gate registered runtime validate/estimate/run on a locked design and config bytes."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from experiment_contract import validate_plan, verify_runtime_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="Run physics after validate and estimate")
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        validate_plan(plan)
        config = verify_runtime_config(plan, args.repo_root)
        env = {**os.environ, "PYTHONPATH": str(args.repo_root.resolve() / "python")}
        for stage in ("validate", "estimate", "run") if args.execute else ("validate", "estimate"):
            command = [sys.executable, "-m", "signal_space", "--workspace", str(args.workspace.resolve()), stage,
                       "--config", str(config.resolve())]
            completed = subprocess.run(command, cwd=args.repo_root, env=env, text=True, capture_output=True)
            if completed.returncode:
                print(completed.stderr or completed.stdout, file=sys.stderr)
                return completed.returncode
            print(json.dumps({"stage": stage, "result": json.loads(completed.stdout)}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"plan run rejected: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
