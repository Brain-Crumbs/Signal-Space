"""Saved-data figures and interpreted report for the causal interface audit."""
import csv
import html
import shutil
import textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from signal_space.runtime.io import read_json,write_json


def render_report(run_path,report_path,manifest,analysis,render_provenance):
    source=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figs=report_path/'figures'
    plots.mkdir();figs.mkdir()
    for path in source.iterdir():shutil.copy2(path,plots/path.name)
    summary=read_json(plots/'summary.json');interpretations={};figures=[];specs=[]
    with (plots/'traces.csv').open() as f:traces=list(csv.DictReader(f))
    with (plots/'drives.csv').open() as f:drives=list(csv.DictReader(f))
    waves=('broad','carrier','new');values=lambda rows,key:np.asarray([float(x[key]) for x in rows])
    plt.rcParams.update({'font.size':9,'axes.spines.right':False,'axes.spines.top':False})
    def save(fig,key,q,reading,meaning,limit,data):
        interpretations[key]={'question':q,'reading':reading,'significance':meaning,'limitation':limit}
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,'source_datasets':['plot-data/'+x for x in data],
            'transformations':['direct saved traces and differences','no fitted coefficients or extrapolation'],
            'axes':{'x':{'unit':'as labeled'},'y':{'unit':'as labeled'}},'ranges':'shown on axes','normalization':'c=hbar=m=1; a=.012*b/.1',
            'downsampling':'all saved samples in plotted range','fit_window':None,'renderer':'matplotlib-'+matplotlib.__version__})
        for ext in ('png','svg','pdf'):fig.savefig(figs/f'{key}.{ext}',dpi=150 if ext=='png' else None)
        figures.append(fig);specs.append(f'figures/{key}.figure.json')
    fig,axes=plt.subplots(3,3,figsize=(12,9),layout='constrained')
    for col,wave in enumerate(waves):
        rows=[x for x in traces if x['wave']==wave];t=values(rows,'time');row=summary['metrics']['finest-'+wave]
        for method in ('source','full','short','no_memory'):
            for ax in axes[:,col]:ax.plot(t,values(rows,method),label=method,lw=1)
        pair=row['methods']['source']['events']
        if pair:
            for ax in axes[:,col]:
                for mark in pair:ax.axvline(mark,color='black',ls=':',lw=.6)
            for j,mark in enumerate(pair,1):
                ax=axes[j,col];window=(t>=mark-.03)&(t<=mark+.03)
                visible=np.concatenate([values(rows,m)[window] for m in ('source','full','short','no_memory')])
                lo=min(float(visible.min()),-1e-4);hi=max(float(visible.max()),1e-4);pad=.1*(hi-lo)
                ax.set(xlim=(mark-.03,mark+.03),ylim=(lo-pad,hi+pad))
                ax.axhline(1e-4,color='gray',ls='--',lw=.6);ax.axhline(-1e-4,color='gray',ls='--',lw=.6)
        axes[0,col].set(title=wave+' local history',xlabel='time (m^-1)',ylabel='a (m)');axes[0,col].legend(fontsize=7)
        axes[1,col].set(title='First rise: event neighborhood',xlabel='time (m^-1)',ylabel='a (m)')
        axes[2,col].set(title='First fall: event neighborhood',xlabel='time (m^-1)',ylabel='a (m)')
    err=max(r['methods']['full']['relative_waveform_error'] for r in summary['metrics'].values())
    save(fig,'boundary-local','Does retained exterior memory reproduce the local waveform and prospective events?',
        f'Complete-acquisition maximum relative waveform error is {err:.3e}. Finest no-memory errors are 1.0005 to 1.0017. Source, full and cutoff traces nearly overlap; separate budgets resolve their small differences.',
        'Retaining exterior response removes the large truncation error. The cutoff control retains memory and therefore does not repeat the earlier abrupt state projection.',
        'The source and predictor share their frozen linear discretization. No nonlinear clock response or measured laboratory noise is included.', ['traces.csv','summary.json'])
    fig,axes=plt.subplots(2,3,figsize=(12,6),layout='constrained')
    for col,wave in enumerate(waves):
        ax=axes[0,col]
        rows=[x for x in drives if x['wave']==wave];t=values(rows,'time')
        for key in ('measured_exterior','exterior_response','incoming_drive'):ax.plot(t,values(rows,key),label=key)
        ax.axvline(16,color='black',ls=':');ax.set(title=wave,xlabel='time (m^-1)',ylabel='boundary b');ax.legend(fontsize=7)
        ax=axes[1,col];ax.plot(t,values(rows,'incoming_drive'),color='tab:green')
        ax.axvline(16,color='black',ls=':');ax.set(title='Free drive on its own scale',xlabel='time (m^-1)',ylabel='boundary b')
    save(fig,'boundary-drive','How much of the surface field is incoming drive versus exterior response?',
        'The measured exterior node is split into the causal response to the interior surface and the remaining free exterior drive. Their subtraction leaves a much smaller drive, shown separately. The dotted line marks cutoff 16.',
        'Shows the information that a boundary-memory method must retain or independently acquire.',
        'This decomposition assumes the registered frozen exterior operator and initially empty interior. The entire primary surface history extends to 60.', ['drives.csv'])
    fig,axes=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for col,wave in enumerate(waves):
        for j,event in enumerate(('rise','fall')):
            ax=axes[j,col];row=summary['budgets'][wave].get(event)
            if row is None:ax.text(.1,.5,'Missing event: unresolved');continue
            vals=[row['error'],row['budget'],row['target']]
            ax.bar(['replay error','error budget','target'],np.maximum(vals,1e-16))
            ax.set(yscale='log',title=wave+' / '+event,ylabel='absolute time (m^-1)')
    save(fig,'boundary-budgets','Do both prospective events meet their separate reconstruction budgets?',
        'The locked prospective-event classification is '+summary['checks']['prospective-events']+'. Bars compare finest same-grid residuals with the full direct-difference budget and 1e-4 target.',
        'Prevents tiny same-grid differences from being mistaken for independently resolved event predictions.',
        'These are linear interface residual budgets. Absolute continuum shifts and nonlinear phase uncertainty require their own checks.', ['summary.json'])
    fig,axes=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for col,wave in enumerate(waves):
        for j,event in enumerate(('rise','fall')):
            ax=axes[j,col]
            for method in ('source','full'):
                times=[summary['metrics'][g+'-'+wave]['methods'][method]['events'] for g in ('coarse','fine','finest')]
                if all(x is not None for x in times):ax.loglog([.05,.025],np.maximum(abs(np.diff([x[j] for x in times])),1e-16),'o-',label=method+' mesh shift')
            budget=summary['budgets'][wave].get(event)
            if budget:
                ax.scatter([.0125],[max(budget['components']['output_sampling'],1e-16)],marker='x',label='output sampling')
                ax.scatter([.0125],[max(budget['components']['surface_sampling'],1e-16)],marker='+',label='surface sampling')
            ax.set(title=wave+' / '+event,xlabel='coarser h / finest sample controls',ylabel='event change (m^-1)');ax.legend(fontsize=7)
    save(fig,'boundary-convergence','Do absolute event shifts and sampling changes converge independently of replay agreement?',
        'The locked absolute-event convergence classification is '+summary['checks']['event-convergence']+' and sampling is '+summary['checks']['sampling']+'. Mesh changes use independently solved profiles.',
        'Separates accuracy of boundary replay on a fixed grid from the continuum event limit.',
        'The three spatial resolutions and difference budgets are finite numerical evidence. No extrapolated continuum event is claimed.', ['summary.json'])
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Test 7 causal boundary memory','',f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
        'Linear prerequisite only. No new nonlinear clock forecast; Test 7 acceptance remains pending and Test 8 blocked.','',
        'Primary protocol: full two-site acquisition to 60, causal exterior memory, first complete local threshold excursion.',
        'Cutoff at16 and historical last-crossing markers are retained as diagnostics.','']
    lines += [f'{k}: {v}' for k,v in summary['checks'].items()]
    for wave,records in summary['budgets'].items():
        for event,row in records.items():lines.append(f"{wave} {event}: error={row['error']:.6e}; budget={row['budget']:.6e}; target=1e-4.")
    for key,item in interpretations.items():lines+=['',key]+[f'{k.title()}: {v}' for k,v in item.items()]
    md='\n'.join(lines)+'\n';(report_path/'report.md').write_text(md, encoding="utf-8")
    (report_path/'report.html').write_text('<!doctype html><meta charset="utf-8"><pre>'+html.escape(md)+'</pre>'+''.join(f'<img width="900" src="figures/{k}.svg">' for k in interpretations), encoding="utf-8")
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[x for line in lines for x in (textwrap.wrap(line,100) or [''])]
        for off in range(0,len(wrapped),42):
            page=plt.figure(figsize=(8.5,11));page.text(.07,.96,'Test 7 causal boundary memory',fontsize=16,va='top')
            page.text(.07,.91,'\n'.join(wrapped[off:off+42]),fontsize=8,va='top');pdf.savefig(page);plt.close(page)
        for fig in figures:pdf.savefig(fig);plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],f"{analysis['path']}/derived/summary.json",f"{analysis['path']}/checks.json"],
        'figure_specs':specs,'interpretations':'interpretations.json'}
