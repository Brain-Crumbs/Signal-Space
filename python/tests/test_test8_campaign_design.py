"""Planning controls only: never start a solver or registered run."""
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('test8_design', ROOT/'scripts/preflight-test8-acceptance.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Test8DesignTests(unittest.TestCase):
    def setUp(self):
        self.design = MODULE.read(MODULE.DESIGN)
        self.timing = MODULE.read(ROOT/self.design['benchmark'])

    def test_complete_design_still_exposes_resource_blocker(self):
        variants, cases = MODULE.validate(self.design, self.timing)
        estimate = MODULE.estimate(self.design, variants, cases)
        self.assertEqual(estimate['stages']['S4']['evolutions'], 99)
        self.assertGreater(estimate['total_serial_wall_hours_proxy'], 48)
        self.assertGreater(estimate['one_fine_case_full_snapshots_every_0_4_gib'], 4)
        self.assertFalse(self.design['manual_execution']['enabled'])

    def test_missing_gate_and_removed_object_control_rejected(self):
        for field in ('gates', 'preparations'):
            altered = copy.deepcopy(self.design)
            altered[field].pop()
            with self.assertRaises(ValueError):
                MODULE.validate(altered, self.timing)

    def test_confounding_domain_and_sponge_is_rejected(self):
        row = next(v for v in self.design['numerical_variants'] if v['id'] == 'domain')
        row['sponge_width'] = 6
        with self.assertRaisesRegex(ValueError, 'confounds'):
            MODULE.validate(self.design, self.timing)

    def test_shortened_survival_or_fabricated_runtime_lock_is_rejected(self):
        self.design['error_budget']['thresholds']['post_periods'] = 6
        with self.assertRaises(ValueError):
            MODULE.validate(self.design, self.timing)
        self.setUp()
        self.design['runtime_config'] = 'fixtures/nonexistent.json'
        with self.assertRaises(ValueError):
            MODULE.validate(self.design, self.timing)

    def test_corrupted_timing_rejected(self):
        self.timing['cases'][0]['wall_seconds'] *= .1
        with self.assertRaisesRegex(ValueError, 'timing arithmetic'):
            MODULE.validate(self.design, self.timing)

    def test_cli_refuses_launch_and_returns_nonready_status(self):
        command = [sys.executable, str(ROOT/'scripts/preflight-test8-acceptance.py')]
        result = subprocess.run([*command, '--require-executable'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        status = json.loads(result.stdout)
        self.assertTrue(status['design_valid'])
        self.assertFalse(status['execution_ready'])
        self.assertFalse(status['physics_executed'])
        checks = {row['id']: row for row in status['readiness_checks']}
        self.assertFalse(checks['exchange-registration']['ready'])
        self.assertTrue(checks['frozen-profile']['ready'])
        self.assertFalse(checks['locked-stage-plans']['ready'])
        self.assertFalse(checks['measured-resource-packet']['ready'])
        refused = subprocess.run([*command, '--execute'], capture_output=True, text=True)
        self.assertEqual(refused.returncode, 2)
        self.assertIn('unrecognized arguments', refused.stderr)

    def test_six_period_quiet_plugin_does_not_satisfy_exchange_registration(self):
        altered = copy.deepcopy(self.design)
        altered['proposed_experiment_id'] = 'gross.two-object-quiet-calibration.v1'
        checks = {row['id']: row for row in MODULE.readiness(altered)}
        self.assertFalse(checks['exchange-registration']['ready'])
        self.assertIn('missing capabilities', checks['exchange-registration']['reason'])


if __name__ == '__main__':
    unittest.main()
