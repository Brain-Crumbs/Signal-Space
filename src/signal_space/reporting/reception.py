"""Test 7 question-driven figures, rendered from immutable analysis only."""
import csv
import html
import shutil
import textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import SymLogNorm
from signal_space.runtime.io import read_json,write_json


def render_report(run_path,report_path,manifest,analysis,render_provenance):
    derived=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figs=report_path/'figures';plots.mkdir();figs.mkdir()
    for p in derived.iterdir():shutil.copy2(p,plots/p.name)
    s=read_json(plots/'summary.json');interpretations={};made=[];specs=[]
    def rows(name):
        with (plots/name).open() as f:return list(csv.DictReader(f))
    traces=rows('traces.csv');markers=rows('markers.csv')
    def nums(rows,key):return np.asarray([float(x[key]) for x in rows])
    def case(name,grid='finer'):return [x for x in traces if x['grid']==grid and x['case']==name]
    def save(fig,key,q,reading,significance,limitation,sources,transforms):
        interpretations[key]={'question':q,'reading':reading,'significance':significance,'limitation':limitation}
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,
           'source_datasets':['plot-data/'+x for x in sources],'transformations':transforms,
           'axes':{'x':{'unit':'as labeled'},'y':{'unit':'as labeled'}},'ranges':'shown on axes',
           'normalization':'natural units c=hbar=m=1; cycles = radians/(2*pi)',
           'downsampling':'all saved local samples; spatial views saved every 1 time unit and 0.2 radius',
           'fit_window':None,'renderer':'matplotlib-'+matplotlib.__version__})
        for ext in ('png','svg','pdf'):fig.savefig(figs/f'{key}.{ext}',dpi=150 if ext=='png' else None)
        made.append(fig);specs.append(f'figures/{key}.figure.json')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    surface=rows('surface.csv');fig,axs=plt.subplots(2,1,figsize=(10,6),layout='constrained')
    for j in (0,1):
        d=[x for x in surface if int(x['pulse'])==j];t=nums(d,'time')
        axs[0].plot(t,nums(d,'a'),label=f'pulse {j+1}')
        axs[1].plot(t,nums(d,'incoming'),label=f'incoming {j+1}')
        axs[1].plot(t,nums(d,'outgoing'),'--',label=f'outgoing {j+1}')
    for ax in axs:ax.axvspan(0,16,color='green',alpha=.07);ax.legend(ncols=2,fontsize=8)
    axs[0].set(ylabel='a at r=14, per unit A',title='Only upstream field and derivatives cross the prediction boundary')
    axs[1].set(xlabel='time (m^-1)',ylabel='characteristic derivative',title='Solid: incoming; dashed: outgoing; shaded: inversion window')
    save(fig,'surface-characteristics','Can the upstream record distinguish incoming drive from returning radiation?',
      'Incoming and outgoing characteristics are built from a, a_t and a_r. Only t=0..16 is inverted.',
      'The predictor no longer consumes the prescribed interior neutral history.',
      'This is a linear acquisition on a frozen core. Exterior vacuum inversion has mesh and tail errors.',
      ['surface.csv'],['I=(r*a_t+a+r*a_r)/2; O=(r*a_t-a-r*a_r)/2'])
    space=rows('spacetime.csv');fig,axs=plt.subplots(1,2,figsize=(11,5),layout='constrained')
    d=[x for x in space if x['case']=='both'];r=np.unique(nums(d,'radius'));t=np.unique(nums(d,'time'))
    for ax,key in zip(axs,('a','invariant')):
        z=nums(d,key).reshape(len(t),len(r))
        if key=='a':z=z*r[None,:]
        limit=np.max(abs(z));norm=SymLogNorm(linthresh=limit*.001,vmin=-limit,vmax=limit) if key=='invariant' else None
        im=ax.pcolormesh(r,t,z,cmap='RdBu_r',norm=norm,shading='nearest',rasterized=True)
        ax.set(xlabel='radius (m^-1)',ylabel='time (m^-1)',ylim=(0,55),title='Radial neutral amplitude r*a' if key=='a' else 'Gradient contraction (symmetric log)')
        ax.axvline(14,ls=':',color='black');fig.colorbar(im,ax=ax,label='r*a (dimensionless)' if key=='a' else '(partial a)^2 (m^4)')
    save(fig,'packet-overlap','Where do the reflected first pulse and incoming second pulse overlap?',
      'Both packets begin outside r=14. Central reflection sends the first outward through the second incoming packet.',
      'This supplies opposite radial directions and allows both-minus-each-alone subtraction.',
      'The left panel removes the 1/r focusing factor. The right uses symmetric log color; this is not two planar beams.',
      ['spacetime.csv'],['base grid; reshape time/radius rows; multiply a by r to expose radial transport; signed contraction uses symmetric log normalization with linear threshold 0.001 of its maximum absolute value; show t<=55'])
    fig,axs=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    for col,name in enumerate(('single','both')):
        d=case(name);t=nums(d,'time')
        axs[0,col].plot(t,nums(d,'delta_chi'),label='held-out actual')
        axs[0,col].plot(t,nums(d,'predicted_delta_chi'),'--',label='surface prediction')
        axs[0,col].set(title=name,ylabel='local delta chi (m)');axs[0,col].legend(fontsize=8)
        axs[1,col].plot(t,nums(d,'delta_density'),label='actual')
        axs[1,col].plot(t,nums(d,'predicted_density'),'--',label='predicted')
        axs[1,col].set(xlabel='time (m^-1)',ylabel='local delta density (m^2)');axs[1,col].legend(fontsize=8)
    m=s['metrics']['finer']
    save(fig,'withheld-response','Does surface-only prediction match the withheld local clock and density response?',
      f"Finest trace errors: single {m['trace_prediction_relative'][2]:.3%}; both {m['trace_prediction_relative'][6]:.3%}.",
      'This tests the neutral-to-core-to-clock coefficient without fitting the withheld evolution.',
      'The Taylor and full evolutions share the discrete Hamiltonian. Agreement is bounded by independent numerical controls.',
      ['traces.csv','summary.json'],['finer grid h=.025; matched quiet subtraction; multiply Taylor coefficients by A squared'])
    fig,axs=plt.subplots(3,1,figsize=(10,9),layout='constrained')
    for name in ('single','both'):
        d=case(name);t=nums(d,'time');axs[0].plot(t,abs(nums(d,'local_a')),label=name)
        axs[1].plot(t,nums(d,'delta_cycles'),label=name+' actual')
        axs[1].plot(t,nums(d,'predicted_cycles'),'--',label=name+' prediction')
        axs[2].plot(t,nums(d,'delta_cycles')-nums(d,'predicted_cycles'),label=name)
        mark=next(x for x in markers if x['grid']=='finer' and x['case']==name)
        if mark['start'] and mark['end']:
            for ax in axs:
                ax.axvline(float(mark['start']),color='gray',lw=.7,ls=':');ax.axvline(float(mark['end']),color='gray',lw=.7,ls=':')
    axs[0].axhline(1e-4,color='black',ls='--',label='marker threshold')
    axs[0].set(ylabel='|a| at r=0.1 (m)',title='Start: first rise; end: last fall through local threshold')
    axs[1].set(xlabel='local proper time (m^-1)',ylabel='matched local phase (cycles)',title='Interval record is the difference between endpoint phase offsets')
    axs[2].set(xlabel='local proper time (m^-1)',ylabel='actual - predicted (cycles)',title='Held-out local phase residual')
    for ax in axs:ax.legend(fontsize=8,ncols=2)
    save(fig,'local-markers','Do locally triggered intervals carry a resolved predicted clock record?',
      f"Local marker check: {s['checks']['local-markers']}; resolution: {s['checks']['record-resolution']}; interval prediction: {s['checks']['marker-prediction']}.",
      'The interval uses locally recorded neutral events and local clock quadrature, rather than coordinate arrival alone.',
      'The quiet history is evaluated at counterfactual event times. Last-fall selection is retrospective in a finite window.',
      ['markers.csv','traces.csv','summary.json'],['local atan2 phase from chi and chi_dot; quiet subtraction; first/last absolute-a threshold crossings'])
    fig,axs=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    for name in ('half','single','double'):
        d=case(name);A=float(d[0]['amplitude']);axs[0,0].plot(nums(d,'time'),nums(d,'delta_chi')/A**2,label=name)
    plus=case('single');minus=case('negative');t=nums(plus,'time')
    axs[0,1].plot(t,(nums(plus,'delta_chi')+nums(minus,'delta_chi'))/2,label='even')
    axs[0,1].plot(t,(nums(plus,'delta_chi')-nums(minus,'delta_chi'))/2,'--',label='odd')
    a=case('single');b=case('second');both=case('both')
    for key,style,title in [('delta_chi','-','actual'),('predicted_delta_chi','--','prediction')]:axs[1,0].plot(t,nums(both,key)-nums(a,key)-nums(b,key),style,label=title)
    for name in ('single','phase'):
        d=case(name);axs[1,1].plot(t,nums(d,'delta_chi'),label=name);axs[1,1].plot(t,nums(d,'predicted_delta_chi'),'--')
    axs[1,1].plot(t,np.zeros_like(t),':',color='black',label='frozen-core prediction')
    for ax,title,y in zip(axs.flat,('Amplitude ladder','Sign reversal','Both minus each alone','Clock phase and frozen-core control'),('delta chi / A^2','delta chi (m)','interaction delta chi (m)','delta chi (m)')):
        ax.set(xlabel='time (m^-1)',ylabel=y,title=title);ax.legend(fontsize=8)
    save(fig,'controls','Do sign, amplitude, pulse-overlap and clock-phase controls support the response mechanism?',
      f"Weak amplitude exponent {m['weak_slope']:.6f}; overlap check {s['checks']['pulse-overlap']}; frozen-core control {s['checks']['frozen-core-control']}.",
      'Individual pulses isolate the interaction term; clock phase changes test a held-out response configuration.',
      'Sign symmetry is enforced by the action and is not independent evidence for the response coefficient.',
      ['traces.csv','summary.json'],['divide amplitude traces by A squared; half-sum/difference; both-minus-single-minus-second; h=.025'])
    fig,axs=plt.subplots(1,2,figsize=(11,5),layout='constrained');names=['single','second','both','phase'];ids=['2','5','6','9'];x=np.arange(4)
    values=[s['record_error_budgets'][j] for j in ids]
    for offset,key,label in [(-.24,'signal','|record|'),(0,'absolute_error','error budget'),(.24,'prediction_error','prediction residual')]:
        y=[max(abs(v[key]),1e-16) if v[key] is not None else np.nan for v in values];axs[0].bar(x+offset,y,.24,label=label)
    axs[0].set(xticks=x,xticklabels=names,yscale='log',ylabel='cycles',title='Local interval and absolute error budget');axs[0].legend(fontsize=8)
    for j,name in zip(ids,names):
        d=s['numerical_controls'][j];axs[1].plot(['h/2','dt/2','2R','h/4 vs h/2'],[max(d[k],1e-16) for k in ('fine','time','wide','finer_vs_fine')],'o-',label=name)
    axs[1].set(yscale='log',ylabel='relative L2 clock-response difference',title='Independent discretization and boundary controls');axs[1].axhline(.05,color='red',ls='--');axs[1].legend(fontsize=8)
    save(fig,'error-budget','Is the local record larger than independent numerical errors?',
      'Bars compare absolute interval magnitude, direct numerical error and prediction residual. Resolution requires signal greater than five error budgets.',
      'A good-looking trace cannot substitute for a resolved local interval.',
      'The budget is deterministic, not a statistical confidence interval. The finest profile is interpolated, not independently re-solved.',
      ['summary.json'],['absolute values; log floor1e-16; budgets from finer/fine + base/time + base/wide +1e-11 cycles'])
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Signal Space Test 7: surface-only reception','',f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
       'Scope: frozen calibrated flat radial receiver; SS OCF 1 action unchanged.',
       'All predictions are saved before nonlinear receiver evolution. Quiet marker times are a counterfactual reference.',
       'No two-object recoil, observer invariance, angular stability or emergent spacetime is established.','']
    lines += [f"Technical execution completed; {sum(v=='pass' for v in s['checks'].values())} checks pass and {sum(v=='fail' for v in s['checks'].values())} fail.",
       f"Locked local interval prediction: {s['checks']['marker-prediction']}; local marker timing: {s['checks']['local-markers']}.",
       'These checks concern the response approximation and protocol; they do not re-test clock existence.', '',
       'Finest-grid local interval results (cycles; deterministic error budgets):']
    for name,j in zip(('single','second','both','changed phase'),('2','5','6','9')):
        v=s['record_error_budgets'][j]
        lines += [f"{name}: actual {v['signal']:.6e}; error budget {v['absolute_error']:.3e}; prediction discrepancy {v['prediction_error']:.3e}."]
    lines += ['', 'No acceptance threshold was changed after execution. See the reviewed analysis for the next calculation.', '']
    lines += [f"{key}: {value}" for key,value in s['checks'].items()]
    for key,item in interpretations.items():lines += ['',key]+[f'{k.title()}: {v}' for k,v in item.items()]
    md='\n'.join(lines)+'\n';(report_path/'report.md').write_text(md)
    (report_path/'report.html').write_text('<!doctype html><meta charset="utf-8"><pre style="white-space:pre-wrap">'+html.escape(md)+'</pre>'+''.join(f'<img width="900" src="figures/{key}.svg">' for key in interpretations))
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[x for line in lines for x in (textwrap.wrap(line,100) or [''])]
        for start in range(0,len(wrapped),42):
            fig=plt.figure(figsize=(8.5,11));fig.text(.07,.95,'Test 7: predicted reception',fontsize=16,va='top');fig.text(.07,.90,'\n'.join(wrapped[start:start+42]),fontsize=8.5,va='top');pdf.savefig(fig);plt.close(fig)
        for fig in made:pdf.savefig(fig);plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],f"{analysis['path']}/derived/summary.json",f"{analysis['path']}/checks.json"], 'figure_specs':specs,'interpretations':'interpretations.json'}
