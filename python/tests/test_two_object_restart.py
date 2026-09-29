"""Complete quiet-worker restart across sampling and local crossing events."""
import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from signal_space.numerics import two_object_quiet as quiet
from signal_space.runtime.io import read_json, sha256_file, write_json


class QuietRestartTests(unittest.TestCase):
    def request(self, root, backend='numpy'):
        source = root / 'profile.npz'
        r = np.linspace(0, 8, 81)
        np.savez(source, r=r, u=r[1:-1]*.1*np.exp(-r[1:-1]**2),
                 mode=r[1:-1]*np.exp(-r[1:-1]**2))
        scenario = dict(label='fixture', pair=False, h=.5, radius=3, half_length=4,
                        absorber_width=1, absorber_strength=.12, dt=.02,
                        periods=.5, sample_stride=2)
        return {'config': {'parameters': {'profile': {'path': str(source), 'sha256': sha256_file(source)},
                     'separation': 2., 'scenarios': [scenario, dict(scenario, label='second')],
                     'execution': {'backend': backend, 'neutral_mode': 'full', 'checkpoint_stride': 90}}},
                'config_hash': 'test-config', 'code_identity_hash': 'test-code',
                'seed_ledger': {'unused': 123}, 'attempt_id': 'attempt-0001',
                'parent_attempt_id': None, 'resume_checkpoint': None}

    def execute(self, root, request):
        attempt = root / 'attempts' / request['attempt_id']
        attempt.mkdir(parents=True)
        request['attempt_path'] = str(attempt)
        path = attempt / 'request.json'
        write_json(path, request)
        return quiet.execute(path), attempt

    def test_split_worker_preserves_crossing_records_fields_and_completed_cases(self):
        backends = ['numpy'] + (['numba'] if importlib.util.find_spec('numba') else [])
        for backend in backends:
            with self.subTest(backend=backend), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                request = self.request(root, backend)
                code, whole = self.execute(root / 'whole', copy.deepcopy(request))
                self.assertEqual(code, 0)
                split_request = copy.deepcopy(request)
                original = quiet.local_observables
                previous = None
                seen_crossing = False
                def observe(*args):
                    nonlocal previous, seen_crossing
                    result = original(*args)
                    q = result[0]['mode_q']
                    if previous is not None and previous*q < 0 and not seen_crossing:
                        seen_crossing = True
                        (Path(split_request['attempt_path']) / 'cancel.request').touch()
                    previous = q
                    return result
                with patch.object(quiet, 'local_observables', observe):
                    code, first = self.execute(root / 'split', split_request)
                self.assertTrue(seen_crossing)
                self.assertEqual(code, 130)
                frozen = {str(p): sha256_file(p) for p in first.rglob('*') if p.is_file()}
                saved = read_json(sorted((first / 'checkpoints').glob('*.json'))[-1])
                request.update(attempt_id='attempt-0002', parent_attempt_id='attempt-0001', resume_checkpoint=saved)
                code, resumed = self.execute(root / 'split', request)
                self.assertEqual(code, 0)
                for label in ('fixture', 'second'):
                    self.assertEqual(read_json(whole/'raw'/f'{label}-traces.json'),
                                     read_json(resumed/'raw'/f'{label}-traces.json'))
                    with np.load(whole/'raw'/f'{label}-final.npz') as a, np.load(resumed/'raw'/f'{label}-final.npz') as b:
                        for key in a.files:
                            np.testing.assert_array_equal(a[key], b[key])
                self.assertEqual(frozen, {str(p): sha256_file(p) for p in first.rglob('*') if p.is_file()})

    def test_resume_copies_completed_cases_and_rejects_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            request = self.request(root)
            original = quiet.append_event
            def event(path, kind, *args):
                original(path, kind, *args)
                if kind == 'scenario-completed':
                    (path.parent/'cancel.request').touch()
            with patch.object(quiet, 'append_event', event):
                code, first = self.execute(root, request)
            self.assertEqual(code, 130)
            saved = read_json(sorted((first/'checkpoints').glob('*.json'))[-1])
            self.assertEqual(len(saved['completed_outputs']), 2)
            bad = copy.deepcopy(request)
            bad.update(attempt_id='attempt-0002', parent_attempt_id='attempt-0001', resume_checkpoint=saved)
            code, resumed = self.execute(root, bad)
            self.assertEqual(code, 0)
            self.assertEqual(sha256_file(first/'raw/fixture-final.npz'), sha256_file(resumed/'raw/fixture-final.npz'))
            (first/'raw/fixture-final.npz').write_bytes(b'corrupt')
            bad['attempt_id'] = 'attempt-0003'
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                self.execute(root, bad)

    def test_execution_options_keep_physics_locked(self):
        from signal_space.experiments.two_object_quiet import TwoObjectQuietExperiment
        from signal_space.contracts.validation import ContractError
        plugin = TwoObjectQuietExperiment()
        config = plugin.schema()['default']
        config['parameters']['execution'] = {'backend': 'numba', 'neutral_mode': 'exact-zero', 'checkpoint_stride': 1000}
        plugin.validate(config)
        altered = copy.deepcopy(config)
        altered['parameters']['scenarios'][0]['dt'] *= 2
        with self.assertRaises(ContractError):
            plugin.validate(altered)
        config['parameters']['execution']['backend'] = 'numpy'
        with self.assertRaises(ValueError):
            plugin.validate(config)
        config['parameters']['execution']['backend'] = 'unknown'
        with self.assertRaises(ContractError):
            plugin.validate(config)
        config['parameters']['execution']['backend'] = 'numba'
        dense = plugin.estimate(config)['disk_mb']
        config['parameters']['execution']['checkpoint_stride'] = 5000
        sparse = plugin.estimate(config)['disk_mb']
        self.assertGreater(dense, sparse)
        self.assertGreater(dense, config['resources']['max_output_mb'])
        self.assertLess(sparse, config['resources']['max_output_mb'])

    def test_runtime_worker_cancel_resume_and_package_verification(self):
        from signal_space.experiments.two_object_quiet import TwoObjectQuietExperiment
        from signal_space.runtime.package import RunPackage
        from signal_space.runtime.runner import ResearchRuntime
        plugin = TwoObjectQuietExperiment()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            backend = 'numba' if importlib.util.find_spec('numba') else 'numpy'
            config = plugin.schema()['default']
            config['parameters'] = self.request(root, backend)['config']['parameters']
            runtime = ResearchRuntime()
            # Only the test's tiny manufactured preparation bypasses the
            # six-period recipe lock; use the real worker and package lifecycle.
            with patch.object(TwoObjectQuietExperiment, 'validate', lambda self, value: value):
                created = runtime.create_run(config, root/'work')
                package = RunPackage(Path(created['path']))
                result = runtime._attempt(package, plugin, config, None,
                    on_started=lambda _: runtime.cancel(root/'work', created['run_id']))
                self.assertEqual(result['state'], 'cancelled')
                self.assertTrue(result['resumable'])
                self.assertTrue(runtime.verify(root/'work', created['run_id'])['valid'])
                resumed = runtime.resume(root/'work', created['run_id'])
                self.assertEqual(resumed['state'], 'completed')
                self.assertTrue(runtime.verify(root/'work', created['run_id'])['valid'])
                manifest = package.manifest
                self.assertEqual(len(manifest['attempts']), 2)
                self.assertEqual(manifest['attempts'][1]['parent_attempt_id'], 'attempt-0001')


if __name__ == '__main__':
    unittest.main()
