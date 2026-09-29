"""Operational policy, host discovery and native thread control (no physics)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import shutil
import sys
from typing import Any

import psutil

THREAD_VARIABLES = ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
                    'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS',
                    'NUMBA_NUM_THREADS')


def cpu_capacity() -> int:
    count = os.cpu_count() or 1
    try:
        count = min(count, len(psutil.Process().cpu_affinity()))
    except (AttributeError, psutil.Error):
        pass
    try:
        quota, period = Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if quota != 'max':
            count = min(count, max(1, int(quota) // int(period)))
    except (OSError, ValueError):
        pass
    return max(1, count)


def memory_capacity_mb() -> int:
    available = psutil.virtual_memory().available
    try:
        limit = Path('/sys/fs/cgroup/memory.max').read_text().strip()
        used = int(Path('/sys/fs/cgroup/memory.current').read_text())
        if limit != 'max':
            available = min(available, max(0, int(limit) - used))
    except (OSError, ValueError):
        pass
    return max(1, int(available * .85) // 1048576)


def disk_capacity_mb(path: Path) -> int:
    while not path.exists():
        path = path.parent
    return int(shutil.disk_usage(path).free * .9) // 1048576


@dataclass(frozen=True)
class ExecutionPolicy:
    threads: int = 1
    case_jobs: int = 1

    def __post_init__(self):
        for value in (self.threads, self.case_jobs):
            if type(value) is not int or value < 1:
                raise ValueError('threads and case_jobs must be positive integers')
        if self.cpu_slots > cpu_capacity():
            raise ValueError('requested native threads × case jobs exceed available CPU slots')

    @property
    def cpu_slots(self) -> int:
        return self.threads * self.case_jobs

    def record(self) -> dict[str, int]:
        return asdict(self)

    def environment(self) -> dict[str, str]:
        return {**{name: str(self.threads) for name in THREAD_VARIABLES},
                'MPLBACKEND': 'Agg', 'PYTHONUNBUFFERED': '1'}

    @classmethod
    def from_record(cls, value: dict[str, Any] | None) -> 'ExecutionPolicy':
        return cls(**(value or {}))


def process_metrics_available() -> bool:
    """Reject virtual /proc views whose PIDs do not describe our process namespace."""
    try:
        return Path(psutil.Process().exe()).resolve() == Path(sys.executable).resolve()
    except (psutil.Error, OSError):
        return False
