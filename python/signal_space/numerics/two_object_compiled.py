"""Serial, strict IEEE CPU implementation of the Test 8 annular FV RK4 step.

The NumPy grid remains the equation/diagnostic reference. No fast math or
threaded reductions are used. Work arrays belong to one integrator; advancing
mutates its owned state, never the constructor's input. Copy state to retain it.
"""
from __future__ import annotations

import numpy as np
from numba import njit


@njit(cache=True, fastmath=False)
def _density(phi, density):
    for i in range(phi.shape[0]):
        for j in range(phi.shape[1]):
            density[i, j] = abs(phi[i, j]) ** 2


@njit(cache=True, fastmath=False)
def _rhs(fields, out, density, volume, kr, kz, gamma, h, neutral_zero):
    phi, pi, chi, pchi, a, pia = fields
    nr, nz = phi.shape
    energy_sink, charge_sink = 0., 0.
    for i in range(nr):
        for j in range(nz):
            s = density[i, j]
            stiffness = 1 + .2 * s
            lp, lc, la, grad = 0.j, 0., 0., 0.
            # Same face conductances, coefficient averages and accumulation
            # order as AxisGrid; absent faces implement axis/mirror boundaries.
            for direction in range(4):
                ii, jj = i, j
                if direction == 0:
                    if i == nr - 1:
                        continue
                    ii, area, sign = i + 1, kr[i], 1.
                elif direction == 1:
                    if i == 0:
                        continue
                    ii, area, sign = i - 1, kr[i - 1], -1.
                elif direction == 2:
                    if j == nz - 1:
                        continue
                    jj, area, sign = j + 1, kz[i], 1.
                else:
                    if j == 0:
                        continue
                    jj, area, sign = j - 1, kz[i], -1.
                dp = sign * (phi[ii, jj] - phi[i, j])
                dc = sign * (chi[ii, jj] - chi[i, j])
                lp += sign * (area * dp / h)
                lc += sign * (area * dc / h)
                if not neutral_zero:
                    da = sign * (a[ii, jj] - a[i, j])
                    coefficient = .5 * (stiffness + 1 + .2 * density[ii, jj])
                    la += sign * (area * coefficient * da / h)
                    grad += area * da ** 2 / h
            v = 0. if neutral_zero else pia[i, j] / stiffness
            force = (1 - 2 * s + 3 * s * s
                     + .5 * (-.4 + .4 * s) * chi[i, j] ** 2
                     - .1 * (v ** 2 - .5 * grad / volume[i]))
            g = gamma[i, j]
            out[0][i, j] = pi[i, j]
            out[1][i, j] = lp / volume[i] - force * phi[i, j] - g * pi[i, j]
            out[2][i, j] = pchi[i, j]
            out[3][i, j] = (lc / volume[i] - (.25 - .4*s + .2*s*s)*chi[i, j]
                             - .1*chi[i, j]**3 - g*pchi[i, j])
            out[4][i, j] = v
            out[5][i, j] = 0. if neutral_zero else la / volume[i] - g * pia[i, j]
            power = 2 * abs(pi[i, j])**2 + pchi[i, j]**2
            if not neutral_zero:
                power += pia[i, j]**2 / stiffness
            energy_sink += volume[i] * (g * power)
            charge_sink += volume[i] * (g * (-2 * (phi[i, j].conjugate()*pi[i, j]).imag))
    return energy_sink, charge_sink


@njit(cache=True, fastmath=False)
def _stage(base, tangent, factor, out):
    for i in range(base.shape[0]):
        for j in range(base.shape[1]):
            out[i, j] = base[i, j] + factor * tangent[i, j]


@njit(cache=True, fastmath=False)
def _finish(base, a, b, c, d, dt):
    for i in range(base.shape[0]):
        for j in range(base.shape[1]):
            base[i, j] += dt * (a[i, j] + 2*b[i, j] + 2*c[i, j] + d[i, j]) / 6


class CompiledStepper:
    """Own a float64/complex128 state and reusable nonaliasing RK4 buffers.

    ``exact_zero`` is only valid for this closed, homogeneous neutral equation.
    It rejects any nonzero neutral value, including subnormal values. The full
    backend is the default and must remain available for neutral-null controls.
    """

    def __init__(self, grid, state, *, exact_zero=False):
        from signal_space.numerics.two_object_quiet import AbsorbingGrid
        if type(grid) is not AbsorbingGrid:
            raise ValueError('compiled equations require the registered AbsorbingGrid')
        if len(state) != 8:
            raise ValueError('six fields and two integrated sinks are required')
        self.grid = grid
        self.fields = tuple(np.array(x, copy=True, order='C') for x in state[:6])
        for k, x in enumerate(self.fields):
            dtype = np.dtype('complex128' if k < 2 else 'float64')
            if x.shape != (grid.nr, grid.nz) or x.dtype != dtype or not np.isfinite(x).all():
                raise ValueError('fields require finite, matching float64/complex128 arrays')
        self.sinks = tuple(float(x) for x in state[6:])
        if not np.isfinite(self.sinks).all():
            raise ValueError('sinks must be finite')
        self.exact_zero = exact_zero
        self._check_neutral()
        self.stages = tuple(tuple(np.empty_like(x) for x in self.fields) for _ in range(4))
        self.work = tuple(np.empty_like(x) for x in self.fields)
        self.density = np.empty_like(self.fields[2])
        # Fixed geometry is copied as radial vectors, not rebuilt per stage.
        self.geometry = (grid.volume[:, 0].copy(), grid.kr[:, 0].copy(),
                         grid.kz[:, 0].copy(), grid.gamma.copy(), grid.h)

    @property
    def state(self):
        return (*self.fields, *self.sinks)

    def _check_neutral(self):
        if self.exact_zero and (np.any(self.fields[4] != 0) or np.any(self.fields[5] != 0)):
            raise ValueError('exact-zero specialization cannot discard a neutral field')

    def _evaluate(self, fields, out):
        _density(fields[0], self.density)
        return _rhs(fields, out, self.density, *self.geometry, self.exact_zero)

    def derivative(self):
        self._check_neutral()
        sinks = self._evaluate(self.fields, self.stages[0])
        return (*(x.copy() for x in self.stages[0]), *sinks)

    def advance(self, dt):
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError('dt must be finite and positive')
        self._check_neutral()
        a, b, c, d = self.stages
        sa = self._evaluate(self.fields, a)
        for tangent, factor, out in ((a, dt/2, b), (b, dt/2, c), (c, dt, d)):
            for base, delta, work in zip(self.fields, tangent, self.work):
                _stage(base, delta, factor, work)
            sinks = self._evaluate(self.work, out)
            if out is b:
                sb = sinks
            elif out is c:
                sc = sinks
            else:
                sd = sinks
        for values in zip(self.fields, a, b, c, d):
            _finish(*values, dt)
        self.sinks = tuple(x + dt*(ka+2*kb+2*kc+kd)/6
                           for x, ka, kb, kc, kd in zip(self.sinks, sa, sb, sc, sd))
        return self.state
