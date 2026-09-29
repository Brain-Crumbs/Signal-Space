"""Bounded linear reconstruction prerequisite for Test 7."""
from signal_space.experiments.reception import ReceptionExperiment
from signal_space.experiments.prereception import ROOT
from signal_space.runtime.io import read_json


class ReconstructionExperiment(ReceptionExperiment):
    experiment_id='gross.reconstruction.v1'
    model_id='signal-space.ss-ocf-1.flat-neutral-clock.v1'
    version='1.0.0'

    def describe(self):
        d=super().describe()
        d.update(experiment_id=self.experiment_id,name='Test 7 bounded reconstruction and event timing',
            claims='Linear inverse observability and causal surface-capture diagnostic only',
            equation_sources=[{'label':'Reconstruction protocol','path':'docs/research/gross-test-07-reconstruction.md','catalog_id':'gross-test-07-reconstruction'}])
        return d

    def schema(self):return read_json(ROOT/'contracts/research/reconstruction.schema.json')
    def estimate(self,config):return {'cpu_seconds':3600,'wall_seconds':4000,'memory_mb':1600,'disk_mb':250,'wall_time_class':'long'}
    def known_gaps(self,config):return [
        'No nonlinear receiver or new clock phase forecast; this cannot promote Test 7 or unblock Test 8.',
        'Singular sensitivity bound assumes declared surface tolerance and initial-data norm radius; it is a linear root estimate.',
        'Causal capture adds a neighboring surface site, stops acquisition at t=16, and omits residual exterior state.',
        'Acquisition and prediction share the registered discrete operator; no independent measurement-noise or discretization model.',
        'Three linear shapes, fixed support and incoming rule; radial flat sector only.']
    def run(self,request_path):
        from signal_space.numerics.reconstruction import execute
        return execute(request_path)
    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.reconstruction import analyze
        return analyze(run_path,analysis_path,config)
    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.reconstruction import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
