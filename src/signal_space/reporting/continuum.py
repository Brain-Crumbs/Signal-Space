"""Reader figures and canonical report from immutable Test 5 analysis."""
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

QUESTIONS={
 'characteristic-surfaces':'Do all six matter sectors share one coframe null cone in shifted coordinates?',
 'action-audit':'Do action derivatives agree with the written equations on nonzero jets?',
 'failure-controls':'Do unhealthy Z and quartic orientation change distinct accepted properties?',
}


def render_report(run_path,report_path,manifest,analysis,render_provenance):
    derived=run_path/analysis['path']/'derived';plots=report_path/'plot-data';figs=report_path/'figures'
    plots.mkdir();figs.mkdir()
    names=['samples.csv','characteristics.csv','controls.json','summary.json']
    for name in names: shutil.copy2(derived/name,plots/name)
    def read_rows(name):
        with (plots/name).open(newline='') as stream: return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
    samples=read_rows('samples.csv');roots=read_rows('characteristics.csv');controls=read_json(plots/'controls.json');summary=read_json(plots/'summary.json')
    made=[];specs=[]
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,key,sources,transforms):
        write_json(figs/f'{key}.figure.json',{'schema_version':'research-figure-spec-v1','id':key,
          'source_datasets':[f'plot-data/{n}' for n in sources],'transformations':transforms,
          'axes':{'x':{'unit':'dimensionless, as labeled'},'y':{'unit':'dimensionless, as labeled'}},
          'ranges':'shown on axes','normalization':'c=hbar=m=M0=1; local covectors normalized to |k|=1',
          'downsampling':'first four of 200 samples for root overlays; all 200 samples for residuals',
          'fit_window':None,'renderer':f'matplotlib-{matplotlib.__version__}'})
        for ext in ('png','svg','pdf'): fig.savefig(figs/f'{key}.{ext}',dpi=160 if ext=='png' else None)
        made.append(fig);specs.append(f'figures/{key}.figure.json')
    fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
    for sample,color in [(0,'#236e96'),(1,'#279b76'),(2,'#ab7136'),(3,'#864c8e')]:
        for branch in (0,1):
            s=sorted((r for r in roots if r['sample']==sample and r['field']==0 and r['branch']==branch),key=lambda r:r['direction'])
            ax.plot([r['direction'] for r in s],[r['omega'] for r in s],'-',color=color,label=f'coframe {sample}' if branch==0 else None)
            other=sorted((r for r in roots if r['sample']==sample and r['field']==4 and r['branch']==branch),key=lambda r:r['direction'])
            ax.scatter([r['direction'] for r in other],[r['omega'] for r in other],marker='x',s=15,color=color)
    ax.set(xlabel='Direction index (fixed Fibonacci-sphere directions)',ylabel='Coordinate frequency omega at |k|=1',title='Lines: core; crosses: neutral field; all six roots checked in saved data')
    ax.legend(ncol=2,fontsize=8);ax.grid(alpha=.2)
    save(fig,'characteristic-surfaces',['characteristics.csv'],['display four seeded coframes and core/neutral roots; no fit','all six fields and 200 coframes retained in raw roots'])
    fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
    for key,color in [('hessian_error','#236e96'),('equation_error','#279b76')]:
        ax.scatter([r['condition_coframe'] for r in samples],[max(r[key],1e-18) for r in samples],s=13,alpha=.6,label=key.replace('_',' '),color=color)
    ax.axhline(1e-10,ls='--',color='#b7444d',label='locked gate')
    ax.set(xlabel='Coframe condition number',ylabel='Normalized residual (zeros displayed at 1e-18)',yscale='log',ylim=(1e-18,1e-8),title='200 independently sampled matter backgrounds; nonzero gradients and clock')
    ax.grid(alpha=.2);ax.legend()
    save(fig,'action-audit',['samples.csv'],['scale-normalized maximum tensor/equation residual per sample','log display floor only; exact zeros retained'])
    fig,axes=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    axes[0].bar(['valid q','Z=-0.5'],[summary['min_valid_field_kinetic_eigenvalue'],controls['negative_z']],color=['#279b76','#b7444d'])
    axes[0].axhline(0,color='black',lw=.7);axes[0].set(ylabel='Field-space kinetic eigenvalue',title='Artificial negative Z fails health')
    axes[1].bar(['SS OCF 1','quartic orientation'],[1,controls['orientation_speed']],color=['#279b76','#b7444d'])
    axes[1].set(ylim=(0,1.1),ylabel='Speed parallel to orientation gradient',title='Separate model: p=0.6, kappa=0.4')
    fig.suptitle('Test 5 | Deliberately broken controls, not alternative fits')
    save(fig,'failure-controls',['controls.json','summary.json'],['orientation speed from kinetic Hessian of separate quartic action','valid matter speed normalized to metric null speed'])
    interp={
      'characteristic-surfaces':{'question':QUESTIONS['characteristic-surfaces'],
        'reading':f"The six saved roots coincide across 20 directions on 200 coframes; maximum null-polynomial/root residual {summary['max_root_residual']:.3g}. Coordinate drift differs across coframes.",
        'significance':'The action implementation retains the selected common matter principal cone even in shifted coordinate frames.',
        'limitation':'Only four coframes and two of six fields are displayed; all saved sectors enter the check. Local frozen coefficients do not establish a metric derived from microscopic reception.'},
      'action-audit':{'question':QUESTIONS['action-audit'],
        'reading':f"Maximum Hessian residual {summary['max_hessian_residual']:.3g}; equation residual {summary['max_equation_residual']:.3g}; operator metric residual {summary['max_operator_metric_residual']:.3g} against 1e-10.",
        'significance':'Independent action polarization and complex-step force distinguish the written equations from a copied principal matrix.',
        'limitation':'Finite smooth local jets; no on-shell solution, spatial grid, long-time conservation test or nonlinear gravity constraint solution.'},
      'failure-controls':{'question':QUESTIONS['failure-controls'],
        'reading':f"Negative Z=-0.5 fails kinetic positivity; separately versioned quartic orientation action gives speed {controls['orientation_speed']:.6g} versus metric speed 1.",
        'significance':'The audit can detect both a bad kinetic sign and an extra material characteristic that a common coordinate shift cannot remove.',
        'limitation':'The quartic term is excluded from SS OCF 1 and tested on one flat static gradient. It neither proves topology protection nor exhausts all constitutive alternatives.'}}
    write_json(report_path/'interpretations.json',interp)
    lines=['# Signal Space / GROSS Test 5','',f"Technical completion: completed; bounded classification: {analysis['classification']}.",
      f"Run: {manifest['run_id']}; analysis: {analysis['analysis_id']}.",f"Solver commit: {manifest['code_identity']['revision']}; renderer commit: {render_provenance['code_identity']['revision']}",
      '', '200 seeded invertible coframes with nonzero core/neutral gradients and clock fields; six real matter fields, 20 directions and two roots each. Natural units c=hbar=m=M0=1. The Hermitian coframe and four-dimensional domain are assumptions of SS OCF 1.',
      '',f"Matter Hessian residual {summary['max_hessian_residual']:.6g}; equations {summary['max_equation_residual']:.6g}; characteristic residual {summary['max_root_residual']:.6g}.",
      f"Gravity: flat linearized harmonic-gauge TT symbol/gauge/Hamiltonian/momentum constraint residual {summary['gravity_symbol_constraint_residual']:.6g}. Nonlinear Einstein constraints and evolution were not evaluated.",
      '', 'Negative Z and separately named quartic orientation actions are failure controls. Characteristic agreement follows the chosen universal metric coupling; it is an implementation audit, not empirical support for emergence.',
      '', 'No clock, detector record, boundary/continuum convergence, stress-energy conservation in evolution, or nonlinear gravity solution is claimed.',
      '', 'Next: Test 6 bound-clock radial profile/eigenmode screen in the flat decoupling limit. Compare branches and trapping removed before long reception protocols.']
    for key,item in interp.items(): lines+=['',f'## {key}']+[f'{k.title()}: {v}' for k,v in item.items()]
    markdown='\n'.join(lines)+'\n';(report_path/'report.md').write_text(markdown)
    (report_path/'report.html').write_text("<!doctype html><html><meta charset='utf-8'><title>Test 5</title><body><pre style='white-space:pre-wrap'>"+html.escape(markdown)+'</pre>'+''.join(f"<img width='900' src='figures/{k}.svg' alt='{html.escape(q)}'>" for k,q in QUESTIONS.items())+'</body></html>')
    # Expose the PDF only after PdfPages has written its trailer and closed.
    temporary_pdf=report_path/'report.pdf.tmp'
    with PdfPages(temporary_pdf) as pdf:
        wrapped=[piece for line in lines for piece in (textwrap.wrap(line,100) or [''])]
        for start in range(0,len(wrapped),48):
            page=plt.figure(figsize=(8.5,11));page.text(.07,.96,'Continuum action: evidence and limits',fontsize=15,weight='bold',va='top')
            page.text(.07,.91,'\n'.join(wrapped[start:start+48]),fontsize=9,va='top',linespacing=1.35);pdf.savefig(page);plt.close(page)
        for fig in made: pdf.savefig(fig);plt.close(fig)
    with temporary_pdf.open('rb') as stream:
        import os
        os.fsync(stream.fileno())
    temporary_pdf.replace(report_path/'report.pdf')
    return {'required_inputs':[analysis['raw_source'],*[f"{analysis['path']}/derived/{n}" for n in names],f"{analysis['path']}/checks.json"],
            'figure_specs':specs,'interpretations':'interpretations.json'}
