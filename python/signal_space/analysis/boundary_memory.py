"""Locked transfer and prospective marker gates; legacy markers are diagnostics."""
import json
import numpy as np
from signal_space.runtime.io import read_json, write_json
from signal_space.numerics.prereception import ROOT, digest
from signal_space.numerics.boundary_memory import events
from signal_space.analysis.clock import save_csv


def analyze(run_path,output,config):
    p=config['parameters'];raw=next((run_path/'attempts').glob('*/raw'))
    derived=output/'derived';derived.mkdir(parents=True)
    log=[json.loads(x) for x in (raw.parent/'events.jsonl').read_text().splitlines()]
    valid=all(digest(ROOT/x['path'])==x['sha256'] for x in p['frozen_inputs'])
    metrics={};traces=[];drive_rows=[];scale=p['amplitude']/p['local_radius']
    for variant in p['variants']:
        name=variant['name'];lock=read_json(raw/f'lock-{name}.json')
        valid=valid and all(digest(raw/f'{kind}-{name}.npz')==lock[kind+'_sha256'] for kind in ('surface','forecast'))
        li=next(i for i,e in enumerate(log) if e['type']=='prediction-locked' and e['payload']['variant']==name)
        ai=next(i for i,e in enumerate(log) if e['type']=='source-audit-started' and e['payload']['variant']==name)
        valid=valid and li<ai and log[li]['payload']['sha256']==digest(raw/f'lock-{name}.json')
        with np.load(raw/f'forecast-{name}.npz') as f,np.load(raw/f'audit-{name}.npz') as a:
            t=f['t'];forecast=f['records'];source=a['records'];deci=f['decimated'];drives=f['drives']
            audit=read_json(raw/f'audit-{name}.json')
            for j,wave in enumerate(p['waveforms']):
                tag=name+'-'+wave['name'];row={'energy_drift':audit['relative_energy_drift'][j], 'methods':{}}
                for method,data in [('source',source[:,j]),('full',forecast[:,0,j]),('short',forecast[:,1,j]),('no_memory',forecast[:,2,j])]:
                    pair=events(t,scale*data[:,0],scale*data[:,1]);legacy=events(t,scale*data[:,0],scale*data[:,1],'legacy')
                    down=events(t[::2],scale*data[::2,0],scale*data[::2,1])
                    row['methods'][method]={'events':pair,'legacy_events':legacy,'decimated_events':down,
                        'relative_waveform_error':float(np.linalg.norm(data[:,0]-source[:,j,0])/np.linalg.norm(source[:,j,0])),
                        'max_field_error':float(scale*np.max(abs(data[:,0]-source[:,j,0])))}
                row['surface_decimated_events']=events(t,scale*deci[:,0,j,0],scale*deci[:,0,j,1])
                for method in ('full','short','no_memory'):
                    for field in ('events','legacy_events'):
                        x=row['methods'][method][field];y=row['methods']['source'][field]
                        row['methods'][method][field+'_residual']=None if x is None or y is None else (np.asarray(x)-y).tolist()
                metrics[tag]=row
                if name=='finest':
                    for k,time in enumerate(t):
                        traces.append({'wave':wave['name'],'time':float(time),'source':float(scale*source[k,j,0]),
                            'full':float(scale*forecast[k,0,j,0]),'short':float(scale*forecast[k,1,j,0]),
                            'no_memory':float(scale*forecast[k,2,j,0])})
                        drive_rows.append({'wave':wave['name'],'time':float(time),'measured_exterior':float(drives[k,j,0]),
                            'exterior_response':float(drives[k,j,1]),'incoming_drive':float(drives[k,j,2])})
    checks=[]
    def check(key,condition,value,unresolved=False):
        checks.append({'id':key,'status':'unresolved' if unresolved else ('pass' if condition else 'fail'),
            'value':value,'evidence':'derived/summary.json'})
    check('prediction-first',valid,{'hashes_and_order':valid})
    wave_error=max(row['methods']['full']['relative_waveform_error'] for row in metrics.values())
    check('boundary-waveform',wave_error<=1e-5,{'max_relative_l2':wave_error})
    energy=max(row['energy_drift'] for row in metrics.values())
    check('linear-energy',energy<=1e-6,{'max_relative_drift':energy,'clock_energy':'not evaluated'})
    budgets={};convergence={};complete=True;resolved=True;accurate=True;conv=True;sample_max=0.
    for wave in p['waveforms']:
        w=wave['name'];get=lambda grid:metrics[grid+'-'+w]
        x,f,c,tm,wide=[get(grid) for grid in ('finest','fine','coarse','time','wide')]
        budgets[w]={};convergence[w]={}
        for j,label in enumerate(('rise','fall')):
            required=[row['methods'][method]['events'] for row in (x,f,c,tm,wide) for method in ('full','source')]
            required+=[x['methods'][method]['decimated_events'] for method in ('full','source')]+[x['surface_decimated_events']]
            if any(value is None for value in required):complete=False;continue
            residual=lambda row:row['methods']['full']['events_residual'][j]
            sampling=max(abs(x['methods'][m]['events'][j]-x['methods'][m]['decimated_events'][j]) for m in ('source','full'))
            surface_sampling=abs(x['surface_decimated_events'][j]-x['methods']['full']['events'][j])
            parts={'mesh':abs(residual(x)-residual(f)),'time':abs(residual(x)-residual(tm)),
                'domain':abs(residual(f)-residual(wide)),'output_sampling':sampling,'surface_sampling':surface_sampling,'floor':1e-7}
            B=sum(parts.values());error=abs(residual(x));resolved=resolved and B<=1e-4;accurate=accurate and error<=min(B,1e-4)
            budgets[w][label]={'components':parts,'budget':B,'error':error,'target':1e-4}
            sample_max=max(sample_max,sampling,surface_sampling)
            for method in ('source','full'):
                value=lambda row:row['methods'][method]['events'][j]
                mesh=abs(value(x)-value(f));previous=abs(value(f)-value(c))
                extra=abs(value(x)-value(tm))+abs(value(f)-value(wide))+sampling+surface_sampling+1e-7
                ok=mesh<=.6*previous+extra and mesh+extra<=.1
                conv=conv and ok
                convergence[w][method+'-'+label]={'mesh_change':mesh,'previous_change':previous,'nonspatial':extra,'within_gate':ok}
    check('prospective-events',accurate and complete,budgets,not complete or not resolved)
    check('event-convergence',conv and complete,convergence,not complete or not conv)
    check('sampling',sample_max<=1e-4 and complete,{'maximum_event_change':sample_max},not complete or sample_max>1e-4)
    summary={'metrics':metrics,'budgets':budgets,'convergence':convergence,'checks':{x['id']:x['status'] for x in checks},
        'test7_acceptance':'not evaluated by this linear prerequisite','test8':'blocked pending fresh nonlinear acceptance',
        'primary_protocol':'complete t<=60 two-site acquisition and prospective first threshold excursion',
        'legacy_scope':'t<=16 and last-crossing are diagnostics, not repaired claims'}
    write_json(derived/'summary.json',summary);save_csv(derived/'traces.csv',traces);save_csv(derived/'drives.csv',drive_rows)
    result={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',result)
    return {'raw_source':str(raw.relative_to(run_path)/'execution.json'),'checks':result,'summary':summary}
