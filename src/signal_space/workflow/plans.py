"""Resolve byte-locked plans and derive explicit operational revisions."""
from copy import deepcopy
from pathlib import Path
import sys

from signal_space.runtime.io import read_json, write_json, sha256_file, pretty_bytes

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '.agents/scripts'))
from experiment_contract import validate_plan, verify_runtime_config, canonical_plan, digest


def load_plan(path):
    path = Path(path).resolve()
    plan = read_json(path)
    validate_plan(plan)
    # Portable derived/pipeline folders use a sibling config.json. Repository
    # plans continue to resolve their unchanged repository-relative paths.
    roots = [path.parent, ROOT] if plan['runtime_config'] == 'config.json' else [ROOT, path.parent]
    errors = []
    for root in roots:
        try:
            config_path = verify_runtime_config(plan, root)
            return plan, read_json(config_path), config_path
        except ValueError as error:
            errors.append(str(error))
    raise ValueError('; '.join(errors))


def validate_bound_plan(path, config):
    plan, bound, _ = load_plan(path)
    if bound != config:
        raise ValueError('selected report plan does not bind the run configuration')
    return plan


def derive(source, output, changes, *, execution=None):
    from signal_space.runtime.runner import ResearchRuntime
    plan, original, source_config = load_plan(source)
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('derived plan directory already exists; choose a new identity')
    allowed = {'max_cpu_seconds', 'max_wall_seconds', 'max_memory_mb', 'max_output_mb'}
    if not changes and not execution:
        raise ValueError('derive requires an explicit resource or execution change')
    if set(changes) - allowed or any(type(v) is not int or v < 1 for v in changes.values()):
        raise ValueError('resource overrides require known keys and positive integer limits')
    config = deepcopy(original)
    config['resources'].update(changes)
    if execution:
        if config['experiment_id'] != 'gross.two-object-quiet-calibration.v1':
            raise ValueError('execution derivation is registered only for quiet Test 8')
        config['parameters']['execution'] = {**config['parameters'].get('execution', {
            'backend': 'numpy', 'neutral_mode': 'full', 'checkpoint_stride': 1000}), **execution}
    ResearchRuntime().validate(config)
    revised = deepcopy(plan)
    revised['runtime_config'] = 'config.json'
    revised['runtime_config_sha256'] = digest(pretty_bytes(config))
    revised['resources'] = deepcopy(config['resources'])
    revised['locked_sha256'] = digest(canonical_plan(revised))
    validate_plan(revised)
    record = {'schema_version': 'gross-plan-derivation-v1',
              'parent_plan_sha256': sha256_file(Path(source)), 'parent_lock': plan['locked_sha256'],
              'parent_config_sha256': sha256_file(source_config),
              'resources_before': original['resources'], 'resources_after': config['resources'],
              'execution_before': original['parameters'].get('execution'),
              'execution_after': config['parameters'].get('execution'),
              'physical_parameters_and_criteria_preserved': True,
              'plan_lock': revised['locked_sha256']}
    output.mkdir(parents=True)
    write_json(output / 'config.json', config)
    write_json(output / 'plan.json', revised)
    write_json(output / 'derivation.json', record)
    load_plan(output / 'plan.json')
    return {**record, 'plan': str(output / 'plan.json'),
            'estimate': ResearchRuntime().estimate(config)}
