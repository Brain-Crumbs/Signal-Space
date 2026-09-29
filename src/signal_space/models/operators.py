"""Signal Space operator constitution v1, program v0.2 sections 2--4.

Algebra only: no event dynamics, metric identification or physical action.
"""

import numpy as np

MODEL_ID = "signal-space.operator-constitution.v1"
I = np.eye(2, dtype=complex)
SIGMA = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]])


def hermitian(c):
    return c[0] * I + np.einsum("i,ijk->jk", c[1:], SIGMA)


def lorentz(x, y):
    return float(((np.trace(x) * np.trace(y) - np.trace(x @ y)) / 2).real)


def projector(z):
    rho = float(np.vdot(z, z).real)
    if rho <= 0:
        raise ValueError("zero state has no ray")
    return np.outer(z, z.conj()) / rho


def observer(j, condition_limit=100.0):
    eigenvalues = np.linalg.eigvalsh(j)
    if eigenvalues[0] <= 0:
        raise ValueError("aggregate has no positive full-rank observer")
    if eigenvalues[-1] / eigenvalues[0] > condition_limit:
        raise ValueError("aggregate outside declared conditioning domain")
    return j / np.sqrt(np.linalg.det(j).real)


def norm(z, t):
    return float(np.vdot(z, np.linalg.solve(t, z)).real)


def euclidean(t, x, y):
    return 2 * lorentz(t, x) * lorentz(t, y) - lorentz(x, y)


def su2(rng):
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    return q[0] * I + 1j * np.einsum("i,ijk->jk", q[1:], SIGMA)
