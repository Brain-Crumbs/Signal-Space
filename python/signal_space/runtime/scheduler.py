"""Bounded independent GROSS jobs, supervised in threads and solved in processes.

Reservations use locked resource ceilings. No solver runs in this process and
no configuration is rewritten to obtain admission. Record order is input order.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from dataclasses import dataclass
from pathlib import Path
import threading
import uuid
from typing import Any

from signal_space.runtime.errors import ResourceRejected
from signal_space.runtime.execution import ExecutionPolicy, cpu_capacity, memory_capacity_mb, disk_capacity_mb
from signal_space.runtime.io import canonical_bytes, sha256_bytes, write_json, now


@dataclass(frozen=True)
class Budget:
    jobs: int = 1
    cpu_slots: int | None = None
    memory_mb: int | None = None
    output_mb: int | None = None

    def resolve(self, workspace: Path) -> 'Budget':
        resolved = Budget(self.jobs, self.cpu_slots if self.cpu_slots is not None else cpu_capacity(),
                          self.memory_mb if self.memory_mb is not None else memory_capacity_mb(),
                          self.output_mb if self.output_mb is not None else disk_capacity_mb(workspace))
        if any(type(x) is not int or x < 1 for x in (resolved.jobs, resolved.cpu_slots, resolved.memory_mb, resolved.output_mb)):
            raise ValueError('scheduler budgets must be positive integers')
        if resolved.cpu_slots > cpu_capacity():
            raise ResourceRejected('CPU budget exceeds host capacity')
        if resolved.memory_mb > memory_capacity_mb():
            raise ResourceRejected('memory budget exceeds currently available host capacity')
        if resolved.output_mb > disk_capacity_mb(workspace):
            raise ResourceRejected('output budget exceeds available disk capacity')
        return resolved


def run_batch(runtime, configs: list[dict[str, Any]], workspace: Path,
              budget: Budget | None = None, policy: ExecutionPolicy | None = None,
              cancel_event: threading.Event | None = None) -> dict[str, Any]:
    if not configs:
        raise ValueError('batch requires at least one configuration')
    policy = policy or ExecutionPolicy()
    budget = (budget or Budget()).resolve(workspace)
    cancel_event = cancel_event or threading.Event()
    resolved, seen = [], set()
    for config in configs:
        value = runtime.validate(config)
        estimate = runtime.estimate(value)
        if not estimate['accepted']:
            raise ResourceRejected('batch member exceeds its locked resource ceilings')
        resources = value['resources']
        if policy.cpu_slots > budget.cpu_slots or resources['max_memory_mb'] > budget.memory_mb:
            raise ResourceRejected('batch member cannot fit CPU/memory budget')
        key = sha256_bytes(canonical_bytes(value))
        if key in seen:
            raise ValueError('duplicate resolved configuration in batch')
        seen.add(key)
        resolved.append(value)
    # Completed results remain on disk; reserve the whole campaign, not just active jobs.
    if sum(c['resources']['max_output_mb'] for c in resolved) > budget.output_mb:
        raise ResourceRejected('batch output ceilings exceed retained-output budget')
    path = workspace / 'batches' / f'batch-{uuid.uuid4().hex}.json'
    rows = [{'index': i, 'config_sha256': sha256_bytes(canonical_bytes(c)),
             'experiment_id': c['experiment_id'], 'status': 'queued'} for i, c in enumerate(resolved)]
    record = {'schema_version': 'gross-batch-v1', 'state': 'running', 'created_at': now(),
              'budget': vars(budget), 'execution_policy': policy.record(), 'members': rows,
              'planned': len(rows), 'executed': 0, 'path': str(path)}
    active, pending = {}, list(range(len(rows)))
    memory_used = cpu_used = 0
    executor = ThreadPoolExecutor(max_workers=budget.jobs, thread_name_prefix='gross-supervisor')
    write_json(path, record)
    try:
        while pending or active:
            try:
                if cancel_event.is_set():
                    for i in pending:
                        rows[i]['status'] = 'cancelled-before-start'
                    pending.clear()
                # First-fit avoids a large queued member blocking smaller ready work.
                for i in list(pending):
                    memory = resolved[i]['resources']['max_memory_mb']
                    if len(active) >= budget.jobs:
                        break
                    if memory_used + memory > budget.memory_mb or cpu_used + policy.cpu_slots > budget.cpu_slots:
                        continue
                    rows[i]['status'] = 'running'
                    pending.remove(i)
                    future = executor.submit(runtime.run, resolved[i], workspace,
                                             policy=policy, cancel_event=cancel_event)
                    active[future] = i
                    memory_used += memory
                    cpu_used += policy.cpu_slots
                    record['executed'] += 1
                    write_json(path, record)
                if not active:
                    break
                done, _ = wait(active, timeout=.1, return_when=FIRST_COMPLETED)
                for future in done:
                    i = active.pop(future)
                    memory_used -= resolved[i]['resources']['max_memory_mb']
                    cpu_used -= policy.cpu_slots
                    try:
                        result = future.result()
                        rows[i].update(status=result['state'], result=result)
                    except Exception as error:
                        rows[i].update(status='failed', error={'code': getattr(error, 'code', 'MEMBER_FAILED'), 'message': str(error)})
                    write_json(path, record)
            except KeyboardInterrupt:
                cancel_event.set()
        states = {row['status'] for row in rows}
        record['state'] = ('failed' if 'failed' in states else 'interrupted' if 'interrupted' in states
                           else 'cancelled' if states & {'cancelled', 'cancelled-before-start'} else 'completed')
        record['finished_at'] = now()
        write_json(path, record)
        return record
    finally:
        # Even unexpected supervisor failure must not strand numerical subprocesses.
        if active:
            cancel_event.set()
        executor.shutdown(wait=True, cancel_futures=True)
        if record['state'] == 'running':
            record['state'] = 'interrupted'
            record['finished_at'] = now()
            write_json(path, record)
