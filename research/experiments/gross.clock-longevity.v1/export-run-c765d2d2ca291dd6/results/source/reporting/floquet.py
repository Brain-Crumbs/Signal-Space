"""Saved-data Floquet figures; no physical evolution in the renderer."""
import csv
import html
import shutil
import textwrap
from signal_space.runtime.io import read_json, write_json
QUESTIONS={
'complete-spectrum':'Do all physical wave and memory variations propagate on one cone?',
'growth-backreaction':'Does the nonzero background activate memory response, and is exponential growth detected?',
'causal-memory-response':'Where can a local physical memory perturbation influence the circuit?',
'directional-sectors':'Does this specified routing generate leading drift or only finite-band asymmetry?',
'accuracy-audit':'Are recurrence, differential accuracy, phase redundancy and local conservation controlled?'}


def read_rows(path):
    with path.open() as f: return [{k:v if k in ('background','set') else float(v) for k,v in r.items()} for r in csv.DictReader(f)]


def render_report(run_path,report_path,manifest,analysis,render_provenance):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import numpy as np
    plots=report_path/'plot-data'; figs=report_path/'figures'; plots.mkdir(); figs.mkdir()
    names=['spectrum.csv','diagnostics.csv','impulses.csv','directional.csv','summary.json']
    for name in names: shutil.copy2(run_path/analysis['path']/'derived'/name,plots/name)
    spectrum=read_rows(plots/'spectrum.csv'); impulse=read_rows(plots/'impulses.csv'); direction=read_rows(plots/'directional.csv')
    summary=read_json(plots/'summary.json'); checks=read_json(run_path/analysis['path']/'checks.json')['checks']; labels=['vacuum','equal','counter']; colors=['#236e96','#279b76','#b7444d']; made=[]; specs=[]
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,key,sources,transforms):
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,'source_datasets':[f'plot-data/{s}' for s in sources],'transformations':transforms,'axes':{'x':{'unit':'dimensionless, as labeled'},'y':{'unit':'dimensionless, as labeled'}},'ranges':'shown on axes','normalization':'ell=tau_c=1; tangent norm is not energy','downsampling':'specified slices only; no smoothing','fit_window':None,'renderer':f'matplotlib-{matplotlib.__version__}'})
        for ext in ['png','svg','pdf']: fig.savefig(figs/f'{key}.{ext}',dpi=150 if ext=='png' else None)
        made.append(fig); specs.append(f'figures/{key}.figure.json')
    fig,axes=plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for col,label in enumerate(labels):
        for row in range(2):
            rows=[r for r in spectrum if r['background']==label and r['set']=='path' and row*65<=r['point']<(row+1)*65]
            x=[(r['point']%65)*2*np.pi/64-np.pi for r in rows]
            im=axes[row,col].scatter(x,[r['phase'] for r in rows],c=[r['memory_participation'] for r in rows],vmin=0,vmax=1,cmap='coolwarm',s=9,alpha=.65)
            axes[row,col].set(title=f'{label.title()} | '+('axis' if row==0 else 'face diagonal'),xlabel='Signed path wave number',ylabel='Quasiphase (radian)',ylim=(-3.3,3.3)); axes[row,col].grid(alpha=.2)
    fig.colorbar(im,ax=axes,label='Memory coordinate participation (not energy)',shrink=.85)
    fig.suptitle('Test 4 | All 20 physical tangent multipliers at every plotted point\nOverlapping flat modes retained; phase-sorted scatter does not track branches',fontsize=12)
    save(fig,'complete-spectrum',['spectrum.csv'],['axis and face-diagonal full-zone paths; all 20 multipliers','scatter color is eigenvector memory norm fraction; degenerate values basis-dependent'])
    fig,axes=plt.subplots(1,2,figsize=(11,4.7),layout='constrained')
    for label,color in zip(labels,colors):
        rows=[r for r in spectrum if r['background']==label and r['set']=='low']
        radii=sorted(set(round(np.linalg.norm([r['qx'],r['qy'],r['qz']]),8) for r in rows))
        growth=[max(r['growth'] for r in rows if abs(np.linalg.norm([r['qx'],r['qy'],r['qz']])-radius)<1e-7) for radius in radii]
        axes[0].plot(radii,growth,'o-',label=label,color=color)
    axes[0].axhline(1e-5,color='gray',ls=':',label='minimum growth gate'); axes[0].set_yscale('symlog',linthresh=1e-5); axes[0].set(xlabel='|q|',ylabel='Largest log |multiplier| per cycle',title='Sampled exponential growth');axes[0].legend(fontsize=8)
    axes[1].bar(labels,[max(summary['backgrounds'][l]['backreaction_difference'],1e-16) for l in labels],color=colors);axes[1].set(yscale='log',ylabel='max |full map - frozen map|',title='Does memory backreaction matter?'); axes[1].axhline(1e-3,color='gray',ls=':')
    fig.suptitle('Test 4 | Spectral growth and the frozen-memory control')
    save(fig,'growth-backreaction',['spectrum.csv','summary.json'],['maximum growth over all 26 directions and 20 modes per radius','symlog linear core 1e-5; difference display floor 1e-16'])
    fig,axes=plt.subplots(2,3,figsize=(11,6.7),layout='constrained')
    for col,label in enumerate(labels):
        selected=[r for r in impulse if r['background']==label]
        for row,kind in enumerate(['wave_norm2','memory_norm2']):
            data=np.array([[r[kind] for r in selected if r['cycle']==t] for t in range(4)])
            im=axes[row,col].imshow(np.log10(np.maximum(data,1e-14)),origin='lower',aspect='auto',extent=(-4.5,4.5,-.5,3.5),vmin=-14,vmax=max(0,float(np.log10(max(data.max(),1)))),cmap='magma',interpolation='nearest')
            axes[row,col].set(title=f'{label.title()} | '+('wave response' if row==0 else 'memory response'),xlabel='x cell offset (sum over y,z)',ylabel='Circuit cycles',yticks=range(4))
            fig.colorbar(im,ax=axes[row,col],label='log10 squared tangent amplitude',shrink=.85)
    fig.suptitle('Test 4 | Local memory-orientation impulse; no response beyond causal support\n9³ box shown, independently compared with 13³ before wraparound',fontsize=12)
    save(fig,'causal-memory-response',['impulses.csv'],['sum squared tangent components over y,z, separately wave and memory','log10 floor 1e-14; no physical energy interpretation'])
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for index,label,color in [(13,'axis','#236e96'),(16,'face diagonal','#279b76'),(25,'body diagonal','#b7444d')]:
        rows=[r for r in direction if r['direction']==index]
        axes[0].plot([r['radius'] for r in rows],[r['odd_over_radius'] for r in rows],'o-',color=color,label=label)
        axes[0].axhline(rows[0]['predicted_drift'],color=color,ls='--',lw=.8)
        axes[1].plot([r['radius'] for r in rows],[r['even_over_radius'] for r in rows],'o-',color=color,label=label)
    axes[1].axhline(.5,color='gray',ls='--',label='derived cone speed')
    axes[0].set(xlabel='|q|',ylabel='[omega_A(q)-omega_A(-q)] / (2 |q|)',title='Solid: exact upper signed A branch\nDashed: routing-derived drift')
    axes[1].set(xlabel='|q|',ylabel='[omega_A(q)+omega_A(-q)] / (2 |q|)',title='Even part approaches speed 1/2')
    for ax in axes: ax.legend(fontsize=8); ax.grid(alpha=.2)
    fig.suptitle('Test 4 / Test 11 | Port B has the opposite leading drift; memories stay flat\nThis circuit differs from Test 3. No invariant clock record is measured.',fontsize=12)
    save(fig,'directional-sectors',['directional.csv'],['independent exact complex A port block; upper signed near-origin branch','paired q/-q directions; no positive-frequency assumption or fitted metric'])
    fig,ax=plt.subplots(figsize=(10,5.5),layout='constrained')
    res=summary['residuals']; keys=['periodicity','conservation','map_refinement','ode_jacobian','vacuum_reference','phase_null','outside_causal_support','box_difference','impulse_fourier']
    ax.barh(keys,[max(res[k],1e-18) for k in keys],color='#236e96'); ax.set(xscale='log',xlabel='Maximum residual (zeros displayed at 1e-18)',title='Test 4 | Independent numerical controls');ax.axvline(1e-10,color='#279b76',ls='--',label='conservation/recurrence');ax.axvline(2e-6,color='#b7444d',ls=':',label='differential/reference');ax.legend()
    save(fig,'accuracy-audit',['summary.json'],['scalar maxima from saved independent controls; display floor 1e-18 only'])
    statuses={r['id']:r['status'] for r in checks}
    interpretations={
'complete-spectrum':{'question':QUESTIONS['complete-spectrum'],'reading':f"All 20 multipliers are retained. Vacuum has twelve stationary physical memory dimensions; memory identity residual {res['memory_identity']:.3g}. Strong vacuum cone status: {statuses['vacuum-common-cone']}.",'significance':'Propagating wave sectors do not by themselves define one geometry for the complete physical state. The equal nonzero preparation retains the vacuum obstruction.','limitation':'The displayed axis/diagonal sections are finite samples. Degenerate eigenvector colors can change basis, and neither quasiphase nor memory participation is a measured clock record.'},
'growth-backreaction':{'question':QUESTIONS['growth-backreaction'],'reading':f"Counter full/frozen difference {summary['backgrounds']['counter']['backreaction_difference']:.5g}; low-q maximum growth {summary['backgrounds']['counter']['max_low_q_growth']:.5g}. Counter stability: {statuses['counter-stability']}.",'significance':'The opposing-port background can distinguish reciprocal memory dynamics from imposed projector coefficients. Growth above numerical uncertainty would reject its stability.','limitation':'No growth detection is not a stability proof; Jordan effects, untested wavevectors and nonlinear perturbations remain. Frozen memory is an intervention, not a gauge transformation.'},
'causal-memory-response':{'question':QUESTIONS['causal-memory-response'],'reading':f"Outside-support amplitude {res['outside_causal_support']:.3g}; two-box difference {res['box_difference']:.3g}; impulse Fourier discrepancy {res['impulse_fourier']:.3g}.",'significance':'The explicit local incidence constrains response. A physical orientation perturbation can remain at rest or seed a wave depending on background.','limitation':'Three cycles of the linearized circuit, with one impulse direction. Squared tangent amplitude is not physical energy. Projection sums over transverse cells.'},
'directional-sectors':{'question':QUESTIONS['directional-sectors'],'reading':'The exact A-port odd/even phases are compared with v_A=-(1,1,1)/2 and D=I/4; B has opposite drift. All 26 directions and four radii remain in the data.','significance':'Leading drift follows from this explicit incidence. A single common coordinate shift cannot erase opposite drift in two physical port sectors. Directional asymmetry alone is not grounds to reject a geometric signal sector.','limitation':'Vacuum/equal background wave sectors only. Signed frequency pairing is used because some directions are supercritical; no clock calibration, invariant record or full operational Test 11.'},
'accuracy-audit':{'question':QUESTIONS['accuracy-audit'],'reading':f"Periodicity {res['periodicity']:.3g}; conservation {res['conservation']:.3g}; differential refinement {res['map_refinement']:.3g}; independent ODE Jacobian {res['ode_jacobian']:.3g}.",'significance':'The gates check self-consistent backgrounds, complete differential maps, exact phase redundancy and local conserved ledgers before physical interpretation.','limitation':'Deterministic tolerances are not statistical confidence. No kinetic positivity theorem, globally conserved circuit Hamiltonian, or spacetime momentum is asserted.'}}
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Signal Space / GROSS Test 4','',f"Technical execution: completed. Scientific classification: {analysis['classification']}.",'',f"Run: {manifest['run_id']}",f"Analysis: {analysis['analysis_id']}",f"Solver commit: {manifest['code_identity']['revision']}",f"Config SHA-256: {manifest['config_hash']}",f"Renderer commit: {render_provenance['code_identity']['revision']}",'','Three exact backgrounds, twenty physical tangent dimensions, six reciprocal gates. This is an explicit new routing ansatz, not a claim of equivalence to the Test 3 reduced stencil. Numerical controls and scientific cone/stability hypotheses are separate.']
    lines += [f"{r['id']}: {r['status']}; {r.get('value')}" for r in checks]
    lines += ['','Strong all-sector vacuum geometry fails only if the numerical controls pass. The equal nonzero preparation has the same decoupling. Counter stability and generic nonzero backgrounds remain separate questions. No autonomous clock, material-response completion or emergent spacetime is established.','', 'Next: derive a non-collinear unequal-port periodic background with active memory response, then test its complete tangent spectrum and withheld sectors.']
    for key,interp in interpretations.items(): lines+=['',f'## {key}']+[f'{k.title()}: {v}' for k,v in interp.items()]
    markdown='\n'.join(lines)+'\n';(report_path/'report.md').write_text(markdown)
    (report_path/'report.html').write_text("<!doctype html><meta charset='utf-8'><title>Full spectrum</title><pre style='white-space:pre-wrap'>"+html.escape(markdown)+'</pre>'+''.join(f"<img width='950' src='figures/{k}.svg' alt='{html.escape(q)}'>" for k,q in QUESTIONS.items()))
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[part for line in lines for part in (textwrap.wrap(line,100) or [''])]
        for start in range(0,len(wrapped),47):
            page=plt.figure(figsize=(8.5,11));page.text(.07,.96,'Full reciprocal spectrum: evidence and limits',fontsize=15,weight='bold',va='top');page.text(.07,.91,'\n'.join(wrapped[start:start+47]),fontsize=9,va='top',linespacing=1.35);pdf.savefig(page);plt.close(page)
        for fig in made: pdf.savefig(fig);plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],*[f"{analysis['path']}/derived/{n}" for n in names],f"{analysis['path']}/checks.json"],'figure_specs':specs,'interpretations':'interpretations.json'}
