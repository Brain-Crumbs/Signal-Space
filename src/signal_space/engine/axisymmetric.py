"""Pure flat axisymmetric finite-volume equations, preparation and diagnostics.

No repository paths, events, artifacts, or campaign policy belong in this module.
The fixed annular discretization and RK4 arithmetic are the registered reference.
"""
import numpy as np
from signal_space.engine.ss_ocf_flat import (
    charge_density, clock_well, clock_well_prime, neutral_stiffness,
    potential, potential_prime,
)


def compile_probe():
    """A tiny synthetic zero-state toolchain probe, not research evidence."""
    from signal_space.numerics.two_object_compiled import CompiledStepper
    import time
    grid = AbsorbingGrid(.5, 3., 4., 1., .12)
    shape = (grid.nr, grid.nz)
    state = (np.zeros(shape, dtype=complex), np.zeros(shape, dtype=complex),
             *(np.zeros(shape) for _ in range(4)), 0., 0.)
    start = time.perf_counter()
    result = CompiledStepper(grid, state).advance(.001)
    if any(np.any(x) for x in result):
        raise ValueError('zero-state compiled probe failed')
    return {'seconds': time.perf_counter()-start, 'scope': 'synthetic zero-state import/compile/step only'}

class AxisGrid:
    def __init__(self, h: float, radius: float, half_length: float):
        self.h = h
        self.nr = round(radius / h)
        self.nz = round(2 * half_length / h)
        if self.nr < 3 or self.nz < 6:
            raise ValueError('insufficient axisymmetric cells')
        self.r = (np.arange(self.nr) + .5) * h
        self.z = (np.arange(self.nz) + .5) * h - self.nz * h / 2
        self.volume = (2 * np.pi * self.r * h * h)[:, None] * np.ones((1, self.nz))
        self.kr = (2 * np.pi * np.arange(1, self.nr) * h * h)[:, None] * np.ones((1, self.nz))
        self.kz = (2 * np.pi * self.r * h)[:, None] * np.ones((1, self.nz - 1))

    def faces(self, q, coefficient=None):
        dr = q[1:] - q[:-1]
        dz = q[:, 1:] - q[:, :-1]
        if coefficient is None:
            cr, cz = 1, 1
        else:
            cr = .5 * (coefficient[1:] + coefficient[:-1])
            cz = .5 * (coefficient[:, 1:] + coefficient[:, :-1])
        return self.kr * cr * dr / self.h, self.kz * cz * dz / self.h

    def divergence(self, flux_r, flux_z):
        accum = np.zeros((self.nr, self.nz), dtype=np.result_type(flux_r, flux_z))
        accum[:-1] += flux_r
        accum[1:] -= flux_r
        accum[:, :-1] += flux_z
        accum[:, 1:] -= flux_z
        return accum / self.volume

    def laplacian(self, q, coefficient=None):
        return self.divergence(*self.faces(q, coefficient))

    def squared_gradient(self, q):
        """Cell gradient from the exact face Hamiltonian derivative w.r.t. s."""
        fr = self.kr * (q[1:] - q[:-1])**2 / self.h
        fz = self.kz * (q[:, 1:] - q[:, :-1])**2 / self.h
        accum = np.zeros_like(q)
        accum[:-1] += fr
        accum[1:] += fr
        accum[:, :-1] += fz
        accum[:, 1:] += fz
        return .5 * accum / self.volume

    def energy_charge(self, state):
        phi, pi, chi, pchi, a, pia = state
        s = abs(phi)**2
        Z = neutral_stiffness(s)
        volume = self.volume
        local = (abs(pi)**2 + potential(s) + .5 * (pchi**2 + clock_well(s)*chi**2)
                 + .025 * chi**4 + .5 * pia**2 / Z)
        e = float(np.sum(volume * local))
        for q, coefficient, factor in ((phi, None, 1), (chi, None, .5), (a, Z, .5)):
            fr, fz = self.faces(q, coefficient)
            e += float(factor * (np.sum(np.real(np.conj(q[1:]-q[:-1])*fr))
                                 + np.sum(np.real(np.conj(q[:, 1:]-q[:, :-1])*fz))))
        charge = float(np.sum(volume * charge_density(phi, pi)))
        return e, charge

    def rhs(self, state):
        phi, pi, chi, pchi, a, pia = state
        s = abs(phi)**2
        Z = neutral_stiffness(s)
        neutral_v = pia / Z
        force = (potential_prime(s) + .5*clock_well_prime(s)*chi**2
                 - .1*(neutral_v**2 - self.squared_gradient(a)))
        return (pi, self.laplacian(phi) - force*phi,
                pchi, self.laplacian(chi) - clock_well(s)*chi - .1*chi**3,
                neutral_v, self.laplacian(a, Z))


def initial_state(grid, profile, separation, amplitude=.001, pair=False):
    r = profile['r']
    radial_core = np.r_[profile['u'][0]/r[1], profile['u']/r[1:-1], 0.]
    radial_mode = np.r_[profile['mode'][0]/r[1], profile['mode']/r[1:-1], 0.]
    radial_mode *= amplitude / np.max(radial_mode)
    centers = (-separation/2, separation/2) if pair else (0.,)
    core = np.zeros((grid.nr, grid.nz))
    chi = np.zeros_like(core)
    for center in centers:
        distance = np.hypot(grid.r[:, None], grid.z[None, :] - center)
        core += np.interp(distance, r, radial_core, left=radial_core[0], right=0)
        chi += np.interp(distance, r, radial_mode, left=radial_mode[0], right=0)
    zero = np.zeros_like(core)
    return (core.astype(complex), (-.9j*core).astype(complex), chi, zero.copy(),
            zero.copy(), zero.copy())


def step_rk4(grid, state, dt):
    def add(base, tangent, factor):
        return tuple(b + factor*k for b, k in zip(base, tangent))
    k1 = grid.rhs(state)
    k2 = grid.rhs(add(state, k1, dt/2))
    k3 = grid.rhs(add(state, k2, dt/2))
    k4 = grid.rhs(add(state, k3, dt))
    return tuple(q + dt/6*(x+2*y+2*z+w)
                 for q, x, y, z, w in zip(state, k1, k2, k3, k4))



class AbsorbingGrid(AxisGrid):
    def __init__(self, h: float, radius: float, half_length: float, width: float, strength: float):
        super().__init__(h, radius, half_length)
        r = np.clip((self.r[:, None] - (radius - width)) / width, 0, 1)
        z = np.clip((abs(self.z[None, :]) - (half_length - width)) / width, 0, 1)
        self.gamma = strength * np.maximum(np.sin(np.pi * r / 2) ** 2,
                                            np.sin(np.pi * z / 2) ** 2)

    def rhs_with_sinks(self, state):
        fields = state[:6]
        phi, pi, chi, pchi, a, pia = fields
        spatial = self.rhs(fields)
        gamma = self.gamma
        z = neutral_stiffness(abs(phi) ** 2)
        power = gamma * (2 * abs(pi) ** 2 + pchi ** 2 + pia ** 2 / z)
        removed_charge = gamma * charge_density(phi, pi)
        return (spatial[0], spatial[1] - gamma * pi,
                spatial[2], spatial[3] - gamma * pchi,
                spatial[4], spatial[5] - gamma * pia,
                float(np.sum(self.volume * power)),
                float(np.sum(self.volume * removed_charge)))


def step(grid, state, dt):
    def add(base, k, factor):
        return tuple(x + factor * dx for x, dx in zip(base, k))
    a = grid.rhs_with_sinks(state)
    b = grid.rhs_with_sinks(add(state, a, dt / 2))
    c = grid.rhs_with_sinks(add(state, b, dt / 2))
    d = grid.rhs_with_sinks(add(state, c, dt))
    return tuple(x + dt * (ka + 2 * kb + 2 * kc + kd) / 6
                 for x, ka, kb, kc, kd in zip(state, a, b, c, d))


def frozen_mode(grid, profile, center):
    r = profile['r']
    shape = np.r_[profile['mode'][0] / r[1], profile['mode'] / r[1:-1], 0.]
    distance = np.hypot(grid.r[:, None], grid.z[None, :] - center)
    return np.interp(distance, r, shape, left=shape[0], right=0.)


def local_observables(grid, state, profile, nominal_centers, separation):
    phi, pi, chi, pchi, _, _ = state[:6]
    rho_limit = min(grid.r[-1], 20.)
    observations = []
    density = charge_density(phi, pi)
    local = (9 * chi[0] - chi[1]) / 8
    radial_shape = np.r_[profile['mode'][0] / profile['r'][1], profile['mode'] / profile['r'][1:-1], 0.]
    for center in nominal_centers:
        mask_z = abs(grid.z - center) < separation / 4 if len(nominal_centers) == 2 else abs(grid.z) < 20
        mask_r = grid.r < rho_limit
        mask = mask_r[:, None] & mask_z[None, :]
        positive_weight = grid.volume * np.maximum(density, 0) * mask
        total = float(np.sum(positive_weight))
        measured_center = float(np.sum(positive_weight * grid.z[None, :]) / total) if total > 0 else float('nan')
        distance = np.hypot(grid.r[:, None], grid.z[None, :] - measured_center)
        mode = np.interp(distance, profile['r'], radial_shape, left=radial_shape[0], right=0.)
        weights = grid.volume * mask
        norm = float(np.sum(weights * mode ** 2))
        q = float(np.sum(weights * mode * chi) / norm)
        p = float(np.sum(weights * mode * pchi) / norm)
        observations.append({'center': measured_center, 'charge': float(np.sum(grid.volume * density * mask)),
                             'mode_q': q, 'mode_p': p,
                             'mode_energy': .5 * norm * (p * p + .41274991 ** 2 * q * q),
                             'axis_chi': float(np.interp(measured_center, grid.z, local))})
    return observations
