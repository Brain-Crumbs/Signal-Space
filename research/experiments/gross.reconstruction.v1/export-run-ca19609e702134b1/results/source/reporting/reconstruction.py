"""Question-driven saved-data report for the linear reconstruction audit."""
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


def render_report(run_path,report_path,manifest,analysis,render_provenance):
    source=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figs=report_path/'figures'
    plots.mkdir();figs.mkdir()
    for f in source.iterdir():shutil.copy2(f,plots/f.name)
    summary=read_json(plots/'summary.json');specs=[];figures=[];interpretations={}
    with (plots/'traces.csv').open() as f:traces=list(csv.DictReader(f))
    with (plots/'singular.csv').open() as f:singular=list(csv.DictReader(f))
    values=lambda rows,key:np.asarray([float(row[key]) for row in rows])
    waves=('broad','carrier','new');h=np.array([.05,.025,.0125]);grids=('coarse','fine','finest')
    plt.rcParams.update({'font.size':9,'axes.spines.right':False,'axes.spines.top':False})
    def save(fig,key,question,reading,significance,limitation,data):
        interpretations[key]={'question':question,'reading':reading,'significance':significance,'limitation':limitation}
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,
            'source_datasets':['plot-data/'+x for x in data],'transformations':['direct saved history and event comparisons','SVD event coefficients','no fitting or extrapolation'],
            'axes':{'x':{'unit':'as labeled'},'y':{'unit':'as labeled'}},'ranges':'shown on axes',
            'normalization':'c=hbar=m=1; a=A*b/r with A=.012','downsampling':'all saved displayed samples','fit_window':None,
            'renderer':'matplotlib-'+matplotlib.__version__})
        for ext in ('png','svg','pdf'):fig.savefig(figs/f'{key}.{ext}',dpi=150 if ext=='png' else None)
        figures.append(fig);specs.append(f'figures/{key}.figure.json')
    fig,axes=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for col,wave in enumerate(waves):
        rows=[r for r in traces if r['case']=='finest-'+wave];t=values(rows,'time')
        m=summary['metrics']['finest-'+wave]['source_markers']
        for method in ('source','inverse','causal'):
            y=values(rows,method+'_a');axes[0,col].plot(t,y,label=method)
            axes[1,col].plot(t,y,label=method)
        axes[0,col].set(title=wave+' local field',xlabel='time (m^-1)',ylabel='a (m)')
        if m:
            axes[1,col].set(xlim=(m[1]-.12,m[1]+.12),ylim=(-1.3e-4,1.3e-4))
        for sign in (-1,1):axes[1,col].axhline(sign*1e-4,color='black',ls=':',lw=.7)
        axes[1,col].set(title='Source last-event neighborhood',xlabel='time (m^-1)',ylabel='a (m)')
        axes[0,col].legend(fontsize=8)
    save(fig,'local-reconstruction','How do the inverse and causal surface capture reproduce the local waveform and its late tail?',
        'The main pulses overlap closely. Near the source last event, the inverse has a small ripple while finite causal capture has rapid ringing. Its last event moves by 4.01 to 7.33 time units on the finest grid.',
        'A close overall waveform can still produce a sensitive late threshold time.',
        'Causal capture uses an extra neighboring surface site. The known-source curve is a downstream audit; no nonlinear clock is evolved.', ['traces.csv','summary.json'])
    fig,axes=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for col,wave in enumerate(waves):
        for event in ('first','last'):
            rows=[r for r in singular if r['case']=='finest-'+wave and r['event']==event]
            x=values(rows,'index');s=values(rows,'relative_singular_value');c=abs(values(rows,'event_field_coefficient'))
            if event=='first':axes[0,col].semilogy(x,np.maximum(s,1e-18))
            axes[1,col].semilogy(x,np.maximum(c,1e-18),label=event)
        rank=summary['metrics']['finest-'+wave]['rank']
        axes[0,col].axhline(1e-10,color='red',ls='--');axes[0,col].axvline(rank,color='gray',ls=':')
        axes[0,col].set(title=wave+' surface singular spectrum',xlabel='singular index',ylabel='sigma / sigma_max')
        axes[1,col].axvline(rank,color='gray',ls=':');axes[1,col].legend()
        axes[1,col].set(xlabel='singular index',ylabel='absolute local event field coefficient',title='Event sensitivity in the same directions')
    save(fig,'singular-observability','Which surface singular directions remain relevant to each local event?',
        'The inverse retains 451 of 641 directions. Discarded directions have almost no first-event coefficient, while substantial last-event coefficients persist beyond the cutoff. Surface-consistent finite witnesses move the last event by over 11 time units.',
        'Observability depends on interior sensitivity as well as the size of the surface singular value.',
        'The norm radii and surface tolerance are declared conditional assumptions; root linearization is checked with finite witnesses but is not a global event theorem.', ['singular.csv','summary.json'])
    fig,axes=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for col,wave in enumerate(waves):
        for j,event in enumerate(('first','last')):
            ax=axes[j,col];b=summary['event_budgets'][wave].get(event)
            if not b:ax.text(.1,.5,'Missing event: unresolved');continue
            row=summary['metrics']['finest-'+wave]
            labels=['inverse error','capture error','capture budget','target']
            vals=[abs(row['inverse_residual'][j]),b['error'],b['total'],b['target']]
            ax.bar(range(4),np.maximum(vals,1e-16));ax.set(yscale='log',xticks=range(4),xticklabels=labels,
                title=wave+' / '+event,ylabel='absolute time (m^-1)');ax.tick_params(axis='x',rotation=20)
    save(fig,'event-budgets','Are first and last reconstruction errors separately below their uncertainty budgets?',
        'All three causal first events meet the 1e-4 target and their separate budgets. Every last-event budget exceeds that target; inverse last-event errors are 1.49e-3 to 3.51e-3.',
        'Tests a strict reconstruction prerequisite with target 1e-4 time units, preserving the original Test 7 thresholds.',
        'Budgets are direct difference estimates. They measure reconstruction residuals; absolute continuum event shifts and nonlinear phase acceptance are separate.', ['summary.json'])
    fig,axes=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for col,wave in enumerate(waves):
        for method in ('source','inverse','causal'):
            for j,event in enumerate(('first','last')):
                times=[summary['metrics'][grid+'-'+wave][method+'_markers'] for grid in grids]
                if all(x is not None for x in times):
                    shifts=abs(np.diff([x[j] for x in times]))
                    axes[j,col].loglog(h[:-1],np.maximum(shifts,1e-16),'o-',label=method+' mesh change')
                sample=summary['metrics']['finest-'+wave]['output_sampling'][method]
                if sample:axes[j,col].scatter([h[-1]],[max(sample[j],1e-16)],marker='x')
        for j,event in enumerate(('first','last')):
            axes[j,col].set(title=wave+' / '+event,xlabel='coarser h; x = finest output sampling',ylabel='absolute event change (m^-1)')
            axes[j,col].legend(fontsize=7)
    save(fig,'sampling-continuum','How much do sampling and mesh changes move each event?',
        'First-event mesh shifts remain 0.043 to 0.081 despite excellent same-mesh reconstruction. Last-event convergence is uneven; the broad causal last event moves 0.209 under output decimation.',
        'Separates absolute event convergence from agreement between source and reconstruction on one grid.',
        'The h=0.0125 source is not an exact continuum reference. Surface-sampling and independent time/domain components are also retained in the saved budgets.', ['summary.json'])
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Test 7: bounded reconstruction and event timing','',
        f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
        'No nonlinear receiver or new clock-phase forecast was executed. Original Test 7 remains failed and Test 8 remains blocked.','']
    lines += [f"{k}: {v}" for k,v in summary['checks'].items()]
    for wave,budgets in summary['event_budgets'].items():
        for event,b in budgets.items():lines.append(f"{wave} {event}: causal error {b['error']:.6e}; budget {b['total']:.6e}; target {b['target']:.1e} inverse-mass units.")
    for key,item in interpretations.items():lines+=['',key]+[f'{k.title()}: {v}' for k,v in item.items()]
    md='\n'.join(lines)+'\n';(report_path/'report.md').write_text(md)
    (report_path/'report.html').write_text('<!doctype html><meta charset="utf-8"><pre>'+html.escape(md)+'</pre>'+''.join(f'<img width="900" src="figures/{k}.svg">' for k in interpretations))
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[x for line in lines for x in (textwrap.wrap(line,100) or [''])]
        for offset in range(0,len(wrapped),44):
            page=plt.figure(figsize=(8.5,11));page.text(.07,.96,'Test 7 reconstruction audit',fontsize=16,va='top')
            page.text(.07,.91,'\n'.join(wrapped[offset:offset+44]),fontsize=8,va='top');pdf.savefig(page);plt.close(page)
        for fig in figures:pdf.savefig(fig);plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],f"{analysis['path']}/derived/summary.json",f"{analysis['path']}/checks.json"],
            'figure_specs':specs,'interpretations':'interpretations.json'}
