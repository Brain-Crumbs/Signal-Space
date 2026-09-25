"""Generic bounded-process entry point for a registered experiment plugin."""

from __future__ import annotations

import argparse
from pathlib import Path

from signal_space.runtime.io import read_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    request_path = Path(args.request)
    request = read_json(request_path)
    import os
    if os.name == "posix":
        from signal_space.runtime.limits import _resource_limiter
        _resource_limiter(request["config"]["resources"])()
    from signal_space.experiments.registry import get_experiment
    plugin = get_experiment(request["config"]["experiment_id"])
    return plugin.run(request_path)


if __name__ == "__main__":
    raise SystemExit(main())
