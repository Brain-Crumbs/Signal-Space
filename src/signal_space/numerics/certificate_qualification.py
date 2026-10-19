"""The existing exact-law proof producer, bounded at four endpoints."""
import os
import time
from pathlib import Path

from signal_space.runtime.io import read_json, write_json, sha256_file


def execute(request_path):
    if any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')):
        raise ValueError('one native thread required')
    from signal_space.numerics.record_tubes import produce
    from signal_space.numerics.record_certificate_check import check_file
    from signal_space.numerics.certificate_controls import evaluate_controls
    request = read_json(request_path)
    p = request['config']['parameters']
    raw = Path(request['attempt_path'])/'raw'
    raw.mkdir(exist_ok=True)
    start, cpu = time.monotonic(), time.process_time()
    rows, primary = [], []
    for bits in p['precision_bits']:
        for seed in p['seeds']:
            began, process = time.monotonic(), time.process_time()
            packet = produce(seed, bits=bits, gates=4,
                             wall_seconds=max(.001, min(12, 26-(time.monotonic()-start))))
            path = raw/f'{seed}-{bits}.json'
            write_json(path, packet)  # save before checking, including unclosed prefixes
            checked = check_file(path)
            rows.append(dict(seed=seed, bits=bits, file=path.name, sha256=sha256_file(path),
                             check=checked, termination=packet['termination'],
                             cpu_seconds=time.process_time()-process,
                             wall_seconds=time.monotonic()-began, bytes=path.stat().st_size,
                             gate_evaluations=len(packet['steps']),
                             transition_products=sum(range(1, len(packet['steps'])+1))))
            if bits == 96:
                primary.append(packet)
    controls = evaluate_controls(primary, raw)
    peak, method = None, 'unavailable'
    if os.name == 'posix':
        import resource
        import sys
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform == 'darwin' else 1024)
        method = 'kernel-self-maxrss'
    else:
        try:
            import psutil
            peak, method = psutil.Process().memory_info().rss, 'sampled-self-rss'
        except (ImportError, OSError):
            pass
    write_json(raw/'execution.json', dict(parameters=p, rows=rows, controls=controls,
               worker_cpu_seconds=time.process_time()-cpu, worker_wall_seconds=time.monotonic()-start,
               rss_bytes=peak, rss_measurement=method, control_file_sha256=sha256_file(raw/'local-controls.json'),
               output_bytes=sum(x.stat().st_size for x in raw.rglob('*') if x.is_file())))
    return 0
