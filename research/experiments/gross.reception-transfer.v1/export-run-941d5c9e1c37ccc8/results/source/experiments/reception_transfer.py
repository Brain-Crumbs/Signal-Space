"""Registered, bounded Test 7 discrete-transfer discriminator."""
from signal_space.experiments.reception import ReceptionExperiment
from signal_space.experiments.prereception import ROOT
from signal_space.runtime.io import read_json


class ReceptionTransferExperiment(ReceptionExperiment):
    experiment_id='gross.reception-transfer.v1'
    model_id='signal-space.ss-ocf-1.flat-neutral-clock.v1'
    version='1.0.0'
    def describe(self):
        d=super().describe();d.update(experiment_id=self.experiment_id,
            name='Test 7 discrete surface transfer and fourth-order discrimination',
            claims='Two spectral preparations and resolved numerical budget; separate acceptance review required',
            equation_sources=[{'label':'Discrete transfer protocol','path':'docs/research/gross-test-07-transfer.md','catalog_id':'gross-test-07-transfer'}])
        return d
    def schema(self):return read_json(ROOT/'contracts/research/reception-transfer.schema.json')
    def estimate(self,config):return {'cpu_seconds':6300,'wall_seconds':7000,'memory_mb':1400,'disk_mb':250,'wall_time_class':'long'}
    def known_gaps(self,config):return ['Linear synthetic surface acquisition with exact known support and incoming derivative rule.',
        'SVD estimates initial data, not a response coefficient; cutoff sensitivity is explicitly budgeted.',
        'Independent profile refinement changes the discrete preparation and does not certify clock longevity.',
        'Flat spherical shells; no two-object recoil, invariance, gravity, angular stability or emergent spacetime.',
        'Original Test 7 remains failed and Test 8 requires a separate acceptance review.']
    def run(self,request_path):
        from signal_space.numerics.reception_transfer import execute
        return execute(request_path)
    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.reception_transfer import analyze
        return analyze(run_path,analysis_path,config)
    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.reception_transfer import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
