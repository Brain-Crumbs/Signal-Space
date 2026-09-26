"""Registered bounded action/characteristic audit for SS OCF 1."""
from copy import deepcopy
from pathlib import Path
from signal_space.contracts.e01 import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]
CRITERIA = {
    'coverage': '200 smooth local samples, 20 directions, all six matter fields, all controls complete',
    'hessian': 'Action derivative Hessian versus written principal equations <1e-10 normalized',
    'equations': 'Euler-Lagrange jet coefficients, including nonzero a and core gradients and chi, agree with written equations <1e-10',
    'characteristics': 'All six characteristic roots agree with the coframe null cone within 1e-10 normalized',
    'positive-kinetic': 'Valid Z and timelike kinetic eigenvalues strictly positive; artificial Z<0 detected',
    'orientation-control': 'Separate quartic orientation model exhibits additional cone >1e-3 from metric cone',
    'gravity-symbol': 'Harmonic-gauge linearized TT symbol, gauge and flat linearized Hamiltonian/momentum constraints <1e-10',
}


class ContinuumExperiment(ExperimentPlugin):
    experiment_id = 'gross.continuum-action.v1'
    model_id = 'signal-space.ss-ocf-1.action-audit.v1'
    version = '1.0.0'

    def describe(self):
        return {'experiment_id':self.experiment_id,'model_id':self.model_id,'version':self.version,
                'name':'GROSS Test 5: continuum action and characteristics',
                'claims':'Frozen matter principal audit and flat linearized gravity symbol, not nonlinear evolution',
                'equations':['Operator Program v0.2 sections 7-8,12.3,15.5'],
                'equation_sources':[{'label':'Test 5 protocol','path':'docs/research/gross-test-05.md','catalog_id':'gross-test-05'}],
                'capabilities':['analysis','report','seeded-coframe-audit'],
                'unavailable_capabilities':['resume','nonlinear Einstein evolution','bound clock','emergent metric']}

    def schema(self):
        schema=read_json(ROOT/'contracts/research/continuum.schema.json')
        schema['default']=read_json(ROOT/'fixtures/research/gross-test-05.json')
        return schema

    def validate(self, config):
        check(config,self.schema())
        return deepcopy(config)

    def acceptance_criteria(self,config):
        return [{'id':k,'description':v,'evidence':None} for k,v in CRITERIA.items()]

    def known_gaps(self,config):
        return ['Frozen local jets, not solutions to nonlinear matter/Einstein equations.',
                'Harmonic-gauge gravitational symbol and linearized flat TT constraints only; nonlinear Einstein constraints and propagation not evaluated.',
                'No spatial discretization, boundaries, conservation evolution or bound clock.',
                'The flat internal connection is set to zero locally; general bundle holonomy is not tested.',
                'Quartic orientation term is a separate versioned failure control, not SS OCF 1.']

    def estimate(self,config):
        return {'cpu_seconds':20,'wall_seconds':35,'memory_mb':256,'disk_mb':8,'wall_time_class':'short'}

    def prepare(self,config,run_path,attempt_path,resume):
        if resume: raise ValueError('atomic Test 5 does not support resume')
        value={'model':self.model_id,'parameters':config['parameters'],'source':'docs/research/gross-test-05.md'}
        write_json(attempt_path/'preparation.json',value)
        return value

    def run(self,request_path):
        from signal_space.numerics.continuum import execute
        return execute(request_path)

    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.continuum import analyze
        return analyze(run_path,analysis_path,config)

    def classify(self,checks,config):
        statuses={r['id']:r['status'] for r in checks['checks']}
        if set(statuses)!=set(CRITERIA): return 'unresolved'
        return 'pass' if all(v=='pass' for v in statuses.values()) else 'fail'

    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.continuum import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
