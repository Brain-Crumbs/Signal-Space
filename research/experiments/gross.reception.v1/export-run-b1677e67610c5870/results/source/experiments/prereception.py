"""Two bounded prerequisite registrations; SS OCF 1 action is unchanged."""
from copy import deepcopy
from pathlib import Path
from signal_space.contracts.e01 import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {
    'longevity': ['frozen-inputs', 'local-record', 'lifetime', 'convergence', 'charge-ledger'],
    'response': ['frozen-inputs', 'prediction-first', 'sign-even', 'amplitude-square',
                 'response-match', 'counter-match', 'common-markers', 'numerical-controls', 'conservation']
}

class PrereceptionExperiment(ExperimentPlugin):
    version = '1.0.0'
    def __init__(self, kind):
        self.kind = kind
        self.experiment_id = f'gross.clock-{kind}.v1'
        self.model_id = ('signal-space.ss-ocf-1.flat-clock.v1' if kind == 'longevity'
                         else 'signal-space.ss-ocf-1.flat-neutral-clock.v1')
    def describe(self):
        return {'experiment_id': self.experiment_id, 'model_id': self.model_id,
                'version': self.version, 'name': f'Test 6 prerequisite: {self.kind}',
                'claims': 'Bounded radial flat prerequisite, not full Test 7',
                'equations': ['Operator Program v0.2 sections 7-9'],
                'equation_sources': [{'label': 'Prereception protocol', 'path': 'docs/research/gross-test-06-prerequisites.md', 'catalog_id': 'gross-test-06-prerequisites'}],
                'capabilities': ['analysis', 'report'], 'unavailable_capabilities': ['resume', 'nonspherical beams', 'gravity', 'recoil']}
    def schema(self):
        return read_json(ROOT / f'contracts/research/clock-{self.kind}.schema.json')
    def validate(self, config):
        check(config, self.schema())
        return deepcopy(config)
    def acceptance_criteria(self, config):
        return [{'id': k, 'description': config['analysis'][k], 'evidence': None} for k in CRITERIA[self.kind]]
    def known_gaps(self, config):
        return ['Flat spherical sector only; no recoil or observer transformations.',
                'Clock radiation is not isolated by the historical total-energy diagnostic.',
                'Concentric counterpropagating shells are not opposing planar beams.',
                'Marker pairing is ideal local field readout; physical trigger hardware not modeled.']
    def estimate(self, config):
        return {'cpu_seconds': 500, 'wall_seconds': 600, 'memory_mb': 600, 'disk_mb': 30, 'wall_time_class': 'medium'}
    def prepare(self, config, run_path, attempt_path, resume):
        if resume: raise ValueError('atomic prerequisite run does not resume')
        write_json(attempt_path / 'preparation.json', config['parameters'])
        return config['parameters']
    def run(self, request_path):
        from signal_space.numerics.prereception import execute
        return execute(request_path)
    def analyze(self, run_path, analysis_path, config):
        from signal_space.analysis.prereception import analyze
        return analyze(run_path, analysis_path, config)
    def classify(self, checks, config):
        statuses = {x['id']: x['status'] for x in checks['checks']}
        if set(statuses) != set(CRITERIA[self.kind]): return 'unresolved'
        if 'fail' in statuses.values(): return 'fail'
        return 'pass' if set(statuses.values()) == {'pass'} else 'unresolved'
    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.prereception import render_report
        return render_report(run_path, report_path, manifest, analysis, render_provenance)
