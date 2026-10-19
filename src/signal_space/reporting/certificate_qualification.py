"""Four question-driven figures from saved C1 qualification evidence."""
import csv
from fractions import Fraction as Q
import html
import shutil
import textwrap

from signal_space.runtime.io import read_json, write_json

QUESTIONS = {
    'internal-records': 'How do moving memories coexist with predictable local records?',
    'amplification-sensitivity': 'Which internal changes are visible to the three records?',
    'certified-budgets': 'How many ordered endpoints fit every error allocation?',
    'obstruction-precision': 'Does nonlinear growth or numerical precision limit the prefix?',
}


def render_report(run_path, output, manifest, analysis, render_provenance):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from signal_space.numerics.operators import write_rows
    data, figures = output/'plot-data', output/'figures'
    data.mkdir()
    figures.mkdir()
    derived = run_path/analysis['path']/'derived'
    for name in ('record-budgets.csv', 'tube-majorants.csv', 'summary.json'):
        shutil.copy2(derived/name, data/name)
    def rows(name):
        with (data/name).open() as stream:
            return list(csv.DictReader(stream))
    records, majorants = rows('record-budgets.csv'), rows('tube-majorants.csv')
    summary = analysis['summary']
    raw = (run_path/analysis['raw_source']).parent
    centers = []
    for seed in ('active-plus', 'active-minus'):
        proof = read_json(raw/f'{seed}-96.json')
        for n, center in [(0, proof['initial_center'])]+[(s['index'], s['center']) for s in proof['steps']]:
            v = [float(Q(int(x['lo']), 1 << x['bits'])) for x in center]
            centers.append(dict(seed=seed, endpoint=n, A_x=2*v[12], A_y=2*v[13], A_z=2*v[14],
                                B_x=2*v[15], B_y=2*v[16], B_z=2*v[17]))
    write_rows(data/'internal-endpoints.csv', centers)
    made, specs, interpretations = [], [], {}
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    colors = {'active-plus': '#247d76', 'active-minus': '#526ab2'}
    def save(fig, key, datasets, reading, significance, limitation):
        for ext in ('png', 'svg', 'pdf'):
            fig.savefig(figures/f'{key}.{ext}', dpi=160, bbox_inches='tight')
        spec = dict(schema_version='research-figure-spec-v1', id=key,
                    source_datasets=['plot-data/'+s for s in datasets],
                    transformations=['Exact rational/interval quantities converted to display floats; labelled maxima only; no fitting or smoothing.'],
                    axes={'x': {'unit': 'ordered endpoint or internal Bloch coordinate'}, 'y': {'unit': 'dimensionless'}},
                    ranges='Labelled axes; only saved endpoints are plotted.', normalization='Physical preparation radius1e-6; P=I/2+x.sigma.',
                    downsampling='none', fit_window=None, renderer='matplotlib-'+matplotlib.__version__)
        write_json(figures/f'{key}.figure.json', spec)
        specs.append(f'figures/{key}.figure.json')
        made.append(fig)
        interpretations[key] = dict(question=QUESTIONS[key], reading=reading,
                                    significance=significance, limitation=limitation)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.3), layout='constrained')
    for col, seed in enumerate(colors):
        for memory, marker in (('A', 'o'), ('B', 's')):
            points = [r for r in centers if r['seed'] == seed]
            axes[0, col].scatter([r[memory+'_x'] for r in points], [r[memory+'_y'] for r in points], marker=marker, label=memory)
            labels = {}
            for r in points:
                labels.setdefault((r[memory+'_x'], r[memory+'_y']), []).append(str(r['endpoint']))
            for position, indices in labels.items():
                axes[0, col].annotate(memory+','.join(indices), position,
                                     xytext=(4, 6 if memory == 'A' else -12), textcoords='offset points', fontsize=8)
        axes[0, col].set(title=seed, xlabel='Internal Bloch x', ylabel='Internal Bloch y', xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))
        axes[0, col].legend()
        for record in (1, 2, 3):
            chosen = [r for r in records if r['seed'] == seed and r['bits'] == '96' and r['record'] == str(record)]
            axes[1, col].plot([int(r['endpoint']) for r in chosen], [float(r['readout_center']) for r in chosen], '-o', label=f'r{record}')
        axes[1, col].set(xlabel='Ordered endpoint (odd A, even B)', ylabel='Nominal local record')
        axes[1, col].legend()
    save(fig, 'internal-records', ['internal-endpoints.csv', 'record-budgets.csv'],
         'Top: reference memory projections, labelled by endpoint. Bottom: the three active-event records; their event label alternates A/B.',
         'Internal motion and local predictability are separate questions. These centers give intuition; the budget figure supplies the certificate.',
         'Illustrative projection, not physical space or a within-gate path. Different events are different measurements, so connecting points does not define a continuous detector trace.')
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), layout='constrained')
    for ax, seed in zip(axes, colors):
        chosen = [r for r in majorants if r['seed'] == seed and r['bits'] == '96']
        ax.semilogy([int(r['endpoint']) for r in chosen], [float(r['tangent_norm_upper']) for r in chosen], '-o', color='black', label='Full response norm upper')
        for record in (1, 2, 3):
            rs = [r for r in records if r['seed'] == seed and r['bits'] == '96' and r['record'] == str(record)]
            ax.semilogy([int(r['endpoint']) for r in rs], [float(r['K']) for r in rs], '-o', label=f'Reference r{record} row norm upper')
        ax.set(title=seed, xlabel='Ordered endpoint', ylabel='Enclosed response/record norm')
        ax.legend(fontsize=8)
    save(fig, 'amplification-sensitivity', ['record-budgets.csv', 'tube-majorants.csv'],
         'The full18x16 response bound includes beta, its difference from the reference product. Each reference record row is the stored gradient contracted with that product; all sixteen initial directions remain present.',
         'A record observes a projection of the full response. Multiplying a global state bound by a global detector norm can lose this information.',
         'Diagnostic upper bounds with different observation normalization, not measured singular amplification or a standalone nonlinear certificate. Only saved endpoints are covered.')
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), layout='constrained')
    for ax, seed in zip(axes, colors):
        for bits, style in (('96', '-o'), ('128', '--s')):
            for field in ('preparation', 'total'):
                chosen = [r for r in records if r['seed'] == seed and r['bits'] == bits]
                ns = sorted({int(r['endpoint']) for r in chosen})
                ax.semilogy(ns, [max(float(r[field]) for r in chosen if int(r['endpoint']) == n) for n in ns], style,
                            label=f'{bits}-bit {field}', markersize=5)
        ax.axhline(.00025, color='#ad5555', ls=':', label='Each allocation2.5e-4')
        ax.axhline(.001, color='black', ls=':', label='Total1e-3')
        ax.set(title=seed, xlabel='Ordered endpoint', ylabel='Maximum record bound')
        ax.legend(fontsize=7)
    save(fig, 'certified-budgets', ['record-budgets.csv'],
         'Each point is the worst of the three records at that endpoint. Both precisions are independently checked; preparation and total can visually coincide.',
         'Shows the finite prefix supported under the unchanged allocations. Read the saved per-record horizons; an unproved suffix never extends a prefix.',
         'Evidentiary upper bounds for this specified mathematical circuit and preparation ball. No unrun endpoint, physical detector noise or32-cycle result is plotted.')
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), layout='constrained')
    for ax, seed in zip(axes, colors):
        for bits, style in (('96', '-o'), ('128', '--s')):
            chosen = [r for r in records if r['seed'] == seed and r['bits'] == bits]
            ns = sorted({int(r['endpoint']) for r in chosen})
            for field in ('linear', 'remainder', 'numerical', 'readout'):
                ax.semilogy(ns, [max(float(r[field]) for r in chosen if int(r['endpoint']) == n) for n in ns], style,
                            label=f'{bits} {field}', markersize=4)
        ax.set(title=seed, xlabel='Ordered endpoint', ylabel='Maximum separate contribution')
        ax.legend(fontsize=6.7, ncol=2)
    save(fig, 'obstruction-precision', ['record-budgets.csv', 'tube-majorants.csv', 'summary.json'],
         'Compare linear sensitivity, nonlinear remainder, numerical propagation and scalar readout at both precisions. Full-domain Hessians and tube radii are saved in the companion table.',
         'Distinguishes an arithmetic-width problem from conservative nonlinear transport. Precision alone cannot cure a large curvature remainder or an unqualified cost model.',
         'Diagnostic decomposition of upper bounds. Large upper bounds are not physical counterexamples. The long-prefix cost projection remains unmeasured.')
    write_json(output/'interpretations.json', interpretations)
    metrics = summary['worker_metrics']
    largest = max((float(r['preparation']) for r in records), default=None)
    paragraphs = [
        f"Qualification classification: {analysis['classification']}. Common certified horizon: {summary['common_endpoint_horizon']} ordered endpoints / {summary['common_endpoint_horizon']//2} full AB cycles.32-cycle confirmation: BLOCKED / NOT EVALUATED.",
        ('All covered preparation bounds are below2.85e-6, against allocation2.5e-4; the full preparation ball is covered.'
         if largest is not None and largest < 2.85e-6 else
         'Read the per-record budget table for the actual proved prefix; missing or excessive bounds remain unresolved.'),
        'Question: Does doubling the existing prefix reveal excessive bound growth or clarify the conservative cost obstruction? This is a predeclared two-cycle qualification, not a32-cycle confirmation.',
        'The unchanged CandidateA law couples three coherent complex doublets to two projector memories. A uses ports1/2 and memoryA; B uses ports2/3 and memoryB. Coupling is exact pi/2, lambda=0, transports identity. All variables and gate parameters are dimensionless.',
        'The squared physical discrepancy is the sum of squared wave norms plus half the sum of squared projector Frobenius norms. The preparation ball has radius1e-6 in that norm. Its chart retains12 real wave directions and2 memory directions each. The ambient proof transports18 coordinates; it does not reset at event switches.',
        'At each active event, r1=zi-dagger P zi, r2=zj-dagger P zj, r3=(zi-zj)-dagger P(zi-zj). Preparation, numerical and readout bounds each have allocation2.5e-4; exact-law omitted error is0. Total allocation is1e-3. Taylor remainders belong to preparation.',
        'The mechanism: propagate the full initial response and all accumulated nonlinear and rounding forcing. Contract record gradients against that response before taking norms. A large state response need not mean a large local readout error.',
        'Each source/tube/curvature/transition/readout obligation is reconstructed from saved proof objects.96-bit and128-bit arithmetic independently enclose the quantities. Floating DOP853 agreement is a diagnostic only. The checker shares the qualified dyadic/local-gate kernel and analytic chart theorem; it is not a formal proof assistant.',
        f"Measured worker CPU {metrics['worker_cpu_seconds']:.3f}s; wall {metrics['worker_wall_seconds']:.3f}s; RSS {metrics['rss_bytes']}bytes ({metrics['rss_measurement']}). Missing supervisor process metrics remain unavailable, never zero.",
        'Budget: original pilot reservations60s, this qualification45s, remaining confirmation195s (worker145 + saved checker50); total ceiling300 CPU/wall seconds. Scientific output reservations16+16+96MiB=128MiB. Failed stages do not refund reservations.',
        'The same conservative cost model is recalibrated at four endpoints. CPU/wall project the complete measured per-seed producer/checker cost with a quadratic intact-product count and2x safety; memory scales16x. This is neither a measured32-cycle run nor a rigorous runtime bound.',
        'Admission blockers: '+('; '.join(summary['blockers']) or 'none')+'. No confirmation command or lock is supplied.',
        'Strongest result is the independently reconstructed finite endpoint horizon listed above. No actual failing perturbation was sought. Unclosed upper bounds or cost admission mean unresolved feasibility, not a physical robustness failure.',
        'No within-gate or all-time conclusion, stable object, autonomous clock, emergent metric or transfer to CandidateB follows. Tests1-11 and the earlier linked-memory fail/unresolved classification remain unchanged.',
        f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; committed scientific source {manifest['code_identity']['revision']}."
    ]
    lines = ['# C1 two-cycle qualification']+paragraphs
    for key, parts in interpretations.items():
        lines += [key]+[k.title()+': '+v for k, v in parts.items()]
    (output/'report.md').write_text('\n\n'.join(lines)+'\n')
    (output/'report.html').write_text('<html><meta charset="utf-8"><pre style="white-space:pre-wrap">'+html.escape('\n\n'.join(lines))+'</pre></html>')
    with PdfPages(output/'report.pdf') as pdf:
        for start in range(0, len(paragraphs), 4):
            page = plt.figure(figsize=(8.5, 11))
            page.text(.08, .95, 'C1 | Two-cycle qualification', fontsize=16, weight='bold', va='top')
            content = '\n\n'.join('\n'.join(textwrap.wrap(p, 87)) for p in paragraphs[start:start+4])
            page.text(.08, .89, content, fontsize=10, va='top', linespacing=1.35)
            pdf.savefig(page)
            plt.close(page)
        for key, fig in zip(interpretations, made):
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
    return dict(required_inputs=[analysis['raw_source'], f"{analysis['path']}/checks.json",
                f"{analysis['path']}/derived/summary.json", f"{analysis['path']}/derived/record-budgets.csv",
                f"{analysis['path']}/derived/tube-majorants.csv"], figure_specs=specs, interpretations='interpretations.json')
