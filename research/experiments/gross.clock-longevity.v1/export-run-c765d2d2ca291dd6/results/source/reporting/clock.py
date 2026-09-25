"""Question-driven figures and canonical report from saved Test 6 analysis."""
import csv
import html
import shutil
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from signal_space.runtime.io import read_json, write_json

QUESTIONS={
 'core-and-well':'Which trial core supplies a spatial mass well and localized clock eigenfunction?',
 'bound-control':'Does the bound eigenvalue survive resolution controls and disappear without trapping?',
 'local-trace':'Does a local field trace tick for 100 periods when the unexcited core does not?',
 'lifetime-convergence':'Does the mode persist with controlled charge, amplitude, grid and boundary errors?'
}


def render_report(run_path,report_path,manifest,analysis,render_provenance):
    derived=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figs=report_path/'figures'
    plots.mkdir();figs.mkdir()
    for name in ('profiles.csv','radial.csv','refinements.csv','evolutions.csv','summary.json'):
        if (derived/name).is_file():shutil.copy2(derived/name,plots/name)
    summary=read_json(plots/'summary.json');selected=summary['selection']
    def rows(name):
        if not (plots/name).is_file():return []
        with (plots/name).open(newline='') as stream:return list(csv.DictReader(stream))
    profiles=rows('profiles.csv');radial=rows('radial.csv');evolutions=rows('evolutions.csv')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    made=[];specs=[]
    def save(fig,key,sources,transforms,axes,downsampling):
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,
            'source_datasets':[f'plot-data/{n}' for n in sources],
            'transformations':transforms,'axes':axes,'ranges':'shown on axes',
            'normalization':'c=hbar=m=1; radial fields normalized as labeled',
            'downsampling':downsampling,'fit_window':None,
            'renderer':f'matplotlib-{matplotlib.__version__}'})
        for ext in ('png','svg','pdf'):fig.savefig(figs/f'{key}.{ext}',dpi=160 if ext=='png' else None)
        made.append(fig);specs.append(f'figures/{key}.figure.json')
    def missing(ax):
        ax.text(.5,.5,'No accepted core; dependent record unresolved',ha='center',va='center',transform=ax.transAxes)
        ax.set(xticks=[],yticks=[])

    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    if selected:
        x=[float(z['radius']) for z in radial]
        axes[0].plot(x,[float(z['core']) for z in radial],label='core F(r)')
        axes[0].plot(x,[float(z['mode']) for z in radial],label='clock f(r) (L2 normalized)')
        axes[0].legend();axes[0].set(xlim=(0,60),xlabel='radius (m^-1)',ylabel='field / normalized eigenmode')
        axes[1].plot(x,[float(z['well']) for z in radial],label='V chi(F²)')
        axes[1].axhline(.25,color='#b7444d',ls='--',label='vacuum continuum')
        axes[1].axhline(summary['selected_profile']['eigenvalue'],color='#269777',ls=':',label='lowest eigenvalue')
        axes[1].set(xlim=(0,60),xlabel='radius (m^-1)',ylabel='clock mass squared (m²)');axes[1].legend()
    else:
        for ax in axes:missing(ax)
    fig.suptitle('Spatial core and independently computed clock mode')
    save(fig,'core-and-well',['radial.csv','summary.json'] if selected else ['profiles.csv','summary.json'],
         ['F=u/r and mode=f/r for r>0; no spatial smoothing','show first 60 radial units'],
         {'x':{'unit':'m^-1'},'y':{'unit':'field or m²'}},'display first 60 units; full domain saved')

    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    numeric=[z for z in profiles if z.get('profile')=='solved']
    if numeric:
        axes[0].scatter([float(z['omega']) for z in numeric],[float(z['E_over_Q']) for z in numeric],label='solved E/Q')
        axes[0].axhline(1,color='#b7444d',ls='--',label='free quantum mass')
        absent=[z for z in profiles if z.get('profile')!='solved']
        for z in absent:
            axes[0].annotate('unresolved', (float(z['omega']),.99), rotation=60,
                             fontsize=8,color='#b7444d')
        if absent:axes[0].scatter([float(z['omega']) for z in absent],[.99]*len(absent),marker='x',color='#b7444d')
        axes[0].set(xlabel='core phase frequency / m',ylabel='E/(m Q)');axes[0].legend()
        if selected:
            c=summary['selected_profile']['eigenvalue']
            labels=['base','h/2','2R','nu=0']
            values=[c,*[next((z['eigenvalue'] for z in summary['refinements'] if z['label']==n and z['status']=='solved'),float('nan')) for n in ('fine','wide')],summary['controls']['nu-off']['eigenvalue']]
            axes[1].scatter(labels,values,color=['#236e96','#279b76','#ab7136','#b7444d'])
            axes[1].axhline(.25,color='#b7444d',ls='--',label='continuum threshold')
            axes[1].set(ylabel='lowest clock eigenvalue (m²)');axes[1].legend()
        else:missing(axes[1])
    else:
        for ax in axes:missing(ax)
    fig.suptitle('Core energetics and trapping failure control')
    save(fig,'bound-control',['profiles.csv','refinements.csv','summary.json'] if selected else ['profiles.csv','summary.json'],
         ['plot eigenvalue directly; no fit','threshold fixed at vacuum V chi(0)=0.25'],
         {'x':{'unit':'branch frequency or control'},'y':{'unit':'E/Q or m²'}},'all solved trial profiles')

    fig,axes=plt.subplots(2,1,figsize=(10,6),layout='constrained')
    if selected:
        period=2*3.141592653589793/summary['omega_chi']
        for key,color,lab in [('0.0000','#b7444d','unexcited'),('0.0010','#236e96','weak clock')]:
            trace=[z for z in evolutions if z['preparation']==key]
            for ax,left,right in [(axes[0],0,5*period),(axes[1],95*period,100*period)]:
                subset=[z for z in trace if left<=float(z['time'])<=right]
                ax.plot([float(z['time'])/period for z in subset],[float(z['local_chi']) for z in subset],
                        color=color,label=lab)
        axes[0].set(xlabel='time / eigenperiod',ylabel='local chi (m)',title='first five periods')
        axes[1].set(xlabel='time / eigenperiod',ylabel='local chi (m)',title='last five periods')
        axes[0].legend()
    else:
        for ax in axes:missing(ax)
    fig.suptitle('Local readout near core center, not a global fitted projection')
    save(fig,'local-trace',['evolutions.csv','summary.json'] if selected else ['summary.json'],
         ['plot saved r=dr local trace; no interpolation in display','time divided by independent eigenperiod'],
         {'x':{'unit':'eigenperiods'},'y':{'unit':'m'}},'first and last five of nominal 100 periods')

    fig,axes=plt.subplots(2,2,figsize=(11,7.5),layout='constrained')
    if selected:
        main=[z for z in evolutions if z['preparation']=='0.0010']
        x=[float(z['time'])*summary['omega_chi']/(2*3.141592653589793) for z in main]
        axes[0,0].semilogy(x,[max(abs(1-float(z['mode_energy_fraction'])),1e-10) for z in main],label='absolute mode-energy change')
        axes[0,0].axhline(.01,color='#b7444d',ls='--',label='1% gate')
        axes[0,0].set(xlabel='nominal eigenperiods',ylabel='|1 - E mode / E0| (log)',title='100-period lifetime');axes[0,0].legend(fontsize=8)
        axes[0,1].semilogy(x,[max(abs(float(z['charge_balance_fraction'])),1e-18) for z in main],label='charge after sponge sink')
        axes[0,1].axhline(.01,color='#b7444d',ls='--',label='1% gate')
        axes[0,1].set(xlabel='nominal eigenperiods',ylabel='|Q+sink-Q0| / Q0 (log)',title='charge ledger');axes[0,1].legend(fontsize=8)
        labels=['half','nominal','double','h/2','2R']
        keys=['0.0005','0.0010','0.0020','fine','wide']
        offsets=[1e6*(summary['observations'][k]['frequency']/summary['omega_chi']-1) for k in keys]
        axes[1,0].bar(labels,offsets,color=['#279b76','#236e96','#279b76','#ab7136','#ab7136'])
        axes[1,0].axhline(0,color='black',lw=.7)
        axes[1,0].set(ylabel='(local / eigen - 1), ppm',title='20-period controls; nominal shown over 100')
        residual=[(float(z['total_energy'])+float(z['outer_energy_sink'])-float(main[0]['total_energy']))/
                   summary['nominal_mode_initial_energy'] for z in main]
        axes[1,1].plot(x,residual,color='#864c8e')
        axes[1,1].set(xlabel='nominal eigenperiods',ylabel='total-energy ledger residual / initial clock energy',
                      title='Clock-scale radiation energy unresolved')
    else:
        for ax in axes.flat:missing(ax)
    fig.suptitle('Mode, charge and background energy ledgers with frequency controls')
    save(fig,'lifetime-convergence',['evolutions.csv','summary.json'] if selected else ['summary.json'],
         ['projected eigenmode energy from saved quadratures','finite outer sink added to charge balance'],
         {'x':{'unit':'eigenperiods'},'y':{'unit':'relative'}},'all nominal saved samples')

    if selected:
        base=summary['observations']['0.0010'];c=summary['selected_profile']
        interpretations={
         'core-and-well':{'question':QUESTIONS['core-and-well'],
             'reading':f"Selected omega_Q={c['omega']:.3f}; core center F={c['center']:.4g}; clock eigenvalue {c['eigenvalue']:.6g} below vacuum 0.25.",
             'significance':'The declared core density produces a spatially resolved clock mass well and a separately solved localized mode.',
             'limitation':'Flat spherical branch only; neither gravity nor nonspherical perturbations follow from this profile.'},
         'bound-control':{'question':QUESTIONS['bound-control'],
             'reading':f"Selected E/Q={c['E_over_Q']:.6g}; removing nu gives lowest eigenvalue {summary['controls']['nu-off']['eigenvalue']:.6g} versus 0.25 threshold. Eigen error estimate {summary['eigen_error_estimate']:.3g}.",
             'significance':'The trapping coefficient is causally relevant to this bound mode in the registered family.',
             'limitation':'A finite-box eigenvalue above 0.25 is a nonbound control. Radial Hessian diagnostics do not exclude all nonlinear or angular instabilities.'},
         'local-trace':{'question':QUESTIONS['local-trace'],
             'reading':f"Nominal local trace completes {base['signed_cycles']:.2f} inferred signed cycles; local frequency {base['frequency']:.6g} versus eigenfrequency {summary['omega_chi']:.6g}. Unexcited trace is zero.",
             'significance':'Unlike the stationary core density/projector, the field sampled inside the core has a repeatable local zero-crossing record.',
             'limitation':'This is an ideal local field probe in the flat limit. Marker coupling, device noise and invariant reception comparison are future tests.'},
         'lifetime-convergence':{'question':QUESTIONS['lifetime-convergence'],
         'reading':f"Over 100 periods mode-energy loss {summary['mode_energy_loss_fraction']:.3g}; maximum charge ledger error {base['max_charge_balance_error']:.3g}; short-run frequency grid/domain difference {summary['frequency_convergence_fraction']:.3g}. Total-energy ledger residual is {summary['energy_residual_over_clock_mode']:.3g} initial clock-mode energies.",
         'significance':'The duration and numerical controls quantify whether this core can provisionally serve as Test 7 calibration.',
         'limitation':'Refined/wider runs and half/double amplitude controls cover 20 periods. Background-scale energy error exceeds the clock energy, so sponge loss cannot be assigned to clock radiation; nonspherical dynamics are untested.'}}
    else:
        interpretations={key:{'question':q,'reading':'No accepted bound core was found in the locked trial set; dependent figure is blank.',
            'significance':'This run cannot calibrate a local clock for reception.',
            'limitation':'Review profile attempts and uncertainty before interpreting this as a universal no-go.'} for key,q in QUESTIONS.items()}
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Signal Space / GROSS Test 6','',f"Technical completion: completed; bounded scientific classification: {analysis['classification']}.",
           f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}.",
           f"Solver revision {manifest['code_identity']['revision']}; renderer revision {render_provenance['code_identity']['revision']}.",
           '','Flat decoupling limit of SS OCF 1, c=hbar=m=1; constant internal doublet direction, a=0, gravity decoupled.',
           'Four trial core frequencies 0.868, 0.875, 0.90, 0.94. Independently solved bound spectrum and trapping-off control.',
           'Nominal peak chi=0.001 for 100 eigenperiods; zero, half and double controls for 20 periods; independent h/2 and 2R controls for 20 periods.',
           '',f"Selected branch: {selected or 'none'}. Numerically unresolved trial profiles: {', '.join(summary['unresolved_profile_samples']) or 'none'}; these are not evidence against those branches.",
           'Outer energy sink is recorded, but background energy residual is too large relative to clock-mode energy to isolate radiated clock energy.',
           'No emergent geometry, Test 7 reception or nonspherical stability established.']
    for key,item in interpretations.items():
        lines+=['',f'## {key}']+[f'{heading.title()}: {content}' for heading,content in item.items()]
    markdown='\n'.join(lines)+'\n';(report_path/'report.md').write_text(markdown)
    (report_path/'report.html').write_text("<!doctype html><html><meta charset='utf-8'><title>Test 6</title><body><pre style='white-space:pre-wrap'>"+html.escape(markdown)+'</pre>'+''.join(f"<img width='900' src='figures/{k}.svg' alt='{html.escape(q)}'>" for k,q in QUESTIONS.items())+'</body></html>')
    temporary=report_path/'report.pdf.tmp'
    with PdfPages(temporary) as pdf:
        wrapped=[piece for line in lines for piece in (textwrap.wrap(line,100) or [''])]
        for start in range(0,len(wrapped),45):
            page=plt.figure(figsize=(8.5,11));page.text(.07,.96,'Bound clock: evidence and limits',fontsize=15,weight='bold',va='top')
            page.text(.07,.91,'\n'.join(wrapped[start:start+45]),fontsize=8.5,va='top',linespacing=1.33)
            pdf.savefig(page);plt.close(page)
        for fig in made:pdf.savefig(fig);plt.close(fig)
    with temporary.open('rb') as stream:
        import os
        os.fsync(stream.fileno())
    temporary.replace(report_path/'report.pdf')
    return {'required_inputs':[analysis['raw_source'],*[f"{analysis['path']}/derived/{n}" for n in ('profiles.csv','summary.json')],
                                f"{analysis['path']}/checks.json"],
            'figure_specs':specs,'interpretations':'interpretations.json'}
