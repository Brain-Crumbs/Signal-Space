"""Saved pilot verification in a runtime-supervised, separately reserved process."""
import json
from pathlib import Path
from fractions import Fraction as Q
from signal_space.runtime.io import read_json,write_json,sha256_file


def analyze(run_path,output,config):
    from signal_space.numerics.record_certificate_check import check_file
    from signal_space.numerics.certificate_controls import evaluate_controls
    from signal_space.numerics.operators import write_rows
    executions=sorted(run_path.glob('attempts/*/raw/execution.json'))
    if len(executions)!=1:raise ValueError('pilot needs exactly one completed worker attempt')
    raw=executions[0].parent;execution=read_json(executions[0]);p=config['parameters']
    if execution['parameters']!=p:raise ValueError('raw parameters differ from lock')
    expected={(s,b) for s in p['seeds'] for b in p['precision_bits']}
    if len(execution['rows'])!=4 or {(r['seed'],r['bits']) for r in execution['rows']}!=expected:
        raise ValueError('incomplete precision/seed coverage')
    terms=[];summaries=[];primary=[]
    for row in execution['rows']:
        name=f"{row['seed']}-{row['bits']}.json"
        if row['file']!=name or sha256_file(raw/name)!=row['sha256']:
            raise ValueError('changed proof bytes')
        proof=read_json(raw/name)
        if proof['config']['seed']!=row['seed'] or proof['config']['bits']!=row['bits'] or proof['config']['gates']!=2:
            raise ValueError('changed proof source/precision/coverage')
        result=check_file(raw/name)
        if not result['verified']:raise ValueError('invalid saved proof: '+result['reason'])
        if result!=row['check']:raise ValueError('worker check does not reproduce from saved objects')
        summaries.append(dict(bits=row['bits'],**result))
        for step in proof['steps']:
            for l,t in enumerate(step['record_terms']):
                terms.append(dict(seed=row['seed'],bits=row['bits'],endpoint=step['index'],event=step['event'],record=l+1,
                                  **{k:float(Q(t[k])) for k in ('readout_center','linear','remainder','preparation','numerical','readout','total')}))
        if row['bits']==96:primary.append(proof)
    primary.sort(key=lambda x:p['seeds'].index(x['config']['seed']))
    derived=output/'derived';derived.mkdir()
    if sha256_file(raw/'local-controls.json')!=execution['control_file_sha256']:
        raise ValueError('changed saved control bytes')
    replay=evaluate_controls(primary,derived/'controls-replay',saved=raw)
    if replay!=execution['controls']:raise ValueError('control quantities do not reproduce')
    controls_ok=all(r['status']=='pass' for r in replay) and [r['id'] for r in replay]==p['controls']
    statuses={'coverage':all(s['verified_endpoints']==2 for s in summaries),
              'saved-proofs':all(s['verified'] for s in summaries),
              'one-cycle-budgets':all(s['target_met'] for s in summaries),
              'controls':controls_ok,'precision':all(s['target_met'] for s in summaries)}
    checks=dict(schema_version='research-checks-v1',checks=[dict(id=k,status='pass' if v else 'unresolved',
                value=int(v),evidence='derived/summary.json') for k,v in statuses.items()])
    # Deliberately conservative extrapolation: preserve the observed complete
    # producer/checker unit cost and charge it for every future product count.
    # No claimed wall-time guarantee or extra long-prefix execution is hidden here.
    max_seed_cpu=max(r['cpu_seconds'] for r in execution['rows'] if r['bits']==96)
    max_seed_wall=max(r['wall_seconds'] for r in execution['rows'] if r['bits']==96)
    work_ratio=(64+64*65/2)/(2+2*3/2)
    projected_cpu=2*2*work_ratio*max_seed_cpu
    projected_wall=2*2*work_ratio*max_seed_wall
    max_bytes=max(r['bytes'] for r in execution['rows'])
    estimate=dict(cpu_seconds=projected_cpu,wall_seconds=projected_wall,
        memory_mb=max(512,(execution['rss_bytes'] or 0)/1024**2*32) if execution['rss_bytes'] is not None else None,
        output_mb=2*max_bytes*32*2/1024**2,
        basis='2x safety * two seeds * measured max complete per-seed producer/checker cost * (g+g(g+1)/2) work ratio; g64 vs g2. Includes controls/checks conservatively in full budget. This is an extrapolation, not measured long-prefix feasibility.',
        measured_pilot_cpu_seconds=execution['worker_cpu_seconds'],measured_pilot_wall_seconds=execution['worker_wall_seconds'],
        measured_gate_evaluations=sum(r["gate_evaluations"] for r in execution["rows"]),measured_transition_products=sum(r["transition_products"] for r in execution["rows"]),measured_max_seed_cpu_seconds=max_seed_cpu)
    blockers=[]
    if not all(statuses.values()):blockers.append('pilot certificate or control gate unresolved')
    for k,limit in (('cpu_seconds',190),('wall_seconds',190),('memory_mb',1024),('output_mb',96)):
        if estimate[k] is None or estimate[k]>limit:blockers.append('unqualified confirmatory '+k+' admission')
    # Actual process monitoring plus kernel self metrics are never treated as
    # available merely because the supervisor serialized a zero placeholder.
    summary=dict(stage='pilot',seeds=summaries,controls=replay,confirmatory_estimate=estimate,
                 launch_allowed=not blockers,blockers=blockers,
                 reservation=dict(pilot_worker_cpu_wall=45,pilot_analysis_cpu_wall=15,
                                  confirmation_worker_cpu_wall=190,confirmation_analysis_cpu_wall=50,
                                  total_cpu_wall_ceiling=300,remaining_reserved_cpu_wall=240,
                                  pilot_output_mb=16,confirmation_output_mb=112,total_output_mb=128),
                 pilot_scope='one AB cycle / two endpoints, both seeds, full radius ball; no Tests1-11 promotion',
                 worker_metrics=dict(cpu_seconds=execution['worker_cpu_seconds'],wall_seconds=execution['worker_wall_seconds'],
                                     rss_bytes=execution['rss_bytes'],rss_measurement=execution['rss_measurement']))
    if terms:write_rows(derived/'record-budgets.csv',terms)
    else:(derived/'record-budgets.csv').write_text('seed,bits,endpoint,event,record,readout_center,linear,remainder,preparation,numerical,readout,total\n')
    write_json(derived/'summary.json',summary)
    write_json(output/'checks.json',checks)
    result=dict(raw_source=executions[0].relative_to(run_path).as_posix(),checks=checks,summary=summary)
    write_json(output/'result.json',result)
    return result


def main():
    import sys,os
    request=read_json(Path(sys.argv[1]))
    if os.name=='posix':
        from signal_space.runtime.limits import _resource_limiter
        _resource_limiter(dict(max_cpu_seconds=14,max_wall_seconds=14,max_memory_mb=1024,max_output_mb=4))()
    analyze(Path(request['run_path']),Path(request['output']),request['config'])


if __name__=='__main__':main()
