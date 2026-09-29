"""Internal worker for one preregistered independent quiet-control scenario."""
import argparse
from pathlib import Path
import os
import signal

from signal_space.runtime.io import read_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--request', type=Path, required=True)
    args = parser.parse_args()
    request = read_json(args.request)
    signal.signal(signal.SIGTERM, lambda *_: (Path(request['attempt_path'])/'cancel.request').touch())
    if os.name == 'posix':
        from signal_space.runtime.limits import _resource_limiter
        _resource_limiter(request['worker_limits'])()
    from signal_space.numerics.two_object_quiet import execute
    return execute(args.request)


if __name__ == '__main__':
    raise SystemExit(main())
