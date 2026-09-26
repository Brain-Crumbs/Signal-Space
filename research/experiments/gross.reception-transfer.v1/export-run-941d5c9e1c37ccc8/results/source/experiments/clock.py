"""Registered Test 6 flat SS OCF 1 bound-clock calculation."""
from copy import deepcopy
from pathlib import Path
from signal_space.contracts.e01 import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT=Path(__file__).resolve().parents[3]
CRITERIA={
 'profiles':'Four trial branch samples attempted; accepted profile has a converged discrete residual, positive nodeless core and localized tail',
 'core-energetics':'Accepted profile has E/Q<1 and bounded core drift after charge sink',
 'bound-spectrum':'Independent chi eigenvalue lies >5 estimated errors from zero and the continuum threshold',
 'trapping-control':'nu=0 has no eigenvalue below vacuum threshold; unexcited chi=0 has no local ticks',
 'grid-domain':'Selected eigenvalue and profile converge on h/2 and 2R independently',
 'branch-screen':'Radial Hessian/charge-slope diagnostics and 100-period evolution have no resolved core instability',
 'local-record':'At least 100 signed cycles measurable locally with frequency near independent eigenvalue',
 'lifetime':'Clock-mode energy loss <1% over 100 periods at peak chi=0.001',
 'amplitude':'Half/base/double amplitudes have a controlled frequency shift below 1%',
 'charge-ledger':'Core charge drift after outer sink <1% over 100 periods'
}


class ClockExperiment(ExperimentPlugin):
    experiment_id='gross.bound-clock.v1'
    model_id='signal-space.ss-ocf-1.flat-clock.v1'
    version='1.0.0'

    def describe(self):
        return {'experiment_id':self.experiment_id,'model_id':self.model_id,'version':self.version,
                'name':'GROSS Test 6: localized bound clock',
                'claims':'Flat spherical core plus reciprocal weak clock, no gravitational evolution',
                'equations':['Operator Program v0.2 sections 7, 9, 15.6'],
                'equation_sources':[{'label':'Test 6 protocol','path':'docs/research/gross-test-06.md','catalog_id':'gross-test-06'}],
                'capabilities':['analysis','report','bound-clock'],
                'unavailable_capabilities':['resume','nonlinear Einstein evolution','nonradial evolution','detector reception']}

    def schema(self):
        schema=read_json(ROOT/'contracts/research/clock.schema.json')
        schema['default']=read_json(ROOT/'fixtures/research/gross-test-06.json')
        return schema

    def validate(self,config):
        check(config,self.schema())
        return deepcopy(config)

    def acceptance_criteria(self,config):
        return [{'id':k,'description':v,'evidence':None} for k,v in CRITERIA.items()]

    def known_gaps(self,config):
        return ['Spherical flat decoupling sector only; gravitational and nonradial stability untested.',
                'Outer finite domain has a documented dissipative layer; infinite-domain lifetime is inferred only within convergence controls.',
                'No neutral emission/reception, recoil, autonomous geometry or operator-to-continuum derivation.',
                'Half/double amplitude and refined controls run for 20 periods; 100-period longevity is evaluated at nominal amplitude.']

    def estimate(self,config):
        return {'cpu_seconds':400,'wall_seconds':500,'memory_mb':500,'disk_mb':18,'wall_time_class':'medium'}

    def prepare(self,config,run_path,attempt_path,resume):
        if resume: raise ValueError('atomic Test 6 does not support resume')
        value={'model':self.model_id,'parameters':config['parameters'],'source':'docs/research/gross-test-06.md'}
        write_json(attempt_path/'preparation.json',value)
        return value

    def run(self,request_path):
        from signal_space.numerics.clock import execute
        return execute(request_path)

    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.clock import analyze
        return analyze(run_path,analysis_path,config)

    def classify(self,checks,config):
        statuses={row['id']:row['status'] for row in checks['checks']}
        if set(statuses)!=set(CRITERIA): return 'unresolved'
        if any(s=='fail' for s in statuses.values()): return 'fail'
        if any(s!='pass' for s in statuses.values()): return 'unresolved'
        return 'pass'

    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.clock import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
