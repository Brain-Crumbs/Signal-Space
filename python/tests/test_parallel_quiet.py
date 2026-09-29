"""Serial/parallel/restarted quiet controls must preserve physical arrays exactly."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from signal_space.numerics import two_object_quiet as quiet
from signal_space.runtime import quiet_cases
from signal_space.runtime.execution import cpu_capacity
from signal_space.runtime.io import read_json, write_json, sha256_file


class ParallelQuietTests(unittest.TestCase):
    def request(self, root):
        source = root/'profile.npz'
        r = np.linspace(0, 8, 81)
        np.savez(source, r=r, u=r[1:-1]*.1*np.exp(-r[1:-1]**2), mode=r[1:-1]*np.exp(-r[1:-1]**2))
        case = dict(label='first', pair=False, h=.5, radius=3, half_length=4,
                    absorber_width=1, absorber_strength=.12, dt=.02, periods=.15, sample_stride=2)
        return {'config': {'parameters': {'profile': {'path': str(source), 'sha256': sha256_file(source)},
                  'separation': 2., 'scenarios': [case, dict(case, label='second'), dict(case, label='third')],
                  'execution': {'backend': 'numpy', 'neutral_mode': 'full', 'checkpoint_stride': 20}},
                  'resources': {'max_memory_mb': 2048, 'max_cpu_seconds': 120, 'max_wall_seconds': 120, 'max_output_mb': 128}},
                'config_hash': 'test-config', 'code_identity_hash': 'test-code', 'seed_ledger': {'unused': 123},
                'attempt_id': 'attempt-0001', 'parent_attempt_id': None, 'resume_checkpoint': None}

    def execute(self, root, request):
        child = root/'attempts'/request['attempt_id']
        child.mkdir(parents=True)
        request['attempt_path'] = str(child)
        write_json(child/'request.json', request)
        return quiet.execute(child/'request.json'), child

    def compare(self, a, b):
        self.assertEqual(read_json(a/'raw/scenarios.json'), read_json(b/'raw/scenarios.json'))
        for label in ('first', 'second', 'third'):
            self.assertEqual(read_json(a/'raw'/f'{label}-traces.json'), read_json(b/'raw'/f'{label}-traces.json'))
            with np.load(a/'raw'/f'{label}-final.npz') as x, np.load(b/'raw'/f'{label}-final.npz') as y:
                for key in x.files: np.testing.assert_array_equal(x[key], y[key])

    @unittest.skipIf(cpu_capacity() < 2, 'requires two CPU slots')
    def test_parallel_and_interrupted_resume_are_bitwise_serial(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            request = self.request(root)
            code, serial = self.execute(root/'serial', deepcopy(request))
            self.assertEqual(code, 0)
            request['execution_policy'] = {'threads': 1, 'case_jobs': 2}
            code, parallel = self.execute(root/'parallel', deepcopy(request))
            self.assertEqual(code, 0)
            self.compare(serial, parallel)
            split = deepcopy(request)
            original = quiet_cases.write_json
            interrupted = False
            def write(path, value, **kwargs):
                nonlocal interrupted
                original(path, value, **kwargs)
                if value.get('kind') == quiet_cases.KIND and value['solver_state']['step'] >= 20 and not interrupted:
                    interrupted = True
                    (Path(split['attempt_path'])/'cancel.request').touch()
            with patch.object(quiet_cases, 'write_json', write):
                code, first = self.execute(root/'split', split)
            self.assertTrue(interrupted)
            self.assertEqual(code, 130)
            frozen = {str(p): sha256_file(p) for p in first.rglob('*') if p.is_file()}
            saved = read_json(sorted((first/'checkpoints').glob('*.json'))[-1])
            request.update(attempt_id='attempt-0002', parent_attempt_id='attempt-0001', resume_checkpoint=saved)
            code, resumed = self.execute(root/'split', request)
            self.assertEqual(code, 0)
            self.compare(serial, resumed)
            self.assertEqual(frozen, {str(p): sha256_file(p) for p in first.rglob('*') if p.is_file()})
            checkpoint = next(x['checkpoint'] for x in saved['cases'] if x['checkpoint'])
            (root/'split'/checkpoint['path']).write_bytes(b'corrupt')
            request['attempt_id'] = 'attempt-0003'
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                self.execute(root/'split', request)

    def test_memory_admission_precedes_case_launch(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); request = self.request(root)
            request['execution_policy'] = {'threads': 1, 'case_jobs': 2}
            request['config']['resources']['max_memory_mb'] = 300
            with self.assertRaisesRegex(ValueError, 'cannot fit'):
                self.execute(root/'rejected', request)
            self.assertFalse(list((root/'rejected').rglob('worker.log')))


if __name__ == '__main__': unittest.main()
