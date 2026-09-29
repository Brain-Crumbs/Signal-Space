"""Question-driven figures from saved known-incident acceptance evidence."""
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
    source=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figdir=report_path/'figures'
    plots.mkdir();figdir.mkdir()
    for f in source.iterdir():shutil.copy2(f,plots/f.name)
    s=read_json(plots/'summary.json');data={}
    for name in ('traces','spacetime','surface'):
        with (plots/f'{name}.csv').open() as f:data[name]=list(csv.DictReader(f))
    groups={name:[r for r in data['traces'] if r['case']==name] for name in ('half','single','double','negative','second','both','both-negative','phase')}
    v=lambda rows,k:np.asarray([float(r[k]) for r in rows]);figs=[];specs=[];interpretations={}
    plt.rcParams.update({'font.size':9,'axes.spines.right':False,'axes.spines.top':False})
    def save(fig,key,question,reading,meaning,limit,files):
        interpretations[key]={'question':question,'reading':reading,'significance':meaning,'limitation':limit}
        write_json(figdir/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,
            'source_datasets':['plot-data/'+x for x in files],'transformations':['saved matched differences and formal coefficients; no fitted parameters'],
            'axes':{'x':{'unit':'as labeled'},'y':{'unit':'as labeled'}},'ranges':'shown on axes','normalization':'natural units; phase in cycles',
            'downsampling':'saved finest local traces; base spacetime every1 time and about.2 radius','fit_window':None,'renderer':'matplotlib-'+matplotlib.__version__})
        for ext in ('png','svg','pdf'):fig.savefig(figdir/f'{key}.{ext}',dpi=160 if ext=='png' else None)
        figs.append(fig);specs.append(f'figures/{key}.figure.json')
    fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
    rows=data['spacetime'];bound=max(abs(float(r['a'])) for r in rows)
    for ax,name in zip(axes,('single','second','both')):
        sub=[r for r in rows if r['case']==name];t=np.unique(v(sub,'time'));r=np.unique(v(sub,'radius'));a=v(sub,'a').reshape(len(t),len(r))
        im=ax.pcolormesh(r,t,a,shading='auto',cmap='RdBu_r',vmin=-bound,vmax=bound,rasterized=True)
        for mark in s['event_times']:ax.axhline(mark,color='black',ls=':',lw=.6)
        ax.set(title=name,xlabel='radius (m^-1)',ylabel='time (m^-1)')
    fig.colorbar(im,ax=axes,label='neutral a (m)')
    save(fig,'acceptance-propagation','Where do incoming and reflected pulses overlap?',
        'Saved coupled base-grid fields show the incoming shells and origin reflection. Dotted lines mark the fixed local sampling times.',
        'Grounds the pair-minus-individual test in an executed radial counterpropagation geometry.',
        'Radial shells and fixed origin are not two moving objects or planar beams. The field map alone does not demonstrate clock reception.', ['spacetime.csv'])
    fig,axes=plt.subplots(3,2,figsize=(11,8),layout='constrained')
    for col,name in enumerate(('single','both')):
        rows=groups[name];t=v(rows,'time')
        axes[0,col].plot(t,v(rows,'local_invariant'),label='coupled invariant');axes[0,col].plot(t,v(rows,'predicted_invariant2'),'--',label='leading incident forcing')
        for ax,actual,pred,label in [(axes[1,col],'density_response','predicted_density','density change'),(axes[2,col],'delta_chi','predicted_chi','clock change')]:
            ax.plot(t,v(rows,actual),label='actual');ax.plot(t,v(rows,pred),'--',label='forecast');ax.set(ylabel=label,xlabel='time (m^-1)');ax.legend(fontsize=7)
        axes[0,col].set(title=name,ylabel='derivative invariant (m^4)',xlabel='time (m^-1)');axes[0,col].legend(fontsize=7)
    save(fig,'acceptance-forcing','Does the incident invariant drive the predicted core and clock response?',
        'The invariant, matched core-density change and matched clock-field change are saved separately. Response-trace gate: '+s['checks']['response-traces']+'.',
        'Tests the neutral-to-core-to-clock mechanism rather than arrival time alone.',
        'The invariant overlay is leading order; the response forecast includes fourth order. The source preparation is known, not inferred from surface data.', ['traces.csv'])
    fig,axes=plt.subplots(3,4,figsize=(14,9),layout='constrained')
    for col,name in enumerate(('single','second','both','phase')):
        ax=axes[0,col]
        rows=groups[name];t=v(rows,'time')
        for key,label,style in [('actual_cycles','actual','-'),('predicted_cycles','fourth order','--'),('second_cycles','second order',':')]:ax.plot(t,v(rows,key),style,label=label)
        for mark in s['event_times']:ax.axvline(mark,color='gray',ls=':',lw=.6)
        ax.set(title=name,xlabel='time (m^-1)',ylabel='relative phase (cycles)');ax.legend(fontsize=7)
        for row,key,label in [(1,'second_cycles','actual - second order'),(2,'predicted_cycles','actual - fourth order')]:
            axes[row,col].plot(t,v(rows,'actual_cycles')-v(rows,key))
            axes[row,col].axhline(0,color='gray',lw=.6)
            axes[row,col].set(title=label,xlabel='time (m^-1)',ylabel='residual (cycles)')
    save(fig,'acceptance-phase','Does the locked forecast predict the withheld local phase histories?',
        'Actual relative quadrature phase is compared with independently locked second- and fourth-order coefficients for four primary preparations. Separate residual panels expose differences hidden by the history overlays.',
        'Separates the leading calibrated susceptibility from its unfitted higher-order correction.',
        'Both predictions know the preparation and use a matched quiet reference; no autonomous detector or observer-invariance claim is made.', ['traces.csv'])
    names=list(s['record_budgets']);x=np.arange(len(names));fig,axes=plt.subplots(2,1,figsize=(11,7),layout='constrained')
    records=[s['record_budgets'][n] for n in names]
    axes[0].errorbar(x-.07,[q['signal'] for q in records],yerr=[q['budget'] for q in records],fmt='o',capsize=3,label='actual ± combined budget')
    axes[0].scatter(x+.07,[q['prediction'] for q in records],marker='x',label='locked forecast');axes[0].set(ylabel='interval change (cycles)',xticks=x,xticklabels=names);axes[0].legend()
    axes[1].bar(x,[q['error']/q['allowance'] for q in records]);axes[1].axhline(1,color='red',ls='--',label='acceptance limit');axes[1].set(yscale='log',ylim=(1e-6,2),ylabel='error / allowed error (log scale)',xticks=x,xticklabels=names);axes[1].legend()
    save(fig,'acceptance-intervals','Are nonzero cycle intervals resolved and forecasts within the registered allowance?',
        'Resolution gate: '+s['checks']['record-resolution']+'; interval-prediction gate: '+s['checks']['interval-prediction']+'. The lower panel must be at or below one, and every record must exceed five budgets.',
        'Directly evaluates the Program 15.7 acceptance observable, including both receiver and forecast numerical uncertainty.',
        'Error bars are deterministic direct-difference budgets, not confidence intervals. Fixed proper-time events differ from the historical threshold event protocol.', ['summary.json'])
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained');t=v(groups['single'],'time')
    for name,A in [('half',.002),('single',.004),('double',.008)]:axes[0,0].plot(t,v(groups[name],'delta_chi')/A**2,label=name)
    axes[0,0].set(title='Amplitude-normalized clock response',xlabel='time (m^-1)',ylabel='delta chi / A^2');axes[0,0].legend(fontsize=7)
    for pos,neg in [('single','negative'),('both','both-negative')]:axes[0,1].plot(t,v(groups[pos],'actual_cycles')-v(groups[neg],'actual_cycles'),label=pos)
    axes[0,1].set(title='Sign-reversal null',xlabel='time (m^-1)',ylabel='sign-odd phase (cycles)');axes[0,1].legend(fontsize=7)
    for key,label in [('actual_cycles','actual'),('predicted_cycles','forecast')]:axes[1,0].plot(t,v(groups['both'],key)-v(groups['single'],key)-v(groups['second'],key),label=label)
    axes[1,0].set(title='Both minus each pulse alone',xlabel='time (m^-1)',ylabel='interaction phase (cycles)');axes[1,0].legend(fontsize=7)
    amps=np.array([.002,.004,.008]);magnitudes=[np.linalg.norm(v(groups[n],'delta_chi')) for n in ('half','single','double')]
    axes[1,1].loglog(amps,magnitudes,'o-',label='measured L2');axes[1,1].loglog(amps,magnitudes[0]*(amps/amps[0])**2,'--',label='quadratic reference')
    axes[1,1].set(title='Weak response scaling',xlabel='incident A',ylabel='clock-response L2');axes[1,1].legend(fontsize=7)
    save(fig,'acceptance-controls','Do sign parity, amplitude law and pulse overlap support the response mechanism?',
        f"Weak-amplitude gate: {s['checks']['weak-amplitude-law']}; parity: {s['checks']['sign-even']}; overlap: {s['checks']['pulse-overlap']}. Overlap resolution is {s['overlap']['signal_to_budget']:.3g} budgets.",
        'Checks the predicted even, quadratic weak response and the additional record caused by counterpropagating overlap.',
        'The quadratic reference is normalized to the smallest amplitude for display; it is not a fitted forecast. Frozen-core and quiet null values are in the checks.', ['traces.csv','summary.json'])
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for name in ('single','second','both','phase'):
        c=s['convergence'][name]['actual'];axes[0].loglog([.1,.05],[c['coarse_change'],c['fine_change']],'o-',label=name)
    axes[0].set(xlabel='coarser h (m^-1)',ylabel='phase trace mesh difference (cycles)',title='Independent spatial refinement');axes[0].legend(fontsize=7)
    grids=list(s['metrics']);q=[max(r['charge_error'] for r in s['metrics'][g].values()) for g in grids];e=[max(r['matched_energy_over_incident'] for r in s['metrics'][g].values()) for g in grids]
    axes[1].semilogy(grids,np.maximum(q,1e-16),'o-',label='relative charge drift');axes[1].semilogy(grids,np.maximum(e,1e-16),'s-',label='matched energy / incident')
    axes[1].axhline(1e-5,color='gray',ls=':',label='charge limit');axes[1].axhline(.01,color='red',ls=':',label='matched-energy limit');axes[1].set(ylabel='dimensionless residual',title='Conservation controls');axes[1].legend(fontsize=7)
    save(fig,'acceptance-numerics','Do refinement and conservation support the claimed accuracy?',
        'Numerical-convergence gate: '+s['checks']['numerical-convergence']+'; conservation gate: '+s['checks']['conservation']+'. Time/domain differences and total-energy drift are retained in the summary.',
        'Tests whether prediction agreement survives discretization controls while respecting the reciprocal Hamiltonian.',
        'Refinement retains the accepted prepared profile; it does not prove a new continuum bound state. Finite differences are error estimates, not rigorous bounds.', ['summary.json'])
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Test 7 known-incident full acceptance','',f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
        'Fixed local proper-time interval10..60; known initial incident field; calibrated unfitted fourth-order response.',
        'New Program15.7 radial protocol. Historical surface-only failures remain unchanged.','']
    lines += [f'{k}: {v}' for k,v in s['checks'].items()]
    lines += ['', 'Case: actual cycles; predicted cycles; signal/budget; error/allowance']
    for n,q in s['record_budgets'].items():lines.append(f"{n}: {q['signal']:.7e}; {q['prediction']:.7e}; {q['signal_to_budget']:.3f}; {q['error']/q['allowance']:.3e}")
    for key,item in interpretations.items():lines+=['',key]+[f'{k.title()}: {v}' for k,v in item.items()]
    md='\n'.join(lines)+'\n';(report_path/'report.md').write_text(md);(report_path/'report.html').write_text('<!doctype html><meta charset="utf-8"><pre>'+html.escape(md)+'</pre>'+''.join(f'<img width="900" src="figures/{k}.svg">' for k in interpretations))
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[x for line in lines for x in (textwrap.wrap(line,100) or [''])]
        for off in range(0,len(wrapped),42):
            page=plt.figure(figsize=(8.5,11));page.text(.07,.96,'Test 7 known-incident acceptance',fontsize=16,va='top');page.text(.07,.91,'\n'.join(wrapped[off:off+42]),fontsize=8,va='top');pdf.savefig(page);plt.close(page)
        for fig in figs:pdf.savefig(fig);plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],f"{analysis['path']}/derived/summary.json",f"{analysis['path']}/checks.json"],'figure_specs':specs,'interpretations':'interpretations.json'}
