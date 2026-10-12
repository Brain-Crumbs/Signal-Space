"""Three coherent ports and two ordered SS OPS 1 memories; lambda=0.

The incidence is supplied. This adapter changes neither the event Hamiltonian
nor the model ID. Memory spinor phases are representation gauge directions.
"""
import numpy as np
from scipy.linalg import expm_frechet

from signal_space.models.reciprocal import MODEL_ID, exact_gate, rhs

EVENTS = ((0, 1, 3), (1, 2, 4))
PREPARATIONS = ("dark", "initially-commuting", "active-plus", "active-minus",
                "noncomplement", "coherence-plus", "coherence-minus")
CONTROL_WORDS = {"isolated-A": (0,), "isolated-B": (1,), "reverse": (1, 0)}
ROTATION = np.array([[1, -1j], [-1j, 1]], complex) / np.sqrt(2)
COMMON_PHASE = np.exp(0.37j)


def outer(z):
    return np.einsum("...a,...b->...ab", z, z.conj())


def preparations():
    e1, e2 = np.eye(2, dtype=complex)
    dark = np.array([e1 / np.sqrt(3)] * 3 + [e1, e2])
    commuting = np.array([e1 / np.sqrt(2), 0 * e1, e2 / np.sqrt(2), e1, e2])
    active = np.array([e1 / np.sqrt(3), e2 / np.sqrt(3),
                       (e1 + 1j * e2) / np.sqrt(6), e1, e2])
    minus = active.copy(); minus[2] = active[2].conj()
    noncomplement = active.copy(); noncomplement[4] = (e1 + e2) / np.sqrt(2)
    witnesses = [np.array([e1 / np.sqrt(2), sign * e1 / np.sqrt(2),
                           0 * e1, (e1 + e2) / np.sqrt(2), e2])
                 for sign in (1, -1)]
    return dict(zip(PREPARATIONS, (dark, commuting, active, minus, noncomplement, *witnesses)))


def amplitude_rhs(s, state, event, kappa):
    result = np.zeros((5, 2), complex)
    indices = list(EVENTS[event])
    result[indices] = rhs(s, np.asarray(state).reshape(5, 2)[indices].ravel(), kappa, 0).reshape(3, 2)
    return result


def lift(state):
    return outer(np.asarray(state)[:3].ravel()), outer(np.asarray(state)[3:])


def operator_rhs(s, flat, event, kappa, frozen=False):
    wave = flat[:36].reshape(6, 6)
    memories = flat[36:].reshape(2, 2, 2)
    i, j, memory = EVENTS[event]
    p = memories[memory - 3]
    si, sj = slice(2 * i, 2 * i + 2), slice(2 * j, 2 * j + 2)
    generator = np.zeros((6, 6), complex)
    generator[si, si] = generator[sj, sj] = kappa * p
    generator[si, sj] = generator[sj, si] = -kappa * p
    difference = wave[si, si] + wave[sj, sj] - wave[si, sj] - wave[sj, si]
    dp = np.zeros_like(memories)
    if not frozen:
        dp[memory - 3] = -1j * kappa * (difference @ p - p @ difference)
    return np.concatenate(((-1j * (generator @ wave - wave @ generator)).ravel(), dp.ravel()))


def gate(state, event, kappa, s=1., frozen=False):
    out = np.array(state, complex, copy=True)
    indices = list(EVENTS[event])
    if frozen:
        z1, z2, w = out[indices]
        total, difference = z1 + z2, z1 - z2
        d = (np.eye(2) + (np.exp(-2j * kappa * s) - 1) * outer(w)) @ difference
        out[indices] = [(total + d) / 2, (total - d) / 2, w]
    else:
        out[indices] = exact_gate(out[indices], kappa, 0, s)
    return out


def word(state, kappa, cycles=1, order=(0, 1), frozen=False):
    out = np.array(state, complex, copy=True)
    for _ in range(cycles):
        for event in order:
            out = gate(out, event, kappa, frozen=frozen)
    return out


def gate_tangent(state, deltas, event, kappa, s=1.):
    """Differentiate the closed gate using the matrix-exponential Frechet map.

    Accept all ambient directions, including changes in conserved quantities.
    Physical ray tangents are selected at preparation, not by deleting response.
    """
    indices = list(EVENTS[event])
    z1, z2, w = state[indices]
    d = z1 - z2
    q, m = np.vdot(d, d).real, np.vdot(w, w).real
    matrix = outer(d) + 2 * outer(w)
    values, vectors = np.linalg.eigh(matrix)
    rotation = (vectors * np.exp(-1j * kappa * values * s)) @ vectors.conj().T
    out = np.array(deltas, complex, copy=True)
    for n, delta in enumerate(deltas):
        v1, v2, eta = delta[indices]
        dd = v1 - v2
        ds = (np.outer(dd, d.conj()) + np.outer(d, dd.conj())
              + 2 * (np.outer(eta, w.conj()) + np.outer(w, eta.conj())))
        dr = expm_frechet(-1j * kappa * matrix * s, -1j * kappa * ds * s, compute_expm=False)
        dq, dm = 2 * np.vdot(d, dd).real, 2 * np.vdot(w, eta).real
        vd = np.exp(1j * kappa * q * s) * (rotation @ dd + dr @ d + 1j * kappa * s * dq * rotation @ d)
        vw = np.exp(2j * kappa * m * s) * (rotation @ eta + dr @ w + 2j * kappa * s * dm * rotation @ w)
        out[n, indices] = [(v1 + v2 + vd) / 2, (v1 + v2 - vd) / 2, vw]
    return gate(state, event, kappa, s), out


def variational_rhs(s, flat, event, kappa, count):
    """Independent differential variational equation for sign/refinement tests."""
    rows = flat.reshape(count + 1, 5, 2)
    state, deltas = rows[0], rows[1:]
    out = np.zeros_like(rows)
    out[0] = amplitude_rhs(s, state, event, kappa)
    i, j, a = EVENTS[event]
    d, w = state[i] - state[j], state[a]
    p, matrix = outer(w), outer(d)
    for n, delta in enumerate(deltas, 1):
        dd, eta = delta[i] - delta[j], delta[a]
        dp = np.outer(eta, w.conj()) + np.outer(w, eta.conj())
        dm = np.outer(dd, d.conj()) + np.outer(d, dd.conj())
        out[n, i] = -1j * kappa * (dp @ d + p @ dd)
        out[n, j] = -out[n, i]
        out[n, a] = -1j * kappa * (dm @ w + matrix @ eta)
    return out.ravel()


def tangent_basis(state):
    result = []
    for i in range(3):
        for vector in ((1, 0), (1j, 0), (0, 1), (0, 1j)):
            delta = np.zeros_like(state); delta[i] = vector; result.append(delta)
    for i in (3, 4):
        w = state[i]
        v = np.array([-w[1].conj(), w[0].conj()])
        for vector in (v, 1j * v):
            delta = np.zeros_like(state); delta[i] = vector; result.append(delta)
    return np.array(result)


def retract(state, delta):
    out = state + delta
    out = out.copy()
    out[3:] /= np.linalg.norm(out[3:], axis=1)[:, None]
    return out


def real_vector(z):
    return np.concatenate((np.asarray(z).ravel().real, np.asarray(z).ravel().imag))


def physical_features(state):
    """Wave coordinates plus P/sqrt(2); tangent norm equals horizontal ray norm."""
    return np.concatenate((real_vector(state[:3]), real_vector(outer(state[3:])) / np.sqrt(2)))


def feature_tangent(state, deltas):
    result = []
    for delta in deltas:
        dp = np.array([np.outer(v, w.conj()) + np.outer(w, v.conj())
                       for w, v in zip(state[3:], delta[3:])])
        result.append(np.concatenate((real_vector(delta[:3]), real_vector(dp) / np.sqrt(2))))
    return np.array(result).T


def records(state, event):
    i, j, a = EVENTS[event]
    w, d = state[a], state[i] - state[j]
    return np.array([abs(np.vdot(w, state[i])) ** 2, abs(np.vdot(w, state[j])) ** 2,
                     abs(np.vdot(w, d)) ** 2])


def record_tangent(state, deltas, event):
    i, j, a = EVENTS[event]
    out = []
    for delta in deltas:
        values = []
        for z, dz in ((state[i], delta[i]), (state[j], delta[j]),
                      (state[i] - state[j], delta[i] - delta[j])):
            b = np.vdot(state[a], z)
            db = np.vdot(delta[a], z) + np.vdot(state[a], dz)
            values.append(2 * (b.conjugate() * db).real)
        out.append(values)
    return np.array(out).T


def complement_derivative(state, event, kappa):
    i, j, a = EVENTS[event]
    d, p = state[i] - state[j], outer(state[a])
    matrix = outer(d)
    return -1j * kappa * (matrix @ p - p @ matrix)


def comparison_constants(kappa, initial_error):
    """Exact-region Lipschitz constants; see the protocol's closed-region proof.

    Both trajectories are exact, memory norms one, wave norm at most 1+e0.
    Convex segments stay in those balls. Floating evaluation is not an interval
    certificate of numerical integration or readout hardware.
    """
    n = (1 + initial_error) ** 2
    l = abs(kappa) * (1 + n + np.sqrt((1 - n) ** 2 + 16 * n))
    return float(l), float(4 * np.sqrt(n + n * n)), float(n)
