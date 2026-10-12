"""Unchanged SS OCF 1 action with both complex doublet components retained.

The annular mesh and its variational neutral coupling are shared with Test 8's
reference solver. Preparation corrections precede evolution and are measured;
they are neither an external evolution-time force nor a stationary-pair claim.
"""
from __future__ import annotations

import numpy as np
from scipy.sparse.linalg import LinearOperator, lsmr

from signal_space.models.two_object import (
    clock_well, clock_well_prime, neutral_stiffness, potential, potential_prime,
)
from signal_space.numerics.two_object_quiet import AbsorbingGrid, step


def density(phi):
    return np.sum(abs(phi)**2, axis=0)


def charge_density(phi, pi):
    return -2 * np.imag(np.sum(np.conj(phi) * pi, axis=0))


class DoubletGrid(AbsorbingGrid):
    def rhs(self, state):
        phi, pi, chi, pchi, a, pia = state[:6]
        s = density(phi)
        Z = neutral_stiffness(s)
        av = pia / Z
        force = potential_prime(s) + .5 * clock_well_prime(s) * chi**2
        force -= .1 * (av**2 - self.squared_gradient(a))
        return (pi, np.stack([self.laplacian(q) for q in phi]) - force * phi,
                pchi, self.laplacian(chi) - clock_well(s) * chi - .1 * chi**3,
                av, self.laplacian(a, Z))

    def cell_energy(self, state):
        phi, pi, chi, pchi, a, pia = state[:6]
        s = density(phi)
        Z = neutral_stiffness(s)
        local = (np.sum(abs(pi)**2, axis=0) + potential(s)
                 + .5 * (pchi**2 + clock_well(s) * chi**2)
                 + .025 * chi**4 + .5 * pia**2 / Z)
        energies = self.volume * local
        for q, coefficient, factor in [*( (q, None, 1.) for q in phi),
                                       (chi, None, .5), (a, Z, .5)]:
            fr, fz = self.faces(q, coefficient)
            er = factor * np.real(np.conj(q[1:] - q[:-1]) * fr)
            ez = factor * np.real(np.conj(q[:, 1:] - q[:, :-1]) * fz)
            energies[:-1] += er / 2
            energies[1:] += er / 2
            energies[:, :-1] += ez / 2
            energies[:, 1:] += ez / 2
        return energies

    def energy_charge(self, state):
        return (float(np.sum(self.cell_energy(state))),
                float(np.sum(self.volume * charge_density(*state[:2]))))

    def gradients(self, q):
        return (np.gradient(q, self.h, axis=-2, edge_order=2),
                np.gradient(q, self.h, axis=-1, edge_order=2))

    def momentum_density(self, state):
        phi, pi, chi, pchi, a, pia = state[:6]
        dzphi = self.gradients(phi)[1]
        return (-2 * np.real(np.sum(np.conj(pi) * dzphi, axis=0))
                - pchi * self.gradients(chi)[1] - pia * self.gradients(a)[1])

    def rhs_with_sinks(self, state):
        fields = state[:6]
        phi, pi, chi, pchi, a, pia = fields
        rhs = self.rhs(fields)
        Z = neutral_stiffness(density(phi))
        power = self.gamma * (2 * np.sum(abs(pi)**2, axis=0)
                              + pchi**2 + pia**2 / Z)
        return (*[rhs[i] - self.gamma * fields[i] if i in (1, 3, 5)
                  else rhs[i] for i in range(6)],
                float(np.sum(self.volume * power)),
                float(np.sum(self.volume * self.gamma * charge_density(phi, pi))),
                float(np.sum(self.volume * self.gamma * self.momentum_density(fields))))

    def face_fluxes(self, state):
        """Energy/charge currents from the same discrete face Hamiltonian.

        Momentum stress is a separate continuum-consistent diagnostic. It is
        not an exact discrete Noether invariant on the finite mirror box.
        """
        phi, pi, chi, pchi, a, pia = state[:6]
        Z = neutral_stiffness(density(phi))
        av = pia / Z
        sdot = 2 * np.real(np.sum(np.conj(phi) * pi, axis=0))
        energy, charge = [], []
        for axis in (0, 1):
            left = (slice(None, -1), slice(None)) if axis == 0 else (slice(None), slice(None, -1))
            right = (slice(1, None), slice(None)) if axis == 0 else (slice(None), slice(1, None))
            ef = np.zeros_like(self.kr if axis == 0 else self.kz)
            qf = np.zeros_like(ef)
            for q, v in zip(phi, pi):
                f = self.faces(q)[axis]
                ef -= np.real(np.conj(v[left] + v[right]) * f)
                qf += np.imag(np.conj(q[left] + q[right]) * f)
            ef -= .5 * (pchi[left] + pchi[right]) * self.faces(chi)[axis]
            ef -= .5 * (av[left] + av[right]) * self.faces(a, Z)[axis]
            # The face energy is split between its two cells. Density-dependent
            # Z therefore carries an additional discrete redistribution current.
            # Z_s/8=.025; this term vanishes in the continuum limit but is
            # required for the exact cellwise variational energy balance.
            conductance = (self.kr if axis == 0 else self.kz) / self.h
            ef += .025 * conductance * (a[right] - a[left])**2 * (sdot[left] - sdot[right])
            energy.append(ef)
            charge.append(qf)
        return tuple(energy), tuple(charge)

    def stress(self, state):
        phi, pi, chi, pchi, a, pia = state[:6]
        s = density(phi)
        Z = neutral_stiffness(s)
        pr, pz = self.gradients(phi)
        cr, cz = self.gradients(chi)
        ar, az = self.gradients(a)
        lagrangian = (np.sum(abs(pi)**2 - abs(pr)**2 - abs(pz)**2, axis=0)
                      - potential(s) + .5 * (pia**2 / Z - Z * (ar**2 + az**2))
                      + .5 * (pchi**2 - cr**2 - cz**2 - clock_well(s) * chi**2)
                      - .025 * chi**4)
        return (2 * np.real(np.sum(np.conj(pr) * pz, axis=0)) + Z * ar * az + cr * cz,
                2 * np.sum(abs(pz)**2, axis=0) + Z * az**2 + cz**2 + lagrangian)

    def tube_balance(self, state, center, radius):
        mask = (self.r[:, None] < radius) & (abs(self.z[None, :] - center) < radius)
        energy, charge = self.face_fluxes(state)
        # For a cell mask, the sum of divergence is precisely outward flux.
        out = lambda f: float(np.sum(self.volume * mask * self.divergence(*f)))
        trz, tzz = self.stress(state)
        area_r, area_z = self.kr, self.kz
        stress_flux = (area_r * .5 * (trz[:-1] + trz[1:]),
                       area_z * .5 * (tzz[:, :-1] + tzz[:, 1:]))
        gamma = self.gamma
        phi, pi, chi, pchi, _, pia = state[:6]
        power = gamma * (2 * np.sum(abs(pi)**2, axis=0) + pchi**2
                         + pia**2 / neutral_stiffness(density(phi)))
        return {'energy': float(np.sum(self.cell_energy(state) * mask)),
                'charge': float(np.sum(self.volume * mask * charge_density(phi, pi))),
                'momentum': float(np.sum(self.volume * mask * self.momentum_density(state))),
                'energy_flux': out(energy), 'charge_flux': out(charge),
                'momentum_flux': out(stress_flux),
                'energy_sink_rate': float(np.sum(self.volume * mask * power)),
                'charge_sink_rate': float(np.sum(self.volume * mask * gamma * charge_density(phi, pi))),
                'momentum_sink_rate': float(np.sum(self.volume * mask * gamma * self.momentum_density(state)))}


def radial_fields(profile):
    r = profile['r']
    F = np.r_[profile['u'][0] / r[1], profile['u'] / r[1:-1], 0.]
    f = np.r_[profile['mode'][0] / r[1], profile['mode'] / r[1:-1], 0.]
    return r, F, f


def core_parts(grid, profile, case):
    r, F, _ = radial_fields(profile)
    centers = (-case['separation'] / 2, case['separation'] / 2) if case['pair'] else (0.,)
    directions = (np.array([1., 0.], complex),
                  np.exp(1j * case['matter_phase']) * np.array(
                      [np.cos(case['orientation']), np.sin(case['orientation'])], complex))
    parts = []
    for i, center in enumerate(centers):
        distance = np.hypot(grid.r[:, None], grid.z[None, :] - center)
        parts.append(directions[i][:, None, None] * np.interp(distance, r, F, right=0))
    return parts, centers


def quiet_residual(grid, psi, omega=.9):
    return (-np.stack([grid.laplacian(q) for q in psi])
            + (potential_prime(density(psi)) - omega**2) * psi)


def weighted_norm(grid, field):
    return float(np.sqrt(np.sum(grid.volume * np.sum(abs(field)**2, axis=0))))


def reduce_residual(grid, parts, options):
    """Bounded constrained linear defect correction, with a true residual check.

    Real-linear Hessian, volume-weighted variables; exclude each core's
    amplitude, phase and axial translation tangents. No stationary-pair solve
    is asserted. A failed/backtracked correction is recorded and not hidden.
    """
    psi = sum(parts).copy()
    original = psi.copy()
    rootv = np.sqrt(grid.volume)
    shape = psi.shape
    pack = lambda q: np.concatenate(((q * rootv).real.ravel(), (q * rootv).imag.ravel()))
    def unpack(x):
        n = psi.size
        return (x[:n].reshape(shape) + 1j * x[n:].reshape(shape)) / rootv
    tangents = [pack(q) for part in parts for q in (part, 1j * part, grid.gradients(part)[1])]
    basis, singular, _ = np.linalg.svd(np.stack(tangents, axis=1), full_matrices=False)
    basis = basis[:, singular > singular[0] * 1e-12]
    project = lambda x: x - basis @ (basis.T @ x)
    start = weighted_norm(grid, quiet_residual(grid, psi))
    records = []
    for _ in range(options['iterations']):
        s = density(psi)
        diagonal = potential_prime(s) - .9**2
        def action(x):
            q = unpack(project(x))
            coupling = np.real(np.sum(np.conj(psi) * q, axis=0))
            mq = -np.stack([grid.laplacian(v) for v in q]) + diagonal * q
            mq += 2 * (-2 + 6 * s) * psi * coupling
            return project(pack(mq))
        operator = LinearOperator((2 * psi.size, 2 * psi.size), matvec=action, rmatvec=action)
        residual = quiet_residual(grid, psi)
        solution = lsmr(operator, -project(pack(residual)), damp=options['damping'],
                        atol=1e-7, btol=1e-7, maxiter=options['max_linear_iterations'])
        correction = unpack(project(solution[0]))
        norm = weighted_norm(grid, correction)
        cap = options['max_correction_fraction'] * weighted_norm(grid, psi)
        if norm > cap:
            correction *= cap / norm
        before = weighted_norm(grid, residual)
        accepted = False
        fraction = 1.
        for _ in range(12):
            candidate = psi + fraction * correction
            after = weighted_norm(grid, quiet_residual(grid, candidate))
            if after < before:
                psi = candidate
                accepted = True
                break
            fraction /= 2
        records.append({'before': before, 'after': after if accepted else before,
                        'accepted': accepted, 'fraction': fraction,
                        'linear_stop': int(solution[1]), 'linear_iterations': int(solution[2])})
        if not accepted:
            break
    return psi, {'method': 'constrained-linear-defect-v1', 'initial_norm': start,
                 'final_norm': weighted_norm(grid, quiet_residual(grid, psi)),
                 'corrections': records, 'stationary_pair_established': False,
                 'total_correction_fraction': weighted_norm(grid, psi-original) / weighted_norm(grid, original)}


def initial_state(grid, profile, case, correction):
    parts, centers = core_parts(grid, profile, case)
    naive = sum(parts)
    if case['preparation'] == 'residual-reduced':
        psi, preparation = reduce_residual(grid, parts, correction)
    else:
        psi = naive.copy()
        norm = weighted_norm(grid, quiet_residual(grid, psi))
        preparation = {'method': 'naive-superposition', 'initial_norm': norm,
                       'final_norm': norm, 'corrections': [], 'stationary_pair_established': False}
    r, _, mode = radial_fields(profile)
    mode = mode / np.max(abs(mode)) * case['clock_peak']
    chi = np.zeros_like(grid.volume)
    pchi = np.zeros_like(chi)
    for i, center in enumerate(centers):
        shape = np.interp(np.hypot(grid.r[:, None], grid.z[None, :] - center), r, mode, right=0)
        phase = case['clock_phase'] if i else 0.
        chi += shape * np.cos(phase)
        pchi -= case['omega_clock'] * shape * np.sin(phase)
    pi = -.9j * psi
    a, pia = np.zeros_like(chi), np.zeros_like(chi)
    quiet = (psi.copy(), pi.copy(), chi.copy(), pchi.copy(), a.copy(), pia.copy())
    source = case['source']
    distance = np.hypot(grid.r[:, None], grid.z[None, :] - centers[0])
    bump = np.zeros_like(distance)
    inside = distance < source['radius']
    x = distance[inside] / source['radius']
    bump[inside] = np.exp(1 - 1 / (1 - x*x))
    if source['channel'] == 'neutral':
        a = source['amplitude'] * bump * np.cos(
            source['carrier'] * (grid.z[None, :] - centers[0]) + source['phase'])
        # Right-moving vacuum canonical data are an ansatz in the material core.
        pia = -neutral_stiffness(density(psi)) * grid.gradients(a)[1]
    elif source['channel'] == 'structural':
        perturbation = source['amplitude'] * bump * np.exp(
            1j * (source['carrier'] * (grid.z[None, :] - centers[0]) + source['phase']))
        psi = psi.copy()
        psi[0] += perturbation
        pi = -.9j * psi
    state = (psi, pi, chi, pchi, a, pia, 0., 0., 0.)
    e0, q0 = grid.energy_charge(quiet)
    e1, q1 = grid.energy_charge(state)
    preparation.update({'quiet_energy': e0, 'quiet_charge': q0,
                        'prepared_energy': e1, 'prepared_charge': q1,
                        'source_energy_change': e1 - e0, 'source_charge_change': q1 - q0,
                        'source_momentum_change': float(np.sum(grid.volume * (
                            grid.momentum_density(state) - grid.momentum_density(quiet)))),
                        'coherence': float(np.cos(case['orientation']) * np.cos(case['matter_phase'])),
                        'post_clock_residual_norm': weighted_norm(grid, quiet_residual(grid, quiet[0])
                            + .5 * clock_well_prime(density(quiet[0])) * chi**2 * quiet[0]),
                        'centers': list(centers)})
    return state, preparation


def local_records(grid, state, case, profile):
    phi, pi, chi, pchi, _, _ = state[:6]
    charge = charge_density(phi, pi)
    dpi = grid.rhs_with_sinks(state)[1]
    chargedot = charge_density(phi, dpi)
    _, _, mode = radial_fields(profile)
    records = []
    centers = (-case['separation']/2, case['separation']/2) if case['pair'] else (0.,)
    axis = lambda q: (9 * q[0] - q[1]) / 8
    axis_chi, axis_p = axis(chi), axis(pchi)
    axis_dz = axis(grid.gradients(chi)[1])
    for i, nominal in enumerate(centers):
        mask = (grid.r[:, None] < case['tube_radius']) & (abs(grid.z[None, :] - nominal) < case['tube_radius'])
        weights = grid.volume * mask
        Q = float(np.sum(weights * charge))
        if Q <= 0:
            raise ValueError('nonpositive detector charge; tracking is undefined')
        center = float(np.sum(weights * charge * grid.z[None, :]) / Q)
        speed = float(np.sum(weights * chargedot * (grid.z[None, :] - center)) / Q)
        if abs(speed) >= 1 or abs(center - nominal) >= case['tube_radius'] / 2:
            raise ValueError('detector is non-timelike or left the locked tracking region')
        local = float(np.interp(center, grid.z, axis_chi))
        convective = float(np.interp(center, grid.z, axis_p + speed * axis_dz))
        proper_rate = np.sqrt(1 - speed**2)
        f = np.interp(np.hypot(grid.r[:, None], grid.z[None, :] - center), profile['r'], mode, right=0)
        norm = float(np.sum(weights * f*f))
        q = float(np.sum(weights * f * chi) / norm)
        p = float(np.sum(weights * f * pchi) / norm)
        records.append({'object': 'AB'[i], 'center': center, 'speed': speed,
                        'proper_rate': float(proper_rate), 'chi': local,
                        'dchi_dt': convective, 'dchi_dtau': float(convective / proper_rate),
                        'envelope': float(np.hypot(local, convective / (proper_rate * case['omega_clock']))),
                        'mode_energy': .5 * norm * (p*p + case['omega_clock']**2 * q*q),
                        'tube': grid.tube_balance(state, nominal, case['tube_radius'])})
    return records


def evolve_step(grid, state, dt):
    return step(grid, state, dt)
