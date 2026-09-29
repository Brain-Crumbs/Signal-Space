"""Question-driven, immutable reader figures for frozen-clock prerequisites."""
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


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    derived=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figs=report_path/'figures'
    plots.mkdir();figs.mkdir()
    for p in derived.iterdir():
        if p.suffix in ('.csv','.json'):shutil.copy2(p,plots/p.name)
    s=read_json(plots/'summary.json');kind=s['kind'];interpretations={};made=[];specs=[]
    def rows(name):
        with (plots/name).open() as f:return list(csv.DictReader(f))
    data=rows('traces.csv')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def numbers(rs,key):return np.asarray([float(x[key]) for x in rs])
    def save(fig,key,question,reading,significance,limitation,sources,transforms):
        interpretations[key]={'question':question,'reading':reading,'significance':significance,'limitation':limitation}
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,
            'source_datasets':[f'plot-data/{n}' for n in sources],'transformations':transforms,
            'axes':{'x':{'unit':'as labeled: m^-1, eigenperiods or amplitude'},'y':{'unit':'as labeled: m, dimensionless or cycles'}},
            'ranges':'shown on axes','normalization':'c=hbar=m=1; signed local matched differences; explicit amplitude divisions',
            'downsampling':'all saved samples within labeled windows; physical snapshots every 2 time units and every fourth grid point',
            'fit_window':None,'renderer':f'matplotlib-{matplotlib.__version__}'})
        for ext in ('png','svg','pdf'):fig.savefig(figs/f'{key}.{ext}',dpi=150 if ext=='png' else None)
        made.append(fig);specs.append(f'figures/{key}.figure.json')
    if kind=='longevity':
        o=s['observations'];period=2*np.pi/s['calibration']['omega_chi']
        fig,axs=plt.subplots(2,1,figsize=(10,6),layout='constrained')
        for label in ('base','fine','time'):
            d=[x for x in data if x['preparation']==label];t=numbers(d,'time')/period;y=numbers(d,'local_chi')
            for ax,left,right in ((axs[0],0,4),(axs[1],96,100)):
                mask=(t>=left)&(t<=right);ax.plot(t[mask],y[mask],label=label)
                ax.set(xlabel='time / frozen eigenperiod',ylabel='chi at r=0.1 (m)')
        axs[0].legend(ncols=3);axs[0].set_title('First four periods');axs[1].set_title('Last four periods')
        save(fig,'local-ticks','Does the same local radius keep ticking over 100 periods on each grid?',
             f"All grids have 100 positive-going ticks. Fine frequency {o['fine']['frequency']:.9f}; largest relative grid/time difference {s['metrics']['frequency_difference']:.3g}.",
             'The full refined duration now supports using this radial core as a finite-duration local clock.',
             'The ideal probe samples r=0.1 in the fixed flat rest frame; no remote marker or nonspherical stability is established.',
             ['traces.csv','summary.json'],['time divided by frozen nominal eigenperiod; first/last four periods; raw local field'])
        fig,axs=plt.subplots(2,2,figsize=(11,7),layout='constrained')
        for label in ('base','fine','time'):
            d=[x for x in data if x['preparation']==label];t=numbers(d,'time')/period
            axs[0,0].plot(t,numbers(d,'mode_energy_fraction')-1,label=label)
            axs[0,1].plot(t,numbers(d,'charge_balance_fraction'),label=label)
            axs[1,0].plot(t,numbers(d,'core_peak')/float(d[0]['core_peak'])-1,label=label)
        axs[0,0].set(ylabel='E_mode/E_mode(0) - 1',title='Small projected-mode change')
        axs[0,1].set(ylabel='(Q + sink - Q0) / Q0',title='Charge balance')
        axs[1,0].set(ylabel='core peak / initial - 1',title='Core drift')
        axs[1,1].bar(list(o),[x['energy_residual_over_mode'] for x in o.values()],color=['#287a9c','#44956d','#bd793a'])
        axs[1,1].set(ylabel='energy residual / initial mode energy',title='Radiation energy still unresolved')
        for ax in (axs[0,0],axs[0,1],axs[1,0]):ax.set_xlabel('frozen eigenperiods');ax.legend(fontsize=8)
        save(fig,'long-baseline','Do mode energy and charge remain controlled for the full refined baseline?',
             f"Final fine-grid mode change {o['fine']['mode_energy_change']:.3g}; fine energy residual {o['fine']['energy_residual_over_mode']:.3g} initial mode energies.",
             'Refined and time-step controls close the missing 100-period usability check. The energy diagnostic improves with time refinement.',
             'Near-constant projection does not measure a tiny radiation spectrum. A 100-period wide-box run and angular stability remain untested.',
             ['traces.csv','summary.json'],['subtract initial normalized quantities; historical energy residual divided by initial mode energy'])
    else:
        m=s['metrics'];base=m['base']
        def case(j,grid='base'):return [x for x in data if x['grid']==grid and int(x['case'])==j]
        space=rows('spacetime.csv');fig,axs=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
        for ax,j in zip(axs,(2,5)):
            d=[x for x in space if int(x['case'])==j];r=np.unique(numbers(d,'radius'));t=np.unique(numbers(d,'time'))
            a=numbers(d,'a').reshape(len(t),len(r));limit=np.max(abs(a))
            im=ax.pcolormesh(r,t,a,cmap='RdBu_r',vmin=-limit,vmax=limit,shading='nearest',rasterized=True)
            ax.axvline(14,color='k',ls=':',lw=1,label='upstream sphere')
            ax.axvspan(0,10,color='k',alpha=.06,label='approximate core region')
            ax.set(xlabel='radius (m^-1)',ylabel='time (m^-1)',title='Inward packet' if j==2 else 'Inward + outward packets')
            fig.colorbar(im,ax=ax,label='neutral a (m)');ax.legend(fontsize=8,loc='upper right')
        save(fig,'packet-history','Where do the compact neutral packets travel relative to the clock core?',
             'Saved radial neutral-field histories show incoming propagation, central reflection and the separately prepared outgoing control. The upstream sphere is r=14.',
             'This locates the forcing in space and time and makes the concentric-shell geometry explicit.',
             'Spherical focusing is physical in this restricted preparation; it is not an opposing-beam or recoil experiment. Color scales are independent.',
             ['spacetime.csv'],['reshape saved t,r rows into heatmaps; independent symmetric color scales; approximate core band 0<r<10'])
        fig,axs=plt.subplots(2,1,figsize=(10,6),layout='constrained')
        for j in (1,2,3,4,5):
            d=case(j);a=float(d[0]['amplitude']);axs[0].plot(numbers(d,'time'),numbers(d,'upstream_a'),label=f'case {j}, A={a:g}')
            axs[1].plot(numbers(d,'time'),numbers(d,'upstream_a')/a,label=f'case {j}')
        axs[0].set(ylabel='a at r=14 (m)',title='Actual recorded upstream field');axs[0].legend(fontsize=8,ncols=3)
        axs[1].set(xlabel='time (m^-1)',ylabel='a / signed A',title='Amplitude-normalized incident and returning waveform');axs[1].legend(fontsize=8,ncols=3)
        save(fig,'upstream-waveform','What neutral waveform actually reaches the upstream recording sphere?',
             'The saved trace includes both initial passage and later returning radiation. Dividing by signed A overlays the weak single-packet waveforms.',
             'Reception is compared against a recorded input field, with compact preparations and sign controls available for audit.',
             'A single scalar waveform does not separate incoming/outgoing characteristics; this run predicts from full registered initial data, not waveform-only inversion.',
             ['traces.csv'],['select base grid cases 1-5; divide each waveform by its signed input coefficient'])
        fig,axs=plt.subplots(2,2,figsize=(11,7),layout='constrained')
        for col,j in enumerate((2,5)):
            d=case(j);t=numbers(d,'time');actual=numbers(d,'delta_chi');pred=numbers(d,'predicted_delta_chi')
            axs[0,col].plot(t,actual,label='nonlinear minus no pulse')
            axs[0,col].plot(t,pred,'--',label='saved O(A²) prediction')
            axs[0,col].set(title='Single packet' if j==2 else 'Counterpropagating shells',ylabel='local delta chi (m)');axs[0,col].legend(fontsize=8)
            for grid in ('base','fine','time','wide'):
                dd=case(j,grid);axs[1,col].plot(numbers(dd,'time'),numbers(dd,'delta_chi')-numbers(dd,'predicted_delta_chi'),label=grid)
            axs[1,col].set(xlabel='time (m^-1)',ylabel='actual - predicted (m)');axs[1,col].legend(fontsize=8)
        save(fig,'prediction-response','Does the precomputed second-order response predict the local clock difference?',
             f"Base relative L2 prediction error is {base['prediction_relative']['2']:.3g} for one packet and {base['prediction_relative']['5']:.3g} for counterpropagating shells. Prediction files were locked before receiver runs.",
             'Agreement tests the derived neutral-to-core-to-clock response coefficient, beyond the symmetry-enforced sign parity.',
             'The Taylor predictor and nonlinear solver share the discrete Hamiltonian; independent Hamiltonian and Taylor checks plus numerical refinements constrain, but do not eliminate, shared implementation error.',
             ['traces.csv','summary.json'],['matched no-pulse subtraction at the same radius and time; subtract saved A² prediction; no fitting'])
        fig,axs=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
        for j in (1,2,3):
            d=case(j);a=float(d[0]['amplitude']);axs[0].plot(numbers(d,'time'),numbers(d,'delta_chi')/a**2,label=f'A={a:g}')
        plus=case(2);minus=case(4);t=numbers(plus,'time')
        even=(numbers(plus,'delta_chi')+numbers(minus,'delta_chi'))/2
        odd=(numbers(plus,'delta_chi')-numbers(minus,'delta_chi'))/2
        axs[1].plot(t,even,label='sign-even component');axs[1].plot(t,odd,'--',label='sign-odd component')
        axs[0].set(xlabel='time (m^-1)',ylabel='delta chi / A²',title=f"Weak response slope = {base['weak_slope']:.6f}");axs[0].legend()
        axs[1].set(xlabel='time (m^-1)',ylabel='local delta chi (m)',title='Global packet sign reversal');axs[1].legend()
        save(fig,'parity-scaling','Is the clock difference even in packet sign and quadratic in amplitude?',
             f"Weak amplitude exponent {base['weak_slope']:.7f}; normalized ladder difference {base['scaling_difference']:.3g}; sign-odd/even norm ratio {base['sign_odd_fraction']:.3g}.",
             'The amplitude ladder discriminates second-order forcing from a linear response, while sign parity checks the exact action symmetry.',
             'Exact numerical sign parity is strongly enforced by this deterministic action. It alone does not validate the magnitude or operational meaning of the clock response.',
             ['traces.csv','summary.json'],['divide matched difference by A squared; compute half-sum and half-difference of +/-A responses; no fitted curves'])
        markers=rows('markers.csv');fig,axs=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
        for grid in ('base','fine','time','wide'):
            dd=[x for x in markers if x['grid']==grid and int(x['case'])==2]
            axs[0].plot(numbers(dd,'tick'),numbers(dd,'delta_cycles'),'o-',label=grid)
        dd=[x for x in markers if x['grid']=='base' and int(x['case'])==2]
        axs[0].plot(numbers(dd,'tick'),numbers(dd,'predicted_cycles'),'k--',label='base prediction')
        axs[0].set(xlabel='paired local positive-going tick index',ylabel='clock advance (cycles)',title='Local tick shifts; common preparation');axs[0].legend(fontsize=8)
        names=['h/2','dt/2','2R'];x=np.arange(3)
        for caseid,offset in (('2',-.18),('5',.18)):
            vals=[max(v,1e-16) for v in s['numerical_errors'][caseid].values()]
            # Explicit order follows persisted JSON keys, so select by name below.
            vals=[max(s['numerical_errors'][caseid][k],1e-16) for k in ('fine','time','wide')]
            axs[1].bar(x+offset,vals,.36,label='single' if caseid=='2' else 'counter')
        axs[1].set(xticks=x,xticklabels=names,yscale='log',ylabel='relative L2 response difference',title='Independent numerical controls')
        axs[1].axhline(.05,color='red',ls='--',label='5% gate');axs[1].legend(fontsize=8)
        save(fig,'marker-convergence','Are corresponding local tick shifts reproducible under mesh, time and box controls?',
             f"Every base preparation has {base['baseline_crossings']} baseline ticks available for pairing. Largest base tick shift {base['maximum_tick_shift_cycles']:.3g} cycles; largest predicted tick-shift error {base['maximum_tick_prediction_error_cycles']:.3g} cycles.",
             'The measured response reaches an identifiable local clock record, with numerical sensitivity displayed independently.',
             'Tick ordinals are anchored to the common preparation in one flat frame. Physical emission/reception marker invariance and two-object recoil are still untested. Values below 1e-16 are plotted at that floor.',
             ['markers.csv','summary.json'],['linearly interpolate positive-going local zeros; delta_N=-Omega*delta_t/(2*pi); ordinal pairing; direct grid/time/box differences'])
    write_json(report_path/'interpretations.json',interpretations)
    lines=[f'# Signal Space: Test 6 {kind} prerequisite','',f"Technical state: completed. Scientific classification: {analysis['classification']}.",
       f"Run: {manifest['run_id']}. Analysis: {analysis['analysis_id']}.",
       f"Source profile run: {s['source_run']}; frozen omega_Q=0.900, Omega=0.41274991; local radius=0.1.",
       f"Solver revision: {manifest['code_identity']['revision']}; renderer revision: {render_provenance['code_identity']['revision']}.",
       'The exact locked method, thresholds and controls are in the plan. Scope: flat spherical matter; no gravitational or nonspherical result.',
       '', 'Locked scientific checks:']+[f"- {k}: {v}" for k,v in s['checks'].items()]
    for key,item in interpretations.items():lines += ['',f'## {key}']+[f'{k.title()}: {v}' for k,v in item.items()]
    markdown='\n'.join(lines)+'\n';(report_path/'report.md').write_text(markdown)
    (report_path/'report.html').write_text('<!doctype html><html><meta charset="utf-8"><body><pre style="white-space:pre-wrap">'+html.escape(markdown)+'</pre>'+''.join(f'<img width="900" src="figures/{key}.svg" alt="{key}">' for key in interpretations)+'</body></html>')
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[x for line in lines for x in (textwrap.wrap(line,100) or [''])]
        for start in range(0,len(wrapped),45):
            fig=plt.figure(figsize=(8.5,11));fig.text(.07,.95,f'Test 6: {kind}',fontsize=16,weight='bold',va='top')
            fig.text(.07,.90,'\n'.join(wrapped[start:start+45]),fontsize=8.5,va='top',linespacing=1.3);pdf.savefig(fig);plt.close(fig)
        for fig in made:pdf.savefig(fig);plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],f"{analysis['path']}/derived/summary.json",f"{analysis['path']}/derived/traces.csv",f"{analysis['path']}/checks.json"],
            'figure_specs':specs,'interpretations':'interpretations.json'}
