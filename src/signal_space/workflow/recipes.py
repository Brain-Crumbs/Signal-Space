"""One discoverable recipe catalog for local CLI, pipeline and campaign use."""
from signal_space.workflow.plans import ROOT, load_plan

RECIPES = {f'gross-test-{n:02d}': f'docs/research/plans/gross-test-{n:02d}.json' for n in range(1, 6)}
RECIPES['gross-test-06'] = 'docs/research/plans/gross-test-06-v2.json'
for suffix in ('longevity', 'response'):
    RECIPES[f'gross-test-06-{suffix}'] = f'docs/research/plans/gross-test-06-{suffix}.json'
RECIPES['gross-test-07'] = 'docs/research/plans/gross-test-07.json'
for suffix in ('order4', 'boundary', 'acceptance', 'reconstruction', 'transfer'):
    RECIPES[f'gross-test-07-{suffix}'] = f'docs/research/plans/gross-test-07-{suffix}.json'
for suffix in ('calibration', 'quiet', 'quiet-optimized'):
    RECIPES[f'gross-test-08-{suffix}'] = f'docs/research/plans/gross-test-08-{suffix}.json'


def recipe_path(name):
    if name not in RECIPES:
        raise ValueError(f'unknown recipe {name}; use signal-space recipes')
    return ROOT / RECIPES[name]


def catalog():
    from signal_space.runtime.runner import ResearchRuntime
    from signal_space.experiments.registry import get_experiment
    records = []
    for name in RECIPES:
        plan, config, _ = load_plan(recipe_path(name))
        estimate = ResearchRuntime().estimate(config)
        from signal_space.workflow.preflight import frozen_inputs
        try:
            prerequisites=frozen_inputs(config); missing=[]
        except ValueError as error:
            prerequisites=[]; missing=[str(error)]
        records.append({'recipe': name, 'plan': RECIPES[name], 'question': plan['question'],
                        'experiment_id': config['experiment_id'], 'model_id': config['model_id'],
                        'backend': config['parameters'].get('execution', {}).get('backend', 'numpy'),
                        'estimate_accepted': estimate['accepted'], 'rejected_limits': estimate['rejected_limits'],
                        'recommended': name == 'gross-test-08-quiet-optimized',
                        'frozen_prerequisites':prerequisites, 'prerequisite_blockers':missing,
                        'known_gaps': get_experiment(config['experiment_id']).known_gaps(config)})
    return records
