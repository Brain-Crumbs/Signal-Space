"""Analyze saved six-period spatial and quiet-pair controls."""

import csv

import numpy as np

from signal_space.runtime.io import read_json, write_json

PERIOD = 2 * np.pi / .41274991


def positive_crossings(t, q):
    indexes = np.flatnonzero((q[:-1] <= 0) & (q[1:] > 0))
    return t[indexes] - q[indexes] * (t[indexes+1] - t[indexes]) / (q[indexes+1] - q[indexes])


def clock_measurements(samples, index):
    t = np.array([row['t'] for row in samples])
    q = np.array([row['clocks'][index]['mode_q'] for row in samples])
    e = np.array([row['clocks'][index]['mode_energy'] for row in samples])
    z = np.array([row['clocks'][index]['center'] for row in samples])
    charge = np.array([row['clocks'][index]['charge'] for row in samples])
    ticks = positive_crossings(t, q)
    intervals = np.diff(ticks)
    post = e[t >= 2 * PERIOD]
    return {'ticks': ticks.tolist(),
            'frequency_fraction': float(abs(2 * np.pi / np.mean(intervals) / .41274991 - 1)) if len(intervals) >= 3 else None,
            'jitter_fraction': float(np.max(abs(intervals - np.mean(intervals))) / PERIOD) if len(intervals) >= 3 else None,
            'minimum_post_mode_fraction': float(np.min(post) / post[0]) if len(post) else None,
            'maximum_post_mode_fraction': float(np.max(post) / post[0]) if len(post) else None,
            'max_center_displacement': float(np.max(abs(z-z[0]))),
            'minimum_charge_fraction': float(np.min(charge) / charge[0])}


def trace_error(reference, candidate):
    t = np.array([x['t'] for x in reference])
    y = np.array([x['clocks'][0]['mode_q'] for x in reference])
    tc = np.array([x['t'] for x in candidate])
    yc = np.array([x['clocks'][0]['mode_q'] for x in candidate])
    common = t <= tc[-1]
    return float(np.max(abs(y[common] - np.interp(t[common], tc, yc))) / max(abs(y[0]), 1e-30))


def analyze(run_path, analysis_path, config):
    attempt = sorted((run_path / 'attempts').glob('attempt-*'))[-1]
    raw = attempt / 'raw'
    cases = read_json(raw / 'scenarios.json')
    traces = {c['label']: read_json(raw / f"{c['label']}-traces.json")['samples'] for c in cases}
    derived = analysis_path / 'derived'
    derived.mkdir(parents=True, exist_ok=True)
    rows = []
    observations = {}
    for case in cases:
        label = case['label']
        samples = traces[label]
        e0 = samples[0]['energy']
        q0 = samples[0]['charge']
        mode0 = sum(c['mode_energy'] for c in samples[0]['clocks'])
        eb = max(abs(x['energy'] + x['energy_sink'] - e0) for x in samples) / mode0
        qb = max(abs(x['charge'] + x['charge_sink'] - q0) for x in samples) / abs(q0)
        clocks = [clock_measurements(samples, i) for i in range(len(samples[0]['clocks']))]
        observations[label] = {'energy_residual_over_mode': float(eb),
                               'charge_residual_fraction': float(qb),
                               'clocks': clocks,
                               'absorbed_energy': samples[-1]['energy_sink'],
                               'absorbed_charge': samples[-1]['charge_sink']}
        for x in samples:
            for j, clock in enumerate(x['clocks']):
                rows.append({'scenario': label, 'object': 'AB'[j], 'time': x['t'],
                             'energy': x['energy'], 'energy_sink': x['energy_sink'],
                             'charge': x['charge'], 'charge_sink': x['charge_sink'],
                             'center': clock['center'], 'mode_q': clock['mode_q'],
                             'mode_p': clock['mode_p'], 'mode_energy': clock['mode_energy'],
                             'local_chi': clock['axis_chi']})
    with (derived / 'traces.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    comparisons = {name: trace_error(traces['pair-base'], traces[name])
                   for name in ('pair-fine', 'pair-time', 'pair-wide')}
    min_distance = min(abs(x['clocks'][1]['center'] - x['clocks'][0]['center'])
                       for x in traces['pair-base'])
    limits = config['analysis']
    check_results = [
        ('source-identity', 'pass', read_json(raw / 'source.json')),
        ('neutral-null', 'pass' if all(c['max_neutral'] == 0 for c in cases) else 'fail',
         {c['label']: c['max_neutral'] for c in cases}),
        ('sink-ledger', 'pass' if all(v['energy_residual_over_mode'] < limits['mode_scale_energy_residual']
                                     and v['charge_residual_fraction'] < limits['charge_residual_fraction']
                                     for v in observations.values()) else 'fail',
         {k: {'energy_over_mode': v['energy_residual_over_mode'], 'charge': v['charge_residual_fraction']}
          for k, v in observations.items()}),
        ('distinct-pair', 'pass' if min_distance > 3 * 17.8 and
                              all(c['minimum_charge_fraction'] >= .99 and c['max_center_displacement'] < 2
                                  for label, case in observations.items() if label.startswith('pair-')
                                  for c in case['clocks']) else 'fail',
         {'minimum_separation': float(min_distance), 'required': 3 * 17.8}),
    ]
    clock_ok = all(c['frequency_fraction'] is not None and
                   c['frequency_fraction'] < limits['frequency_fraction'] and
                   c['jitter_fraction'] < limits['jitter_fraction'] and
                   c['minimum_post_mode_fraction'] >= limits['minimum_mode_fraction'] and
                   c['maximum_post_mode_fraction'] <= 2 - limits['minimum_mode_fraction']
                   for case in observations.values() for c in case['clocks'])
    check_results.extend([
        ('short-clocks', 'pass' if clock_ok else 'fail', observations),
        ('independent-controls', 'pass' if all(x < limits['trace_difference_fraction']
                                               for x in comparisons.values()) else 'fail', comparisons),
        ('joint-preparation', 'unresolved', {'reason': 'Free evolution of superposed data does not solve the joint stationary preparation.'}),
        ('long-clocks', 'unresolved', {'reason': 'Six periods cannot prove 100-period isolated and quiet longevity.'}),
        ('full-exchange', 'not-evaluated', {'reason': 'No source, B reception, recoil or postinteraction survival was evolved.'}),
    ])
    checks = {'schema_version': 'research-checks-v1', 'checks': [
        {'id': name, 'status': status, 'value': value, 'evidence': 'derived/summary.json'}
        for name, status, value in check_results]}
    summary = {'scope': 'six-period outgoing-layer quiet qualification, not Test 8 acceptance',
               'cases': cases, 'observations': observations, 'comparisons': comparisons,
               'minimum_pair_separation': float(min_distance),
               'thresholds': limits, 'classification': {c['id']: c['status'] for c in checks['checks']}}
    write_json(derived / 'summary.json', summary)
    write_json(analysis_path / 'checks.json', checks)
    return {'raw_source': (raw / 'scenarios.json').relative_to(run_path).as_posix(),
            'checks': checks, 'summary': summary}
