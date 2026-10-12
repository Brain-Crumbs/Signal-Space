"""Analyze saved detector records; never substitute mode phases for local ticks."""
import csv

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import CubicHermiteSpline

from signal_space.runtime.io import read_json, write_json


def clock_history(samples, index, omega):
    t = np.asarray([s['t'] for s in samples])
    clocks = [s['clocks'][index] for s in samples]
    tau = np.r_[0., cumulative_trapezoid([c['proper_rate'] for c in clocks], t)]
    chi = np.asarray([c['chi'] for c in clocks])
    derivative = np.asarray([c['dchi_dtau'] for c in clocks])
    w = chi - 1j * derivative / omega
    # The quadratic readout is invariant under chi -> -chi. One cycle of
    # w^2 is one invariant tick, and two ticks are one signed-field period.
    phase = np.unwrap(np.angle(w*w)) / (2*np.pi)
    ticks = phase - phase[0]
    spline = CubicHermiteSpline(tau, chi, derivative, extrapolate=False)
    zeros = spline.roots(extrapolate=False)
    zeros = zeros[np.isfinite(zeros) & (zeros >= tau[0]) & (zeros <= tau[-1])]
    slopes = abs(spline.derivative()(zeros))
    tube = [c['tube'] for c in clocks]
    balances = {}
    for name in ('energy', 'charge', 'momentum'):
        values = np.asarray([c[name] for c in tube])
        net_rate = np.asarray([c[name+'_flux'] + c[name+'_sink_rate'] for c in tube])
        integral = np.r_[0., cumulative_trapezoid(net_rate, t)]
        balances[name] = values - values[0] + integral
    return {'t': t, 'tau': tau, 'chi': chi, 'derivative': derivative,
            'ticks': ticks, 'signed_cycles': ticks/2,
            'predicted_tick_residual': ticks - omega*tau/np.pi,
            'zero_times': zeros.tolist(), 'zero_slopes': slopes.tolist(),
            'minimum_zero_slope_fraction': float(min(slopes)/(omega*clocks[0]['envelope'])) if len(slopes) else 0.,
            'minimum_envelope_fraction': float(min(c['envelope'] for c in clocks) / clocks[0]['envelope']),
            'maximum_center_motion': float(max(abs(c['center'] - clocks[0]['center']) for c in clocks)),
            'balances': balances}


def analyze(run_path, analysis_path, config):
    raw = sorted((run_path / 'attempts').glob('attempt-*'))[-1] / 'raw'
    cases = read_json(raw / 'scenarios.json')
    derived = analysis_path / 'derived'
    derived.mkdir(parents=True, exist_ok=True)
    traces, histories, observations, rows = {}, {}, {}, []
    limits = config['analysis']
    for case in cases:
        label, settings = case['label'], case['case']
        samples = read_json(raw / f'{label}-traces.json')['samples']
        traces[label] = samples
        history = [clock_history(samples, i, settings['omega_clock'])
                   for i in range(len(samples[0]['clocks']))]
        histories[label] = history
        e0, q0 = samples[0]['energy'], samples[0]['charge']
        mode0 = sum(c['mode_energy'] for c in samples[0]['clocks'])
        energy_error = max(abs(s['energy'] + s['energy_sink'] - e0) for s in samples)
        charge_error = max(abs(s['charge'] + s['charge_sink'] - q0) for s in samples)
        preparation = case['preparation']
        observations[label] = {'energy_residual_fraction': energy_error/abs(e0),
                              'charge_residual_fraction': charge_error/abs(q0),
                              'energy_residual_over_initial_mode': energy_error/mode0,
                              'residual_ratio': preparation['final_norm']/preparation['initial_norm'],
                              'source_energy_change': preparation['source_energy_change'],
                              'clocks': [{'minimum_envelope_fraction': h['minimum_envelope_fraction'],
                                          'maximum_center_motion': h['maximum_center_motion'],
                                          'zero_times': h['zero_times'], 'zero_slopes': h['zero_slopes'],
                                          'minimum_zero_slope_fraction': h['minimum_zero_slope_fraction'],
                                          'maximum_predicted_tick_residual': float(max(abs(h['predicted_tick_residual']))),
                                          'maximum_tube_energy_balance': float(max(abs(h['balances']['energy']))),
                                          'maximum_tube_charge_balance': float(max(abs(h['balances']['charge']))),
                                          'maximum_tube_momentum_balance': float(max(abs(h['balances']['momentum'])))}
                                         for h in history]}
        for i, h in enumerate(history):
            for n, sample in enumerate(samples):
                c = sample['clocks'][i]
                rows.append({'scenario': label, 'object': c['object'], 'time': sample['t'],
                             'proper_time': h['tau'][n], 'local_chi': c['chi'],
                             'local_dchi_dtau': c['dchi_dtau'], 'envelope': c['envelope'],
                             'center': c['center'], 'speed': c['speed'], 'mode_energy': c['mode_energy'],
                             'invariant_ticks': h['ticks'][n], 'signed_cycles': h['signed_cycles'][n],
                             'predicted_tick_residual': h['predicted_tick_residual'][n],
                             'global_energy_balance': sample['energy'] + sample['energy_sink'] - e0,
                             'global_charge_fraction': (sample['charge'] + sample['charge_sink'] - q0)/abs(q0),
                             'tube_energy_balance': h['balances']['energy'][n],
                             'tube_charge_balance': h['balances']['charge'][n],
                             'tube_momentum_balance': h['balances']['momentum'][n]})
    base = histories['pair-base']
    comparisons = {}
    for label in ('pair-space', 'pair-time', 'pair-wide'):
        differences = []
        for i in range(2):
            other = histories[label][i]
            differences.append(float(max(abs(base[i]['chi'] - np.interp(
                base[i]['t'], other['t'], other['chi']))) / traces['pair-base'][0]['clocks'][i]['envelope']))
        comparisons[label] = differences
    neutral_sign_error = 0.
    with np.load(raw / 'neutral-plus-final.npz') as plus, np.load(raw / 'neutral-minus-final.npz') as minus:
        for key in ('phi', 'pi', 'chi', 'pchi'):
            neutral_sign_error = max(neutral_sign_error, float(np.max(abs(plus[key]-minus[key]))))
        for key in ('a', 'pia'):
            neutral_sign_error = max(neutral_sign_error, float(np.max(abs(plus[key]+minus[key]))))
    checks = [
        ('source-identity', 'pass', read_json(raw/'source.json')),
        ('neutral-null', 'pass' if all(c['max_neutral'] == 0 for c in cases
                                      if c['case']['source']['channel'] != 'neutral') else 'fail',
         {c['label']: c['max_neutral'] for c in cases}),
        ('global-ledgers', 'pass' if all(o['energy_residual_fraction'] < limits['energy_fraction']
                                       and o['charge_residual_fraction'] < limits['charge_fraction']
                                       for o in observations.values()) else 'fail', observations),
        ('residual-reduction', 'pass' if all(observations[label]['residual_ratio'] < 1
                                            for label in ('pair-reduced', 'isolated-reduced')) else 'fail',
         {label: observations[label]['residual_ratio'] for label in ('pair-reduced', 'isolated-reduced')}),
        ('local-records', 'pass' if all(h['minimum_envelope_fraction'] >= limits['minimum_envelope_fraction']
                                      and h['minimum_zero_slope_fraction'] >= limits['minimum_zero_slope_fraction']
                                      for hs in histories.values() for h in hs) else 'fail',
         {'definition': 'local chi with convective proper-time derivative; simple zero events retained',
          'minimum_envelope_fraction': min(h['minimum_envelope_fraction'] for hs in histories.values() for h in hs)}),
        ('independent-controls', 'pass' if all(d < limits['trace_difference_fraction']
                                              for diffs in comparisons.values() for d in diffs) else 'fail', comparisons),
        ('source-controls', 'pass' if neutral_sign_error < limits['neutral_sign_absolute'] else 'fail',
         {'neutral_sign_maximum_error': neutral_sign_error,
          'note': 'Structural +/- is a physical phase-sensitive control; it is not expected to be even.'}),
        ('long-clocks', 'not-evaluated', {'reason': 'The pilot is shorter than 100 signed periods; no postinteraction survival gate.'}),
        ('exchange-recoil', 'not-evaluated', {'reason': 'No held-out exchange, weak-signal error closure or G0-G9 acceptance.',
          'weak_mode_ledger_qualified': all(o['energy_residual_over_initial_mode'] < .01 for o in observations.values()),
          'stress_scope': 'fixed-tube continuum stress diagnostic requires independent convergence'})]
    checks = {'schema_version': 'research-checks-v1', 'checks': [
        {'id': key, 'status': status, 'value': value, 'evidence': 'derived/summary.json'}
        for key, status, value in checks]}
    summary = {'scope': 'implementation pilot; full Test 8 remains unresolved', 'cases': cases,
               'observations': observations, 'comparisons': comparisons,
               'classification': {c['id']: c['status'] for c in checks['checks']},
               'nominal_calibration': 'Test 6 omega=.41274991; frequency is predicted, not fitted to this run',
               'tick_definition': 'one invariant tick is pi signed phase; two ticks are one signed period',
               'thresholds': limits}
    with (derived/'traces.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_json(derived/'summary.json', summary)
    write_json(analysis_path/'checks.json', checks)
    # Include exact spatial views so reports need not open raw solver arrays.
    with np.load(raw/'pair-base-initial.npz') as initial, np.load(raw/'pair-base-final.npz') as final:
        np.savez_compressed(derived/'spatial.npz', rho=initial['rho'], z=initial['z'],
                            initial_density=np.sum(abs(initial['phi'])**2, axis=0),
                            final_density=np.sum(abs(final['phi'])**2, axis=0),
                            initial_chi=initial['chi'], final_chi=final['chi'])
    return {'raw_source': (raw/'scenarios.json').relative_to(run_path).as_posix(), 'checks': checks, 'summary': summary}
