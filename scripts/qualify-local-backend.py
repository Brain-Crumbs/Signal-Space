"""Fixed, bounded engineering smoke; never launches a scientific experiment."""
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter, process_time

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from signal_space.numerics.validated_linked_memory import ball_box, evaluate, source_chart, source_contract
from fractions import Fraction


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: python scripts/qualify-local-backend.py NEW_OUTPUT_DIRECTORY')
    destination=Path(sys.argv[1]);destination.mkdir(exist_ok=False,parents=True)
    config=json.loads((ROOT/'tests/fixtures/local-record-backend-smoke.json').read_text())
    limits=config['limits']; rows=[]; output_bytes=0
    start,cpu=perf_counter(),process_time()
    sources=['src/signal_space/numerics/dyadic.py','src/signal_space/numerics/validated_linked_memory.py',
             'docs/research/gross-local-record-theorem.md','research/papers/gross-operator-program-v0.2.md',
             'scripts/qualify-local-backend.py','tests/fixtures/local-record-backend-smoke.json',
             'requirements-validated-lock.txt']
    report={'kind':config['kind'],'scientific_budget_used':0,'python':platform.python_version(),
            'platform':platform.platform(),'config':config,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},'rows':rows}
    peak=0
    try:
        for bits in config['bits']:
            for seed in config['seeds']:
                for event in config['events']:
                    for radius in config['radii']:
                        if len(rows)>=limits['calls']: raise RuntimeError('call ceiling')
                        if process_time()-cpu>limits['cpu_seconds'] or perf_counter()-start>limits['wall_seconds']:
                            raise RuntimeError('smoke time ceiling')
                        wall,proc=perf_counter(),process_time()
                        result=evaluate(ball_box(source_chart(seed,bits=bits),radius,bits),event,bits=bits,
                                        duration=config['duration'],coupling=config['coupling'],
                                        wall_seconds=min(30,limits['wall_seconds']-(perf_counter()-start)))
                        elapsed,used=perf_counter()-wall,process_time()-proc
                        name=f'{seed}-event{event}-{bits}-radius{radius}.json'
                        raw=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
                        output_bytes+=len(raw)
                        peak=max(peak,psutil.Process().memory_info().rss)
                        if output_bytes>limits['output_bytes'] or peak>limits['rss_bytes']:
                            raise RuntimeError('smoke size ceiling')
                        (destination/name).write_bytes(raw)
                        row={'name':name,'bits':bits,'seed':seed,'event':event,'radius':radius,
                             'status':result['status'],'wall_seconds':elapsed,'cpu_seconds':used,
                             'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
                        if result['status']=='enclosed':
                            row.update({k:float(Fraction(result['gate'][k])) for k in
                                        ('value_error_norm_upper','derivative_operator_error_upper')})
                            row['gate_hessian_upper']=float(Fraction(result['bounds']['gate_hessian_upper']))
                            row['readout_radius_max']=max(float(Fraction(x)) for x in result['records']['radii'])
                        rows.append(row)
                        if result['status']!='enclosed': raise RuntimeError(result['reason'])
        report['status']='completed-local-qualification'
    except (ValueError,RuntimeError) as exc:
        report['status']='unresolved';report['reason']=str(exc)
    report.update(wall_seconds=perf_counter()-start,cpu_seconds=process_time()-cpu,
                  sampled_rss_peak_bytes=peak,output_bytes=output_bytes)
    if report['wall_seconds']>limits['wall_seconds'] or report['cpu_seconds']>limits['cpu_seconds']:
        report['status']='unresolved';report['reason']='smoke aggregate time ceiling'
    (destination/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    (destination/'source-contract.json').write_text(json.dumps(source_contract(),indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','source_sha256','config')},indent=2))
    return int(report['status']=='unresolved')


if __name__=='__main__': raise SystemExit(main())
