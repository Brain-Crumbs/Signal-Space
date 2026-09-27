"""Stage A / short Stage B pilot for Test 8; never claims Test 8 acceptance."""
from copy import deepcopy
from pathlib import Path

from signal_space.contracts.e01 import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {
    'frozen-source': 'Original accepted Test 6 profile bytes agree with the locked hash.',
    'closed-sector': 'The initially zero neutral field and momentum stay at floating-point zero.',
    'short-ledgers': 'Energy and charge drifts are below the prospective pilot bounds in every short run.',
    'spatial-calibration': '100-period isolated clocks and a genuinely prepared quiet pair pass independent mesh, time and domain controls.',
    'full-exchange': 'Issue #82 G0–G9, including both channels and the held-out comparison matrix.'
}


class TwoObjectCalibrationExperiment(ExperimentPlugin):
    experiment_id = 'gross.two-object-calibration.v1'
    model_id = 'signal-space.ss-ocf-1.flat-axisymmetric-neutral-clock.v1'
    version = '0.1.0'

    def describe(self):
        return {'experiment_id':self.experiment_id,'model_id':self.model_id,
                'version':self.version,'name':'GROSS Test 8 spatial feasibility pilot',
                'equations':['Operator Program v0.2 sections 7-10, 15.8'],
                'equation_sources':[{'label':'Test 8 issue','path':'docs/research/gross-test-08.md',
                                     'catalog_id':'gross-test-08'}],
                'capabilities':['axisymmetric','short-calibration','analysis','report'],
                'unavailable_capabilities':['accepted Test 8','relaxed joint pair','restart',
                  'absorbers','recoil ledger','held-out comparison matrix','Test 9 handoff']}

    def schema(self):
        schema = read_json(ROOT/'contracts/research/two-object-calibration.schema.json')
        schema['default'] = read_json(ROOT/'fixtures/research/gross-test-08-calibration.json')
        return schema

    def validate(self, config):
        check(config, self.schema())
        p = config['parameters']
        if len({s['label'] for s in p['scenarios']}) != len(p['scenarios']):
            raise ValueError('scenario labels must be unique')
        if not any(s['pair'] for s in p['scenarios']) or not any(not s['pair'] for s in p['scenarios']):
            raise ValueError('pilot requires isolated and pair preparations')
        for s in p['scenarios']:
            h = s['h']
            if abs(round(s['radius']/h)*h-s['radius'])>1e-9 or abs(round(2*s['half_length']/h)*h-2*s['half_length'])>1e-9:
                raise ValueError('domain must be divisible by spatial step')
            if s['pair'] and (s['half_length'] < p['separation']/2+20 or s['radius'] < 22):
                raise ValueError('pair domain cuts into calibrated core/clock containment')
            if s['dt'] > .25*h/(2**.5):
                raise ValueError('time step exceeds declared 2D CFL safety factor')
        return deepcopy(config)

    def acceptance_criteria(self, config):
        return [{'id':name,'description':description,'evidence':None}
                for name,description in CRITERIA.items()]

    def known_gaps(self, config):
        return ['Short embedding pilot only; no 100-period spatial clock longevity.',
                'Pair is a measured naive superposition; no joint relaxation.',
                'Reflecting box; no emission/recoil acceptance or 20-period survival.',
                'Fixed internal doublet direction, axisymmetric flat decoupling only.']

    def estimate(self, config):
        scenarios = config['parameters']['scenarios']
        units = sum(round(s['radius']/s['h'])*round(2*s['half_length']/s['h'])*round(s['duration']/s['dt'])
                    for s in scenarios)
        return {'cpu_seconds':max(30,int(units/100000)),
                'wall_seconds':max(45,int(units/100000)),
                'memory_mb':max(180,int(max(round(s['radius']/s['h'])*round(2*s['half_length']/s['h'])
                                          for s in scenarios)*.003)+100),
                'disk_mb':max(10,int(sum(round(s['radius']/s['h'])*round(2*s['half_length']/s['h'])
                                          for s in scenarios)*.0002)+5),
                'wall_time_class':'medium'}

    def prepare(self, config, run_path, attempt_path, resume):
        if resume:
            raise ValueError('short pilot cannot resume')
        result = {'model':self.model_id,'stage':'axisymmetric spatial calibration pilot',
                  'source':'docs/research/gross-test-08.md'}
        write_json(attempt_path/'preparation.json',result)
        return result

    def run(self, request_path):
        from signal_space.numerics.two_object import execute
        return execute(request_path)

    def analyze(self, run_path, analysis_path, config):
        from signal_space.analysis.two_object import analyze
        return analyze(run_path, analysis_path, config)

    def classify(self, checks, config):
        statuses = {row['id']:row['status'] for row in checks['checks']}
        if set(statuses) != set(CRITERIA):
            return 'unresolved'
        if any(s == 'fail' for s in statuses.values()):
            return 'fail'
        return 'pass' if all(s == 'pass' for s in statuses.values()) else 'unresolved'

    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.two_object import render_report
        return render_report(run_path, report_path, manifest, analysis, render_provenance)
