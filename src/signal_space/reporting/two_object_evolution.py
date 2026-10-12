"""Question-driven Test 8 implementation figures from saved data only."""
import csv
import html
import shutil
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from signal_space.runtime.io import read_json, write_json

QUESTIONS = {
    'pair-fields': 'What changes when the quiet pair is allowed to evolve freely?',
    'preparation-residuals': 'Does a bounded preparation correction reduce the actual residual?',
    'local-clock-records': 'Can both local detector records be retained without using global mode phase?',
    'conservation-scales': 'Do conservation errors resolve the weak clock energy scale?',
    'independent-controls': 'How sensitive are local records and fixed-tube balances to numerical controls?'
}


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    source = run_path/analysis['path']/'derived'
    plots, figures = report_path/'plot-data', report_path/'figures'
    plots.mkdir()
    figures.mkdir()
    for name in ('summary.json', 'traces.csv', 'spatial.npz'):
        shutil.copy2(source/name,plots/name)
    summary = read_json(plots/'summary.json')
    duration = summary['cases'][0]['duration']
    source_cases = [c['case'] for c in summary['cases'] if c['case']['source']['channel'] != 'none']
    earliest_tube_arrival = min(c['separation'] - c['tube_radius'] - c['source']['radius'] - c['h']
                               for c in source_cases)
    window_limit = ('It ends before nominal source-to-receiver-tube arrival.'
                    if duration < earliest_tube_arrival else
                    'Received signal attribution is not qualified in this implementation stage.')
    passed = sum(status == 'pass' for status in summary['classification'].values())
    with (plots/'traces.csv').open(newline='',encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    specs, interpretations, created = [], {}, []
    def trace(label,obj='A'):
        subset=[row for row in rows if row['scenario']==label and row['object']==obj]
        return {key:np.asarray([float(row[key]) for row in subset])
                for key in subset[0] if key not in ('scenario','object')}
    def save(fig,key,reading,significance,limitation,transforms,data):
        interpretation={'question':QUESTIONS[key],'reading':reading,
                        'significance':significance,'limitation':limitation}
        spec={'schema_version':'research-figure-spec-v1','id':key,
              'source_datasets':data,'transformations':transforms,
              'axes':{'x':{'unit':'as labeled'},'y':{'unit':'as labeled'}},
              'ranges':'shown on axes','normalization':'c=hbar=m=1; nominal Test 6 calibration',
              'downsampling':'none','fit_window':None,'renderer':f'matplotlib-{matplotlib.__version__}',
              'interpretation':interpretation,
              'role':'evidentiary' if key in ('preparation-residuals','conservation-scales') else 'diagnostic'}
        write_json(figures/f'{key}.figure.json',spec)
        fig.suptitle(QUESTIONS[key],fontsize=12)
        for extension in ('png','svg','pdf'):
            fig.savefig(figures/f'{key}.{extension}',dpi=150 if extension=='png' else None)
        specs.append(f'figures/{key}.figure.json')
        interpretations[key]=interpretation
        created.append(fig)
    fig,axes=plt.subplots(1,2,figsize=(9.5,4.5),layout='constrained')
    with np.load(plots/'spatial.npz') as data:
        rho,z=data['rho'],data['z']
        axes[0].plot(z,data['initial_density'][0],label='initial')
        axes[0].plot(z,data['final_density'][0],label='final')
        axes[0].set(xlabel='z (m$^{-1}$)',ylabel='density at first radial cell (m$^2$)')
        mesh=axes[1].pcolormesh(z,rho,data['final_chi'],shading='nearest',cmap='RdBu_r')
        axes[1].set(xlabel='z (m$^{-1}$)',ylabel='rho (m$^{-1}$)',title='final clock field (m)')
        fig.colorbar(mesh,ax=axes[1],shrink=.8)
    axes[0].legend()
    save(fig,'pair-fields','Two freely evolved matter peaks and the shared real clock field are shown.',
         'The nonlinear pair is evolved rather than held as a frozen potential.',
         f"The {summary['cases'][0]['duration']:g}-time-unit coarse-grid window does not establish long-time survival, binding or generic angular stability.",
         ['First radial cell for density; all cells for final chi; no rescaling.'],['plot-data/spatial.npz'])
    fig,axes=plt.subplots(1,2,figsize=(9.5,4.5),layout='constrained')
    labels=['isolated-base','isolated-reduced','pair-base','pair-reduced','pair-quadrature','pair-orthogonal']
    norms=[summary['observations'][label]['residual_ratio'] for label in labels]
    axes[0].bar(np.arange(len(labels)),norms,color=['#8596b0','#2a7f8f']*3)
    axes[0].set(xticks=np.arange(len(labels)),xticklabels=labels,ylabel='final preparation residual / initial')
    axes[0].tick_params(axis='x',rotation=45,labelsize=8)
    for label in ('pair-base','pair-reduced','isolated-base','isolated-reduced'):
        t=trace(label)
        axes[1].plot(t['time'],t['center']-t['center'][0],label=label)
    axes[1].set(xlabel='time (m$^{-1}$)',ylabel='tracked axial displacement (m$^{-1}$)')
    axes[1].legend(fontsize=7)
    save(fig,'preparation-residuals',
         'Reduced/initial quiet residual ratios: '+', '.join(f"{label}={summary['observations'][label]['residual_ratio']:.5g}"
                                                            for label in ('pair-reduced','isolated-reduced'))+'.',
         'The true unprojected residual is checked after correction; the isolated control separates mesh embedding from pair interaction.',
         'This is constrained defect correction before seeding clocks, not a stationary joint solution or stability bound.',
         ['Volume-weighted unprojected residual norms; subtract each initial charge centroid.'],['plot-data/summary.json','plot-data/traces.csv'])
    fig,axes=plt.subplots(2,1,figsize=(9.5,6),layout='constrained')
    for label in ('pair-base','pair-reduced','pair-quadrature','pair-orthogonal'):
        for obj in ('A','B'):
            t=trace(label,obj)
            axes[0].plot(t['proper_time'],t['local_chi'],label=f'{label} {obj}',ls='-' if obj=='A' else '--')
            axes[1].plot(t['proper_time'],t['predicted_tick_residual'],ls='-' if obj=='A' else '--')
    axes[0].set(ylabel='local chi (m)')
    axes[1].set(xlabel='detector proper time (m$^{-1}$)',ylabel='tick discrepancy')
    axes[0].legend(fontsize=7,ncols=2)
    save(fig,'local-clock-records','Both detectors retain field samples, convective derivatives, simple zero times and slopes.',
         'Tick count uses the sign-invariant quadratic local readout; one signed-field period is two invariant ticks.',
         'Nominal isolated frequency is predicted, not fitted. Startup, finite-mode corrections and calibration error remain in the discrepancy.',
         ['Proper time integrated from tracked timelike speed; phase of (chi-i*dchi_dtau/Omega)^2, unwrapped.'],['plot-data/traces.csv'])
    fig,axes=plt.subplots(2,1,figsize=(9.5,6),layout='constrained')
    for label in ('pair-base','pair-space','pair-time','pair-wide','neutral-plus','structural-plus'):
        t=trace(label)
        # Recover the same recorded projection scale without reading raw data.
        mode0=sum(trace(label,obj)['mode_energy'][0] for obj in ('A','B'))
        axes[0].plot(t['time'],t['global_energy_balance']/mode0,label=label)
        axes[1].plot(t['time'],t['global_charge_fraction'],label=label)
    axes[0].axhline(.01,color='black',ls=':',label='future weak-mode allowance')
    axes[0].axhline(-.01,color='black',ls=':')
    axes[0].set(ylabel='energy balance /\ninitial mode energy')
    axes[1].set(xlabel='time (m$^{-1}$)',ylabel='charge balance / Q0')
    axes[0].legend(fontsize=7,ncols=2)
    save(fig,'conservation-scales','Global energy/charge include the RK4-integrated numerical absorber sinks.',
         'Small rest-energy errors can still be too large for a weak received signal; both scales remain visible.',
         'The locked engineering gate is 0.1% total E and Q. The dotted 1% mode-energy level is a disclosed future requirement, not this pilot acceptance.',
         ['Subtract initial E and Q, add recorded sinks, normalize energy to the summed initial projected modes.'],['plot-data/traces.csv','plot-data/summary.json'])
    fig,axes=plt.subplots(2,1,figsize=(9.5,6),layout='constrained')
    reference=trace('pair-base','B')
    for label in ('pair-space','pair-time','pair-wide'):
        t=trace(label,'B')
        axes[0].plot(reference['time'],(reference['local_chi']-np.interp(reference['time'],t['time'],t['local_chi']))
                     /reference['envelope'][0],label=label)
        axes[1].plot(t['time'],t['tube_momentum_balance'],label=label)
    axes[0].set(ylabel='B waveform difference /\ninitial envelope')
    axes[1].set(xlabel='time (m$^{-1}$)',ylabel='tube momentum balance (m)')
    axes[0].legend(fontsize=8)
    save(fig,'independent-controls','Space changes at fixed dt, time changes at fixed grid, and domain changes at fixed grid/dt/sponge.',
         'The output separates numerical sensitivities and exposes the continuum stress diagnostic before claiming recoil.',
         'No third-grid contraction, signal-scale momentum certification, moving worldtube or Test 9 reconstruction is claimed.',
         ['Linear alignment of saved local samples; trapezoidal integration of stress and sink rates.'],['plot-data/traces.csv','plot-data/summary.json'])
    write_json(report_path/'interpretations.json',interpretations)
    md=['# Test 8 doublet pair implementation pilot','',
        f"Run `{manifest['run_id']}`. Scientific status: **{manifest['scientific_classification']}**.",
        '', 'This report evaluates an implementation stage, not the full Test 8 acceptance campaign.',
        f"The {summary['cases'][0]['duration']:g}-time-unit startup window covers "
        f"{summary['cases'][0]['duration']*.41274991/(2*np.pi):.3f} signed clock periods. {window_limit}",
        f'{passed} engineering checks pass; long-clock survival and exchange/recoil are not evaluated.',
        '', '## Locked checks','']
    md.extend(f'- {key}: **{status}**' for key,status in summary['classification'].items())
    for key,item in interpretations.items():
        md.extend(['',f'## {key}','',*(f'{name.title()}: {value}' for name,value in item.items())])
    (report_path/'report.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    (report_path/'report.html').write_text('<html><body><pre>'+html.escape('\n'.join(md))+'</pre></body></html>',encoding='utf-8')
    with PdfPages(report_path/'report.pdf') as pdf:
        def text_page(title, paragraphs):
            page=plt.figure(figsize=(8.5,11))
            page.text(.09,.93,title,fontsize=17,weight='bold',va='top')
            y=.86
            for paragraph in paragraphs:
                lines=textwrap.wrap(paragraph,width=88)
                page.text(.09,y,'\n'.join(lines),fontsize=10.5,va='top',linespacing=1.4)
                y-=.022*len(lines)+.032
            page.text(.09,.055,'Candidate B / Test 8 implementation pilot',fontsize=9,color='#526078')
            pdf.savefig(page)
            plt.close(page)
        text_page('Two objects: the implementation stage',[
            'Question: can the unchanged action evolve both complex doublet components while retaining local detector records and auditable preparations?',
            f"This is a short startup and implementation qualification. The window is {summary['cases'][0]['duration']:g} time units, "
            f"about {summary['cases'][0]['duration']*.41274991/(2*np.pi):.3f} signed clock periods. {window_limit}",
            'Reduced preparations are measured constrained initial corrections. Neither a stationary pair nor long clock survival is established.',
            'Checks: '+', '.join(f'{k}: {v}' for k,v in summary['classification'].items()),
            'The canonical data retain both initial and final fields, conjugate momenta, checkpoints, raw local records and source energy/charge/momentum changes.',
            'Next gate: qualify free quiet-pair survival and numerical errors on the weak clock scale before a held-out exchange campaign.'
        ])
        for fig, key in zip(created,interpretations):
            pdf.savefig(fig)
            plt.close(fig)
            item=interpretations[key]
            text_page(key.replace('-',' ').title(),[f'{name.title()}: {value}' for name,value in item.items()])
    return {'required_inputs':[f"{analysis['path']}/derived/{name}" for name in ('summary.json','traces.csv','spatial.npz')]
                              +[f"{analysis['path']}/checks.json"],
            'figures':specs,'plot_data':['plot-data/summary.json','plot-data/traces.csv','plot-data/spatial.npz']}
