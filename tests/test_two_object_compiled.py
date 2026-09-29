"""Backend equivalence and independent annular-action controls; no acceptance claims."""
import importlib.util
import unittest

import numpy as np

from signal_space.numerics.two_object_quiet import AbsorbingGrid, step


def fixture(grid, active=True):
    rng = np.random.default_rng(821)
    shape = (grid.nr, grid.nz)
    return tuple(.1*(rng.normal(size=shape)+1j*rng.normal(size=shape)) if k < 2
                 else .01*rng.normal(size=shape) if active or k < 4 else np.zeros(shape)
                 for k in range(6)) + (.02, -.01)


@unittest.skipUnless(importlib.util.find_spec('numba'), 'optional compiled backend not installed')
class CompiledTests(unittest.TestCase):
    def make(self, grid, state, **kwargs):
        from signal_space.numerics.two_object_compiled import CompiledStepper
        return CompiledStepper(grid, state, **kwargs)

    def assert_state(self, reference, actual):
        for x, y in zip(reference, actual):
            np.testing.assert_allclose(x, y, rtol=1e-12, atol=1e-14)

    def test_derivatives_steps_and_accumulated_sinks(self):
        for h in (.5, .25):
            for active in (False, True):
                grid = AbsorbingGrid(h, 3, 4, 1, .12)
                original = fixture(grid, active)
                state = tuple(x.copy() if hasattr(x, 'copy') else x for x in original)
                fast = self.make(grid, state)
                self.assert_state(grid.rhs_with_sinks(state), fast.derivative())
                for _ in range(100):
                    state = step(grid, state, .002)
                    fast.advance(.002)
                self.assert_state(state, fast.state)
                self.assert_state(original, fixture(grid, active))

    def test_neutral_null_parity_and_subnormal_rejection(self):
        grid = AbsorbingGrid(.5, 3, 4, 1, .12)
        zero = fixture(grid, False)
        full, quiet = self.make(grid, zero), self.make(grid, zero, exact_zero=True)
        for _ in range(30):
            self.assert_state(full.advance(.005), quiet.advance(.005))
        self.assertFalse(np.any(quiet.state[4]))
        self.assertFalse(np.any(quiet.state[5]))
        tiny = list(zero)
        tiny[4] = tiny[4].copy()
        tiny[4][0, 0] = np.nextafter(0., 1.)
        with self.assertRaises(ValueError):
            self.make(grid, tiny, exact_zero=True)
        active = fixture(grid)
        reversed_state = (*active[:4], -active[4], -active[5], *active[6:])
        plus, minus = self.make(grid, active), self.make(grid, reversed_state)
        for _ in range(20):
            plus.advance(.002)
            minus.advance(.002)
        self.assert_state(plus.state[:4], minus.state[:4])
        self.assert_state(plus.state[4:6], tuple(-x for x in minus.state[4:6]))
        self.assert_state(plus.state[6:], minus.state[6:])

    def test_manufactured_axis_and_vacuum_dispersion(self):
        grid = AbsorbingGrid(.2, 4, 6, 1, 0)
        shape = (grid.nr, grid.nz)
        zero = np.zeros(shape)
        a = grid.r[:, None]**2 + grid.z[None, :]**2
        state = (zero.astype(complex), zero.astype(complex), zero.copy(), zero.copy(), a, zero.copy(), 0., 0.)
        rhs = self.make(grid, state).derivative()
        np.testing.assert_allclose(rhs[5][:-1, 1:-1], 6, atol=1e-11)
        # Mirror-compatible axial eigenmode; neutral is exactly linear in vacuum.
        wave = np.broadcast_to(np.cos(3*np.pi*(np.arange(grid.nz)+.5)/grid.nz), shape).copy()
        state = (*state[:4], wave, zero.copy(), 0., 0.)
        rhs = self.make(grid, state).derivative()
        eigenvalue = -4*np.sin(3*np.pi/(2*grid.nz))**2/grid.h**2
        np.testing.assert_allclose(rhs[5], eigenvalue*wave, atol=1e-12)
        self.assertLess(abs(np.sum(grid.volume*rhs[5])), 1e-11)
        amplitude = 1e-8
        # Core mass=1 and clock mass²=.25 in the vacuum linearization.
        state = ((amplitude*wave).astype(complex), zero.astype(complex),
                 amplitude*wave, zero.copy(), zero.copy(), zero.copy(), 0., 0.)
        rhs = self.make(grid, state).derivative()
        np.testing.assert_allclose(rhs[1], (eigenvalue-1)*state[0], rtol=1e-12, atol=1e-20)
        np.testing.assert_allclose(rhs[3], (eigenvalue-.25)*state[2], rtol=1e-12, atol=1e-20)

    def test_hamiltonian_derivative_interior_axis_and_boundary(self):
        grid = AbsorbingGrid(.5, 3, 4, 1, 0)
        state = fixture(grid)
        rhs = self.make(grid, state).derivative()
        for i, j in ((0, 0), (2, 4), (grid.nr-1, grid.nz-1)):
            for direction in (1, 1j):
                delta = 1e-6
                def energy(sign):
                    fields = list(state[:6])
                    fields[0] = fields[0].copy()
                    fields[0][i, j] += sign * direction * delta
                    return grid.energy_charge(fields)[0]
                numerical = (energy(1)-energy(-1))/(2*delta)
                expected = -2*grid.volume[i,j]*(rhs[1][i,j].real if direction == 1 else rhs[1][i,j].imag)
                self.assertAlmostEqual(numerical, expected, delta=3e-8)

    def test_input_precision_and_alias_contract(self):
        grid = AbsorbingGrid(.5, 3, 4, 1, .12)
        state = fixture(grid)
        before = tuple(x.copy() for x in state[:6])
        fast = self.make(grid, state)
        fast.advance(.002)
        for x, y in zip(before, state):
            np.testing.assert_array_equal(x, y)
        bad = list(state)
        bad[2] = bad[2].astype('float32')
        with self.assertRaises(ValueError):
            self.make(grid, bad)
        with self.assertRaises(ValueError):
            fast.advance(float('nan'))


if __name__ == '__main__':
    unittest.main()
