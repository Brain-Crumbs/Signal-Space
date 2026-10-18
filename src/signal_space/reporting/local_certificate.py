"""Intuition-first pilot figures from immutable saved proof data only."""
import csv
import shutil
import textwrap
from signal_space.runtime.io import read_json,write_json


def render_report(run_path,output,manifest,analysis,render_provenance):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    data=output/'plot-data';figures=output/'figures'
    data.mkdir();figures.mkdir()
    derived=run_path/analysis['path']/'derived'
    shutil.copy2(derived/'record-budgets.csv',data/'record-budgets.csv')
    shutil.copy2(derived/'summary.json',data/'summary.json')
    raw=run_path/analysis['raw_source'];summary=analysis['summary']
    with (data/'record-budgets.csv').open() as f:rows=list(csv.DictReader(f))
    states=[]
    for seed in ('active-plus','active-minus'):
        packet=read_json(raw.parent/f'{seed}-96.json')
        for n,center in [(0,packet['initial_center'])]+[(s['index'],s['center']) for s in packet['steps']]:
            from fractions import Fraction
            vals=[float(Fraction(int(x['lo']),1<<x['bits'])) for x in center]
            states.append(dict(seed=seed,endpoint=n,A_x=2*vals[12],A_y=2*vals[13],B_x=2*vals[15],B_y=2*vals[16]))
    from signal_space.numerics.operators import write_rows
    write_rows(data/'internal-endpoints.csv',states)
    made=[];specs=[];interpretations={}
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,key,sources,question,reading,significance,limitation):
        for ext in ('png','svg','pdf'):fig.savefig(figures/f'{key}.{ext}',dpi=160,bbox_inches='tight')
        spec=dict(schema_version='research-figure-spec-v1',id=key,
            source_datasets=['plot-data/'+s for s in sources],transformations=['96-bit endpoint centers or max over three records; no fitted/smoothed data'],
            axes={'x':{'unit':'ordered endpoint or internal Bloch coordinate'},'y':{'unit':'dimensionless'}},
            ranges='labelled axes; log bounds plotted without replacing exact data',normalization='P=I/2+x.sigma; physical radius1e-6',
            downsampling='none',fit_window=None,renderer='matplotlib-'+matplotlib.__version__)
        write_json(figures/f'{key}.figure.json',spec);specs.append(f'figures/{key}.figure.json');made.append(fig)
        interpretations[key]=dict(question=question,reading=reading,significance=significance,limitation=limitation)
    fig,axes=plt.subplots(1,2,figsize=(10,4.4),layout='constrained')
    for ax,seed in zip(axes,('active-plus','active-minus')):
        selected=[s for s in states if s['seed']==seed]
        for memory,marker in (('A','o'),('B','s')):
            ax.scatter([s[memory+'_x'] for s in selected],[s[memory+'_y'] for s in selected],label='Memory '+memory,marker=marker,s=70)
            for s in selected:ax.annotate(str(s['endpoint']),(s[memory+'_x'],s[memory+'_y']),xytext=(5,5),textcoords='offset points')
        ax.set(xlabel='Internal Bloch x',ylabel='Internal Bloch y',title=seed,xlim=(-1.1,1.1),ylim=(-1.1,1.1),aspect='equal');ax.legend()
    save(fig,'internal-endpoints',['internal-endpoints.csv'],
         'What changes while local records remain predictable?',
         'Markers0,1,2 are the initial state and the A/B gate endpoints. Memories can move internally even when their record bounds remain small.',
         'Separates internal deformation from loss of readable records.',
         'A two-coordinate projection of numerical reference centers, not physical space or a within-gate path. Coincident markers can overlap.')
    fig,axes=plt.subplots(1,2,figsize=(10,4.4),layout='constrained')
    for seed,color in (('active-plus','#247d76'),('active-minus','#526ab2')):
        for bits,style in (('96','-o'),('128','--s')):
            chosen=[r for r in rows if r['seed']==seed and r['bits']==bits]
            for field,ax in (('preparation',axes[0]),('numerical',axes[1]),('readout',axes[1])):
                if not chosen:
                    ax.text(.5,.5,'No qualified record prefix',transform=ax.transAxes,ha='center');continue
                ys=[max(float(r[field]) for r in chosen if r['endpoint']==str(n)) for n in (1,2)]
                ax.semilogy([1,2],ys,style,color=color,label=f'{seed}/{bits} {field}',markersize=5)
    axes[0].axhline(.00025,color='#ad5555',ls=':',label='Preparation allocation')
    axes[0].set(title='Whole preparation ball',ylabel='Maximum bound over three records')
    axes[1].set(title='Numerical and readout contributions',ylabel='Outward upper bound')
    for ax in axes:ax.set(xlabel='Ordered endpoint (A=1, B=2)',xticks=[1,2]);ax.legend(fontsize=7)
    save(fig,'record-budgets',['record-budgets.csv'],
         'Does every endpoint fit every allocation?',
         'Preparation error dominates this short pilot. Numerical and scalar readout bounds are many orders smaller. Each curve is independently enclosed.',
         'Tests combined perturbations across all sixteen physical directions, with separate error allocations.',
         'Only one cycle. A smaller rounding width at higher precision does not remove later nonlinear growth or wrapping. No extrapolated horizon is certified.')
    write_json(output/'interpretations.json',interpretations)
    est=summary['confirmatory_estimate'];blocked=not summary['launch_allowed']
    paragraphs=[f"Scientific pilot classification: {analysis['classification']}. Confirmation launch: {'BLOCKED' if blocked else 'admissible subject to a separate lock'}.",
      'Question: Can the full physical preparation ball keep all three mathematical records predictable through one ordered AB cycle?',
      'Model: unchanged SS OPS1 lambda=0, exact pi/2, three coherent ports and two projector memories. Gate order and transports are supplied; the gate parameter is dimensionless.',
      'The mechanism: transport all sixteen initial directions in eighteen ambient coordinates, and keep every nonlinear/arithmetic forcing across switches. Local records can be insensitive to large internal state changes.',
      'Preparation compares exact perturbed and exact nominal records. Numerical compares exact nominal and the stored reference. Readout bounds scalar evaluation. The total must fit1e-3 and each allocation2.5e-4.',
      'Both active seeds and both declared precisions are checked at every one-cycle A/B endpoint. Numerical agreement alone is not a certificate: source, tube, curvature, product and readout obligations are independently reconstructed.',
      f"Measured worker CPU/wall: {summary['worker_metrics']['cpu_seconds']:.3f}s / {summary['worker_metrics']['wall_seconds']:.3f}s. RSS method: {summary['worker_metrics']['rss_measurement']}.",
      f"Conservative confirmation extrapolation: CPU {est['cpu_seconds']:.1f}s, wall {est['wall_seconds']:.1f}s; worker allowance190s, with50s separately reserved for saved analysis. This is not a measured32-cycle runtime.",
      'Admission blockers: '+('; '.join(summary['blockers']) or 'none'),
      'A blocked launch is unresolved feasibility, not evidence that records fail. No32-cycle confirmation was run. A larger campaign or sharper measured cost qualification needs a new reviewed lock and budget decision.',
      'No physical detector noise, within-gate uniformity, all-time stability, autonomous clock or emergent geometry is claimed. Tests1-11 and CandidateB classifications remain unchanged.',
      f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; source {manifest['code_identity']['revision']}."]
    lines=['# C1 one-cycle pilot and launch readiness','']+paragraphs
    for key,parts in interpretations.items():lines+=['',key]+[k.title()+': '+v for k,v in parts.items()]
    (output/'report.md').write_text('\n\n'.join(lines)+'\n')
    import html
    (output/'report.html').write_text('<html><meta charset="utf-8"><body><pre style="white-space:pre-wrap">'+html.escape('\n\n'.join(lines))+'</pre></body></html>')
    with PdfPages(output/'report.pdf') as pdf:
        # Two explanatory pages keep type readable; figures have their own pages.
        for start in (0,6):
            page=plt.figure(figsize=(8.5,11));page.text(.08,.95,'C1 | One-cycle records and launch gate',fontsize=16,weight='bold',va='top')
            content='\n\n'.join('\n'.join(textwrap.wrap(p,89)) for p in paragraphs[start:start+6])
            page.text(.08,.89,content,fontsize=10,va='top',linespacing=1.35)
            pdf.savefig(page);plt.close(page)
        for key,fig in zip(interpretations,made):
            fig.text(.5,-.03,'Question: '+interpretations[key]['question'],ha='center',fontsize=10)
            pdf.savefig(fig,bbox_inches='tight');plt.close(fig)
    return dict(required_inputs=[analysis['raw_source'],f"{analysis['path']}/checks.json",f"{analysis['path']}/derived/summary.json",f"{analysis['path']}/derived/record-budgets.csv"],
                figure_specs=specs,interpretations='interpretations.json')
