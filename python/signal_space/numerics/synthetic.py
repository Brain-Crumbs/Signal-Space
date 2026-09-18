from __future__ import annotations

from signal_space.models.synthetic import advance


def recurrence(initial: float, gain: float, forcing: float, steps: int) -> list[float]:
    values = [initial]
    for _ in range(steps):
        values.append(advance(values[-1], gain, forcing))
    return values
