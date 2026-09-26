"""Separate event budgets, conditional observability, and causal replay checks."""
import json
import numpy as np
from signal_space.runtime.io import read_json, write_json
from signal_space.numerics.prereception import ROOT, digest
from signal_space.numerics.reconstruction import markers
from signal_space.analysis.clock import save_csv


def analyze(run_path, output, config):
    p=config['parameters'];raw=next((run_path/'attempts').glob('*/raw'))
    derived=output/'derived';derived.mkdir(parents=True)
    events=[json.loads(line) for line in (raw.parent/'events.jsonl').read_text().splitlines()]
    valid=all(digest(ROOT[x['path']])==x['sha256'] for x in p['frozen_inputs'])
    checks=[];metrics={};traces=[];singular=[]
    def check(key,condition,value,unresolved=False):
        checks.append({'id':key,'status':'unresolved' if unresolved else ('pass' if condition else 'fail'),
                       'value':value,'evidence':'derived/summary.json'})
    for variant in p['variants']:
        name=variant['name']
        index=next(i for i,e in enumerate(events) if e['type']=='variant-predictions-locked' and e['payload']['variant']==name)
        lock=read_json(raw/f'prediction-lock-{name}.json')
        valid=valid and digest(raw/f'prediction-lock-{name}.json')==events[index]['payload']['sha256']
        s=np.load(raw/f'operators-{name}.npz')['s']
        for item in lock:
            tag=item['case']
            valid=valid and all(digest(raw/f'forecast-{tag}.{ext}')==item[ext] for ext in ('npz','json'))
            valid=valid and index<next(i for i,e in enumerate(events) if e['type']=='source-audit-started' and e['payload']['case']==tag)
            forecast=read_json(raw/f'forecast-{tag}.json');audit=read_json(raw/f'audit-{tag}.json')
            with np.load(raw/f'forecast-{tag}.npz') as f, np.load(raw/f'audit-{tag}.npz') as a:
                t=f['t'];source=a['source'];row={**forecast,**audit,'sample':{},'output_sampling':{}}
                for method in ('inverse','causal','source'):
                    data=source if method=='source' else f[method]
                    m=markers(t,data,p);down=markers(t,data,p,2);older=markers(t,data,p,4)
                    row[method+'_markers']=m
                    row['sample'][method]={'full':m,'decimated2':down,'decimated4':older}
                    row['output_sampling'][method]=None if m is None or down is None else abs(np.asarray(m)-down).tolist()
                for method in ('inverse','causal'):
                    a1=row[method+'_markers'];a2=row['source_markers']
                    row[method+'_residual']=None if a1 is None or a2 is None else (np.asarray(a1)-a2).tolist()
                    row[method+'_relative_l2']=float(np.linalg.norm(f[method][:,0]-source[:,0])/np.linalg.norm(source[:,0]))
                m=row['causal_markers'];down=row['causal_surface_decimated_markers']
                row['surface_sampling']=None if m is None or down is None else abs(np.asarray(m)-down).tolist()
                row['decomposition_relative']=float(audit['decomposition_residual']/max(np.linalg.norm(source-f['inverse']),1e-300))
                row['source_minus_inverse_norm']=float(np.linalg.norm(source-f['inverse']))
                if name=='finest':
                    scale=p['amplitude']/p['local_radius']
                    traces.extend({'case':tag,'time':float(ti),'source_a':float(scale*x),'inverse_a':float(scale*y),
                        'causal_a':float(scale*z),'retained_error_a':float(scale*er),'discarded_error_a':float(scale*ed)}
                        for ti,x,y,z,er,ed in zip(t,source[:,0],f['inverse'][:,0],f['causal'][:,0],a['retained_error'][:,0],a['discarded_error'][:,0]))
                    for sense in forecast['sensitivity']:
                        singular.extend({'case':tag,'event':sense['event'],'index':j,'relative_singular_value':float(sv/s[0]),
                            'event_field_coefficient':float(c),'retained':bool(sv>p['cutoff']*s[0])}
                            for j,(sv,c) in enumerate(zip(s,sense['singular_event_coefficients'])))
                metrics[tag]=row
    check('prediction-first',valid,{'hashes_and_sequence':valid})
    decomposition=max(x['decomposition_residual']/max(x['source_minus_inverse_norm'],1e-2) for x in metrics.values())
    check('decomposition',decomposition<1e-8,{'max_relative_with_floor':decomposition})
    replay=max(x['relative_surface_residual'] for x in metrics.values())
    check('surface-replay',replay<1e-7,{'max_relative_residual':replay})
    energy=max(x['source_energy_relative_drift'] for x in metrics.values())
    check('source-energy',energy<1e-6,{'max_frozen_linear_energy_drift':energy,'clock_radiation':'not evaluated'})
    finest=[metrics['finest-'+w['name']] for w in p['waveforms']]
    sensitivity=max((e['linear_timing_sensitivity'] for row in finest for e in row['sensitivity']),default=float('inf'))
    witness_max=0.;witness_failure=False;witness_rows=[]
    for row in finest:
        for w in row['witnesses']:
            admissible=w['surface_relative_residual']<=p['surface_relative_tolerance']*(1+1e-5) and w['input_relative_change']<=p['input_radius_factor']*(1+1e-5)
            shift=None if w['marker_shift'] is None else max(abs(x) for x in w['marker_shift'])
            if admissible and (shift is None or shift>p['timing_target']):witness_failure=True
            if shift is not None and admissible:witness_max=max(witness_max,shift)
            witness_rows.append({'case':row['case'],**w,'admissible':admissible})
    check('inverse-observability',sensitivity<=p['timing_target'] and not witness_failure,
          {'max_linear_sensitivity':sensitivity,'max_admissible_witness_shift':witness_max,'finite_witness_rejects_robustness':witness_failure},
          sensitivity>p['timing_target'] and not witness_failure)
    capture=max(x['capture_energy_error_relative'] for x in metrics.values())
    check('causal-capture',capture<1e-6,{'max_capture_relative_energy_error':capture,
        'max_omitted_exterior_relative_energy':max(x['omitted_exterior_energy_relative'] for x in metrics.values())})
    budgets={};continuum={};timing_present=True;timing_ok=True;timing_resolved=True;continuum_ok=True
    for wave in p['waveforms']:
        name=wave['name'];get=lambda grid:metrics[grid+'-'+name]
        x,f,c,tm,w=get('finest'),get('fine'),get('coarse'),get('time'),get('wide')
        budgets[name]={};continuum[name]={}
        if any(row['causal_residual'] is None or any(v is None for v in row['output_sampling'].values()) or row['surface_sampling'] is None for row in (x,f,c,tm,w)):
            timing_present=False;continue
        for j,event in enumerate(('first','last')):
            parts={'mesh':abs(x['causal_residual'][j]-f['causal_residual'][j]),
                'time':abs(x['causal_residual'][j]-tm['causal_residual'][j]),
                'domain':abs(f['causal_residual'][j]-w['causal_residual'][j]),
                'output_sampling':max(x['output_sampling'][k][j] for k in ('source','causal')),
                'surface_sampling':x['surface_sampling'][j],'floor':p['floor']}
            B=sum(parts.values());error=abs(x['causal_residual'][j])
            budgets[name][event]={'components':parts,'total':B,'error':error,'target':p['timing_target'],
                'resolved':B<=p['timing_target'],'within_budget':error<=B,'within_target':error<=p['timing_target']}
            timing_resolved=timing_resolved and B<=p['timing_target']
            timing_ok=timing_ok and error<=B and error<=p['timing_target']
        for method in ('source','inverse','causal'):
            continuum[name][method]={}
            if any(row[method+'_markers'] is None for row in (x,f,c,tm,w)):
                continuum_ok=False;continue
            for j,event in enumerate(('first','last')):
                mesh=abs(x[method+'_markers'][j]-f[method+'_markers'][j]);old=abs(f[method+'_markers'][j]-c[method+'_markers'][j])
                nonspatial=abs(x[method+'_markers'][j]-tm[method+'_markers'][j])+abs(f[method+'_markers'][j]-w[method+'_markers'][j])+x['output_sampling'][method][j]+p['floor']
                if method=='causal':nonspatial+=x['surface_sampling'][j]
                ok=mesh<=.6*old+nonspatial;continuum_ok=continuum_ok and ok
                continuum[name][method][event]={'mesh':mesh,'previous_mesh':old,'nonspatial':nonspatial,'converged':ok}
    check('causal-timing',timing_ok,budgets,not timing_present or not timing_resolved)
    check('continuum-events',continuum_ok,continuum,not continuum_ok)
    sampling=max((v for row in finest for vals in list(row['output_sampling'].values())+[row['surface_sampling']] if vals is not None for v in vals),default=float('inf'))
    check('sampling',sampling<=p['timing_target'],{'maximum_event_change':sampling},sampling>p['timing_target'])
    summary={'checks':{x['id']:x['status'] for x in checks},'metrics':metrics,'event_budgets':budgets,'continuum':continuum,
        'witnesses':witness_rows,'nonlinear_reception':'not evaluated','test7_acceptance':'not evaluated; original fail retained',
        'test8':'blocked','scope':'Frozen linear neutral reconstruction, conditional single-site inverse robustness, and added two-site causal capture.'}
    write_json(derived/'summary.json',summary);save_csv(derived/'traces.csv',traces);save_csv(derived/'singular.csv',singular)
    out={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',out)
    return {'raw_source':str(raw.relative_to(run_path)/'execution.json'),'checks':out,'summary':summary}
