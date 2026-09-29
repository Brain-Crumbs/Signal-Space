"""Registered Test 7 follow-up; action and calibration retain Test 7 IDs."""
from signal_space.experiments.reception import ReceptionExperiment
from signal_space.experiments.prereception import ROOT
from signal_space.runtime.io import read_json


class ReceptionOrder4Experiment(ReceptionExperiment):
    experiment_id='gross.reception-order4.v1'
    model_id='signal-space.ss-ocf-1.flat-neutral-clock.v1'
    version='1.0.0'
    def describe(self):
        d=super().describe();d.update(experiment_id=self.experiment_id,
            name='Test 7 follow-up: fourth-order and held-out reception',
            claims='Fourth-order Taylor calculation and new held-out radial waveform; Test 7 status unchanged',
            equation_sources=[{'label':'Test 7 fourth-order protocol','path':'docs/research/gross-test-07-order4.md','catalog_id':'gross-test-07-order4'}])
        return d
    def schema(self):return read_json(ROOT/'contracts/research/reception-order4.schema.json')
    def estimate(self,config):return {'cpu_seconds':2300,'wall_seconds':2900,'memory_mb':850,'disk_mb':170,'wall_time_class':'medium'}
    def known_gaps(self,config):return ['Inspected earlier Test 7 histories are diagnostic only.',
        'Flat radial shell and retrospective markers; no two-object recoil or observer invariance.',
        'Optical inversion is leading WKB, not the exact discrete transfer.']
    def run(self,request_path):
        from signal_space.numerics.reception_order4 import execute
        return execute(request_path)
    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.reception_order4 import analyze
        return analyze(run_path,analysis_path,config)
    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.reception_order4 import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
