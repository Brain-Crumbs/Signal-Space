"""Independent event-law controls; no desired research outcome is asserted."""

from copy import deepcopy
import unittest
import numpy as np

from signal_space.experiments.reciprocal import ReciprocalExperiment, ROOT
from signal_space.contracts.validation import ContractError
from signal_space.models.reciprocal import rhs, exact_gate
from signal_space.numerics.reciprocal import gate, circuit, EVENTS, ALTERNATE, dependencies
from signal_space.analysis.reciprocal import ledger
from signal_space.runtime.io import read_json


class ReciprocalTests(unittest.TestCase):
    def setUp(self):
        self.config = read_json(ROOT / "fixtures/research/gross-test-02.json")
        self.p = self.config["parameters"]

    def test_closed_schema_rejects_changed_physics_and_boolean_indices(self):
        ReciprocalExperiment().validate(self.config)
        for mutate in (
            lambda c: c["parameters"].update(frozen=True),
            lambda c: c["analysis"].update(max_residual=1),
            lambda c: c["parameters"]["events"][0].__setitem__(0, False),
            lambda c: c["parameters"].update(lambdas=[0, 0.2]),
        ):
            candidate = deepcopy(self.config)
            mutate(candidate)
            with self.assertRaises(ContractError):
                ReciprocalExperiment().validate(candidate)

    def test_exact_solution_derivative_and_zero_wave_null(self):
        state = np.array([[0.4, 0.3j], [-0.2j, 0.5], [1, 1j]], complex)
        state[2] /= np.sqrt(2)
        epsilon = 1e-6
        derivative = (exact_gate(state, np.pi/2, 0.1, epsilon) - exact_gate(state, np.pi/2, 0.1, -epsilon)) / (2 * epsilon)
        np.testing.assert_allclose(derivative.ravel(), rhs(0, state.ravel(), np.pi/2, 0.1), atol=2e-9)
        zero = state.copy()
        zero[:2] = 0
        np.testing.assert_allclose(gate(zero, self.p, 0.1)[-1], zero, atol=1e-14)

    def test_frozen_router_has_exact_swap_control(self):
        state = np.array([[0.4 + 0.2j, 0.3j], [-0.2j, 0.5], [1, 0]], complex)
        out = gate(state, self.p, 0, frozen=True)[-1]
        expected = np.array([[state[1, 0], state[0, 1]], [state[0, 0], state[1, 1]], [1, 0]])
        np.testing.assert_allclose(out, expected, atol=1e-10)

    def test_wrong_memory_sign_breaks_ledger(self):
        state = np.array([[0.4, 0.3j], [-0.2j, 0.5], [1, 1j]], complex)
        state[2] /= np.sqrt(2)
        derivative = rhs(0, state.ravel(), np.pi/2, 0.1).reshape(3,2)
        def charge_derivative(d):
            return sum(np.outer(v, z.conj()) + np.outer(z, v.conj()) for z,v in zip(state,d))
        self.assertLess(np.linalg.norm(charge_derivative(derivative)), 1e-12)
        derivative[2] *= -1
        self.assertGreater(np.linalg.norm(charge_derivative(derivative)), 0.1)

    def test_schedule_preserves_every_wire_order(self):
        for wire in range(12):
            original = [i for i in range(12) if wire in EVENTS[i]]
            alternate = [i for i in ALTERNATE if wire in EVENTS[i]]
            self.assertEqual(original, alternate)
        self.assertFalse(dependencies()[3,0])
        self.assertFalse(dependencies()[11,0])
        self.assertTrue(dependencies()[8,0])


if __name__ == "__main__":
    unittest.main()
