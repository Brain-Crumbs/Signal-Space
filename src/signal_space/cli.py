"""Python-only GROSS CLI. JSON results on stdout; diagnostics on stderr."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

from signal_space.contracts.validation import ContractError, load_json
from signal_space.runtime.errors import ResearchRuntimeError
from signal_space.runtime.execution import ExecutionPolicy, cpu_capacity, memory_capacity_mb, disk_capacity_mb
from signal_space.runtime.runner import ResearchRuntime
from signal_space.runtime.scheduler import Budget, run_batch

ROOT = Path(__file__).resolve().parents[2]


def _emit(value: Any) -> None:
    print(json.dumps(value, sort_keys=True, allow_nan=False), flush=True)


def _execution_options(command, batch=False):
    command.add_argument('--threads', type=int, default=1, help='native numerical threads per solver process')
    command.add_argument('--case-jobs', type=int, default=1, help='independent quiet Test 8 cases per run')
    if batch:
        command.add_argument('--jobs', type=int, default=1, help='concurrent independent runs')
        command.add_argument('--cpu-slots', type=int)
        command.add_argument('--memory-mb', type=int, help='aggregate reserved memory ceiling')
        command.add_argument('--output-mb', type=int, help='retained output ceiling across the entire batch')


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='signal-space', description='Registered GROSS experiments and immutable evidence')
    parser.add_argument('--workspace', default='.research-work', help='canonical run package root')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    sub.add_parser('doctor')
    schema = sub.add_parser('schema')
    schema.add_argument('--experiment', required=True)
    for name in ('validate', 'estimate', 'run'):
        command = sub.add_parser(name)
        source = command.add_mutually_exclusive_group(required=True)
        source.add_argument('--config')
        source.add_argument('--plan', help='validate locked design and config hash before execution')
        if name == 'run':
            _execution_options(command)
    batch = sub.add_parser('batch', help='parallel independent registered configurations or locked plans')
    source = batch.add_mutually_exclusive_group(required=True)
    source.add_argument('--config', action='append')
    source.add_argument('--plan', action='append')
    _execution_options(batch, batch=True)
    sweep = sub.add_parser('sweep')
    sweep.add_argument('--config', required=True)
    sweep.add_argument('--axis', action='append', required=True, help='closed config path=v1,v2')
    _execution_options(sweep, batch=True)
    for name in ('status', 'cancel', 'resume', 'analyze', 'report', 'verify', 'events'):
        command = sub.add_parser(name)
        command.add_argument('--run-id', required=name != 'status')
        if name == 'report':
            command.add_argument('--analysis-id')
        if name == 'events':
            command.add_argument('--after', type=int, default=0)
            command.add_argument('--follow', action='store_true')
    archive = sub.add_parser('archive')
    archive.add_argument('--run-id', required=True)
    archive.add_argument('--archive-root', default='research/experiments')
    archive.add_argument('--catalog', default='research/catalog.json')
    pipeline = sub.add_parser('pipeline', help='locked run → analysis → report → verified reader package')
    pipeline.add_argument('--experiment', required=True, help='recipe name, e.g. gross-test-01')
    pipeline.add_argument('--output', required=True, help='new directory outside the checkout')
    _execution_options(pipeline)
    return parser


def _locked_config(path: str) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / '.agents/scripts'))
    from experiment_contract import validate_plan, verify_runtime_config
    plan = load_json(path)
    validate_plan(plan)
    return load_json(verify_runtime_config(plan, ROOT))


def _coerce(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _set_closed(config: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split('.')
    target: Any = config
    for part in parts[:-1]:
        if not isinstance(target, dict) or part not in target:
            raise ContractError(f'sweep axis uses unknown path: {path}')
        target = target[part]
    if not isinstance(target, dict) or parts[-1] not in target:
        raise ContractError(f'sweep axis uses unknown path: {path}')
    target[parts[-1]] = value


def _sweep(runtime, config, axes, workspace, budget=None, policy=None):
    members = [config]
    declarations = []
    for axis in axes:
        if '=' not in axis:
            raise ContractError('sweep axis must be path=v1,v2')
        path, raw = axis.split('=', 1)
        values = [_coerce(item) for item in raw.split(',')]
        declarations.append({'path': path, 'values': values})
        expanded = []
        for member in members:
            for value in values:
                copy = deepcopy(member)
                _set_closed(copy, path, value)
                expanded.append(copy)
        members = expanded
    record = run_batch(runtime, members, workspace, budget, policy)
    # Persist declarations with the execution record for reproducible sweeps.
    from signal_space.runtime.io import write_json
    record['axes'] = declarations
    write_json(Path(record['path']), record)
    return record


def _events(runtime, workspace, run_id, after, follow):
    package = runtime._package(workspace, run_id)
    offsets = {}
    while True:
        manifest = package.manifest
        for entry in manifest['attempts']:
            path = package.path / entry['path'] / 'events.jsonl'
            if not path.exists():
                continue
            with path.open(encoding='utf-8') as stream:
                stream.seek(offsets.get(str(path), 0))
                while True:
                    position = stream.tell()
                    line = stream.readline()
                    if not line or not line.endswith('\n'):
                        stream.seek(position)
                        break
                    event = json.loads(line)
                    if event['sequence'] > after:
                        _emit({'run_id': run_id, 'attempt_id': entry['attempt_id'], **event})
                offsets[str(path)] = stream.tell()
        if not follow or not any(row['state'] in {'prepared', 'running'} for row in manifest['attempts']):
            return
        time.sleep(.25)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    runtime = ResearchRuntime()
    workspace = Path(args.workspace).resolve()
    try:
        if args.command == 'list':
            result = {'experiments': runtime.list()}
        elif args.command == 'doctor':
            result = {'cpu_slots': cpu_capacity(), 'available_memory_mb': memory_capacity_mb(),
                      'available_output_mb': disk_capacity_mb(workspace), 'python': sys.version,
                      'source_root': str(ROOT), 'default_execution': ExecutionPolicy().record()}
        elif args.command == 'schema':
            result = runtime.schema(args.experiment)
        elif args.command in ('validate', 'estimate', 'run'):
            config = _locked_config(args.plan) if args.plan else load_json(args.config)
            if args.command == 'validate':
                result = {'config': runtime.validate(config)}
            elif args.command == 'estimate':
                result = runtime.estimate(config)
            else:
                result = runtime.run(config, workspace, policy=ExecutionPolicy(args.threads, args.case_jobs),
                                     on_started=lambda record: print(json.dumps(record), file=sys.stderr, flush=True))
        elif args.command in ('batch', 'sweep'):
            budget = Budget(args.jobs, args.cpu_slots, args.memory_mb, args.output_mb)
            policy = ExecutionPolicy(args.threads, args.case_jobs)
            if args.command == 'batch':
                configs = [_locked_config(p) for p in args.plan] if args.plan else [load_json(p) for p in args.config]
                result = run_batch(runtime, configs, workspace, budget, policy)
            else:
                result = _sweep(runtime, load_json(args.config), args.axis, workspace, budget, policy)
        elif args.command == 'status':
            result = runtime.status(workspace, args.run_id) if args.run_id else {'runs': runtime.list_runs(workspace)}
        elif args.command in ('cancel', 'resume', 'analyze', 'verify'):
            result = getattr(runtime, args.command)(workspace, args.run_id)
        elif args.command == 'report':
            result = runtime.report(workspace, args.run_id, args.analysis_id)
        elif args.command == 'events':
            _events(runtime, workspace, args.run_id, args.after, args.follow)
            return 0
        elif args.command == 'archive':
            from signal_space.runtime.archive import archive_run
            result = archive_run(runtime._package(workspace, args.run_id).path, Path(args.archive_root).resolve(),
                                 Path(args.catalog).resolve() if args.catalog else None)
        elif args.command == 'pipeline':
            return subprocess.call([sys.executable, str(ROOT / '.agents/scripts/run_experiment.py'),
                                    '--experiment', args.experiment, '--output', args.output,
                                    '--threads', str(args.threads), '--case-jobs', str(args.case_jobs)], cwd=ROOT)
        else:
            raise AssertionError(args.command)
        _emit(result)
        if isinstance(result, dict) and (result.get('state') in {'failed', 'interrupted'} or result.get('accepted') is False or result.get('valid') is False):
            return 1
        if isinstance(result, dict) and result.get('state') == 'cancelled':
            return 130
        return 0
    except KeyboardInterrupt:
        return 130
    except (ContractError, ResearchRuntimeError, ValueError, OSError) as error:
        code = getattr(error, 'code', 'INPUT_ERROR')
        print(json.dumps({'error': {'code': code, 'message': str(error)}}, sort_keys=True), file=sys.stderr)
        return 2 if code in {'CHECKPOINT_MISMATCH', 'CORRUPT_ARTIFACT', 'INVALID_STATE'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
