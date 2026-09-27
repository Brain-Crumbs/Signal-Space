"""Registered linear boundary-memory prerequisite, with new local event rule."""
from signal_space.experiments.reception import ReceptionExperiment
from signal_space.experiments.prereception import ROOT
from signal_space.runtime.io import read_json


class BoundaryMemoryExperiment(ReceptionExperiment):
    experiment_id='gross.boundary-memory.v1'
    model_id='signal-space.ss-ocf-1.flat-neutral-clock.v1'
    version='1.0.0'
    def describe(self):
        d=super().describe();d.update(experiment_id=self.experiment_id,name='Test 7 causal exterior memory and local events',
            claims='Linear boundary transfer and prospective event prerequisite only',
            equation_sources=[{'label':'Causal boundary protocol','path':'docs/research/gross-test-07-boundary.md','catalog_id':'gross-test-07-boundary'}]);return d
    def schema(self):return read_json(ROOT/'contracts/research/boundary-memory.schema.json')
    def estimate(self,config):return {'cpu_seconds':2400,'wall_seconds':2700,'memory_mb':700,'disk_mb':100,'wall_time_class':'long'}
    def known_gaps(self,config):return ['No nonlinear receiver or phase forecast; cannot alone accept Test 7.',
        'Complete synthetic two-site record through t=60 is more information than the prior cutoff=16 record.',
        'First complete local threshold excursion is a new prospective marker protocol; last-crossing retained as diagnostic.',
        'Same discrete source and predictor calibration; no physical noise model, angular stability, recoil, or gravity.']
    def run(self,request_path):
        from signal_space.numerics.boundary_memory import execute
        return execute(request_path)
    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.boundary_memory import analyze
        return analyze(run_path,analysis_path,config)
    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.boundary_memory import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
