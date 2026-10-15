"""Bounded diagnostics for C1-1; no campaign or numerical certificate.

Independent Hermitian ODE and explicit polynomial Hessians check the theorem's
algebra. Finite differences and floating inequalities are diagnostics, not proofs
of a preparation ball, a tube enclosure, or the later numerical backend.
"""
import unittest

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from signal_space.models.linked_memory import (
    EVENTS, gate, lift, operator_rhs, preparations, retract, tangent_basis,
    feature_tangent, physical_features,
)
from signal_space.models.operators import SIGMA


def hermitian_gate(wave, memories, event, kappa, duration):
    """Test-local formula on Hermitian memory matrices, including nonprojectors."""
    i, j, a = EVENTS[event]
    a -= 3
    out, ps = wave.copy(), memories.copy()
    d, b = wave[i] - wave[j], wave[i] + wave[j]
    q = np.vdot(d, d).real
    rotation = expm(-1j * kappa * duration * (np.outer(d, d.conj()) + 2 * ps[a]))
    evolved = np.exp(1j * kappa * duration * q) * (rotation @ d)
    out[i], out[j] = (b + evolved) / 2, (b - evolved) / 2
    ps[a] = rotation @ ps[a] @ rotation.conj().T
    return out, ps


class LocalRecordContractTests(unittest.TestCase):
    def test_full_chart_isometry_normalization_and_norm_changing_directions(self):
        for state in preparations().values():
            basis = tangent_basis(state)
            self.assertEqual(basis.shape, (16, 5, 2))
            jacobian = feature_tangent(state, basis)
            np.testing.assert_allclose(jacobian.T @ jacobian, np.eye(16), atol=2e-15)
            # The radial wave direction is retained; no fixed wave norm or charge
            # constraint is silently imposed on the twelve wave coordinates.
            radial = np.zeros_like(state)
            radial[:3] = state[:3]
            self.assertGreater(np.linalg.norm(retract(state, .01 * radial)[:3]),
                               np.linalg.norm(state[:3]))
            h = 1e-5
            for direction in basis:
                plus, minus = (retract(state, sign * h * direction) for sign in (1, -1))
                np.testing.assert_allclose(np.linalg.norm(plus[3:], axis=1), 1, atol=2e-15)
                numeric = (physical_features(plus) - physical_features(minus)) / (2 * h)
                analytic = feature_tangent(state, direction[None])[:, 0]
                np.testing.assert_allclose(numeric, analytic, atol=2e-10)

    def test_combined_chart_inverse_chordal_ball_and_quadratic_remainder(self):
        rng = np.random.default_rng(9301)
        for state in preparations().values():
            basis = tangent_basis(state)
            jacobian = feature_tangent(state, basis)
            for radius in (1e-6, .2):
                # Every sector is nonzero simultaneously, unlike axis-only checks.
                u = rng.normal(size=16)
                u *= radius / np.linalg.norm(u)
                physical = retract(state, np.einsum("i,ijk->jk", u, basis))
                displacement = physical_features(physical) - physical_features(state)
                chord = np.linalg.norm(displacement)
                self.assertLessEqual(chord, radius + 2e-15)
                self.assertLessEqual(np.linalg.norm(displacement - jacobian @ u),
                                     radius ** 2 + 2e-15)
                inverse = physical - state
                for a in (3, 4):
                    phased = physical[a] * np.exp(1j * (.3 + a))
                    inverse[a] = phased / np.vdot(state[a], phased) - state[a]
                    self.assertLess(abs(np.vdot(state[a], inverse[a])), 1e-15)
                recovered = np.array([np.vdot(b, inverse).real for b in basis])
                np.testing.assert_allclose(recovered, u, atol=1e-15)
                self.assertLessEqual(np.linalg.norm(recovered),
                                     chord / np.sqrt(1 - chord ** 2) + 2e-15)

    def test_hermitian_extension_against_independent_operator_ode(self):
        state = preparations()["active-plus"]
        wave, memories = state[:3], lift(state)[1]
        # Trace one but indefinite, deliberately outside the physical ray sphere.
        memories = memories.copy()
        memories[0] = .5 * np.eye(2) + .7 * SIGMA[0] + .2 * SIGMA[2]
        self.assertLess(np.linalg.eigvalsh(memories[0])[0], 0)
        for event in (0, 1):
            for kappa, duration in ((0., .7), (.37, 0.), (.37, .7), (-.37, -.4)):
                out, ps = hermitian_gate(wave, memories, event, kappa, duration)
                if duration:
                    initial = np.concatenate((np.outer(wave.ravel(), wave.ravel().conj()).ravel(), memories.ravel()))
                    solution = solve_ivp(operator_rhs, (0, duration), initial,
                                         args=(event, kappa), method="DOP853",
                                         rtol=2e-12, atol=2e-14, max_step=abs(duration)/8)
                    self.assertTrue(solution.success)
                    expected = np.concatenate((np.outer(out.ravel(), out.ravel().conj()).ravel(), ps.ravel()))
                    np.testing.assert_allclose(expected, solution.y[:, -1], atol=3e-12)
                else:
                    np.testing.assert_allclose(out, wave, atol=1e-15)
                    np.testing.assert_allclose(ps, memories, atol=1e-15)
                np.testing.assert_allclose(np.linalg.eigvalsh(ps), np.linalg.eigvalsh(memories), atol=2e-15)
                self.assertAlmostEqual(np.linalg.norm(out), np.linalg.norm(wave), places=13)
                charge = lambda z, p: np.einsum("ia,ib->ab", z, z.conj()) + p.sum(axis=0)
                np.testing.assert_allclose(charge(out, ps), charge(wave, memories), atol=2e-15)
                inverse, original_p = hermitian_gate(out, ps, event, kappa, -duration)
                np.testing.assert_allclose(inverse, wave, atol=2e-15)
                np.testing.assert_allclose(original_p, memories, atol=2e-15)

    def test_physical_gate_agreement_dark_and_inactive_limits(self):
        for name, state in preparations().items():
            for event in (0, 1):
                out, ps = hermitian_gate(state[:3], lift(state)[1], event, .37, .6)
                physical = gate(state, event, .37, .6)
                np.testing.assert_allclose(out, physical[:3], atol=2e-15)
                np.testing.assert_allclose(ps, lift(physical)[1], atol=2e-15)
                i, j, a = EVENTS[event]
                inactive = ({0, 1, 2} - {i, j}).pop()
                np.testing.assert_array_equal(out[inactive], state[inactive])
                np.testing.assert_array_equal(ps[1 - (a - 3)], lift(state)[1][1 - (a - 3)])
                if name == "dark":
                    np.testing.assert_allclose(out, state[:3], atol=2e-15)
                    np.testing.assert_allclose(ps, lift(state)[1], atol=2e-15)

    def test_record_hessian_block_bound_on_hermitian_segments(self):
        rng = np.random.default_rng(9302)
        # Polynomial Hessian from independent bilinear differentiation in all 18
        # real ambient coordinates; no finite differences or production backend.
        wave_directions = np.zeros((18, 3, 2), complex)
        for n in range(12):
            wave_directions[n].ravel()[n // 2] = 1 if n % 2 == 0 else 1j
        for scale in (0., .5, 1.4):
            wave = scale * (rng.normal(size=(3, 2)) + 1j*rng.normal(size=(3, 2)))
            pmat = .5 * np.eye(2) + .7 * SIGMA[0] - .2 * SIGMA[1]
            p, weight = np.linalg.norm(pmat, 2), np.linalg.norm(wave) ** 2
            for selector in (np.array([1., 0, 0]), np.array([0., 1, 0]), np.array([1., -1, 0])):
                v = selector @ wave
                dv = np.einsum("i,nij->nj", selector, wave_directions)
                dp = np.zeros((18, 2, 2), complex)
                dp[12:15] = SIGMA
                hessian = np.empty((18, 18))
                for h in range(18):
                    for k in range(18):
                        hessian[h, k] = 2 * (np.vdot(dv[h], pmat @ dv[k])
                            + np.vdot(dv[h], dp[k] @ v)
                            + np.vdot(dv[k], dp[h] @ v)).real
                bound = np.dot(selector, selector) * (p + np.sqrt(p*p + 4*weight))
                self.assertLessEqual(np.linalg.norm(hessian, 2), bound + 2e-13)
                np.testing.assert_array_equal(hessian[15:], 0)
                np.testing.assert_allclose(hessian, hessian.T, atol=2e-15)


if __name__ == "__main__":
    unittest.main()
