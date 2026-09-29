"""Question-driven report for the spatial embedding pilot."""
import csv
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from signal_space.runtime.io import read_json, write_json

LOCKED_QUESTIONS = {
    'spatial-embedding': 'Do the frozen radial data embed as distinct spatial cores?',
    'short-ledgers': 'Does the closed spatial scheme preserve energy and charge?',
    'quiet-local-trace': 'Is a short local clock field available in the naive quiet pair?',
}


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    derived = run_path/analysis['path']/'derived'
    plots = report_path/'plot-data'
    figs = report_path/'figures'
    plots.mkdir()
    figs.mkdir()
    for name in ('summary.json','traces.csv'):
        shutil.copy2(derived/name,plots/name)
    summary = read_json(plots/'summary.json')
    with (plots/'traces.csv').open(newline='') as stream:
        trace = list(csv.DictReader(stream))
    attempt = next(iter(sorted((run_path/'attempts').glob('attempt-*'))))
    for label in ('isolated-base','quiet-pair-base'):
        with np.load(attempt/'raw'/f'{label}.npz') as source:
            z = source['z'];core = source['initial_core'];rho = source['rho']
        with (plots/f'{label}-axial.csv').open('w',newline='') as stream:
            writer=csv.writer(stream);writer.writerow(('z','rho','phi_abs'))
            for i in range(len(rho)):
                for j in range(len(z)):
                    writer.writerow((float(z[j]),float(rho[i]),float(core[i,j])))
    specs=[]
    def save(fig, key, sources, question, reading, significance, limitation, axes, role='diagnostic'):
        spec={'schema_version':'research-figure-spec-v1','id':key,
              'source_datasets':[f'plot-data/{name}' for name in sources],
              'transformations':['direct saved samples; no fitted traces'],
              'axes':axes,'ranges':'shown on axes','normalization':'c=hbar=m=1',
              'downsampling':'none','fit_window':None,
              'renderer':f'matplotlib-{matplotlib.__version__}',
              'interpretation':{'question':question,'reading':reading,
                 'significance':significance,'limitation':limitation},'role':role}
        write_json(figs/f'{key}.figure.json',spec)
        for ext in ('png','svg','pdf'):
            fig.savefig(figs/f'{key}.{ext}',dpi=150 if ext=='png' else None)
        specs.append((key,fig,spec))
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,label in zip(axes,('isolated-base','quiet-pair-base')):
        rows=[]
        with (plots/f'{label}-axial.csv').open(newline='') as stream:
            rows=list(csv.DictReader(stream))
        rr=next(x['rho'] for x in rows)
        axial=[x for x in rows if x['rho']==rr]
        ax.plot([float(x['z']) for x in axial],[float(x['phi_abs']) for x in axial])
        ax.set(xlabel='z (m^-1)',ylabel='|Phi| (m)',title=label)
    save(fig,'spatial-embedding',['isolated-base-axial.csv','quiet-pair-base-axial.csv'],
         'Do the frozen radial data embed as distinct spatial cores?',
         'The initial axial cuts show one centered core and a pair centered at ±36.',
         'The initial two-center geometry is explicit and auditable.',
         'Superposition has not been jointly relaxed; this figure cannot establish quiet stability.',
         {'x':{'unit':'m^-1'},'y':{'unit':'m'}})
    fig,axes=plt.subplots(2,1,figsize=(10,6),layout='constrained')
    for case in summary['scenarios']:
        subset=[r for r in trace if r['scenario']==case['label']]
        t=np.array([float(r['t']) for r in subset]);e=np.array([float(r['energy']) for r in subset]);q=np.array([float(r['charge']) for r in subset]);
        axes[0].plot(t,(e-e[0])/e[0],label=case['label'])
        axes[1].plot(t,(q-q[0])/q[0],label=case['label'])
    axes[0].set(ylabel='(E-E0)/E0')
    axes[1].set(xlabel='time (m^-1)',ylabel='(Q-Q0)/Q0')
    axes[0].legend(fontsize=8)
    save(fig,'short-ledgers',['traces.csv','summary.json'],
         'Does the spatial scheme conserve closed-box energy and charge during the pilot?',
         'The directly recomputed Hamiltonian and charge drifts are displayed separately for each spatial grid.',
         'This checks the reciprocal field update and weighted face-energy implementation in a short run.',
         'Total energy includes core rest energy and cannot bound a small later receiver impulse; no open boundary flux is present.',
         {'x':{'unit':'m^-1'},'y':{'unit':'fraction'}},'evidentiary')
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    for label in ('quiet-pair-base','quiet-pair-fine'):
        subset=[r for r in trace if r['scenario']==label]
        ax.plot([float(r['t']) for r in subset],[float(r['chi_A']) for r in subset],label=f'{label} at A')
    ax.set(xlabel='time (m^-1)',ylabel='local chi (m)')
    ax.legend(fontsize=8)
    save(fig,'quiet-local-trace',['traces.csv'],
         'Is a local clock quadrature available in the naive quiet pair?',
         'The field at the innermost radial cell and A axial center oscillates for the short interval.',
         'This supplies a first numerical embedding diagnostic before joint-data relaxation.',
         'A sample trace is not a 100-period longevity or postinteraction survival test; spatial sampling errors are unbounded here.',
         {'x':{'unit':'m^-1'},'y':{'unit':'m'}},'diagnostic')
    checks=analysis['checks']['checks'] if 'checks' in analysis else read_json(run_path/analysis['path']/'checks.json')['checks']
    title='Test 8 spatial calibration pilot: unresolved full acceptance'
    md=[f'# {title}','',f"Model: {manifest['model_id']}; run: {manifest['run_id']}.",'',
        'The first 16 time units test numerical embedding and a quiet superposition. No Test 8 reception or recoil is claimed.','',
        '## Preregistered checks','']
    for check in checks:
        md.append(f"- {check['id']}: **{check['status']}** — {check.get('value', {})}")
    for key,_,spec in specs:
        i=spec['interpretation'];md.extend(['',f'## {key}','',
         f"Question: {i['question']}",f"Reading: {i['reading']}",
         f"Significance: {i['significance']}",f"Limitation: {i['limitation']}"])
    write_json(report_path/'interpretations.json',
               {key:{**spec['interpretation'],'question':LOCKED_QUESTIONS[key]}
                for key,_,spec in specs})
    (report_path/'report.md').write_text('\n'.join(md)+'\n', encoding="utf-8")
    (report_path/'report.html').write_text('<html><body><pre>'+__import__('html').escape('\n'.join(md))+'</pre></body></html>', encoding="utf-8")
    with PdfPages(report_path/'report.pdf') as pdf:
        for _,fig,_ in specs:
            pdf.savefig(fig)
            plt.close(fig)
    return {'required_inputs':[f"{analysis['path']}/derived/summary.json",
                               f"{analysis['path']}/derived/traces.csv",
                               f"{analysis['path']}/checks.json"],
            'figures':[f'figures/{name}.figure.json' for name,_,_ in specs],
            'plot_data':[f'plot-data/{name}' for name in ('summary.json','traces.csv','isolated-base-axial.csv','quiet-pair-base-axial.csv')]}
