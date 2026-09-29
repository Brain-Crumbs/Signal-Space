#!/usr/bin/env python3
"""Bounded engineering benchmark: logging and independent GROSS algebra batches.

No model, numerical resolution or acceptance threshold is changed. This measures
runner overhead/concurrency, not the speed or acceptance of the full Test 8 PDE
campaign. Outputs and run packages must live outside the source checkout.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from signal_space.runtime.events import append_event, read_events
from signal_space.runtime.execution import cpu_capacity, process_metrics_available
from signal_space.runtime.io import read_json, write_json, sha256_file, now
from signal_space.runtime.package import code_identity, environment_identity
from signal_space.runtime.runner import ResearchRuntime
from signal_space.runtime.scheduler import Budget, run_batch


def legacy_scan_append(path, i):
    # Isolate the removed O(n) full-log parse. Omit the old lock overhead, which
    # makes this a conservative baseline, not a timing of the whole old runner.
    existing = read_events(path)
    value = {'schema_version': 'research-event-v1', 'sequence': len(existing)+1,
             'timestamp': now(), 'type': 'benchmark', 'stage': 'engineering',
             'payload': {'i': i, 'padding': 'x'*128}}
    with path.open('a') as stream:
        stream.write(json.dumps(value,sort_keys=True,separators=(',', ':'))+'\n')
        stream.flush(); os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--members', type=int, default=4, choices=range(2,9))
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--events', type=int, default=1500, choices=range(100,5001))
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT): parser.error('output must be outside the source checkout')
    if not 1 <= args.jobs <= cpu_capacity(): parser.error('jobs exceed CPU capacity')
    if code_identity()['tree_state'] != 'clean': parser.error('commit source before benchmarking')
    output.mkdir(parents=True,exist_ok=False)
    result = {'scope':'engineering only; GROSS algebra fixture, no new physics acceptance',
              'code':code_identity(),'environment':environment_identity(),
              'process_metrics_available': process_metrics_available(), 'cpu_slots':cpu_capacity(),
              'configuration':vars(args)|{'output':str(output)}, 'logging':{}, 'batches':{}}
    for name in ('full-log-scan','tail-append'):
        path = output/(name+'.jsonl'); started=time.perf_counter()
        for i in range(args.events):
            if name == 'full-log-scan': legacy_scan_append(path,i)
            else: append_event(path,'benchmark','engineering',{'i':i,'padding':'x'*128})
        result['logging'][name]={'seconds':time.perf_counter()-started,'events':len(read_events(path)),
                                  'bytes':path.stat().st_size,'sha256':sha256_file(path)}
    runtime=ResearchRuntime()
    base=read_json(ROOT/'fixtures/research/gross-test-01.json')
    configs=[]
    for i in range(args.members):
        value=deepcopy(base);value['seeds']['root']=1000+i;configs.append(value)
    records={}
    for name,jobs in (('serial',1),('parallel',args.jobs)):
        started=time.perf_counter()
        batch=run_batch(runtime,configs,output/name,Budget(jobs=jobs))
        elapsed=time.perf_counter()-started
        if batch['state']!='completed': raise RuntimeError(f'{name} did not complete: {batch["path"]}')
        records[name]=batch
        result['batches'][name]={'seconds':elapsed,'jobs':jobs,'members':args.members,
                                 'run_ids':[x['result']['run_id'] for x in batch['members']],
                                 'batch_record':str(Path(batch['path']).relative_to(output))}
        for item in batch['members']:
            runtime.verify(output/name,item['result']['run_id'])
    comparisons=[]
    for a,b in zip(records['serial']['members'],records['parallel']['members']):
        for name in ('measurements.csv','controls.json','conditioning.json','rng-start.json','rng-end.json'):
            left=Path(a['result']['path'])/'attempts/attempt-0001/raw'/name
            right=Path(b['result']['path'])/'attempts/attempt-0001/raw'/name
            equal=sha256_file(left)==sha256_file(right)
            comparisons.append({'member':a['index'],'file':name,'sha256':sha256_file(left),'equal':equal})
    if not all(x['equal'] for x in comparisons): raise RuntimeError('serial/parallel raw mismatch')
    result['raw_equivalence']=comparisons
    result['speedup']={'logging':result['logging']['full-log-scan']['seconds']/result['logging']['tail-append']['seconds'],
                       'batch':result['batches']['serial']['seconds']/result['batches']['parallel']['seconds']}
    result['limitations']=['One bounded sample on this host, not a statistical throughput study.',
                          'Batch timing includes startup, metadata, immutable hashing and output I/O.',
                          'Does not measure long Test 8 cases, compiled-kernel scaling, or full acceptance runtime.',
                          'The logging baseline omits its obsolete lock overhead.',
                          'Opaque process namespaces cannot supply trustworthy psutil tree metrics.']
    write_json(output/'benchmark.json',result)
    print(json.dumps({'output':str(output/'benchmark.json'),'speedup':result['speedup']},sort_keys=True))


if __name__=='__main__': main()
