"""Honest recipe readiness and desktop/overnight capacity profiles."""
import ast
import importlib.util
from pathlib import Path
import subprocess

from signal_space.runtime.admission import admit
from signal_space.runtime.errors import ResourceRejected
from signal_space.runtime.execution import ExecutionPolicy, cpu_capacity, memory_capacity_mb, disk_capacity_mb
from signal_space.runtime.io import sha256_file
from signal_space.workflow.plans import ROOT, load_plan


def profile(name='desktop'):
    if name not in {'desktop', 'overnight', 'explicit'}:
        raise ValueError('profile must be desktop, overnight or explicit')
    cpu = cpu_capacity()
    slots = max(1, cpu // 2) if name == 'desktop' else cpu
    memory = memory_capacity_mb()
    return {'name': name, 'cpu_slots': slots, 'jobs': min(slots, 2 if name == 'desktop' else 4),
            'memory_mb': max(1, int(memory * (.7 if name == 'desktop' else .9))),
            'threads': 1, 'note': 'capacity ceilings, not a speedup prediction; locked scientific budgets remain unchanged'}


def frozen_inputs(config):
    rows = []
    def visit(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
                path = (ROOT / value['path']).resolve()
                if not path.is_relative_to(ROOT) or not path.is_file() or sha256_file(path) != value['sha256']:
                    raise ValueError(f'missing or mismatched frozen input: {value["path"]}')
                rows.append({'path': value['path'], 'sha256': value['sha256']})
            for child in value.values(): visit(child)
        elif isinstance(value, list):
            for child in value: visit(child)
    visit(config['parameters'])
    return rows


def visual_contract(plan):
    """Check every declared question without importing a plotting backend.

    Literal question tables and save(fig,key,question,...) declarations are
    inspected structurally. The quiet renderer binds its questions from the
    plan at render time. Full saved-data rendering is a separate smoke gate.
    """
    from signal_space.experiments.registry import get_experiment
    plugin = get_experiment(plan['experiment_id'])
    module = plugin.__class__.__module__.rsplit('.', 1)[-1]
    path = ROOT / 'src/signal_space/reporting' / f'{module}.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    observed = {}; ids = set(); signatures = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            if any(isinstance(target, ast.Name) and target.id in {'QUESTIONS','LOCKED_QUESTIONS'} for target in node.targets):
                observed.update(ast.literal_eval(node.value))
        if isinstance(node, ast.FunctionDef) and node.name == 'save':
            names=[arg.arg for arg in node.args.args]
            signatures[node.name]=names
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in signatures:
            names=signatures[node.func.id]
            values=dict(zip(names,node.args)); key=values.get('key')
            if not isinstance(key,ast.Constant) or not isinstance(key.value,str): continue
            ids.add(key.value)
            question=values.get('question',values.get('q'))
            if isinstance(question,ast.Constant) and key.value not in observed:
                observed[key.value]=question.value
    planned={r['figure_id']:r['question'] for r in plan['visualization_plan'] if r['required']}
    if set(planned)-ids: raise ValueError('renderer lacks declared figures: '+', '.join(sorted(set(planned)-ids)))
    if module != 'two_object_quiet':
        mismatched=[key for key,q in planned.items() if observed.get(key)!=q]
        if mismatched: raise ValueError('renderer questions differ from locked plan: '+', '.join(mismatched))
    return {'state':'bound-at-render' if module=='two_object_quiet' else 'static-contract-verified',
            'renderer_sha256':sha256_file(path),'required_figures':sorted(planned),
            'rendered':False,'note':'Static contract only. Saved-data render/export fixtures validate runtime inputs and packaging.'}


def check(plan_path, workspace, policy=None, *, require_clean=True, compile_backend=False, export_headroom=True):
    from signal_space.runtime.runner import ResearchRuntime
    plan, config, config_path = load_plan(plan_path)
    policy = policy or ExecutionPolicy()
    results, blockers = {}, []
    source = subprocess.run(['git','status','--porcelain'], cwd=ROOT, text=True, capture_output=True)
    results['source_clean'] = source.returncode == 0 and not source.stdout.strip()
    if require_clean and not results['source_clean']:
        blockers.append('source checkout must be clean before a pipeline executes')
    for label, action in (
        ('config', lambda: ResearchRuntime().validate(config)),
        ('frozen_inputs', lambda: frozen_inputs(config)),
        ('visual_contract', lambda: visual_contract(plan)),
    ):
        try: results[label] = action()
        except (ValueError, OSError) as error: blockers.append(f'{label}: {error}')
    estimate = ResearchRuntime().estimate(config, policy=policy)
    results['estimate'] = estimate
    if not estimate['accepted']:
        blockers.append('locked limits reject estimate: ' + ', '.join(estimate['rejected_limits']))
    backend = config['parameters'].get('execution', {}).get('backend','numpy')
    results['backend'] = {'name': backend, 'compile_checked': False}
    if backend == 'numba':
        if importlib.util.find_spec('numba') is None:
            blockers.append('numba backend missing: install requirements-performance-lock.txt in the pinned environment')
        elif compile_backend:
            try:
                # A tiny synthetic empty grid checks the actual backend/toolchain.
                from signal_space.engine.axisymmetric import compile_probe
                results['backend']['probe'] = compile_probe()
                results['backend']['compile_checked'] = True
            except Exception as error:
                blockers.append(f'backend compilation: {error}')
    # A full new canonical attempt plus reader/ZIP/temporary copies. Existing
    # attempt bytes already reduce free disk; no old bytes are deleted.
    extra = 3 * config['resources']['max_output_mb'] + 64 if export_headroom else 0
    try: results['host_admission'] = admit(config['resources'], Path(workspace), policy, extra_output_mb=extra)
    except (ValueError, ResourceRejected) as error: blockers.append(str(error))
    results['storage'] = {'new_attempt_ceiling_mb': config['resources']['max_output_mb'],
                          'export_headroom_mb': extra, 'available_mb': disk_capacity_mb(Path(workspace).resolve())}
    return {'schema_version': 'gross-preflight-v1', 'execution_ready': not blockers,
            'physics_executed': False, 'plan_lock': plan['locked_sha256'],
            'config_sha256': sha256_file(config_path), 'blockers': blockers, 'checks': results,
            'estimate_status': 'legacy-unmeasured-for-this-host; use profile collect for measured completed work',
            'scope': plan['question']}
