"""A separately locked, two-cycle continuation of the C1 pilot."""
from copy import deepcopy
from pathlib import Path

from signal_space.contracts.schema import check
from signal_space.experiments.base import ExperimentPlugin
from signal_space.runtime.io import read_json, sha256_file, write_json

ROOT = Path(__file__).resolve().parents[3]
IDS = {
    'coverage': 'Both fixed seeds and precisions retain four ordered endpoints.',
    'saved-proofs': 'All saved proof obligations independently reconstruct.',
    'two-cycle-budgets': 'All records and separate allocations close through two cycles.',
    'controls': 'The unchanged analytic and independent diagnostic controls pass.',
    'precision': 'Both precisions independently qualify the whole preparation ball.',
}


class CertificateQualificationExperiment(ExperimentPlugin):
    experiment_id = 'gross.local-record-qualification.v1'
    model_id = 'signal-space.ss-ops-1.v1'
    version = '1.0.0'

    def describe(self):
        return dict(experiment_id=self.experiment_id, model_id=self.model_id, version=self.version,
                    name='C1 two-cycle bound/cost qualification',
                    capabilities=['analysis', 'report', 'validated-endpoint-certificate'],
                    unavailable_capabilities=['resume', 'checkpoint', '32-cycle confirmation',
                                              'physical detector', 'within-gate certificate'])

    def schema(self):
        schema = read_json(ROOT/'contracts/research/certificate-qualification.schema.json')
        schema['default'] = read_json(ROOT/'fixtures/research/gross-certificate-qualification.json')
        return schema

    def validate(self, config):
        check(config, self.schema())
        from signal_space.numerics.validated_linked_memory import require_runtime
        require_runtime()
        for group in ('source_sha256', 'scientific_source_sha256'):
            for path, digest in config['parameters'][group].items():
                if sha256_file(ROOT/path) != digest:
                    raise ValueError('qualification source changed: '+path)
        return deepcopy(config)

    def acceptance_criteria(self, config):
        return [dict(id=k, description=v, evidence=None) for k, v in IDS.items()]

    def known_gaps(self, config):
        return ['Four endpoints only; 32-cycle target not evaluated.',
                'Shared qualified local arithmetic and chart theorem remain trusted.',
                'No spatial mesh, boundary, proper time or hardware detector.',
                'Continuation consumes45s of the original remaining240s reservation.']

    def estimate(self, config):
        return dict(cpu_seconds=25, wall_seconds=28, memory_mb=512, disk_mb=7,
                    wall_time_class='short',
                    basis='Four four-endpoint variants and unchanged controls; hard30s worker and15s saved-check ceilings. Longer-prefix cost remains unqualified.')

    def prepare(self, config, run_path, attempt_path, resume):
        if resume:
            raise ValueError('qualification has no retry or resume')
        from signal_space.runtime.package import code_identity
        from signal_space.runtime.certificate_qualification import reserve_worker
        if code_identity()['tree_state'] != 'clean':
            raise ValueError('commit qualification sources before reservation')
        self.validate(config)
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location('c1_qualification_plan', ROOT/'.agents/scripts/experiment_contract.py')
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        plan = read_json(ROOT/'docs/research/plans/gross-certificate-qualification.json')
        module.validate_plan(plan)
        path = module.verify_runtime_config(plan, ROOT)
        if read_json(path) != config:
            raise ValueError('qualification differs from locked plan')
        info = dict(plan_sha256=plan['locked_sha256'], config_file_sha256=sha256_file(path),
                    reservation=reserve_worker(run_path, config))
        write_json(attempt_path/'preparation.json', info)
        return info

    def run(self, request_path):
        from signal_space.numerics.certificate_qualification import execute
        return execute(request_path)

    def analyze(self, run_path, analysis_path, config):
        from signal_space.runtime.certificate_qualification import analyze_saved
        return analyze_saved(run_path, analysis_path, config)

    def classify(self, checks, config):
        states = {x['id']: x['status'] for x in checks['checks']}
        return 'pass' if set(states) == set(IDS) and set(states.values()) == {'pass'} else 'unresolved'

    def report(self, run_path, report_path, manifest, analysis, render_provenance):
        from signal_space.reporting.certificate_qualification import render_report
        return render_report(run_path, report_path, manifest, analysis, render_provenance)
