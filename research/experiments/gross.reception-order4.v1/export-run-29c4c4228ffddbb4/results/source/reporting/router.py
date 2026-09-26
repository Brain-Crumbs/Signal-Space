"""Question-driven Test 3 figures, exact plot data and conditional interpretation."""
import csv
import html
import shutil
import textwrap
from signal_space.runtime.io import read_json, write_json

QUESTIONS={
'cone-sections':'Which projector arrangements yield an isotropic, anisotropic or degenerate cone?',
'continuum-convergence':'Does the actual circuit approach its predicted cone as wavelength grows?',
'order-and-direction':'Is opposite-direction asymmetry a finite-band order effect or leading drift?',
'full-zone-spectrum':'What additional low and pi-quasifrequency modes are hidden outside the origin?',
'group-directions':'Does the energy-transport direction follow the wavevector in the oblique case?',
'numerical-audit':'Do explicit port shifts conserve amplitude and agree with the independent Fourier reference?'}


def rows(path):
    with path.open(newline='') as f:
        return [{k:v if k in ('triad','order') else float(v) for k,v in row.items()} for row in csv.DictReader(f)]


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import numpy as np
    derived=run_path/analysis['path']/'derived'
    plots=report_path/'plot-data'; figures=report_path/'figures'
    plots.mkdir(); figures.mkdir()
    names=['dispersion.csv','convergence.csv','groups.csv','nodes.csv','fields.csv','zones.csv','geometry.json','surfaces.npz','summary.json']
    for name in names: shutil.copy2(derived/name,plots/name)
    d=rows(plots/'dispersion.csv'); c=rows(plots/'convergence.csv'); g=rows(plots/'groups.csv'); fields=rows(plots/'fields.csv')
    with np.load(plots/'surfaces.npz') as f: surface={k:f[k] for k in f.files}
    summary=analysis['summary']; geometry=read_json(plots/'geometry.json')
    checks=read_json(run_path/analysis['path']/'checks.json')['checks']; status={r['id']:r['status'] for r in checks}
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    labels=['orthogonal','oblique','collinear']; colors=['#196b9d','#d27630','#568e58']; made=[]; specs=[]
    def save(fig,key,sources,transforms):
        write_json(figures/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,'source_datasets':[f'plot-data/{s}' for s in sources],
          'transformations':transforms,'axes':{'x':{'unit':'dimensionless wavevector or category'},'y':{'unit':'dimensionless phase/residual or ell/tau_c as labeled'}},
          'ranges':'explicit in figure axes','normalization':'q=k ell, phase=omega tau_c; residuals as labeled','downsampling':'none; prescribed plane/direction selections only','fit_window':None,'renderer':f'matplotlib-{matplotlib.__version__}'})
        for ext in ['png','svg','pdf']: fig.savefig(figures/f'{key}.{ext}',dpi=160 if ext=='png' else None)
        made.append(fig); specs.append(f'figures/{key}.figure.json')
    fig,axes=plt.subplots(1,3,figsize=(11,4),layout='constrained')
    q=surface['surface_q']; x=q[:,0].reshape(101,101); y=q[:,1].reshape(101,101)
    for ax,label,geo in zip(axes,labels,geometry):
        exact=surface[f'{label}_forward_surface_phase'].reshape(101,101)
        gram=np.array(geo['gram']); predicted=np.sqrt(np.maximum(0,np.einsum('ni,ij,nj->n',q,gram,q))).reshape(101,101)
        ax.contour(x,y,exact,levels=[0.16],colors=['#196b9d'],linewidths=2.6)
        ax.contour(x,y,predicted,levels=[0.16],colors=['#ed9232'],linestyles='--',linewidths=1.5)
        ax.set(xlabel='qx = kx ell',ylabel='qy = ky ell',title=f'{label.title()} | Gram rank {geo["rank"]}',aspect='equal')
        ax.grid(alpha=.2)
    fig.suptitle('Test 3 | Phase = 0.16 sections at qz = 0\nBlue: exact forward circuit; dashed orange: leading cone',fontsize=12)
    save(fig,'cone-sections',['surfaces.npz','geometry.json'],['101x101 plane; matplotlib linear contour interpolation at phase 0.16','leading phase sqrt(q.G.q); no data fit'])
    fig,axes=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    for ax,order in zip(axes,['forward','reverse']):
        for label,color in zip(labels,colors):
            subset=[r for r in c if r['triad']==label and r['order']==order]
            ax.loglog([r['radius'] for r in subset],[max(r['max_cone_error'],1e-16) for r in subset],'o-',color=color,label=label)
        ax.axhline(.02,color='gray',ls=':',label='gate at smallest q')
        ax.set(xlabel='|q| = |k| ell',ylabel='max |phase² - q.G.q| / |q|²',title=f'{order.title()} order',ylim=(5e-17,.2))
        ax.legend(fontsize=8); ax.grid(alpha=.2)
    fig.suptitle('Test 3 | Leading-cone error across all 26 directions')
    save(fig,'continuum-convergence',['convergence.csv'],['maximum over all 26 directions per radius','log floor 1e-16; saved zeros retained'])
    fig,axes=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    for label,color in zip(labels,colors):
        selected=[r for r in d if r['triad']==label and r['qx']>0 and r['qy']>0 and r['qz']>0]
        forward=sorted([r for r in selected if r['order']=='forward'],key=lambda r:r['radius'])
        reverse=sorted([r for r in selected if r['order']=='reverse'],key=lambda r:r['radius'])
        neg=sorted([r for r in d if r['triad']==label and r['order']=='forward' and r['qx']<0 and r['qy']<0 and r['qz']<0],key=lambda r:r['radius'])
        radius=[r['radius'] for r in forward]
        axes[0].plot(radius,[a['phase']-b['phase'] for a,b in zip(forward,reverse)],'o-',label=label,color=color)
        axes[1].plot(radius,[(a['phase']-b['phase'])/(2*a['radius']) for a,b in zip(forward,neg)],'o-',label=label,color=color)
    axes[0].set(xlabel='|q|',ylabel='Forward phase - reversed phase',title='Same leading cone; different ordered circuit')
    axes[1].set(xlabel='|q|',ylabel='[phase(q) - phase(-q)] / (2 |q|)',title='Finite-band directional asymmetry')
    for ax in axes: ax.axhline(0,color='gray',lw=.6); ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.suptitle('Test 3 | Fixed direction (1,1,1) / sqrt(3); no drift fit')
    save(fig,'order-and-direction',['dispersion.csv'],['select body diagonal and its negative at all radii','subtract phases by order and opposite direction; no branch unwrapping across pi'])
    fig,axes=plt.subplots(2,3,figsize=(11,7),layout='constrained')
    size=32
    for col,label in enumerate(labels):
        z=surface[f'{label}_forward_zone_{size}'].reshape(size,size,size)
        for row,idx in enumerate([size//2,size//4]):
            ax=axes[row,col]
            im=ax.imshow(z[:,:,idx].T,origin='lower',extent=(-np.pi,np.pi,-np.pi,np.pi),vmin=0,vmax=np.pi,cmap='viridis',interpolation='nearest')
            ax.set(xlabel='qx',ylabel='qy',title=f'{label.title()} | qz = {"0" if row==0 else "-pi/2"}')
    fig.colorbar(im,ax=axes,label='Principal positive phase (radian)',shrink=.85)
    fig.suptitle('Test 3 | Full-zone wave bands: ±phase modulo 2 pi\nDark: zero quasiphase; bright: pi quasiphase. Memories not included.',fontsize=12)
    save(fig,'full-zone-spectrum',['surfaces.npz','zones.csv'],['32^3 forward-grid slices at qz=0 and -pi/2; nearest-cell rendering','negative band is -phase; periodic zone, no species identification'])
    fig,axes=plt.subplots(1,3,figsize=(11,4),layout='constrained')
    for ax,label in zip(axes,labels):
        subset=[r for r in g if r['triad']==label and r['order']=='forward' and abs(r['radius']-.02)<1e-9]
        # Direction IDs are joined to the saved wavevectors, no duplicated geometry law.
        ds={int(r['direction']):r for r in d if r['triad']==label and r['order']=='forward' and abs(r['radius']-.02)<1e-9 and abs(r['qz'])<1e-12}
        subset=[r for r in subset if int(r['direction']) in ds]
        for r in subset:
            point=ds[int(r['direction'])]; norm=point['radius']; base=np.array([point['qx'],point['qy']])/norm
            ax.quiver(*base,r['group_x']*.45,r['group_y']*.45,angles='xy',scale_units='xy',scale=1,color='#196b9d',width=.012)
            ax.quiver(*base,r['cone_x']*.45,r['cone_y']*.45,angles='xy',scale_units='xy',scale=1,color='#ed9232',width=.005)
            ax.plot(base[0],base[1],'.',color='black')
        ax.set(xlim=(-1.8,1.8),ylim=(-1.8,1.8),aspect='equal',xlabel='qx / |q|',ylabel='qy / |q|',title=label.title()); ax.grid(alpha=.2)
    fig.suptitle('Test 3 | Group-velocity xy projections at |q| = 0.02\nBlue: circuit derivative; thin orange: leading cone; vector scale 0.45',fontsize=12)
    save(fig,'group-directions',['groups.csv','dispersion.csv'],['select qz=0 forward points at |q|=0.02; omit band touchings explicitly','arrows show xy group components multiplied by .45; out-of-plane components remain in CSV'])
    fig,axes=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
    for i,(label,color) in enumerate(zip(labels,colors)):
        subset=[r for r in fields if r['triad']==label]
        axes[0].scatter([r['box_size']+i*.12 for r in subset],[max(r['norm_error'],1e-18) for r in subset],color=color,marker='o',label=f'{label}: norm')
        axes[0].scatter([r['box_size']+i*.12 for r in subset],[max(r['fourier_error'],1e-18) for r in subset],color=color,marker='x',label=f'{label}: FFT')
    axes[0].set(yscale='log',xlabel='Periodic box points per axis (offset for visibility)',ylabel='Absolute error; fields initially unit norm',title='Direct three-shift field update',ylim=(5e-19,1e-9)); axes[0].axhline(1e-10,color='gray',ls='--'); axes[0].legend(fontsize=7)
    keys=['fourier','rotation','finite_band','zone_reference','group_reference','group_refinement']
    axes[1].barh(keys,[max(summary['residuals'][k],1e-18) for k in keys],color='#196b9d'); axes[1].set(xscale='log',xlabel='Maximum absolute residual',title='Independent formula and derivative audits'); axes[1].axvline(1e-10,color='gray',ls='--',label='matrix gate'); axes[1].axvline(1e-6,color='#d27630',ls=':',label='gradient gate'); axes[1].legend(fontsize=8)
    fig.suptitle('Test 3 | Numerical accuracy controls; log floors retain raw zeros')
    save(fig,'numerical-audit',['fields.csv','summary.json'],['norm and FFT errors at both orders and box sizes','display floor 1e-18 only; derivative and matrix limits differ'])
    interpretations={
'cone-sections':{'question':QUESTIONS['cone-sections'],'reading':f'Gram ranks {[g["rank"] for g in geometry]}; exact and leading contours are compared at phase 0.16. Rank check: {status["triad-rank"]}.','significance':'Independent oblique projectors permit anisotropic propagation; collinear projectors remove two spatial principal directions although the internal matrix algebra is unchanged.','limitation':'A qz=0 section, with interpolation, is not a full spatial surface or detector geometry. The routing directions are assumed.'},
'continuum-convergence':{'question':QUESTIONS['continuum-convergence'],'reading':f'Largest fine-radius residual {summary["worst_cone_error_fine"]:.6g}; worst adjacent fine/coarse ratio {summary["worst_convergence_ratio"]:.6g}. Continuum check: {status["continuum"]}.','significance':'Shrinking finite-band error tests the derived Gram cone without fitting it to the measured dispersion.','limitation':'Four radii and 26 directions; this is a linear wave-sector limit, not a complete coupled-system continuum limit. Collinear roundoff values are not fitted.'},
'order-and-direction':{'question':QUESTIONS['order-and-direction'],'reading':f'Order-control status: {status["order-control"]}; independent-triad minimum of maximum order differences {summary["minimum_order_signal"]:.6g} rad. Opposite-direction odd phase is divided by |q| to expose any leading term.','significance':'The signed triple-sine term can generate directional asymmetry while the leading generator stays traceless. Order is physical incidence data.','limitation':'No leading-drift fit or invariant detector record is measured. Other backgrounds and modified routing laws remain open under Test 11.'},
'full-zone-spectrum':{'question':QUESTIONS['full-zone-spectrum'],'reading':'The full-zone check is '+status['full-zone']+'. Grid counts and exact corner/half-pi node probes are saved. The orthogonal circuit has zero and pi nodes away from the origin.','significance':'The near-origin Weyl cone cannot be interpreted as a unique physical species from the long-wavelength calculation alone.','limitation':'Finite grid inspection does not prove all nodes were found or measure topological charges. Negative wave bands are given by sign reversal; physical memory branches require Test 4.'},
'group-directions':{'question':QUESTIONS['group-directions'],'reading':f'Derivative audit: {status["group-refinement"]}. Maximum analytic-reference error {summary["residuals"]["group_reference"]:.3g}; step-halving difference {summary["residuals"]["group_refinement"]:.3g}. Collinear nodal directions have no arrows.','significance':'Oblique projector geometry can direct group transport away from the wavevector direction without requiring several metrics.','limitation':'These are spectral group derivatives, not tracked wave packets. Arrows project onto xy and exclude touchings; full components remain in saved data.'},
'numerical-audit':{'question':QUESTIONS['numerical-audit'],'reading':f'Fourier-circuit: {status["fourier-circuit"]}; conservation: {status["conservation"]}; common rotation: {status["rotation"]}. Both box sizes and both block orders are included.','significance':'Independent real-space shifts and exponential/quaternion references test signs, order, amplitudes and global basis covariance.','limitation':'Periodic boxes check implementation and norm only. There is no PDE timestep or outgoing boundary; no energy-momentum or nonlinear conservation claim follows.'}}
    write_json(report_path/'interpretations.json',interpretations)
    lines=['# Signal Space / GROSS Test 3','',f'Technical execution: completed. Scientific classification: {analysis["classification"]}.','',
      'The explicit homogeneous router is compared with a derived Gram cone. Incidence and conversion scales are assumed. The complete SS OPS 1 spectrum and autonomous clocks are not measured.',
      '',f'Run: {manifest["run_id"]}',f'Analysis: {analysis["analysis_id"]}',f'Solver commit: {manifest["code_identity"]["revision"]}',f'Config SHA-256: {manifest["config_hash"]}',f'Renderer commit: {render_provenance["code_identity"]["revision"]}',
      '', 'Locked checks:']+[f'{r["id"]}: {r["status"]}; value {r["value"]}' for r in checks]
    lines+=['','Method: exact displacement-stencil composition; independent matrix exponentials; analytic quaternion product and derivative; periodic real-space updates. All 26 signed axial/oblique directions at |q|=0.02,0.04,0.08,0.16. Three triads, two orders, zone grids 16^3/32^3 and random boxes 8^3/12^3.',
      '', 'Error budget: floating-point roundoff, finite-difference group derivatives, finite sampling and contour interpolation. No numerical time integration. Conservation is wave amplitude norm; no physical detector record or mechanical energy-momentum inferred.',
      '', 'Next: Test 4 zero-wave complete tangent spectrum, retaining physical stationary memory variations. Only then attempt one bounded self-consistent nonzero periodic background. Strong shared-cone and geometric-wave-plus-material-memory hypotheses remain distinct.']
    for key,value in interpretations.items(): lines+=['',f'## {key}']+[f'{k.title()}: {v}' for k,v in value.items()]
    markdown='\n'.join(lines)+'\n'; (report_path/'report.md').write_text(markdown)
    (report_path/'report.html').write_text("<!doctype html><meta charset='utf-8'><title>Router propagation</title><pre style='white-space:pre-wrap'>"+html.escape(markdown)+'</pre>'+''.join(f"<img width='950' src='figures/{k}.svg' alt='{html.escape(q)}'>" for k,q in QUESTIONS.items()))
    with PdfPages(report_path/'report.pdf') as pdf:
        wrapped=[part for line in lines for part in (textwrap.wrap(line,100) or [''])]
        for start in range(0,len(wrapped),47):
            page=plt.figure(figsize=(8.5,11)); page.text(.07,.96,'Router propagation: evidence and limits',fontsize=15,weight='bold',va='top'); page.text(.07,.91,'\n'.join(wrapped[start:start+47]),fontsize=9,va='top',linespacing=1.35); pdf.savefig(page); plt.close(page)
        for fig in made: pdf.savefig(fig); plt.close(fig)
    return {'required_inputs':[analysis['raw_source'],*[f'{analysis["path"]}/derived/{n}' for n in names],f'{analysis["path"]}/checks.json'],'figure_specs':specs,'interpretations':'interpretations.json'}
