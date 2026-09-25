from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from signal_space.runtime.io import now


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def append_event(path: Path, event_type: str, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(path.suffix + ".lock")
    deadline = time.monotonic() + 10
    descriptor: int | None = None
    while descriptor is None:
        try:
            descriptor = os.open(
                lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600
            )
        except FileExistsError:
            try:
                owner = int(lock.read_text())
                os.kill(owner, 0)
            except (OSError, ValueError):
                lock.unlink(missing_ok=True)
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f"could not lock event log: {path}")
            time.sleep(0.005)
    try:
        os.write(descriptor, str(os.getpid()).encode())
        existing = read_events(path)
        event = {
            "schema_version": "research-event-v1",
            "sequence": len(existing) + 1,
            "timestamp": now(),
            "type": event_type,
            "stage": stage,
            "payload": payload,
        }
        with path.open("a", encoding="utf-8") as stream:
            stream.write(
                json.dumps(
                    event,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                )
                + "\n"
            )
            stream.flush()
            os.fsync(stream.fileno())
        return event
    finally:
        os.close(descriptor)
        lock.unlink(missing_ok=True)
