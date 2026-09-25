"""Non-physical deterministic recurrence used only to test framework behavior."""

from __future__ import annotations


MODEL_ID = "fixture.deterministic-recurrence.v1"
EQUATION_REFERENCE = "fixture:x[n+1]=gain*x[n]+forcing"


def advance(value: float, gain: float, forcing: float) -> float:
    return gain * value + forcing
