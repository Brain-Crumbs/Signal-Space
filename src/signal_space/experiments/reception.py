"""Registered Test 7, preserving the active-neutral SS OCF 1 action."""
from signal_space.experiments.prereception import PrereceptionExperiment, ROOT
from signal_space.runtime.io import read_json

class ReceptionExperiment(PrereceptionExperiment):
    experiment_id='gross.reception.v1'
    model_id='signal-space.ss-ocf-1.flat-neutral-clock.v1'
    version='1.0.0'
    def __init__(self):self.kind='reception'
    def describe(self):
        d=super().describe();d.update(name='Test 7: surface-only predicted reception',
            claims='Bounded radial local reception; no autonomous spacetime or recoil claim',
            equation_sources=[{'label':'Test 7 protocol','path':'docs/research/gross-test-07.md','catalog_id':'gross-test-07'}])
        return d
    def schema(self):return read_json(ROOT/'contracts/research/reception.schema.json')
    def acceptance_criteria(self,config):
        return [{'id':k,'description':v,'evidence':None} for k,v in config['analysis'].items()]
    def known_gaps(self,config):
        return ['Flat spherical receiver; opposite radial directions arise by central reflection.',
                'No two-object recoil, observer transformation, or autonomous Candidate A clock.',
                'Quiet comparison at pulse marker events is a counterfactual local diagnostic, not quiet-pulse detection.',
                'The additional mesh interpolates the frozen fine calibration; no new branch fit.',
                'Surface acquisition is a first-order neutral calculation, not an experimental measurement.']
    def estimate(self,config):
        return {'cpu_seconds':1800,'wall_seconds':2400,'memory_mb':700,'disk_mb':150,'wall_time_class':'medium'}
    def run(self,request_path):
        from signal_space.numerics.reception import execute
        return execute(request_path)
    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.reception import analyze
        return analyze(run_path,analysis_path,config)
    def classify(self,checks,config):
        statuses={c['id']:c['status'] for c in checks['checks']}
        if set(statuses)!=set(config['analysis']):return 'unresolved'
        if 'fail' in statuses.values():return 'fail'
        return 'pass' if set(statuses.values())=={'pass'} else 'unresolved'
    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.reception import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
