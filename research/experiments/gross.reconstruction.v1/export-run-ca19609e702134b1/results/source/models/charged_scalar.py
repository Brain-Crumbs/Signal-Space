"""E01 action ledger; c=hbar=m=g=h=1, neutral field identically zero."""

import numpy as np

MODEL_ID = "charged-scalar-3d-v1"
SOURCE = "research/papers/charged-recurrence-winding-hopf.md"
EQUATIONS = {
    "action": "§§2–3,14",
    "observables": "§§5,7–9",
    "radial": "§8",
    "spectrum": "§10",
    "regulator": "§15",
    "scope": "§23",
}


def force(f, omega):
    return (1 - omega**2) * f - 2 * f**3 + 3 * f**5


def potential(f):
    return f * f - f**4 + f**6


def tail(radius, amplitude, omega, coupling=0.01):
    k = np.sqrt(1 - omega**2)
    a = amplitude**2 * radius**2
    i = a / (2 * k)
    t = a * (k / 2 + 1 / radius)
    r4 = a * (radius**2 / (2 * k) + radius / (2 * k * k) + 1 / (4 * k**3))
    return {
        "i": float(i),
        "t": float(t),
        "r4": float(r4),
        "Q": float(8 * np.pi * omega * i / coupling),
        "E": float(4 * np.pi * ((1 + omega**2) * i + t) / coupling),
    }
