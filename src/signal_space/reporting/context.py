"""Locked visual questions shared by renderers and the reader contract."""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from signal_space.runtime.io import read_json

_PLAN = ContextVar('report_plan', default=None)


@contextmanager
def using_plan(plan):
    token = _PLAN.set(plan)
    try:
        yield
    finally:
        _PLAN.reset(token)


def questions(default_plan: Path):
    plan = _PLAN.get() or read_json(default_plan)
    return {row['figure_id']: row['question'] for row in plan['visualization_plan']}
