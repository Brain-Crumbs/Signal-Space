"""Saved-data visuals for a local Test 8 spatial calibration handoff."""

import csv
import html
import shutil
from pathlib import Path

from signal_space.reporting.context import questions

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from signal_space.runtime.io import read_json, write_json


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    locked_questions = questions(Path(__file__).resolve().parents[3] / 'docs/research/plans/gross-test-08-quiet.json')
    raw = (run_path / analysis['raw_source']).parent
    raw_inputs = []
    source = run_path / analysis['path'] / 'derived'
    plots = report_path / 'plot-data'
    figures = report_path / 'figures'
    plots.mkdir()
    figures.mkdir()
    for name in ('summary.json', 'traces.csv'):
        shutil.copy2(source / name, plots / name)
    summary = read_json(plots / 'summary.json')
    with (plots / 'traces.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    specs = []
    interpretations = {}
    created = []

    def trace(name, obj='A'):
        subset = [r for r in rows if r['scenario'] == name and r['object'] == obj]
        return np.array([float(r['time']) for r in subset]), subset

    def save(fig, key, question, reading, significance, limitation, transforms):
        interpretation = {'question': locked_questions[key], 'reading': reading,
                          'significance': significance, 'limitation': limitation}
        spec = {'schema_version': 'research-figure-spec-v1', 'id': key,
                'source_datasets': ['plot-data/traces.csv', 'plot-data/summary.json'],
                'transformations': transforms,
                'axes': {'x': {'unit': 'm^-1'}, 'y': {'unit': 'as labeled'}},
                'ranges': 'shown on axes', 'normalization': 'c=hbar=m=1; frozen omega_chi=.41274991',
                'downsampling': 'none', 'fit_window': None,
                'renderer': f'matplotlib-{matplotlib.__version__}',
                'interpretation': interpretation, 'role': 'evidentiary'}
        write_json(figures / f'{key}.figure.json', spec)
        for extension in ('png', 'svg', 'pdf'):
            fig.savefig(figures / f'{key}.{extension}', dpi=150 if extension == 'png' else None)
        specs.append(f'figures/{key}.figure.json')
        interpretations[key] = interpretation
        created.append(fig)

    fig, ax = plt.subplots(figsize=(10, 4.5), layout='constrained')
    for label in ('isolated-base', 'isolated-fine', 'pair-base', 'pair-fine'):
        t, data = trace(label)
        mode = np.array([float(row['mode_energy']) for row in data])
        ax.plot(t / (2 * np.pi / .41274991), mode / mode[0] - 1, label=label)
    ax.set(xlabel='time / frozen period', ylabel='projected mode energy / initial - 1')
    ax.legend(fontsize=8)
    save(fig, 'bound-clock-history', 'Do the frozen embedded clocks retain their projected mode energy?',
         'The isolated and first pair clock projections are shown for both spatial resolutions.',
         'Mode loss or drift is visible on the clock energy scale used by the usability gate.',
         'A frozen-profile projection is diagnostic and six periods are insufficient for the required hundred-period baseline.',
         ['Project chi and pchi onto the centered frozen mode; divide by each initial mode energy.'])

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), layout='constrained')
    for label in ('pair-base', 'pair-fine', 'pair-time', 'pair-wide'):
        t, data = trace(label)
        axes[0].plot(t, [float(row['mode_q']) for row in data], label=label)
        axes[1].plot(t, [float(row['center']) for row in data], label=label)
    axes[0].set(ylabel='A local projected clock q')
    axes[1].set(xlabel='time (m^-1)', ylabel='A measured charge center z')
    axes[0].legend(fontsize=8, ncols=2)
    save(fig, 'quiet-pair-controls', 'Is pair drift or boundary placement changing the quiet clock?',
         'The A clock and measured center are compared across mesh, fixed-mesh time and larger-domain controls.',
         'Differences set a baseline error budget before any source-dependent B record is interpreted.',
         'The pair begins as unrelaxed superposition; this figure cannot establish a settled joint solution.',
         ['Weighted charge center in a frozen half-domain; centered mode projection; no smoothing.'])

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), layout='constrained')
    for label in ('isolated-base', 'isolated-fine', 'pair-base', 'pair-fine', 'pair-wide'):
        t, data = trace(label)
        e = np.array([float(r['energy']) for r in data])
        sink = np.array([float(r['energy_sink']) for r in data])
        charge = np.array([float(r['charge']) for r in data])
        q_sink = np.array([float(r['charge_sink']) for r in data])
        mode0 = sum(c['mode_energy'] for c in read_json(
            raw / f'{label}-traces.json')['samples'][0]['clocks'])
        raw_inputs.append((raw / f'{label}-traces.json').relative_to(run_path).as_posix())
        axes[0].plot(t, (e + sink - e[0]) / mode0, label=label)
        axes[1].plot(t, (charge + q_sink - charge[0]) / charge[0], label=label)
    axes[0].set(ylabel='(E + absorber work - E0) / initial mode E')
    axes[1].set(xlabel='time (m^-1)', ylabel='(Q + absorber sink - Q0) / Q0')
    axes[0].legend(fontsize=7, ncols=2)
    save(fig, 'absorber-ledgers', 'Do the measured outgoing-layer sinks close the energy and charge balances?',
         'The full Hamiltonian is corrected by separately accumulated damping power and charge loss.',
         'The energy residual is normalized to the weak clock energy rather than core rest energy.',
         'The absorber changes the outer numerical dynamics; domain controls and direct physical flux measurements remain prerequisites for exchange.',
         ['Add RK4 integrated absorber sinks to direct Hamiltonian/charge; divide by initial scales.'])

    write_json(report_path / 'interpretations.json', interpretations)
    md = ['# Test 8 outgoing-layer quiet calibration', '',
          f"Run `{manifest['run_id']}`; model `{manifest['model_id']}`.", '',
          'The six-period quiet study is a numerical prerequisite, not two-object exchange acceptance.',
          '', '## Locked checks', '']
    for name, status in summary['classification'].items():
        md.append(f'- {name}: **{status}**')
    for key, interpretation in interpretations.items():
        md.extend(['', f'## {key}', '', *(f'{k.title()}: {v}' for k, v in interpretation.items())])
    (report_path / 'report.md').write_text('\n'.join(md) + '\n', encoding="utf-8")
    (report_path / 'report.html').write_text('<html><body><pre>' + html.escape('\n'.join(md)) + '</pre></body></html>', encoding="utf-8")
    with PdfPages(report_path / 'report.pdf') as pdf:
        for fig in created:
            pdf.savefig(fig)
            plt.close(fig)
    return {'required_inputs': [f"{analysis['path']}/derived/summary.json",
                                f"{analysis['path']}/derived/traces.csv",
                                f"{analysis['path']}/checks.json", *raw_inputs],
            'figures': specs,
            'plot_data': ['plot-data/summary.json', 'plot-data/traces.csv']}
