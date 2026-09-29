"""SS OCF 1 flat axisymmetric sector; Program v0.2 sections 7–10, 15.8.

Fixed internal direction Phi=(phi,0) is an exact reduction: all terms in the
action depend on Phi only through Phi†Phi and its ordinary derivatives.  The
second component, initially zero with zero momentum, remains zero.
"""
import numpy as np


def potential(s):
    return s - s * s + s**3


def potential_prime(s):
    return 1 - 2 * s + 3 * s * s


def clock_well(s):
    return .25 - .4 * s + .2 * s * s


def clock_well_prime(s):
    return -.4 + .4 * s


def neutral_stiffness(s):
    return 1 + .2 * s


def charge_density(phi, pi):
    """Positive charge for phi=F exp(-i omega t)."""
    return -2 * np.imag(np.conj(phi) * pi)
