#!/usr/bin/env python3
"""Validate the Test 8 prospective design and cost it without evolving fields.

This is deliberately not a registered experiment launcher. A valid design can
still be non-executable. --require-executable returns 2 for that distinction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'docs/research/plans/test-08-acceptance-design.json'
PREPARATIONS = {
    'quiet', 'neutral-nominal', 'neutral-half', 'neutral-double', 'neutral-negative',
    'quiet-phase', 'neutral-phase', 'structural-plus', 'structural-minus',
    'source-quiet', 'source-neutral', 'source-structural-plus', 'source-structural-minus',
    'receiver-quiet', 'receiver-packet', 'quiet-separation', 'neutral-separation',
    'quiet-mirror', 'neutral-mirror',
}
VARIANTS = {'base', 'space', 'time', 'domain', 'sponge', 'space-third'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(rows, key):
    result = {row[key]: row for row in rows}
    require(len(result) == len(rows), f'duplicate {key}')
    return result


def validate(design, timing, root=ROOT):
    require(design['schema_version'] == 'signal-space-test8-campaign-design-v1', 'wrong design schema')
    require(design['status'] == 'prospective-design-not-executable', 'design cannot claim execution readiness')
    require(design['manual_execution']['enabled'] is False, 'unregistered design cannot launch')
    require('runtime_config' not in design and 'locked_sha256' not in design,
            'a prospective design must not impersonate a locked runtime plan')
    require(design['issue'] == 82, 'wrong acceptance issue')
    require(design['baseline']['run_id'] == timing['run_id'], 'timing/run mismatch')
    require(design['baseline']['classification'] == 'unresolved', 'do not promote prior quiet evidence')
    for source in design['source_equations']:
        # The issue hashes the Git LF blob; Windows checkouts may contain CRLF.
        source_bytes = (root / source['path']).read_text(encoding='utf-8').encode('utf-8')
        require(hashlib.sha256(source_bytes).hexdigest() == source['sha256'],
                'authoritative equation source changed (Git LF representation)')
    gates = unique(design['gates'], 'id')
    require(set(gates) == {f'G{i}' for i in range(10)}, 'G0-G9 coverage incomplete')
    for gate in gates.values():
        require(all(gate.get(k) for k in ('pass_if', 'fail_if', 'unresolved_if', 'uncertainty')),
                f'incomplete decision rule: {gate["id"]}')
    stages = unique(design['stages'], 'id')
    require(set(stages) == {f'S{i}' for i in range(6)}, 'stage coverage incomplete')
    seen, covered = set(), set()
    for stage in design['stages']:
        require(set(stage['depends_on']) <= seen, 'stage dependencies must precede the stage')
        require(set(stage['gates']) <= set(gates), 'unknown stage gate')
        covered.update(stage['gates'])
        seen.add(stage['id'])
    require(covered == set(gates), 'unmapped acceptance gate')
    preparations = unique(design['preparations'], 'id')
    require(set(preparations) == PREPARATIONS, 'mandatory physical control matrix changed')
    for row in preparations.values():
        require(row['quiet_reference'] == 'none' or row['quiet_reference'] in preparations,
                'missing matched quiet preparation')
    variants = unique(design['numerical_variants'], 'id')
    require(set(variants) == VARIANTS, 'independent numerical variants missing')
    require(set(design['matrix']['standard_variants']) == VARIANTS - {'space-third'},
            'all physical preparations need the five declared numerical variants')
    require(set(design['matrix']['third_grid_preparations']) ==
            {'quiet', 'neutral-nominal', 'structural-plus', 'structural-minus'},
            'primary three-grid controls missing')
    base = variants['base']
    for name, fields in (('space', {'h'}), ('space-third', {'h'}), ('time', {'dt'}),
                         ('domain', {'radius', 'half_length'}), ('sponge', {'sponge_width'})):
        changed = {key for key in base if key != 'id' and variants[name][key] != base[key]}
        require(changed == fields, f'{name} confounds independent numerical changes')
    require(variants['space']['h'] == base['h']/2 and variants['space-third']['h'] == base['h']/4,
            'spatial levels must halve h independently')
    require(variants['time']['dt'] == base['dt']/2, 'time control must halve dt')
    for row in variants.values():
        require(all(row[k] > 0 for k in ('h', 'dt', 'radius', 'half_length', 'sponge_width')),
                'nonpositive grid parameter')
        require(row['dt'] <= .25*row['h']/math.sqrt(2), 'violates existing multidimensional safety bound')
        for extent in (row['radius'], 2*row['half_length']):
            require(abs(extent/row['h'] - round(extent/row['h'])) < 1e-8, 'noninteger cell count')
    pilot = design['pilot']
    require(pilot['max_physical_preparations'] == 6 and
            pilot['neutral_candidates'] + pilot['structural_candidates'] <= 6,
            'source pilot exceeds six physical preparations')
    require(design['calibration']['observation_periods'] >= 100, 'longevity gate was shortened')
    required_thresholds = dict(signal_to_error=5, ledger_fraction=.01, ledger_uncertainty_to_impulse=.2,
                               end_interaction_mode_fraction=.9, post_settling_mode_fraction=.99,
                               post_periods=20, frequency_fraction=.01, jitter_fraction=.01,
                               charge_drift_fraction=.01)
    require(design['error_budget']['thresholds'] == required_thresholds, 'issue82 decision thresholds changed')
    hypotheses = unique(design['hypotheses'], 'id')
    figures = unique(design['visualization_plan'], 'figure_id')
    require(len(figures) == 8 and 'energy-flow' in figures and 'decision-margins' in figures,
            'physical and quantitative visual coverage incomplete')
    for fig in figures.values():
        require(fig['required'] and fig['role'] == 'evidentiary', 'missing mandatory evidentiary figure')
        require(set(fig['controls']) <= preparations.keys(), 'unknown figure control')
        require(set(fig['competing_signatures']) <= hypotheses.keys() and len(fig['competing_signatures']) >= 2,
                'unknown/missing competing visual signature')
        require(all(fig.get(k) for k in ('question', 'observables', 'representation', 'source_data',
                                         'transformations', 'uncertainty')), 'incomplete visual specification')
    cases = unique(timing['cases'], 'label')
    require(set(cases) == {'isolated-base', 'isolated-fine', 'pair-base', 'pair-fine', 'pair-time', 'pair-wide'},
            'incomplete measured timing basis')
    for row in cases.values():
        elapsed = (datetime.fromisoformat(row['completed_at']) - datetime.fromisoformat(row['started_at'])).total_seconds()
        require(abs(elapsed-row['wall_seconds']) < 1e-6 and elapsed > 0, 'timing arithmetic differs from saved events')
    return variants, cases


def verify_timing_source(timing, run):
    require(sha(run/'manifest.json') == timing['manifest_sha256'], 'benchmark manifest hash mismatch')
    path = run/'attempts/attempt-0001/events.jsonl'
    require(sha(path) == timing['events_sha256'], 'benchmark events hash mismatch')
    events = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    previous = next(e['timestamp'] for e in events if e['type'] == 'worker-started')
    completed = [e for e in events if e['type'] == 'scenario-completed']
    require(len(completed) == len(timing['cases']), 'benchmark case count mismatch')
    for event, row in zip(completed, timing['cases']):
        require(row['label'] == event['payload']['label'] and row['steps'] == event['payload']['steps']
                and row['started_at'] == previous and row['completed_at'] == event['timestamp'],
                'compact timing record differs from original events')
        previous = event['timestamp']


def estimate(design, variants, cases):
    period = 2*math.pi/design['baseline']['omega_chi']

    def seconds(v, periods, isolated=False):
        key = ('isolated-fine' if v['h'] <= .1 else 'isolated-base') if isolated else (
            'pair-fine' if v['h'] <= .1 else 'pair-time')
        ref = cases[key]
        cells = round(v['radius']/v['h'])*round(2*v['half_length']/v['h'])
        old_cells = round(ref['radius']/ref['h'])*round(2*ref['half_length']/ref['h'])
        steps = round(periods*period/v['dt'])
        return ref['wall_seconds']*(cells/old_cells)*(steps/ref['steps'])

    rows = []
    def add(stage, label, v, periods, isolated=False):
        value = seconds(v, periods, isolated)
        rows.append({'stage': stage, 'case': label, 'periods': periods,
                     'cells': round(v['radius']/v['h'])*round(2*v['half_length']/v['h']),
                     'serial_wall_hours_proxy': value/3600,
                     'two_times_scheduling_hours': design['resources']['wall_headroom_factor']*value/3600})

    for name in ('base', 'domain', 'sponge'):
        for h in (.2, .1):
            add('S1', f'boundary-{name}-h{h}', {**variants[name], 'h': h}, 6)
    for isolated in (True, False):
        for name in design['calibration']['variants']:
            v = variants[name].copy()
            if isolated:
                v['half_length'] = design['calibration']['isolated_wide_half_length' if name == 'domain' else 'isolated_half_length']
            periods = design['calibration']['observation_periods'] + (0 if isolated else design['calibration']['max_pair_preparation_periods'])
            add('S2', f'{"isolated" if isolated else "prepared-pair"}-{name}', v, periods, isolated)
    for i in range(design['pilot']['max_physical_preparations']):
        for name in design['pilot']['numerical_variants']:
            add('S3', f'source-candidate-{i+1}-{name}', variants[name], design['pilot']['illustrative_periods'])
    for prep in design['preparations']:
        for name in design['matrix']['standard_variants']:
            add('S4', f'{prep["id"]}-{name}', variants[name], design['matrix']['illustrative_periods'])
    for name in design['matrix']['third_grid_preparations']:
        add('S4', f'{name}-space-third', variants['space-third'], design['matrix']['illustrative_periods'])
    totals = {stage: {'evolutions': sum(row['stage'] == stage for row in rows),
                       'serial_wall_hours_proxy': sum(row['serial_wall_hours_proxy'] for row in rows if row['stage'] == stage)}
              for stage in ('S1', 'S2', 'S3', 'S4')}
    total = sum(row['serial_wall_hours_proxy'] for row in rows)
    cells = round(variants['space']['radius']/variants['space']['h'])*round(2*variants['space']['half_length']/variants['space']['h'])
    # Two complex and four real float64 fields = 64 bytes/cell. No compression credit.
    snapshots = math.ceil(design['matrix']['illustrative_periods']*period/.4)+1
    return {'stages': totals, 'cases': rows, 'total_serial_wall_hours_proxy': total,
            'two_times_scheduling_hours': total*design['resources']['wall_headroom_factor'],
            'cpu_equivalent_speedup_to_campaign_budget_before_new_overhead': total/design['resources']['total_cpu_hours'],
            'fine_state_mib': cells*64/2**20,
            'one_fine_case_full_snapshots_every_0_4_gib': cells*64*snapshots/2**30,
            'unpriced': ['S0 implementation/validation', 'embedded eigenmode solves', 'independent spatial receiver calibration',
                        'S5 analysis/report/reconstruction replay', 'extra grids or longer source/settling windows',
                        'new stress, tracking, checkpoint and local-event overhead']}


def readiness(design, root=ROOT):
    """Inspect current implementation without accepting a prospective design as a run plan."""
    sys.path.insert(0, str(root / 'python'))
    try:
        from signal_space.experiments.registry import get_experiment

        checks = []

        def record(name, ready, reason):
            checks.append({'id': name, 'ready': ready, 'reason': reason})

        experiment_id = design['proposed_experiment_id']
        try:
            plugin = get_experiment(experiment_id)
        except ValueError:
            record('exchange-registration', False, f'{experiment_id} is not registered')
        else:
            description = plugin.describe()
            needed = {'source-exchange', 'recoil', 'proper-time-events', 'reconstruction-history'}
            available = set(description.get('capabilities', []))
            missing = sorted(needed - available)
            record('exchange-registration', not missing,
                   'registered with required capabilities' if not missing else f'missing capabilities: {missing}')

        profile = design['baseline']
        source_path = root / 'research/experiments/gross.bound-clock.v1/run-080a63d117abd84d/attempts/attempt-0001/raw/profile-0.900.npz'
        record('frozen-profile', source_path.is_file() and sha(source_path) == profile['profile_sha256'],
               'frozen profile bytes verified' if source_path.is_file() and sha(source_path) == profile['profile_sha256']
               else 'frozen Test 6 profile is missing or differs from the declared hash')

        plans = []
        for stage in design['stages']:
            candidate = root / 'docs/research/plans' / f'test-08-{stage["id"].lower()}.json'
            if candidate.is_file():
                plans.append(candidate)
        record('locked-stage-plans', len(plans) == len(design['stages']),
               f'{len(plans)}/{len(design["stages"])} stage plans found; each still requires contract and runtime validation')

        cost_path = root / 'docs/research/test-08-campaign-cost.json'
        record('measured-resource-packet', False,
               'candidate cost packet exists but has not been verified against saved full-physics measurements'
               if cost_path.is_file() else 'no measured final-physics campaign cost packet')

        record('reviewed-launch-design', design['manual_execution']['enabled'] is True and
               design['status'] != 'prospective-design-not-executable',
               'current design is prospective and explicitly disables launch' if not design['manual_execution']['enabled']
               else 'launch is enabled in this design')
        return checks
    finally:
        sys.path.pop(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path, default=DESIGN)
    parser.add_argument('--timing-source-run', type=Path, help='optional original run to verify compact timing provenance')
    parser.add_argument('--details', action='store_true', help='include every costed case, rather than stage totals only')
    parser.add_argument('--require-executable', action='store_true', help='fail if the design is not ready for a manual physics launch')
    args = parser.parse_args()
    try:
        design = read(args.design)
        timing = read(ROOT/design['benchmark'])
        variants, cases = validate(design, timing)
        if args.timing_source_run:
            verify_timing_source(timing, args.timing_source_run)
        costs = estimate(design, variants, cases)
        checks = readiness(design)
        if not args.details:
            costs.pop('cases')
        result = {'design_valid': True, 'execution_ready': False, 'physics_executed': False,
                  'design_sha256': sha(args.design), 'timing_source_verified': bool(args.timing_source_run),
                  'readiness_checks': checks,
                  'blockers': design['implementation_blockers'] +
                  [row['reason'] for row in checks if not row['ready']], 'estimate': costs}
        print(json.dumps(result, indent=2))
        return 2 if args.require_executable else 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'design_valid': False, 'execution_ready': False, 'physics_executed': False, 'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
