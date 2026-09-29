"""Atomic, hash-verified quiet-calibration restart records (not Test 9 slabs).

All evolving fields, sinks, sample history and pending cases are retained.
Quiet diagnostics are stateless projections; crossing/phase analysis consumes
the complete retained sample history. No worldline/proper-time solver or RNG
exists in this prerequisite; those future state variables are not fabricated.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile

import numpy as np

from signal_space.runtime.io import safe_child, sha256_file, write_json

FIELDS = ('phi', 'pi', 'chi', 'pchi', 'a', 'pia')


def atomic_npz(path, **arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError('refusing to replace saved state')
    handle, temporary = tempfile.mkstemp(prefix='.state-', suffix='.npz', dir=path.parent)
    try:
        with os.fdopen(handle, 'wb') as stream:
            np.savez_compressed(stream, **arrays)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_checkpoint(request, *, step, case_index, index, state, grid,
                    samples, cases, max_neutral, initial_energy, initial_charge):
    attempt = Path(request['attempt_path'])
    root = attempt.parent.parent
    directory = attempt / 'checkpoints'
    directory.mkdir(exist_ok=True)
    target = directory / f'checkpoint-{step:010d}.json'
    if target.exists():
        return target  # identical progress already committed before cancellation
    payload = None
    if state is not None:
        path = target.with_suffix('.npz')
        atomic_npz(path, **dict(zip(FIELDS, state[:6])), rho=grid.r, z=grid.z,
                   absorber=grid.gamma, energy_sink=state[6], charge_sink=state[7])
        payload = {'path': path.relative_to(root).as_posix(), 'sha256': sha256_file(path)}
    completed = []
    for case in cases:
        for suffix in ('-final.npz', '-traces.json'):
            path = attempt / 'raw' / (case['label'] + suffix)
            completed.append({'path': path.relative_to(root).as_posix(), 'sha256': sha256_file(path)})
    checkpoint = {
        'schema_version': 'research-checkpoint-v1', 'checkpoint_format_version': 1,
        'kind': 'signal-space-quiet-fv-rk4-v1',
        'producing_attempt_id': request['attempt_id'],
        'parent_attempt_id': request.get('parent_attempt_id'),
        'config_hash': request['config_hash'], 'code_identity_hash': request['code_identity_hash'],
        'seed_ledger': request['seed_ledger'], 'rng_states': None,
        'preparation': request['config']['parameters']['profile'],
        'solver_state': {'step': step, 'case_index': case_index, 'index': index,
                         'state': payload, 'max_neutral': max_neutral,
                         'initial_energy': initial_energy, 'initial_charge': initial_charge},
        'accumulated_diagnostics': {'samples': samples, 'cases': cases},
        'completed_outputs': completed,
    }
    write_json(target, checkpoint, canonical=True)  # publish only after the NPZ is durable
    return target


def restore_checkpoint(request):
    saved = request['resume_checkpoint']
    if saved.get('kind') != 'signal-space-quiet-fv-rk4-v1' or saved.get('checkpoint_format_version') != 1:
        raise ValueError('unsupported quiet checkpoint')
    for key in ('config_hash', 'code_identity_hash', 'seed_ledger'):
        if saved[key] != request[key]:
            raise ValueError(f'checkpoint {key} mismatch')
    if saved['preparation'] != request['config']['parameters']['profile']:
        raise ValueError('checkpoint preparation mismatch')
    if saved['producing_attempt_id'] != request['parent_attempt_id']:
        raise ValueError('checkpoint parent mismatch')
    root = Path(request.get('checkpoint_root', Path(request['attempt_path']).parent.parent))
    references = saved['completed_outputs'] + ([saved['solver_state']['state']] if saved['solver_state']['state'] else [])
    for record in references:
        if sha256_file(safe_child(root, record['path'])) != record['sha256']:
            raise ValueError('checkpoint payload hash mismatch')
    # Copy verified prior outputs; never modify an earlier attempt. The final
    # attempt is self-contained for existing saved-data analysis/reporting.
    for record in saved['completed_outputs']:
        source = safe_child(root, record['path'])
        target = Path(request['attempt_path']) / 'raw' / source.name
        if target.exists():
            raise ValueError('resume output already exists')
        shutil.copyfile(source, target)
    return saved


def restore_fields(request, saved, grid):
    root = Path(request.get('checkpoint_root', Path(request['attempt_path']).parent.parent))
    with np.load(safe_child(root, saved['solver_state']['state']['path']), allow_pickle=False) as data:
        for name, expected in (('rho', grid.r), ('z', grid.z), ('absorber', grid.gamma)):
            if not np.array_equal(data[name], expected):
                raise ValueError('checkpoint grid mismatch')
        return (*(data[name].copy() for name in FIELDS), float(data['energy_sink']), float(data['charge_sink']))
