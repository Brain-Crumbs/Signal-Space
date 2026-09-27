"""Independent local controls for the outgoing-layer Test 8 prerequisite."""

import json
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np

from signal_space.analysis.two_object_quiet import positive_crossings
from signal_space.contracts.validation import ContractError
from signal_space.experiments.two_object_quiet import CRITERIA, TwoObjectQuietExperiment
from signal_space.numerics.two_object_quiet import AbsorbingGrid, step

ROOT = Path(__file__).resolve().parents[2]


class QuietPrerequisiteTests(unittest.TestCase):
    def test_zero_neutral_exact_and_sink_sign(self):
        grid = AbsorbingGrid(.5, 5, 5, 2, .2)
        r, z = grid.r[:, None], grid.z[None, :]
        phi = np.exp(-((r-1)**2 + (z-3)**2)) * np.ones((1, grid.nz), dtype=complex)
        pi = -.9j * phi
        chi = np.broadcast_to(.001 * np.exp(-((r-1)**2 + (z-3)**2)), phi.shape).copy()
        zero = np.zeros_like(chi)
        state = (phi, pi, chi, zero.copy(), zero.copy(), zero.copy(), 0., 0.)
        e0, q0 = grid.energy_charge(state[:6])
        evolved = step(grid, state, .001)
        e1, q1 = grid.energy_charge(evolved[:6])
        self.assertTrue(np.array_equal(evolved[4], zero))
        self.assertTrue(np.array_equal(evolved[5], zero))
        self.assertGreater(evolved[6], 0)
        self.assertGreater(evolved[7], 0)
        self.assertLess(abs(e1 + evolved[6] - e0), 1e-6)
        self.assertLess(abs(q1 + evolved[7] - q0), 1e-6)

    def test_tick_interpolation_and_missing_intervals(self):
        t = np.arange(0, 20, .1)
        ticks = positive_crossings(t, np.cos(t))
        self.assertEqual(len(ticks), 3)
        self.assertLess(np.max(abs(np.diff(ticks) - 2*np.pi)), .002)
        self.assertEqual(len(positive_crossings(t[:5], np.ones(5))), 0)

    def test_recipe_is_locked_and_cannot_be_accepted_by_short_checks(self):
        plugin = TwoObjectQuietExperiment()
        config = json.loads((ROOT / 'fixtures/research/gross-test-08-quiet.json').read_text())
        plugin.validate(config)
        statuses = ['pass' if key not in ('joint-preparation', 'long-clocks')
                    else 'unresolved' for key in CRITERIA]
        rows = [{'id': key, 'status': status} for key, status in zip(CRITERIA, statuses)]
        self.assertEqual(plugin.classify({'checks': rows}, config), 'unresolved')
        altered = json.loads(json.dumps(config))
        altered['parameters']['scenarios'].pop()
        with self.assertRaises(ContractError):
            plugin.validate(altered)

    def test_handoff_archive_preserves_root_and_rejects_overwrite(self):
        script = ROOT / 'scripts/run-test8-local.py'
        spec = importlib.util.spec_from_file_location('test8_local_handoff', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / 'evidence'
            evidence.mkdir()
            (evidence / 'status.json').write_text('{"technical_status":"completed"}\n')
            output = root / 'evidence.zip'
            identity = module.pack(evidence, output)
            self.assertEqual(identity['sha256'], module.sha(output))
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.namelist(), ['evidence/status.json'])
            with self.assertRaises(ValueError):
                module.pack(evidence, output)


if __name__ == '__main__':
    unittest.main()
