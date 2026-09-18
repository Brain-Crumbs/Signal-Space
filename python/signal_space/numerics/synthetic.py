from __future__ import annotations

import math

def recurrence(initial: float, gain: float, forcing: float, steps: int) -> list[float]:
    """Evaluate the recurrence from its closed form, independently of the worker."""
    if gain == 1.0:
        return [initial + forcing * step for step in range(steps + 1)]
    if gain > 0:
        logarithm = math.log1p(gain - 1) if abs(gain - 1) < 0.5 else math.log(gain)
        return [initial * math.exp(step * logarithm) + forcing * math.expm1(step * logarithm) / (gain - 1) for step in range(steps + 1)]
    return [
        (gain**step) * initial
        + forcing * (1.0 - gain**step) / (1.0 - gain)
        for step in range(steps + 1)
    ]
