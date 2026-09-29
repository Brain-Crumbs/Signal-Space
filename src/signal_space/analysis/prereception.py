"""Immutable analysis of the two locked Test 6 prerequisites."""
import hashlib
import json
import numpy as np
from signal_space.analysis.clock import oscillation, save_csv, RECORD_COLUMNS
from signal_space.runtime.io import read_json, write_json

def zeros(t,y):
    i=np.flatnonzero((y[:-1]<0)&(y[1:]>=0))
    return t[i]-y[i]*(t[i+1]-t[i])/(y[i+1]-y[i])

def relative(x,y):
    den=np.linalg.norm(y)
    return float(np.linalg.norm(x-y)/den) if den>1e-30 else None

def analyze(run_path, output, config):
    sources=sorted((run_path/'attempts').glob('*/raw/execution.json'))
    if len(sources)!=1:raise ValueError('expected exactly one completed atomic attempt')
    raw=sources[0].parent;execution=read_json(sources[0]);kind=execution['kind'];p=config['parameters']
    derived=output/'derived';derived.mkdir(parents=True);checks=[];rows=[]
    summary={'kind':kind,'source_run':execution['source_run'],'calibration':execution['calibration'],'metrics':{}}
    def check(key,ok,value,status=None):
        checks.append({'id':key,'status':status or ('pass' if ok else 'fail'),'value':value,'evidence':'derived/summary.json'})
    hashes=[hashlib.sha256((raw/x['name']).read_bytes()).hexdigest()==x['sha256'] for x in p['frozen_inputs']]
    check('frozen-inputs',all(hashes),hashes)
    if kind=='longevity':
        obs={};traces={}
        for item in execution['details']:
            label=item['label'];d=np.load(raw/f'longevity-{label}.npz')['records'];traces[label]=d
            if not np.isfinite(d).all():raise ValueError('nonfinite longevity data')
            obs[label]={**oscillation(d),'mode_energy_change':float(d[-1,4]-1),
              'charge_error':float(np.max(abs(d[:,6]))),'core_peak_shift':float(np.max(abs(d[:,9]/d[0,9]-1))),
              'energy_residual_over_mode':float((d[-1,7]+d[-1,8]-d[0,7])/item['initial_mode_energy']),
              'duration':float(d[-1,0])}
            for line in d:rows.append({'preparation':label,**dict(zip(RECORD_COLUMNS,map(float,line)))})
        freqdiff=max(abs(obs[k]['frequency']/obs['base']['frequency']-1) for k in ('fine','time'))
        modediff=max(abs(obs[k]['mode_energy_change']-obs['base']['mode_energy_change']) for k in ('fine','time'))
        check('local-record',all(x['crossings']>=99 and abs(x['frequency']/p['omega_chi']-1)<.02 for x in obs.values()),obs)
        check('lifetime',all(abs(x['mode_energy_change'])<.01 for x in obs.values()),{k:x['mode_energy_change'] for k,x in obs.items()})
        check('convergence',freqdiff<.01 and modediff<.01,{'frequency_relative':freqdiff,'mode_absolute':modediff})
        check('charge-ledger',all(x['charge_error']<.01 for x in obs.values()),{k:x['charge_error'] for k,x in obs.items()})
        summary['observations']=obs;summary['metrics']={'frequency_difference':freqdiff,'mode_difference':modediff}
    else:
        variants={};metrics={};markerrows=[];spacerows=[]
        locks=read_json(raw/'prediction-lock.json')
        events=[json.loads(x) for x in (raw.parent/'events.jsonl').read_text().splitlines()]
        # Verify actual on-disk order, not only the declared worker path.
        locked_index=next(i for i,x in enumerate(events) if x['type']=='all-predictions-locked')
        first_receiver=min(i for i,x in enumerate(events) if x['type']=='receiver-completed')
        prediction_ok=all(hashlib.sha256((raw/f"prediction-{x['label']}.npz").read_bytes()).hexdigest()==x['prediction_sha256'] for x in locks)
        check('prediction-first',prediction_ok and locked_index<first_receiver,{'hashes_valid':prediction_ok,'lock_event_index':locked_index,'first_receiver_event_index':first_receiver})
        for label in ('base','fine','time','wide'):
            with np.load(raw/f'receiver-{label}.npz') as d: rec=d['records'];fields=d['fields'];rr=d['r']
            pred=np.load(raw/f'prediction-{label}.npz')['records']
            if not np.isfinite(rec).all() or not np.isfinite(pred).all():raise ValueError('nonfinite response data')
            t=rec[:,0,0];delta=rec[:,:,1]-rec[:,0:1,1]
            predicted=np.column_stack([p['amplitudes'][j]**2*pred[:,0 if p['patterns'][j]=='single' else 1,5] for j in range(7)])
            variants[label]=(rec,pred,delta,predicted)
            signal=float(np.sqrt(np.mean(delta[:,2]**2)))
            parity=float(np.linalg.norm(delta[:,2]-delta[:,4])/max(np.linalg.norm(delta[:,2]+delta[:,4]),1e-30))
            cparity=float(np.linalg.norm(delta[:,5]-delta[:,6])/max(np.linalg.norm(delta[:,5]+delta[:,6]),1e-30))
            scaled=[delta[:,j]/p['amplitudes'][j]**2 for j in (1,2,3)]
            scale=max(relative(x,scaled[0]) for x in scaled[1:])
            slope=float(np.log(np.linalg.norm(delta[:,2])/np.linalg.norm(delta[:,1]))/np.log(2))
            errs={str(j):relative(predicted[:,j],delta[:,j]) for j in (1,2,3,5)}
            qerr=float(np.max(abs(rec[:,:,4]/rec[0,:,4]-1)))
            ebal=rec[:,:,3]-rec[0:1,:,3]
            incident=rec[0,:,3]-rec[0,0,3]
            energy=max(float(np.max(abs(ebal[:,j]-ebal[:,0]))/incident[j]) for j in range(1,7))
            basezeros=zeros(t,rec[:,0,1]);paired=True;markermax=0.;marker_error=0.
            for j in range(1,7):
                actual=zeros(t,rec[:,j,1]); forecast=zeros(t,pred[:,0,1]+predicted[:,j])
                valid=len(actual)==len(basezeros)==len(forecast) and len(actual)>=5
                if valid:
                    dtick=actual-basezeros;predtick=forecast-basezeros
                    shifts=-p['omega_chi']*dtick/(2*np.pi);pshifts=-p['omega_chi']*predtick/(2*np.pi)
                    valid=bool(np.all(abs(dtick)<np.pi/(2*p['omega_chi'])))
                    markermax=max(markermax,float(np.max(abs(shifts))))
                    err=float(np.max(abs(shifts-pshifts)));marker_error=max(marker_error,err)
                    valid=valid and err<=max(.1*float(np.max(abs(shifts))),1e-5)
                    for k,(time,shift,pshift) in enumerate(zip(basezeros,shifts,pshifts)):
                        markerrows.append({'grid':label,'case':j,'tick':k,'no_pulse_time':float(time),'delta_cycles':float(shift),'predicted_cycles':float(pshift)})
                paired=paired and valid
            metrics[label]={'signal_rms':signal,'sign_odd_fraction':parity,'counter_sign_odd_fraction':cparity,
                'scaling_difference':scale,'weak_slope':slope,'prediction_relative':errs,
                'charge_error':qerr,'matched_energy_residual_over_incident':energy,
                'markers_valid':paired,'maximum_tick_shift_cycles':markermax,'maximum_tick_prediction_error_cycles':marker_error,
                'baseline_crossings':len(basezeros)}
            for k in range(len(t)):
                for j in range(7):
                    rows.append({'grid':label,'case':j,'pattern':p['patterns'][j],'amplitude':p['amplitudes'][j],
                        'time':float(t[k]),'local_chi':float(rec[k,j,1]),'upstream_a':float(rec[k,j,2]),
                        'delta_chi':float(delta[k,j]),'predicted_delta_chi':float(predicted[k,j]),
                        'total_energy':float(rec[k,j,3]),'charge':float(rec[k,j,4])})
            if label=='base':
                for ti in range(len(fields)):
                    for case in (2,5):
                        for ri,r in enumerate(rr):
                            if r>40:continue
                            spacerows.append({'time':2.*ti,'radius':float(r),'case':case,'a':float(fields[ti,0,case,ri]),'chi':float(fields[ti,1,case,ri])})
        numerical={}
        for case in (2,5):
            numerical[str(case)]={label:relative(variants[label][2][:,case],variants['base'][2][:,case]) for label in ('fine','time','wide')}
        resolved=all(x['signal_rms']>1e-12 for x in metrics.values())
        def match(case):
            control=sum(numerical[str(case)].values())+.002
            errors=[x['prediction_relative'][str(case)] for x in metrics.values()]
            return all(e<.05 and e<5*control for e in errors)
        check('sign-even',all(x['sign_odd_fraction']<1e-5 and x['counter_sign_odd_fraction']<1e-5 for x in metrics.values()),metrics,status=None if resolved else 'unresolved')
        check('amplitude-square',all(x['scaling_difference']<.05 and abs(x['weak_slope']-2)<.1 for x in metrics.values()),{k:[x['scaling_difference'],x['weak_slope']] for k,x in metrics.items()},status=None if resolved else 'unresolved')
        check('response-match',match(2),{k:x['prediction_relative'] for k,x in metrics.items()},status=None if resolved else 'unresolved')
        check('counter-match',match(5),{k:x['prediction_relative']['5'] for k,x in metrics.items()},status=None if resolved else 'unresolved')
        check('common-markers',all(x['markers_valid'] for x in metrics.values()),{k:[x['baseline_crossings'],x['maximum_tick_shift_cycles'],x['maximum_tick_prediction_error_cycles']] for k,x in metrics.items()})
        check('numerical-controls',all(v<.05 for d in numerical.values() for v in d.values()),numerical,status=None if resolved else 'unresolved')
        check('conservation',all(x['charge_error']<1e-5 and x['matched_energy_residual_over_incident']<.01 for x in metrics.values()),{k:[x['charge_error'],x['matched_energy_residual_over_incident']] for k,x in metrics.items()})
        summary['metrics']=metrics;summary['numerical_errors']=numerical
        save_csv(derived/'markers.csv',markerrows);save_csv(derived/'spacetime.csv',spacerows)
    save_csv(derived/'traces.csv',rows)
    summary['checks']={x['id']:x['status'] for x in checks}
    write_json(derived/'summary.json',summary)
    out={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',out)
    return {'raw_source':sources[0].relative_to(run_path).as_posix(),'checks':out,'summary':summary}
