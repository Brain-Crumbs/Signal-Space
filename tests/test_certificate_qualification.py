"""Continuation admission, immutable budget and early-obstruction contracts."""
import copy
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from signal_space.experiments.registry import get_experiment
from signal_space.runtime.certificate_qualification import ALLOCATION, PILOT, RUN, reserve_worker
from signal_space.runtime.io import write_json, sha256_file


class QualificationContracts(unittest.TestCase):
    def test_closed_qualification_preserves_model_and_rejects_confirmation(self):
        plugin = get_experiment('gross.local-record-qualification.v1')
        config = plugin.schema()['default']
        self.assertEqual(plugin.validate(config), config)
        for field, value in (('cycles', 32), ('physical_directions', 15), ('seeds', ['active-plus']),
                             ('coupling', 'machine-pi/2'), ('stage', 'confirmation')):
            changed = copy.deepcopy(config)
            changed['parameters'][field] = value
            with self.assertRaises(ValueError):
                plugin.validate(changed)
        changed = copy.deepcopy(config)
        changed['resources']['max_wall_seconds'] = 31
        with self.assertRaises(ValueError):
            plugin.validate(changed)
        old = get_experiment('gross.local-record-certificate.v1')
        self.assertEqual(old.validate(old.schema()['default']), old.schema()['default'])

    def test_reallocation_requires_old_reservations_and_is_single_use(self):
        self.assertEqual(sum(ALLOCATION[k] for k in ('prior_pilot', 'qualification_worker',
                         'qualification_analysis', 'future_confirmation_worker', 'future_confirmation_analysis')), 300)
        self.assertEqual(sum(ALLOCATION[k] for k in ('prior_output_mb', 'qualification_output_mb', 'remaining_output_mb')), 128)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'runs'
            run = root/'gross.local-record-qualification.v1'/'run-new'
            pilot = root/PILOT/RUN
            pilot.mkdir(parents=True)
            (pilot/'checksums.sha256').write_text('fixture hash index\n')
            write_json(pilot/'manifest.json', dict(scientific_classification='pass', analyses=[{}]))
            config = dict(parameters=dict(pilot_checksums_sha256=sha256_file(pilot/'checksums.sha256')))
            markers = pilot.parent/'.c1-budget-v1'
            markers.mkdir()
            with patch('signal_space.runtime.verify.verify_package', return_value={'valid': True}):
                with self.assertRaises(FileNotFoundError):
                    reserve_worker(run, config)
                for stage, seconds in (('pilot-worker', 45), ('pilot-analysis', 15)):
                    write_json(markers/(stage+'.json'), dict(stage=stage, run_id=RUN,
                               reserved_cpu_seconds=seconds, reserved_wall_seconds=seconds, reserved_output_mb=8))
                write_json(markers/'confirmation-worker.json', {})
                with self.assertRaises(ValueError):
                    reserve_worker(run, config)
                (markers/'confirmation-worker.json').unlink()
                def reserve(_):
                    try:
                        return reserve_worker(run, config)
                    except (ValueError, FileExistsError):
                        return None
                with ThreadPoolExecutor(2) as pool:
                    results = list(pool.map(reserve, range(2)))
                self.assertEqual(sum(r is not None for r in results), 1)
                with self.assertRaises(ValueError):
                    reserve_worker(run.with_name('run-changed-source'), config)

    def test_missing_or_corrupt_pilot_fails_before_reservation(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)/'runs'/'qualification'/'run-new'
            with patch('signal_space.runtime.verify.verify_package', return_value={'valid': False}):
                with self.assertRaises(ValueError):
                    reserve_worker(run, {})
            self.assertFalse((Path(directory)/'runs'/PILOT/'.c1-budget-v1').exists())

    def test_zero_prefix_retains_obstruction_and_never_launches_confirmation(self):
        from signal_space.numerics import record_tubes
        from signal_space.numerics.certificate_qualification import execute
        from signal_space.analysis.certificate_qualification import analyze
        original = record_tubes.produce
        def obstructed(*args, **kwargs):
            with patch('signal_space.numerics.validated_linked_memory.evaluate',
                       return_value={'status': 'unresolved', 'reason': 'injected qualification enclosure obstruction'}):
                return original(*args, **kwargs)
        config = get_experiment('gross.local-record-qualification.v1').schema()['default']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            attempt = root/'attempts'/'attempt-1'
            attempt.mkdir(parents=True)
            write_json(root/'request.json', dict(attempt_path=str(attempt), config=config))
            env = {k: '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')}
            with patch.dict('os.environ', env), patch.object(record_tubes, 'produce', obstructed):
                self.assertEqual(execute(root/'request.json'), 0)
            output = root/'analysis'
            output.mkdir()
            result = analyze(root, output, config)
            self.assertEqual(result['summary']['common_endpoint_horizon'], 0)
            self.assertFalse(result['summary']['launch_allowed'])
            self.assertEqual(result['summary']['reservation']['remaining_confirmation'], 195)
            states = {r['id']: r['status'] for r in result['checks']['checks']}
            self.assertEqual(states['two-cycle-budgets'], 'unresolved')
            self.assertEqual(states['coverage'], 'unresolved')


if __name__ == '__main__':
    unittest.main()
