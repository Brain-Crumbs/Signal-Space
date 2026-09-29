"""SS OPS 1 homogeneous zero-wave routing benchmark, Program v0.2 §6.

The three-direction incidence and scales are supplied, not emergent.
This separately registered sector does not remove the full model's memory modes.
"""
import numpy as np

SIGMA = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]])
I = np.eye(2, dtype=complex)


def projectors(triad):
    generators = np.einsum('ia,abc->ibc', triad, SIGMA)
    return (I + generators) / 2, (I - generators) / 2


def stencil(triad, order):
    """Compose explicit output(m)=sum_d C_d input(m-d) port paths."""
    plus, minus = projectors(triad)
    paths = {(0, 0, 0): I.copy()}
    for axis in order:
        next_paths = {}
        for displacement, coefficient in paths.items():
            for sign, projector in ((1, plus[axis]), (-1, minus[axis])):
                step = list(displacement)
                step[axis] += sign
                key = tuple(step)
                next_paths[key] = next_paths.get(key, 0) + projector @ coefficient
        paths = next_paths
    return np.array(list(paths)), np.array(list(paths.values()))


def fourier(q, displacements, coefficients):
    return np.einsum('...d,dij->...ij', np.exp(-1j * np.asarray(q) @ displacements.T), coefficients)


def phase(u):
    """Principal positive SU(2) phase in [0,pi], stable near both nodes."""
    scalar = np.trace(u, axis1=-2, axis2=-1).real / 2
    vector = (0.5j * np.einsum('...ij,aji->...a', u, SIGMA)).real
    return np.arctan2(np.linalg.norm(vector, axis=-1), scalar)


def apply_shifts(field, triad, order):
    plus, minus = projectors(triad)
    out = field.copy()
    for axis in order:
        out = (np.einsum('ab,...b->...a', plus[axis], np.roll(out, 1, axis=axis))
               + np.einsum('ab,...b->...a', minus[axis], np.roll(out, -1, axis=axis)))
    return out
