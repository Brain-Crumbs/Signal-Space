"""Produce/check the fixed #95 one-cycle engineering fixture, never #97."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
from time import perf_counter, process_time

import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from signal_space.numerics.record_tubes import produce
from signal_space.numerics.record_certificate_check import check_file


def memory_measurement():
    # psutil may see a different PID namespace on managed hosts. Unix rusage
    # measures this process directly and supplies the kernel high-water mark.
    if sys.platform != 'win32':
        import resource
        scale = 1 if sys.platform == 'darwin' else 1024
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*scale, 'getrusage-self-maxrss'
    return psutil.Process().memory_info().rss, 'psutil-sampled-rss'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',nargs='?',type=Path)
    parser.add_argument('--check',type=Path,help='check saved evidence under its recorded source revision')
    args = parser.parse_args()
    if args.check:
        result = check_file(args.check)
        print(json.dumps(result,indent=2))
        return int(not result['verified'])
    if args.output is None:
        parser.error('NEW_OUTPUT_DIRECTORY or --check PROOF.json required')
    args.output.mkdir(parents=True,exist_ok=False)
    fixture = ROOT/'tests/fixtures/record-tube-smoke.json'
    config = json.loads(fixture.read_text())
    limits = config['limits']
    start,cpu = perf_counter(),process_time()
    peak,size = 0,0
    summary = dict(kind=config['kind'],scientific_budget_used=0,config=config,
                   config_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),
                   python=platform.python_version(),platform=platform.platform(),rows=[])
    try:
        for seed in config['seeds']:
            if process_time()-cpu >= limits['cpu_seconds'] or perf_counter()-start >= limits['wall_seconds']:
                raise RuntimeError('engineering aggregate time ceiling')
            wall,proc=perf_counter(),process_time()
            p = produce(seed,bits=config['bits'],gates=config['gates'],
                        wall_seconds=min(30,limits['wall_seconds']-(perf_counter()-start)))
            summary['source_sha256'] = p['source_sha256']
            path = args.output/(seed+'.json')
            raw = (json.dumps(p,sort_keys=True,indent=2)+'\n').encode()
            size += len(raw)
            path.write_bytes(raw) # preserve a failed prefix as well
            result = check_file(path)
            measured,method = memory_measurement()
            peak = max(peak,measured)
            summary['rss_measurement'] = method
            row = dict(seed=seed,proof_sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
                       wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-proc,check=result)
            summary['rows'].append(row)
            if not result['verified'] or not result['target_met'] or p['termination'] != 'completed':
                raise RuntimeError('one-cycle demonstration unresolved')
            if size > limits['output_bytes'] or peak > limits['rss_bytes']:
                raise RuntimeError('engineering size ceiling')
        summary['status']='completed-engineering-demonstration'
    except (ValueError,RuntimeError,ArithmeticError,MemoryError,OSError,psutil.Error) as exc:
        summary['status']='unresolved';summary['reason']=str(exc)
    summary.update(wall_seconds=perf_counter()-start,cpu_seconds=process_time()-cpu,
                   rss_peak_bytes=peak,output_bytes=size)
    if summary['wall_seconds'] > limits['wall_seconds'] or summary['cpu_seconds'] > limits['cpu_seconds']:
        summary['status']='unresolved';summary['reason']='engineering aggregate time ceiling'
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','config')},indent=2))
    return int(summary['status']=='unresolved')


if __name__=='__main__': raise SystemExit(main())
