"""Flat decoupling limit of SS OCF 1, Program v0.2 sections 7 and 9.

Units c=hbar=m=1. The charged doublet has one constant internal direction;
the massless neutral field a is exactly zero for these preparations.
"""
import numpy as np


def core_force(s):
    return 1.0 - 2.0 * s + 3.0 * s * s


def core_potential(s):
    return s - s * s + s * s * s


def clock_mass(s, nu=0.4):
    return 0.25 - nu * s + 0.2 * s * s


def core_clock_force(s):
    """(1/2) V_chi,s chi^2 in the complex core equation."""
    return 0.5 * (-0.4 + 0.4 * s)


def stationary_rhs(f, omega):
    return (1.0 - omega * omega) * f - 2.0 * f**3 + 3.0 * f**5


def radial_energy(r, field, velocity, chi, chi_velocity, dr):
    """Trapezoid radial integral, fields at interior r>0; boundaries vanish."""
    full = np.pad(field, (1, 1))
    cfull = np.pad(chi, (1, 1))
    # u=r Phi, w=r chi. This centered gradient estimates dPhi/dr.
    dfield = (full[2:] - full[:-2]) / (2 * dr) / r - field / (r * r)
    dchi = (cfull[2:] - cfull[:-2]) / (2 * dr) / r - chi / (r * r)
    s = np.abs(field / r)**2
    density = (np.abs(velocity)**2 + 0.5 * chi_velocity**2
               + np.abs(dfield * r)**2 + 0.5 * (dchi * r)**2
               + r * r * (core_potential(s) + 0.5 * clock_mass(s) * (chi / r)**2
                          + 0.025 * (chi / r)**4))
    return float(4 * np.pi * dr * np.sum(density))
