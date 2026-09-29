#!/usr/bin/env python3
"""Verify the GROSS boundary, archived bytes, current plans and research index."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'.agents/scripts'))
from experiment_contract import validate_plan, verify_runtime_config
from signal_space.experiments.registry import list_experiments
from signal_space.runtime.runner import ResearchRuntime


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def research_index():
    paths = sorted(p for p in (ROOT/'research').rglob('*') if p.is_file()
                   and p != ROOT/'research/archive-manifest.json')
    return {'schema_version': 1, 'generated_by': 'scripts/verify-repository.py --write-research-index',
            'file_count': len(paths), 'files': [{'path': p.relative_to(ROOT).as_posix(),
             'size': p.stat().st_size, 'sha256': digest(p)} for p in paths]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-research-index', action='store_true', help='intentional index update after reviewed research changes')
    args = parser.parse_args()
    problems = []
    archived = json.loads((ROOT/'archive/manifest.json').read_text())
    for item in archived['files']:
        path = ROOT/item['archived_path']
        if not path.is_file() or path.stat().st_size != item['size'] or digest(path) != item['sha256']:
            problems.append('archive bytes changed: '+item['archived_path'])
    for directory in ('apps', 'packages', 'python', 'e2e', 'test'):
        if (ROOT/directory).exists(): problems.append('obsolete active directory: '+directory)
    for name in ('package.json','package-lock.json','tsconfig.json','.nvmrc','eslint.config.js'):
        if (ROOT/name).exists(): problems.append('obsolete active toolchain: '+name)
    ids = {item['experiment_id'] for item in list_experiments()}
    if not ids or not all(name.startswith('gross.') for name in ids):
        problems.append('non-GROSS experiment in active registry')
    for p in (ROOT/'src').rglob('*.py'):
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            names = [node.module or ''] if isinstance(node,ast.ImportFrom) else [x.name for x in node.names] if isinstance(node,ast.Import) else []
            for name in names:
                if name.startswith('archive') or any(fragment in name for fragment in ('.synthetic','.charged','.service','.contracts.e01','.contracts.generated')):
                    problems.append(f'archived import in {p.relative_to(ROOT)}: {name}')
    runtime = ResearchRuntime(); plans = 0
    for path in sorted((ROOT/'docs/research/plans').glob('*.json')):
        value = json.loads(path.read_text())
        if 'locked_sha256' not in value:
            continue  # separately registered design-only Test 8 campaign
        validate_plan(value)
        config_path = verify_runtime_config(value, ROOT)
        runtime.validate(json.loads(config_path.read_text()))
        plans += 1
    for path in (ROOT/'fixtures/research').glob('*.json'):
        runtime.validate(json.loads(path.read_text()))
    for entry in json.loads((ROOT/'research/catalog.json').read_text())['entries']:
        path = entry.get('path')
        if path and not (ROOT/path).exists(): problems.append('missing catalog entry: '+path)
    index = research_index()
    manifest = ROOT/'research/archive-manifest.json'
    if args.write_research_index:
        manifest.write_text(json.dumps(index,indent=2)+'\n')
    else:
        stored = json.loads(manifest.read_text())
        if stored['files'] != index['files']:
            problems.append('research content differs from its reviewed index')
    for problem in problems: print(problem, file=sys.stderr)
    print(json.dumps({'valid': not problems, 'archived_files': len(archived['files']),
                      'registered_gross_experiments': len(ids), 'locked_plans': plans,
                      'research_files': index['file_count']}))
    return bool(problems)


if __name__ == '__main__': raise SystemExit(main())
