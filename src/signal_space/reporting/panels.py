"""Reusable saved-data scientific panels; no solver or hidden transformations."""
from pathlib import Path
import csv
import math

from signal_space.runtime.io import read_json, write_json, sha256_file

KINDS={'field-energy-flow','local-markers','clock-record','conservation','convergence','decision-margins'}


def render_panel(spec_path, output):
    """Render a declared long-form CSV (series,x,y) with source-bound semantics.

    Specifications supply kind, units, Question/Reading/Significance/Limitation,
    transformations, and a CSV SHA. A threshold, if present, is a declared
    horizontal guide in the same y units; no threshold is inferred or fitted.
    """
    spec_path=Path(spec_path).resolve();spec=read_json(spec_path)
    required={'schema_version','kind','data','sha256','x_unit','y_unit','interpretation','transformations'}
    if not required<=spec.keys() or spec.keys()-required-{'threshold'} or spec['schema_version']!='gross-panel-v1':
        raise ValueError('closed gross-panel-v1 specification required')
    if spec['kind'] not in KINDS: raise ValueError('unknown saved-data panel kind')
    if set(spec['interpretation'])!={'question','reading','significance','limitation'} or not all(spec['interpretation'].values()):
        raise ValueError('complete scientific interpretation required')
    if not spec['x_unit'] or not spec['y_unit']: raise ValueError('explicit units required')
    data=(spec_path.parent/spec['data']).resolve()
    if sha256_file(data)!=spec['sha256']: raise ValueError('panel source hash differs')
    with data.open(newline='',encoding='utf-8') as stream: rows=list(csv.DictReader(stream))
    series={}
    for row in rows:
        x,y=float(row['x']),float(row['y'])
        if not math.isfinite(x+y): raise ValueError('panel values must be finite')
        series.setdefault(row['series'],[]).append((x,y))
    if not series: raise ValueError('panel source is empty')
    output=Path(output).resolve()
    if output.exists(): raise ValueError('panel output is immutable; choose a new directory')
    output.mkdir(parents=True)
    from signal_space.workflow.pipeline import RENDER_LOCK
    with RENDER_LOCK:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
        try:
            for name,points in series.items():
                ax.plot([p[0] for p in points],[p[1] for p in points],marker='o' if spec['kind']=='local-markers' else None,label=name)
            if 'threshold' in spec:
                if not math.isfinite(spec['threshold']): raise ValueError('threshold must be finite')
                ax.axhline(spec['threshold'],color='black',ls='--',label='declared threshold')
            ax.set(xlabel=spec['x_unit'],ylabel=spec['y_unit'],title=spec['interpretation']['question'])
            ax.legend()
            for extension in ('png','pdf','svg'): fig.savefig(output/f'panel.{extension}',dpi=150)
        finally: plt.close(fig)
    import shutil
    shutil.copy2(data,output/'plot-data.csv')
    write_json(output/'panel.json',{**spec,'data':'plot-data.csv','source_spec_sha256':sha256_file(spec_path),
                                  'downsampling':'none','ordering':'saved row order; no interpolation or fits',
                                  'outputs':{p.name:sha256_file(p) for p in sorted(output.glob('panel.*'))}})
    (output/'interpretation.md').write_text('\n\n'.join(f'{k.title()}: {v}' for k,v in spec['interpretation'].items())+'\n',encoding='utf-8')
    return {'path':str(output),'source_sha256':spec['sha256']}
