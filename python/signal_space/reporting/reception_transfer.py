"""Saved-data figures for the discrete-transfer discriminator."""
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
    source=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figs=report_path/'figures';plots.mkdir();figs.mkdir()
    for f in source.iterdir():shutil.copy2(f,plots/f.name)
    s=read_json(plots/'summary.json');interpretations={};figures=[];specs=[]
    def read(name):
        with (plots/name).open() as f:return list(csv.DictReader(f))
    traces=read('traces.csv');surfaces=read('surface.csv');profiles=read('profiles.csv')
    plt.rcParams.update({'font.size':10,'axes.spines.right':False,'axes.spines.top':False})
    def values(rows,key):return np.asarray([float(r[key]) for r in rows])
    def save(fig,key,question,reading,significance,limitation,datasets):
        interpretations[key]={'question':question,'reading':reading,'significance':significance,'limitation':limitation}
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,'source_datasets':['plot-data/'+x for x in datasets],
            'transformations':['matched quiet quadrature phase in cycles','Hermite threshold markers','direct differences, no extrapolation or fit'],
            'axes':{'x':{'unit':'as labeled'},'y':{'unit':'as labeled'}},'ranges':'shown on axes','normalization':'c=hbar=m=1',
            'downsampling':'all plotted saved samples','fit_window':None,'renderer':'matplotlib-'+matplotlib.__version__})
        for ext in ('png','svg','pdf'):fig.savefig(figs/f'{key}.{ext}',dpi=160 if ext=='png' else None)
        figures.append(fig);specs.append(f'figures/{key}.figure.json')
    fig,ax=plt.subplots(3,2,figsize=(11,9),layout='constrained')
    for col,wave in enumerate(('broad','carrier')):
        ss=[x for x in surfaces if x['waveform']==wave];d=[x for x in traces if x['case']=='finest-'+wave]
        ax[0,col].plot(values(ss,'time'),values(ss,'a'));ax[0,col].set(title=wave+' surface record',xlabel='time (m^-1)',ylabel='a at r=14 (m)')
        for key,label in [('actual_a','receiver'),('predicted_a','surface forecast')]:ax[1,col].plot(values(d,'time'),values(d,key),label=label)
        ax[1,col].set(xlabel='time (m^-1)',ylabel='a at r=0.1 (m)');ax[1,col].legend(fontsize=8)
        for key,label in [('actual_cycles','receiver'),('second_cycles','order 2'),('fourth_cycles','order 4')]:ax[2,col].plot(values(d,'time'),values(d,key),label=label)
        ax[2,col].set(xlabel='time (m^-1)',ylabel='matched phase (cycles)');ax[2,col].legend(fontsize=8)
    save(fig,'surface-transfer','Can an external record determine the local neutral and clock histories?',
        'Each column follows a different recorded spectrum from r=14 to r=0.1, at A=.012.',
        'The prediction uses a discrete initial-data inverse and derived response coefficients.',
        'Synthetic acquisition assumes exact support and v=D_h b; this is not an unknown-source detector.', ['surface.csv','traces.csv'])
    fig,ax=plt.subplots(1,3,figsize=(12,4),layout='constrained')
    for grid in ('fine','finer','finest','frozen'):
        d=[x for x in profiles if x['grid']==grid]
        ax[0].plot(values(d,'r'),values(d,'phi'),label=grid)
        ax[1].plot(values(d,'r'),values(d,'Z')-1,label=grid)
    grids=('base','fine','finer','finest');h=np.array([.1,.05,.025,.0125]);e=np.array([s['profiles'][k]['eigenvalues'][0] for k in grids])
    ax[2].loglog(h[:-1],abs(np.diff(e)),'o-');ax[2].set(xlabel='coarser h (m^-1)',ylabel='adjacent eigenvalue change (m^2)',title='Independent clock eigenproblem')
    ax[0].set(xlabel='r (m^-1)',ylabel='core amplitude (m)',title='Same omega_Q branch');ax[0].legend(fontsize=8)
    ax[1].set(xlabel='r (m^-1)',ylabel='Z - 1',title='Both inertia and stiffness use Z')
    save(fig,'profile-convergence','Does independent radial calibration converge beyond the old interpolated profile?',
        'Profiles are independently solved and frozen at each mesh; frozen denotes the earlier interpolated fine profile.',
        'Separates a refined physical preparation from merely interpolating old samples.',
        'The calibrated readout frequency stays fixed; this does not repeat the 100-period longevity test.', ['profiles.csv','summary.json'])
    fig,ax=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    for col,wave in enumerate(('broad','carrier')):
        b=s['budgets'][wave]
        if 'components' not in b:
            ax[0,col].text(.2,.5,'Missing markers: unresolved');continue
        parts=b['components'];ax[0,col].bar(range(len(parts)),list(parts.values()));ax[0,col].set(xticks=range(len(parts)),xticklabels=list(parts),ylabel='absolute interval error (cycles)',title=wave+' budget')
        ax[0,col].tick_params(axis='x',rotation=25)
        ax[0,col].axhline(b['maximum_discrimination_budget'],color='red',ls='--',label='order separation / 4');ax[0,col].legend(fontsize=8)
        audit=s.get('forecast_convergence_audit',{}).get(wave,{})
        labels=['order 2 error','order 4 error','locked budget','audit budget','order separation'];vals=[b['second_error'],b['fourth_error'],b['total'],audit.get('forecast_inclusive_budget',b['total']),b['order_separation']]
        bars=ax[1,col].bar(range(5),vals);bars[3].set_hatch('//')
        ax[1,col].set(xticks=range(5),xticklabels=labels,yscale='log',ylabel='cycles',title='Registered order gate resolved' if b['resolved'] and b['converged'] else 'Registered order gate unresolved')
        ax[1,col].tick_params(axis='x',rotation=20)
    save(fig,'order-budget','Is the fourth-order improvement larger than every declared uncertainty?',
        'Compare both errors with the locked budget. The hatched post-hoc audit also includes convergence of the forecast itself.',
        'A fourth-order claim requires sufficient resolution on both spectra; the ordinary 5% gate is insufficient.',
        'The audit cannot promote or rewrite a locked check. Budgets are difference estimates, not rigorous bounds.', ['summary.json'])
    fig,ax=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for col,wave in enumerate(('broad','carrier')):
        for event,label in enumerate(('first rise','last fall')):
            errors=[]
            for grid in grids:
                row=s['metrics'][grid+'-'+wave][1]
                errors.append(abs(row['marker_actual'][event]-row['marker_prediction'][event]) if row['marker_actual'] and row['marker_prediction'] else np.nan)
            ax[col].loglog(h,errors,'o-',label=label)
        if wave in s['timing_budgets']:ax[col].axhline(s['timing_budgets'][wave]['budget'],ls='--',label='finest direct budget')
        ax[col].axhline(.1,color='red',ls=':',label='original gate')
        ax[col].set(xlabel='h (m^-1)',ylabel='absolute timing residual (m^-1)',title=wave+' marker transfer');ax[col].legend(fontsize=8)
    save(fig,'marker-convergence','Do first and last marker residuals decrease under refinement?',
        'Each point compares a locked forecast with independently evolved receiver markers on the same mesh.',
        'Tests the discrete transfer separately from clock-phase order discrimination.',
        'First/last events are selected retrospectively in the declared window; no autonomous trigger is modeled.', ['summary.json'])
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Test 7 discrete-transfer discriminator','',f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
        'Original Test 7 remains failed. Test 8 needs separate acceptance. No two-object, gravity, invariance or emergent-spacetime claim.','']
    lines += [f'{k}: {v}' for k,v in s['checks'].items()]
    for wave,b in s['budgets'].items():
        if 'total' in b:lines += [f"{wave}: B={b['total']:.8e} cycles, order separation={b['order_separation']:.8e}, second error={b['second_error']:.8e}, fourth error={b['fourth_error']:.8e}."]
    lines += ['', 'Post-hoc audit: original checks remain unchanged. Forecast convergence and known-source linear replay are additional diagnostics.']
    for wave,audit in s.get('forecast_convergence_audit',{}).items():
        lines += [f"{wave}: forecast-inclusive audit budget {audit['forecast_inclusive_budget']:.8e} versus quarter-order target {audit['quarter_order_separation']:.8e} cycles."]
    for key,value in interpretations.items():lines += ['',key]+[f'{k.title()}: {v}' for k,v in value.items()]
    md='\n'.join(lines)+'\n';(report_path/'report.md').write_text(md)
    (report_path/'report.html').write_text('<!doctype html><meta charset="utf-8"><pre>'+html.escape(md)+'</pre>'+''.join(f'<img width="900" src="figures/{k}.svg">' for k in interpretations))
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[x for line in lines for x in (textwrap.wrap(line,100) or [''])]
        for offset in range(0,len(wrapped),42):
            page=plt.figure(figsize=(8.5,11));page.text(.07,.95,'Test 7: discrete transfer',fontsize=16,va='top');page.text(.07,.90,'\n'.join(wrapped[offset:offset+42]),fontsize=8,va='top');pdf.savefig(page);plt.close(page)
        for fig in figures:pdf.savefig(fig);plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],f"{analysis['path']}/derived/summary.json",f"{analysis['path']}/checks.json"],'figure_specs':specs,'interpretations':'interpretations.json'}
