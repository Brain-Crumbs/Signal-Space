from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from decimal import Decimal, localcontext
from pathlib import Path
from unittest import mock

from signal_space.analysis.synthetic import analyze_series
from signal_space.experiments.synthetic import SyntheticExperiment
from signal_space.numerics.synthetic import recurrence
from signal_space.runtime.errors import CheckpointMismatch, IntegrityError, InvalidState
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.package import RunPackage
from signal_space.runtime.runner import ResearchRuntime, _monitor_process, _terminate_process
from test_runtime import fixture


class ReadinessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.runtime = ResearchRuntime()

    def interrupted(self):
        config = fixture()
        config['fixture_controls']['interrupt_at_step'] = 7
        config['parameters']['checkpoint_interval'] = 5
        return self.runtime.run(config, self.workspace)

    def test_cannot_resume_completed_run_from_old_interrupted_attempt(self):
        first = self.interrupted()
        self.runtime.resume(self.workspace, first['run_id'])
        with self.assertRaisesRegex(InvalidState, 'latest attempt'):
            self.runtime.resume(self.workspace, first['run_id'])
        self.assertEqual(len(self.runtime.status(self.workspace, first['run_id'])['attempts']), 2)

    def test_resume_rejects_changed_numerical_environment(self):
        first = self.interrupted()
        package = self.runtime._package(self.workspace, first['run_id'])
        execution = deepcopy(package.manifest['execution_identity'])
        execution['environment']['numeric_libraries']['numpy'] = 'different'
        with mock.patch('signal_space.runtime.runner.execution_identity', return_value=execution):
            with self.assertRaisesRegex(CheckpointMismatch, 'environment'):
                self.runtime.resume(self.workspace, first['run_id'])
        self.assertEqual(len(package.manifest['attempts']), 1)

    def test_preparation_failure_has_terminal_evidence(self):
        with mock.patch.object(SyntheticExperiment, 'prepare', side_effect=ValueError('invalid radial domain')):
            result = self.runtime.run(fixture(), self.workspace)
        self.assertEqual(result['state'], 'failed')
        manifest = self.runtime.status(self.workspace, result['run_id'])
        self.assertEqual(manifest['attempts'][0]['failure']['code'], 'PREPARATION_FAILED')
        self.assertIn('invalid radial domain', manifest['attempts'][0]['failure']['message'])
        self.assertTrue(self.runtime.verify(self.workspace, result['run_id'])['valid'])

    def test_worker_launch_failure_has_terminal_evidence(self):
        created = self.runtime.create_run(fixture(), self.workspace)
        with mock.patch('signal_space.runtime.runner.subprocess.Popen', side_effect=OSError('launch failed')):
            result = self.runtime.execute(self.workspace, created['run_id'])
        self.assertEqual(result['state'], 'failed')
        manifest = self.runtime.status(self.workspace, result['run_id'])
        self.assertEqual(manifest['attempts'][0]['failure']['code'], 'WORKER_START_FAILED')
        self.assertTrue(self.runtime.verify(self.workspace, result['run_id'])['valid'])

    def test_cancellation_is_bounded_even_for_uncooperative_worker(self):
        process = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], start_new_session=True)
        try:
            (self.workspace / 'cancel.request').touch()
            reason, _ = _monitor_process(process, self.workspace, {'max_wall_seconds': 20, 'max_output_mb': 1})
            self.assertEqual(reason, 'cancel')
        finally:
            _terminate_process(process, cooperative_seconds=0)

    def test_nonseries_plugin_evidence_survives_analysis_and_report(self):
        # Test the extension seam without registering or running new physics.
        result = self.runtime.run(fixture(), self.workspace)
        package = self.runtime._package(self.workspace, result['run_id'])
        profile = package.path / 'attempts/attempt-0001/raw/profile.json'
        write_json(profile, {'r': [0, 1], 'f': [1, 0]})
        package.update(lambda manifest: manifest.update({
            'acceptance_criteria': [{'id': 'profile-check', 'description': 'test-only profile control', 'evidence': None}],
            'known_gaps': ['Test seam only.'],
        }))
        source = profile.relative_to(package.path).as_posix()

        def analyze(_plugin, run, path, config):
            checks = {'checks': [{'id': 'profile-check', 'status': 'unresolved', 'evidence': 'derived/profile.json'}]}
            write_json(path / 'derived/profile.json', read_json(profile))
            write_json(path / 'checks.json', checks)
            return {'raw_source': source, 'checks': checks, 'summary': {}}

        def report(_plugin, run, path, manifest, analysis, provenance):
            (path / 'report.md').write_text('# Profile control\nNo physical claim.\n')
            return {'required_inputs': [source, analysis['path'] + '/derived/profile.json', analysis['path'] + '/checks.json']}

        with mock.patch.object(SyntheticExperiment, 'analyze', analyze), mock.patch.object(SyntheticExperiment, 'classify', return_value='unresolved'), mock.patch.object(SyntheticExperiment, 'report', report):
            analysis = self.runtime.analyze(self.workspace, result['run_id'])
            rendered = self.runtime.report(self.workspace, result['run_id'])
        self.assertEqual(analysis['raw_source'], source)
        self.assertTrue(all('series.csv' not in path for path in rendered['required_inputs']))
        self.assertTrue(self.runtime.verify(self.workspace, result['run_id'])['valid'])

    def test_manifest_uses_plugin_acceptance_metadata(self):
        criteria = [{'id': 'custom-control', 'description': 'custom evidence', 'evidence': None}]
        with mock.patch.object(SyntheticExperiment, 'acceptance_criteria', return_value=criteria), mock.patch.object(SyntheticExperiment, 'known_gaps', return_value=['custom gap']):
            created = self.runtime.create_run(fixture(), self.workspace)
        manifest = self.runtime.status(self.workspace, created['run_id'])
        self.assertEqual(manifest['acceptance_criteria'], criteria)
        self.assertEqual(manifest['known_gaps'], ['custom gap'])

    def test_verify_rejects_resealed_false_config_or_analysis_identity(self):
        result = self.runtime.run(fixture(), self.workspace)
        self.runtime.analyze(self.workspace, result['run_id'])
        package = self.runtime._package(self.workspace, result['run_id'])
        original = deepcopy(package.manifest)
        package.update(lambda manifest: manifest.update({'config_hash': '0'*64}))
        with self.assertRaisesRegex(IntegrityError, 'run identity'):
            self.runtime.verify(self.workspace, result['run_id'])
        package.update(lambda manifest: manifest.update({'config_hash': original['config_hash']}))
        def falsify(manifest):
            analysis = manifest['analyses'][0]
            analysis['input_artifacts'][analysis['raw_source']] = '0'*64
        package.update(falsify)
        with self.assertRaisesRegex(IntegrityError, 'analysis input identity'):
            self.runtime.verify(self.workspace, result['run_id'])

    def test_raw_series_rejects_duplicate_missing_negative_and_nonfinite_samples(self):
        config = fixture()
        config['parameters']['steps'] = 2
        for rows in ([(0, 1), (0, 1), (2, 1)], [(0, 1), (2, 1)], [(-1, 1)], [(0, float('nan'))], []):
            with self.subTest(rows=rows):
                path = self.workspace / 'series.csv'
                with path.open('w') as stream:
                    writer = csv.writer(stream)
                    writer.writerow(['step', 'value'])
                    writer.writerows(rows)
                with self.assertRaises(ValueError):
                    analyze_series(path, self.workspace / 'analysis', config)

    def test_reference_is_stable_near_unit_gain(self):
        gain = 1 + 1e-10
        observed = recurrence(0.7, gain, 0.13, 100)
        with localcontext() as context:
            context.prec = 60
            value = Decimal.from_float(0.7)
            g, forcing = Decimal.from_float(gain), Decimal.from_float(0.13)
            for result in observed:
                self.assertAlmostEqual(result, float(value), places=12)
                value = g*value+forcing

    def test_resumed_output_does_not_inherit_old_classification(self):
        result = self.interrupted()
        self.runtime.analyze(self.workspace, result['run_id'])
        self.runtime.resume(self.workspace, result['run_id'])
        manifest = self.runtime.status(self.workspace, result['run_id'])
        self.assertEqual(manifest['scientific_classification'], 'not-evaluated')
        self.assertFalse(manifest['completeness']['analysis'])
        self.assertEqual(len(manifest['analyses']), 1)
        self.assertTrue(all(item['evidence'] is None for item in manifest['acceptance_criteria']))
        self.assertTrue(self.runtime.verify(self.workspace, result['run_id'])['valid'])

    def test_direct_analysis_import_does_not_load_circular_registry(self):
        result = subprocess.run([sys.executable, '-c', 'from signal_space.analysis.synthetic import analyze_series; from signal_space.experiments.base import ExperimentPlugin'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_package_updates_are_serialized_across_processes(self):
        created = self.runtime.create_run(fixture(), self.workspace)
        script = '''
import sys, time
from pathlib import Path
from signal_space.runtime.package import RunPackage
package = RunPackage(Path(sys.argv[1]))
def update(manifest):
    time.sleep(0.1)
    manifest['known_gaps'].append(sys.argv[2])
package.update(update)
'''
        processes = [subprocess.Popen([sys.executable, '-c', script, created['path'], name]) for name in ('process-a', 'process-b')]
        for process in processes:
            self.assertEqual(process.wait(timeout=10), 0)
        manifest = self.runtime.status(self.workspace, created['run_id'])
        self.assertIn('process-a', manifest['known_gaps'])
        self.assertIn('process-b', manifest['known_gaps'])
        self.assertTrue(self.runtime.verify(self.workspace, created['run_id'])['valid'])
