"""Registered Test 4: a complete, explicitly chosen reciprocal routing circuit."""
from copy import deepcopy
from pathlib import Path
from signal_space.contracts.e01 import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, write_json
ROOT=Path(__file__).resolve().parents[3]
CRITERIA={
'coverage':'Three backgrounds, 20 physical real dimensions, six local gates, both differential steps, all 104 signed low-q points, three full-zone paths and two impulse boxes are finite and complete.',
'periodicity':'Wave and projector period-one residual below 1e-10; raw memory spinor phases need not recur.',
'conservation':'Local total wave norm, memory norm, Hamiltonian and matrix charge residuals below 1e-10 on 24 off-background gates.',
'linearization':'Fine/coarse full map and independent DOP853 local Jacobian differ by less than 2e-6.',
'vacuum-reference':'Vacuum map agrees with independent frozen two-port Fourier construction and memory identity to 2e-6.',
'phase-quotient':'Memory spinor phase leaves wave outputs and projectors invariant below 1e-10; normalized orientation change modifies its overlap by more than 1e-6.',
'causal-domain':'Localized tangent impulse stays inside Chebyshev radius t after t cycles (outside amplitude <1e-10); common centered region agrees between boxes to 1e-10; one-cycle FFT agrees to 2e-6.',
'backreaction':'Counterport full/frozen map difference exceeds 1e-3; vacuum and equal-port differences below 2e-6.',
'vacuum-common-cone':'Strong all-sector common nondegenerate cone: fail if physical memory identity persists across every nonzero q with residual <2e-6, while wave map differs from identity by >1e-3.',
'counter-stability':'Fail for a sampled physical multiplier with log modulus >max(1e-5,5 times matched step-refinement eigenvalue error); otherwise unresolved because finite paths and unit moduli do not exclude Jordan growth or unsampled instability.'}

class FloquetExperiment(ExperimentPlugin):
    experiment_id='gross.full-spectrum.v1'; version='1.0.0'; model_id='signal-space.ss-ops-1.six-gate.v1'
    def describe(self):
        return {'experiment_id':self.experiment_id,'version':self.version,'model_id':self.model_id,'name':'Signal Space / GROSS Test 4: full reciprocal spectrum','claims':'Complete tangent spectrum of three declared backgrounds; no clock or emergent spacetime','equations':['Operator Program v0.2 sections 5, 15.4, 15.11; explicit six-gate circuit'], 'equation_sources':[{'label':'Full spectrum protocol','path':'docs/research/gross-test-04.md','catalog_id':'gross-test-04'}], 'capabilities':['analysis','report','floquet'],'unavailable_capabilities':['resume','clock','nonlinear stability proof']}
    def schema(self):
        s=read_json(ROOT/'contracts/research/floquet.schema.json'); s['default']=read_json(ROOT/'fixtures/research/gross-test-04.json'); return s
    def validate(self,config): check(config,self.schema()); return deepcopy(config)
    def acceptance_criteria(self,config): return [{'id':k,'description':v,'evidence':None} for k,v in CRITERIA.items()]
    def known_gaps(self,config):
        return ['Incidence and calibration scales assumed; this six-gate routing is not Test 3 reduced stencil.', 'Three exact homogeneous backgrounds only; no exhaustive nonzero-background search.', 'Finite spectral sampling cannot prove stability; tangent norm is not conserved physical energy.', 'No autonomous clock, invariant detector record, or validated material-response geometry.', 'No checkpoint/resume. Memory phase removed only because event law depends on its projector.']
    def estimate(self,config): return {'cpu_seconds':60,'wall_seconds':90,'memory_mb':256,'disk_mb':24,'wall_time_class':'short'}
    def prepare(self,config,run_path,attempt_path,resume):
        if resume: raise ValueError('Test 4 does not support resume')
        value={'model':self.model_id,'parameters':config['parameters'],'source':'docs/research/gross-test-04.md'}; write_json(attempt_path/'preparation.json',value); return value
    def run(self,request_path):
        from signal_space.numerics.floquet import execute
        return execute(request_path)
    def analyze(self,run_path,analysis_path,config):
        from signal_space.analysis.floquet import analyze
        return analyze(run_path,analysis_path,config)
    def classify(self,checks,config):
        statuses={c['id']:c['status'] for c in checks['checks']}
        technical=set(CRITERIA)-{'vacuum-common-cone','counter-stability'}
        if set(statuses)!=set(CRITERIA) or any(statuses[k]!='pass' for k in technical): return 'unresolved'
        if any(v=='fail' for v in statuses.values()): return 'fail'
        return 'unresolved'
    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.floquet import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
