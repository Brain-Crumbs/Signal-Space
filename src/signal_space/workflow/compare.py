"""Saved-result comparisons with explicit scientific compatibility and source hashes."""
from pathlib import Path
import csv

from signal_space.runtime.io import read_json, write_json, sha256_file
from signal_space.runtime.verify import verify_package
from signal_space.workflow.plans import ROOT


def differences(left, right, path=''):
    if type(left) is not type(right): return [{'path':path,'left':left,'right':right}]
    if isinstance(left,dict):
        result=[]
        for key in sorted(left.keys()|right.keys()):
            if key not in left or key not in right: result.append({'path':f'{path}/{key}','left':left.get(key),'right':right.get(key)})
            else: result.extend(differences(left[key],right[key],f'{path}/{key}'))
        return result
    if isinstance(left,list) and len(left)==len(right):
        return [row for i,(a,b) in enumerate(zip(left,right)) for row in differences(a,b,f'{path}/{i}')]
    return [] if left==right else [{'path':path,'left':left,'right':right}]


def numerical_change(path):
    if path.startswith(('/resources/','/parameters/execution/')): return True
    # Explicitly scoped controls. Every other parameter change blocks numerical
    # subtraction, including frozen profile/forecast hashes and random seeds.
    return path.startswith('/parameters/scenarios/') and path.rsplit('/',1)[-1] in {
        'h','dt','radius','half_length','absorber_width','absorber_strength','sample_stride'}


def numbers(value, path=''):
    if isinstance(value,dict):
        return {k:v for key,child in value.items() for k,v in numbers(child,f'{path}/{key}').items()}
    if isinstance(value,list):
        return {k:v for i,child in enumerate(value) for k,v in numbers(child,f'{path}/{i}').items()}
    return {path:value} if type(value) in (int,float) else {}


def _source(path):
    path=Path(path).resolve()
    result=verify_package(path)
    if not result['valid']: raise ValueError(f'comparison source is invalid: {path}: {result.get("errors")}')
    manifest=read_json(path/'manifest.json')
    if not manifest['analyses']: raise ValueError('comparison requires saved analysis')
    analysis=manifest['analyses'][-1]
    checks=read_json(path/analysis['path']/'checks.json')['checks']
    return path,manifest,analysis,read_json(path/'resolved-config.json'),checks


def compare(left, right, output=None):
    a,am,aa,ac,ach=_source(left);b,bm,ba,bc,bch=_source(right)
    delta=differences(ac,bc)
    incompatible=[r['path'] for r in delta if not numerical_change(r['path'])]
    compatible=not incompatible
    rows=[]; left_checks={x['id']:x for x in ach};right_checks={x['id']:x for x in bch}
    for key in sorted(left_checks.keys()&right_checks.keys()):
        av,bv=left_checks[key],right_checks[key]
        row={'id':key,'left_status':av['status'],'right_status':bv['status'],'quantities':[]}
        if compatible:
            an,bn=numbers(av.get('value')),numbers(bv.get('value'))
            row['quantities']=[{'path':p,'left':an[p],'right':bn[p],'difference':bn[p]-an[p]}
                               for p in sorted(an.keys()&bn.keys())]
        rows.append(row)
    record={'schema_version':'gross-comparison-v1','compatible':compatible,'config_differences':delta,
            'blocked_quantities':incompatible,'checks':rows,
            'unmatched_checks':{'left':sorted(left_checks.keys()-right_checks.keys()),'right':sorted(right_checks.keys()-left_checks.keys())},
            'sources':[{'path':str(path),'run_id':m['run_id'],'analysis_id':analysis['analysis_id'],
                        'classification':analysis['classification'],'manifest_sha256':sha256_file(path/'manifest.json'),
                        'code_identity':m['code_identity'],'execution_identity':m['execution_identity']}
                       for path,m,analysis in ((a,am,aa),(b,bm,ba))],
            'interpretation':{'question':'Which saved checks change between these explicit configurations?',
                'reading':'Configuration differences precede shared check values. Difference is right minus left; no normalization or acceptance inference.',
                'significance':'Compatible saved checks expose clock, conservation, response and convergence differences in their original units.',
                'limitation':'Different physical inputs, calibration, seeds or criteria block numerical subtraction. Matching check IDs do not establish scientific equivalence; original figures retain event and field detail.'}}
    if output:
        output=Path(output).resolve()
        if output.is_relative_to(ROOT) or output.exists(): raise ValueError('comparison needs a new external directory')
        output.mkdir(parents=True)
        write_json(output/'comparison.json',record)
        with (output/'quantities.csv').open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=['check','path','left','right','difference']);writer.writeheader()
            for row in rows:
                writer.writerows({'check':row['id'],**q} for q in row['quantities'])
        lines=['# Saved-run comparison','',f'Numerical subtraction compatible: **{compatible}**.','',
               '## Configuration differences','', '| Path | Left | Right |','| --- | --- | --- |']
        for row in delta: lines.append(f"| {row['path']} | {str(row['left']).replace('|','/')} | {str(row['right']).replace('|','/')} |")
        lines += ['', '## Shared checks', '', '| Check | Left | Right |','| --- | --- | --- |']
        lines += [f"| {r['id']} | {r['left_status']} | {r['right_status']} |" for r in rows]
        lines += ['',*[f"{k.title()}: {v}\n" for k,v in record['interpretation'].items()]]
        (output/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        record['output']=str(output)
    return record
