"""Append-only event log with kernel-released locking and constant-size tail reads."""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import threading
from typing import Any

from signal_space.runtime.io import now

_GUARD = threading.Lock()
_LOCKS: dict[Path, threading.Lock] = {}


@contextmanager
def _locked(path: Path):
    # flock alone does not serialize threads sharing one process on all platforms.
    with _GUARD:
        lock = _LOCKS.setdefault(path.resolve(), threading.Lock())
    with lock, path.with_suffix(path.suffix + '.lock').open('a+b') as stream:
        if os.name == 'posix':
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        else:
            import msvcrt
            if stream.tell() == 0:
                stream.write(b'0')
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            if os.name == 'posix':
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            else:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


def read_events(path: Path, after: int = 0) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding='utf-8') as stream:
        return [item for line in stream if line.strip()
                if (item := json.loads(line))['sequence'] > after]


def _last_sequence(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    with path.open('rb') as stream:
        stream.seek(0, os.SEEK_END)
        end = stream.tell()
        stream.seek(end - 1)
        if stream.read(1) != b'\n':
            raise ValueError(f'truncated event record: {path}')
        position, tail = end, b''
        while position:
            size = min(4096, position)
            position -= size
            stream.seek(position)
            tail = stream.read(size) + tail
            lines = tail.rstrip(b'\n').split(b'\n')
            if len(lines) > 1 or position == 0:
                return int(json.loads(lines[-1])['sequence'])
    raise ValueError('unreadable event tail')


def append_event(path: Path, event_type: str, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _locked(path):
        event = {'schema_version': 'research-event-v1', 'sequence': _last_sequence(path) + 1,
                 'timestamp': now(), 'type': event_type, 'stage': stage, 'payload': payload}
        with path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        return event
