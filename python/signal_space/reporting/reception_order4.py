"""Question-led figures and exact plot data for the locked fourth-order run."""
import csv
import html
import shutil
import textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from signal_space.runtime.io import read_json, write_json


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    source=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figs=report_path/'figures'
    plots.mkdir();figs.mkdir()
    for item in source.iterdir():shutil.copy2(item,plots/item.name)
    summary=read_json(plots/'summary.json'); figures=[];interpretations={};specs=[]
    with (plots/'traces.csv').open() as handle:traces=list(csv.DictReader(handle))
    plt.rcParams.update({'font.size':10,'axes.spines.right':False,'axes.spines.top':False})
    def save(fig,key,question,reading,significance,limitation,sources,transforms):
        interpretations[key]={'question':question,'reading':reading,'significance':significance,'limitation':limitation}
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,
            'source_datasets':['plot-data/'+name for name in sources], 'transformations':transforms,
            'axes':{'x':{'unit':'as labeled'},'y':{'unit':'as labeled'}},'ranges':'shown on axes',
            'normalization':'c=hbar=m=1; cycles = radians/(2*pi)','downsampling':'all saved samples',
            'fit_window':None,'renderer':'matplotlib-'+matplotlib.__version__})
        for ext in ('png','svg','pdf'):fig.savefig(figs/f'{key}.{ext}',dpi=160 if ext=='png' else None)
        figures.append(fig);specs.append(f'figures/{key}.figure.json')
    diag=summary['prior_inspected_diagnostic'];fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    A=np.asarray([x['amplitude'] for x in diag]);r=np.asarray([x['actual_minus_second_at_fixed_nominal_markers'] for x in diag]);q=np.asarray([x['derived_fourth_at_fixed_nominal_markers'] for x in diag])
    axs[0].plot(A,r,'o-',label='saved residual');axs[0].plot(A,q,'s--',label='derived fourth order')
    axs[0].set(xlabel='incident coefficient A',ylabel='interval cycles',title='Inspected Test 7: diagnostic only');axs[0].legend()
    axs[1].plot(A,r/A**4,'o-',label='saved residual/A^4');axs[1].plot(A,q/A**4,'s--',label='derived coefficient')
    axs[1].set(xlabel='A',ylabel='cycles / A^4',title='No fitted response coefficient');axs[1].legend()
    save(fig,'prior-diagnostic','Does the derived fourth-order coefficient explain the inspected residual sign and scaling?',
        'Compare the saved Test 7 amplitude ladder at the same nominal A=.004 marker times.',
        'This diagnoses the missing order independently of a fitted coefficient.',
        'The prior histories and marker times were already inspected; this is not a prospective prediction.',
        ['summary.json'],['formal Taylor coefficient times A^4; fixed nominal A=.004 markers from old receiver'])
    fig,axs=plt.subplots(2,1,figsize=(11,7),layout='constrained')
    for grid in ('base','fine','finer'):
        d=[x for x in traces if x['grid']==grid];t=np.array([float(x['time']) for x in d]);
        if grid=='finer':
            for key,label in [('actual_cycles','held-out measured'),('second_cycles','second-order forecast'),('fourth_cycles','fourth-order forecast')]:
                axs[0].plot(t,[float(x[key]) for x in d],label=label)
        axs[1].plot(t,[float(x['actual_cycles'])-float(x['fourth_cycles']) for x in d],label=grid)
    axs[0].set(ylabel='matched phase offset (cycles)',title='New waveform: local quadrature record');axs[0].legend()
    axs[1].set(xlabel='local time (m^-1)',ylabel='actual - fourth (cycles)',title='Full residual across meshes');axs[1].legend()
    save(fig,'heldout-phase','Does the locked fourth-order prediction improve a new local clock history?',
        f"Held-out finest trace error: second {summary['heldout']['finer'][0]['trace2_relative']:.4%}, fourth {summary['heldout']['finer'][0]['trace4_relative']:.4%}.",
        'A separate waveform tests the coefficient after the inspected-history diagnostic.',
        'Quiet phase at the pulse markers is counterfactual; grid differences and inversion error remain.',
        ['traces.csv','summary.json'],['matched quiet subtraction; exact quadrature Taylor expansion; no fit'])
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    d=[x for x in traces if x['grid']=='finer'];t=np.array([float(x['time']) for x in d])
    axs[0].plot(t,[abs(float(x['local_a'])) for x in d],label='receiver')
    axs[0].plot(t,[abs(float(x['predicted_a'])) for x in d],label='surface forecast')
    axs[0].axhline(1e-4,ls=':',color='black');axs[0].set(xlim=(10,65),xlabel='time (m^-1)',ylabel='|a| (m)',title='Local threshold events');axs[0].legend()
    cases=summary['heldout']['finer'][0]
    reference=np.array(cases['marker_actual_hermite'])
    for name,style in [('marker_actual_linear','o'),('marker_decimated_linear','v'),('marker_decimated_hermite','^'),
                        ('marker_pred_linear','s'),('marker_pred_hermite','+')]:
        val=cases[name]
        if val:axs[1].scatter([0,1],np.array(val)-reference,marker=style,label=name.replace('marker_','').replace('_',' '))
    axs[1].axhline(0,color='black',lw=.7)
    axs[1].set(xticks=[0,1],xticklabels=['first rise','last fall'],ylabel='timing minus fine actual Hermite (m^-1)',
               title='Magnified timing residual on h=0.025');axs[1].legend(fontsize=7)
    inv=summary['inversion_control']
    # Coarse optical and vacuum inverse errors are recorded numerically in summary.json,
    # since placing different-grid coordinates on this finer-grid residual plot misleads.
    save(fig,'marker-reconstruction','Do derivative-informed markers and twice-frequent output explain local timing error?',
        f"On h=.025, compare markers at 0.05 and decimated 0.1; coarse vacuum/known-Z maximum errors are {inv['vacuum_max_error']:.5f}/{inv['known_Z_max_error']:.5f}.",
        'Separates temporal interpolation from surface-propagation error.',
        'The coarse vacuum control is post-hoc; Hermite cannot repair spatial dispersion or WKB error.',
        ['traces.csv','summary.json'],['linear threshold crossings; cubic Hermite with local a_t; decimate .05 to .1'])
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Test 7 fourth-order follow-up','',f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
        'Unchanged SS OCF 1 action and Test 6 clock calibration. Original Test 7 remains failed.',
        'Prior Test 7 comparison is an inspected-data diagnostic; held-out wave is the prospective check.',
        'No two-object recoil, coordinate invariance, gravity, angular stability, or emergent spacetime is tested.',
        '',f"Held-out interval: actual {cases['actual']:.9e}; order-two {cases['order2']:.9e}; order-four {cases['order4']:.9e} cycles.",
        f"Numerical interval budget {summary['numerical_budget_cycles']:.3e} cycles.",'']
    lines += [f'{k}: {v}' for k,v in summary['checks'].items()]
    for key,value in interpretations.items():lines += ['',key]+[f'{k.title()}: {v}' for k,v in value.items()]
    md='\n'.join(lines)+'\n';(report_path/'report.md').write_text(md)
    (report_path/'report.html').write_text('<!doctype html><meta charset="utf-8"><pre>'+html.escape(md)+'</pre>'+''.join(f'<img width="900" src="figures/{k}.svg">' for k in interpretations))
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[x for line in lines for x in (textwrap.wrap(line,100) or [''])]
        for offset in range(0,len(wrapped),42):
            fig=plt.figure(figsize=(8.5,11));fig.text(.07,.95,'Test 7: fourth-order response',fontsize=16,va='top');fig.text(.07,.90,'\n'.join(wrapped[offset:offset+42]),fontsize=8,va='top');pdf.savefig(fig);plt.close(fig)
        for fig in figures:pdf.savefig(fig);plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],f"{analysis['path']}/derived/summary.json",f"{analysis['path']}/checks.json"],
            'figure_specs':specs,'interpretations':'interpretations.json'}
