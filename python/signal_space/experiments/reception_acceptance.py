"""Complete known-incident Test 7 acceptance suite, independently classified."""
from signal_space.experiments.reception import ReceptionExperiment
from signal_space.experiments.prereception import ROOT
from signal_space.runtime.io import read_json


class ReceptionAcceptanceExperiment(ReceptionExperiment):
    experiment_id='gross.reception-acceptance.v1'
    model_id='signal-space.ss-ocf-1.flat-neutral-clock.v1'
    version='1.0.0'
    def describe(self):
        d=super().describe();d.update(experiment_id=self.experiment_id,name='Test 7: known-incident full acceptance',
            claims='Program 15.7 local cycle prediction and all controls in the calibrated radial sector',
            equation_sources=[{'label':'Known-incident acceptance protocol','path':'docs/research/gross-test-07-acceptance.md','catalog_id':'gross-test-07-acceptance'}]);return d
    def schema(self):return read_json(ROOT/'contracts/research/reception-acceptance.schema.json')
    def estimate(self,config):return {'cpu_seconds':3500,'wall_seconds':4200,'memory_mb':1000,'disk_mb':140,'wall_time_class':'long'}
    def known_gaps(self,config):return ['Known incident preparation; not a surface-only inverse or autonomous detector.',
        'Fixed local proper-time markers and matched quiet reference in flat spherical geometry.',
        'Refinement interpolates the frozen accepted calibration; no refit or nonspherical stability claim.',
        'A pass is limited to Program 15.7 in this sector; Test 8 survival and recoil remain untested.']
    def run(self,request_path):
        from signal_space.numerics.reception_acceptance import execute
        return execute(request_path)
    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.reception_acceptance import analyze
        return analyze(run_path,analysis_path,config)
    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.reception_acceptance import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
