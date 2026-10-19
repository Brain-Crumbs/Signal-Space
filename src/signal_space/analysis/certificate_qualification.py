"""Reconstruct saved four-endpoint proofs; do not rerun the trajectory."""
from fractions import Fraction as Q
from pathlib import Path

from signal_space.runtime.io import read_json, write_json, sha256_file


def analyze(run_path, output, config):
    from signal_space.numerics.record_certificate_check import check_file
    from signal_space.numerics.certificate_controls import evaluate_controls
    from signal_space.numerics.operators import write_rows
    from signal_space.numerics.record_certificate_math import matrix, opnorm
    from signal_space.runtime.certificate_qualification import ALLOCATION
    executions = sorted(run_path.glob('attempts/*/raw/execution.json'))
    if len(executions) != 1:
        raise ValueError('exactly one completed qualification worker required')
    raw = executions[0].parent
    execution = read_json(executions[0])
    p = config['parameters']
    if execution['parameters'] != p:
        raise ValueError('raw parameters differ from lock')
    expected = {(s, b) for s in p['seeds'] for b in p['precision_bits']}
    if len(execution['rows']) != 4 or {(r['seed'], r['bits']) for r in execution['rows']} != expected:
        raise ValueError('missing seed or precision')
    derived = output/'derived'
    derived.mkdir()
    summaries, terms, majorants, primary = [], [], [], []
    for row in execution['rows']:
        name = f"{row['seed']}-{row['bits']}.json"
        if row['file'] != name or sha256_file(raw/name) != row['sha256']:
            raise ValueError('saved proof changed')
        proof = read_json(raw/name)
        if (proof['config']['seed'], proof['config']['bits'], proof['config']['gates']) != (row['seed'], row['bits'], 4):
            raise ValueError('wrong seed, precision or prefix')
        result = check_file(raw/name)
        if not result['verified'] or result != row['check']:
            raise ValueError('saved proof does not independently reconstruct')
        summaries.append(dict(bits=row['bits'], **result))
        for step in proof['steps']:
            for l, t in enumerate(step['record_terms']):
                terms.append(dict(seed=row['seed'], bits=row['bits'], endpoint=step['index'], event=step['event'], record=l+1,
                                  **{k: float(Q(t[k])) for k in ('readout_center', 'K', 'linear', 'remainder', 'preparation', 'numerical', 'readout', 'omitted_law', 'total')}))
            majorants.append(dict(seed=row['seed'], bits=row['bits'], endpoint=step['index'],
                                  tangent_norm_upper=float(opnorm(matrix(step['tangent'], row['bits'], 18, 16), row['bits'])+Q(step['majorants']['beta'])),
                                  **{k: float(Q(v)) for k, v in step['majorants'].items()}))
        if row['bits'] == 96:
            primary.append(proof)
    primary.sort(key=lambda proof: p['seeds'].index(proof['config']['seed']))
    if sha256_file(raw/'local-controls.json') != execution['control_file_sha256']:
        raise ValueError('saved analytic controls changed')
    controls = evaluate_controls(primary, derived/'controls-replay', saved=raw)
    if controls != execution['controls']:
        raise ValueError('control replay changed')
    ok = all(r['status'] == 'pass' for r in controls) and [r['id'] for r in controls] == p['controls']
    statuses = {'coverage': all(s['verified_endpoints'] == 4 for s in summaries),
                'saved-proofs': all(s['verified'] for s in summaries),
                'two-cycle-budgets': all(s['target_met'] for s in summaries),
                'controls': ok, 'precision': all(s['target_met'] for s in summaries)}
    checks = dict(schema_version='research-checks-v1', checks=[dict(id=k, status='pass' if v else 'unresolved',
                  value=int(v), evidence='derived/summary.json') for k, v in statuses.items()])
    # Deliberately retain the same conservative model, now calibrated at4 gates.
    ratio = (64+64*65/2)/(4+4*5/2)
    cpu = 4*ratio*max(r['cpu_seconds'] for r in execution['rows'] if r['bits'] == 96)
    wall = 4*ratio*max(r['wall_seconds'] for r in execution['rows'] if r['bits'] == 96)
    rss = execution['rss_bytes']
    estimate = dict(cpu_seconds=cpu, wall_seconds=wall,
                    memory_mb=None if rss is None else max(512, rss/1024**2*16),
                    output_mb=4*max(r['bytes'] for r in execution['rows'])*16/1024**2,
                    basis='2x safety * two96-bit seeds * measured complete per-seed producer/checker cost * intact-product work ratio g64/g4. Memory scales16x; not a measured long-prefix cost or rigorous runtime bound.')
    blockers = ['32-cycle confirmation registration and reviewed lock absent']
    if not all(statuses.values()):
        blockers.append('four-endpoint certificate/control gate unresolved')
    for key, limit in (('cpu_seconds', 145), ('wall_seconds', 145), ('memory_mb', 1024), ('output_mb', 80)):
        if estimate[key] is None or estimate[key] > limit:
            blockers.append('unqualified confirmatory '+key+' admission')
    summary = dict(stage='two-cycle-qualification', seeds=summaries, controls=controls,
                   confirmatory_estimate=estimate, launch_allowed=False, blockers=blockers,
                   reservation=ALLOCATION, confirmation_status='blocked/not-evaluated',
                   common_endpoint_horizon=min(s['endpoint_horizon'] for s in summaries),
                   worker_metrics={k: execution[k] for k in ('worker_cpu_seconds', 'worker_wall_seconds', 'rss_bytes', 'rss_measurement', 'output_bytes')})
    for name, rows in (('record-budgets', terms), ('tube-majorants', majorants)):
        if rows:
            write_rows(derived/(name+'.csv'), rows)
        else:
            (derived/(name+'.csv')).write_text('seed,bits,endpoint\n')
    write_json(derived/'summary.json', summary)
    write_json(output/'checks.json', checks)
    result = dict(raw_source=executions[0].relative_to(run_path).as_posix(), checks=checks, summary=summary)
    write_json(output/'result.json', result)
    return result


def main():
    import os
    import sys
    request = read_json(Path(sys.argv[1]))
    if os.name == 'posix':
        from signal_space.runtime.limits import _resource_limiter
        _resource_limiter(dict(max_cpu_seconds=14, max_wall_seconds=14, max_memory_mb=1024, max_output_mb=4))()
    analyze(Path(request['run_path']), Path(request['output']), request['config'])


if __name__ == '__main__':
    main()
