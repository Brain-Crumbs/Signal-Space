"""SS OCF 1 matter action, frozen at an event; c=hbar=m=M0=1.

Six real fields q1..q4,a,chi. Connection A is flat and set to zero in its
local trivialization. The metric is calculated from the Hermitian coframe.
The quartic orientation control is a separately named model, not part of OCF 1.
"""
import numpy as np

ETA = np.diag([1., -1., -1., -1.])


def metric(e):
    return e.T @ ETA @ e


def z_of(q, epsilon=0.1):
    return 1 + epsilon * np.dot(q, q) / 2


def kinetic(grad, inv, z):
    """Derivative part of L_m from section 7.3, with real doublet normalization."""
    return np.einsum('am,mn,an->', grad[:4], inv, grad[:4]) / 2 + z * (grad[4] @ inv @ grad[4]) / 2 + (grad[5] @ inv @ grad[5]) / 2


def potentials(q, chi):
    s = np.dot(q, q) / 2
    u = s - 0.5*s*s + 0.25*s**3
    v = 1.0 - 0.5*s + 0.25*s*s
    return u + v*chi*chi/2 + 0.1*chi**4/4


def lagrangian(fields, grad, inv, epsilon=0.1):
    return kinetic(grad, inv, z_of(fields[:4], epsilon)) - potentials(fields[:4], fields[5])


def quartic_control(n, dn, inv, kappa=0.4):
    """Versioned orientation control: -kappa H_ab H^ab/4, H=n.(dn x dn)."""
    h = np.einsum('i,abi->ab', n, np.cross(dn[:, None, :], dn[None, :, :]))
    return -kappa*np.einsum('ab,ac,bd,cd->', h, inv, inv, h)/4
