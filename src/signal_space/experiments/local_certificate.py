"""C1-4 locked pilot registration; confirmation remains a separately gated stage."""
from copy import deepcopy
from pathlib import Path
from signal_space.contracts.schema import check
from signal_space.contracts.validation import ContractError
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json,write_json,sha256_file

ROOT=Path(__file__).resolve().parents[3]
IDS={'coverage':'Both fixed seeds, both precisions and every declared endpoint/record retained.',
     'saved-proofs':'Independent saved-proof checker verifies every full-direction obligation.',
     'one-cycle-budgets':'Both seeds meet every allocation at every one-cycle endpoint.',
     'controls':'All preregistered analytic, diagnostic, negative and serialization controls pass.',
     'precision':'96-bit and 128-bit bounds independently qualify; width need not be monotone.'}


class LocalCertificateExperiment(ExperimentPlugin):
    experiment_id='gross.local-record-certificate.v1'
    model_id='signal-space.ss-ops-1.v1'
    version='1.0.0'
    def describe(self):
        return dict(experiment_id=self.experiment_id,model_id=self.model_id,version=self.version,
                    name='C1 full-direction local-record certificate pilot',
                    capabilities=['analysis','report','validated-endpoint-certificate'],
                    unavailable_capabilities=['resume','checkpoint','32-cycle confirmation without a qualified launch gate','physical detector','within-gate or all-time certificate'])
    def schema(self):
        s=read_json(ROOT/'contracts/research/local-certificate.schema.json')
        s['default']=read_json(ROOT/'fixtures/research/gross-certificate-pilot.json');return s
    def validate(self,config):
        check(config,self.schema())
        from signal_space.numerics.record_tubes import sources
        from signal_space.numerics.validated_linked_memory import require_runtime
        require_runtime()
        if config['parameters']['source_sha256']!=sources():raise ContractError('unqualified enclosure source bytes')
        for name,digest in config['parameters']['scientific_source_sha256'].items():
            if sha256_file(ROOT/name)!=digest:raise ContractError('unlocked scientific source: '+name)
        return deepcopy(config)
    def acceptance_criteria(self,config):
        return [dict(id=k,description=v,evidence=None) for k,v in IDS.items()]
    def known_gaps(self,config):
        return ['One-cycle pilot only; 32-cycle confirmation is not evaluated.',
                'Fixed supplied incidence and mathematical records, not physical detectors or proper time.',
                'Finite-gate precision/analytic controls replace inapplicable spatial boundary and mesh refinements.',
                'Shared dyadic/local-gate arithmetic remains a declared trusted base.',
                'Single-use campaign reservations do not replenish after failed attempts.']
    def estimate(self,config):
        return dict(cpu_seconds=35,wall_seconds=40,memory_mb=512,disk_mb=6,wall_time_class='short',
                    basis='Pre-pilot conservative admission: four two-gate proof/check variants plus all fixed local controls; independent saved-analysis reserves another15s. Not a measured confirmation runtime.')
    def prepare(self,config,run_path,attempt_path,resume):
        if resume:raise ValueError('certificate pilot does not support resume')
        from signal_space.runtime.certificate_budget import reserve
        from signal_space.runtime.package import code_identity
        if code_identity()['tree_state']!='clean':raise ValueError('commit source before scientific pilot')
        self.validate(config)
        # Enforce scientific plan before this one-shot stage is reserved.
        from importlib.util import spec_from_file_location,module_from_spec
        spec=spec_from_file_location('certificate_plan_contract',ROOT/'.agents/scripts/experiment_contract.py')
        module=module_from_spec(spec);spec.loader.exec_module(module)
        plan=read_json(ROOT/'docs/research/plans/gross-certificate-pilot.json')
        module.validate_plan(plan);path=module.verify_runtime_config(plan,ROOT)
        if read_json(path)!=config:raise ValueError('pilot differs from locked configuration')
        info=dict(plan_sha256=plan['locked_sha256'],config_file_sha256=sha256_file(path),
                  source_sha256=config['parameters']['source_sha256'],reservation=reserve(run_path,'pilot-worker'))
        write_json(attempt_path/'preparation.json',info);return info
    def run(self,request_path):
        from signal_space.numerics.local_certificate import execute
        return execute(request_path)
    def analyze(self,run_path,analysis_path,config):
        from signal_space.runtime.certificate_budget import analyze_saved
        return analyze_saved(run_path,analysis_path,config)
    def classify(self,checks,config):
        states={x['id']:x['status'] for x in checks['checks']}
        if set(states)!=set(IDS):return 'unresolved'
        # No physical counterexample is sought here. Invalid/excessive bounds
        # do not falsify robustness and never become a fail verdict.
        return 'pass' if set(states.values())=={'pass'} else 'unresolved'
    def report(self,run_path,report_path,manifest,analysis,render_provenance):
        from signal_space.reporting.local_certificate import render_report
        return render_report(run_path,report_path,manifest,analysis,render_provenance)
