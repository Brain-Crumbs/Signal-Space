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
    import signal
    # Termination first requests a checkpoint; the supervisor provides a bounded grace.
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, lambda *_: (Path(request['attempt_path']) / 'cancel.request').touch())
    if os.name == "posix":
        from signal_space.runtime.limits import _resource_limiter
        limits = dict(request["config"]["resources"])
        from signal_space.runtime.execution import process_metrics_available
        if request.get('execution_policy', {}).get('case_jobs', 1) > 1 and not process_metrics_available():
            limits['max_cpu_seconds'] = max(1, limits['max_cpu_seconds'] // (len(request['config']['parameters']['scenarios']) + 1))
        _resource_limiter(limits)()
    from signal_space.experiments.registry import get_experiment
    plugin = get_experiment(request["config"]["experiment_id"])
    return plugin.run(request_path)


if __name__ == "__main__":
    raise SystemExit(main())
