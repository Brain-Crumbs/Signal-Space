"""SS OPS 1, Operator Program v0.2 section 5; no metric or clock assumed."""

import numpy as np

MODEL_ID = "signal-space.ss-ops-1.v1"


def rhs(s, flat, kappa, lam, frozen=False):
    z1, z2, w = flat.reshape(3, 2)
    d = z1 - z2
    p = np.outer(w, w.conj())
    n = np.vdot(z1, z1).real + np.vdot(z2, z2).real
    return (-1j * np.array([kappa * p @ d + lam * n * z1,
                           -kappa * p @ d + lam * n * z2,
                           np.zeros(2) if frozen else kappa * d * np.vdot(d, w)])).ravel()


def exact_gate(state, kappa, lam, s=1.0):
    """Independent closed solution from constant S=dd†+2ww†; see protocol."""
    z1, z2, w = state
    a, d = z1 + z2, z1 - z2
    n = np.vdot(z1, z1).real + np.vdot(z2, z2).real
    q, m = np.vdot(d, d).real, np.vdot(w, w).real
    eigenvalues, vectors = np.linalg.eigh(np.outer(d, d.conj()) + 2 * np.outer(w, w.conj()))
    rotation = (vectors * np.exp(-1j * kappa * eigenvalues * s)) @ vectors.conj().T
    a = np.exp(-1j * lam * n * s) * a
    d = np.exp(1j * (kappa * q - lam * n) * s) * (rotation @ d)
    w = np.exp(2j * kappa * m * s) * (rotation @ w)
    return np.array([(a + d) / 2, (a - d) / 2, w])
