"""Local reception records and preregistered direct numerical error budget."""
import hashlib
import json
import numpy as np
from signal_space.analysis.clock import save_csv
from signal_space.analysis.prereception import relative, zeros
from signal_space.runtime.io import read_json, write_json


def phase(chi,velocity,omega):
    return np.unwrap(np.arctan2(-velocity/omega,chi))


def markers(t,a,threshold):
    # Sign-independent marker: first rising and last falling |a| threshold.
    # It is retrospective within the registered local acquisition window.
    y=abs(a)-threshold;up=zeros(t,y);down=zeros(t,-y)
    if not len(up) or not len(down) or down[-1]<=up[0]:return None
    return float(up[0]),float(down[-1])


def interval(t,delta_phase,events):
    if events is None:return None
    start,end=events
    return float((np.interp(end,t,delta_phase)-np.interp(start,t,delta_phase))/(2*np.pi))


def analyze(run_path,output,config):
    paths=sorted((run_path/'attempts').glob('*/raw/execution.json'))
    if len(paths)!=1:raise ValueError('expected one completed atomic run')
    raw=paths[0].parent;p=config['parameters'];derived=output/'derived';derived.mkdir(parents=True)
    checks=[];traces=[];markrows=[];spatial=[];surfaces=[];metrics={};arrays={}
    def check(key,ok,value,unresolved=False):
        checks.append({'id':key,'status':'unresolved' if unresolved else ('pass' if ok else 'fail'),'value':value,'evidence':'derived/summary.json'})
    digest=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    check('frozen-inputs',all(digest(raw/x['name'])==x['sha256'] for x in p['frozen_inputs']),p['frozen_inputs'])
    events=[json.loads(x) for x in (raw.parent/'events.jsonl').read_text().splitlines()]
    locked=next(i for i,x in enumerate(events) if x['type']=='all-predictions-locked')
    first=min(i for i,x in enumerate(events) if x['type']=='receiver-started')
    locks=read_json(raw/'prediction-lock.json');valid=all(digest(raw/f'{name}-{x["label"]}.npz')==x[f'{name}_sha256'] for x in locks for name in ('prediction','surface','input','calibration'))
    check('prediction-first',valid and locked<first,{'hashes_valid':valid,'lock_event':locked,'first_receiver_start':first})
    omega=p['omega_chi'];cases=p['cases']
    for label in ('base','fine','finer','time','wide'):
        pred=np.load(raw/f'prediction-{label}.npz')['records'];rec=np.load(raw/f'receiver-{label}.npz')['records']
        if not np.isfinite(pred).all() or not np.isfinite(rec).all():raise ValueError('nonfinite evidence')
        t=rec[:,0,0];delta=[];forecasts=[];cycle=[];forecast_cycle=[];records=[];pmrecords=[];errs=[];marker_valid=True;marker_missing=False
        for j,c in enumerate(cases):
            baseline=c['baseline'];q=c['prediction'];A=c['amplitude'];b=rec[:,baseline]
            d=rec[:,j,1]-b[:,1];forecast=A*A*pred[:,q,9]
            theta=phase(rec[:,j,1],rec[:,j,2],omega)-phase(b[:,1],b[:,2],omega)
            pp=pred[:,q];den=pp[:,1]**2+(pp[:,2]/omega)**2
            dp=A*A*(pp[:,2]*pp[:,9]-pp[:,1]*pp[:,10])/(omega*den)
            actual_events=markers(t,rec[:,j,3],p['marker_threshold']) if A else None
            predicted_events=markers(t,A*pp[:,3],p['marker_threshold']) if A else None
            N=interval(t,theta,actual_events);PN=interval(t,dp,predicted_events)
            if A:
                marker_missing |= actual_events is None or predicted_events is None
                marker_valid &= actual_events is not None and predicted_events is not None
                if actual_events and predicted_events:
                    marker_valid &= max(abs(np.array(actual_events)-predicted_events))<p['marker_time_tolerance']
            records.append(N);pmrecords.append(PN)
            err=relative(forecast,d) if A else 0.;errs.append(err)
            delta.append(d);forecasts.append(forecast);cycle.append(theta/(2*np.pi));forecast_cycle.append(dp/(2*np.pi))
            markrows.append({'grid':label,'case':c['name'],'start':None if not actual_events else actual_events[0],
                'end':None if not actual_events else actual_events[1],'predicted_start':None if not predicted_events else predicted_events[0],
                'predicted_end':None if not predicted_events else predicted_events[1],'record_cycles':N,'prediction_cycles':PN})
            for k in range(len(t)):
                traces.append({'grid':label,'case':c['name'],'amplitude':A,'time':float(t[k]),'chi':float(rec[k,j,1]),
                    'delta_chi':float(d[k]),'predicted_delta_chi':float(forecast[k]),'delta_cycles':float(theta[k]/(2*np.pi)),
                    'predicted_cycles':float(dp[k]/(2*np.pi)),'local_a':float(rec[k,j,3]),'local_invariant':float(rec[k,j,6]),
                    'delta_density':float(rec[k,j,5]-b[k,5]),'predicted_density':float(A*A*pp[k,11])})
        delta=np.array(delta);forecasts=np.array(forecasts);cycle=np.array(cycle);forecast_cycle=np.array(forecast_cycle)
        arrays[label]={'delta':delta,'forecast':forecasts,'cycles':cycle,'predicted_cycles':forecast_cycle,'records':records,'predicted_records':pmrecords}
        # Nominal single (2), second only (5), both (6), and changed phase (9).
        scale=max(relative(delta[j]/cases[j]['amplitude']**2,delta[1]/cases[1]['amplitude']**2) for j in (2,3))
        slope=float(np.log(np.linalg.norm(delta[2])/np.linalg.norm(delta[1]))/np.log(2))
        odd=float(np.linalg.norm(delta[2]-delta[4])/max(np.linalg.norm(delta[2]+delta[4]),1e-30))
        pair_odd=float(np.linalg.norm(delta[6]-delta[7])/max(np.linalg.norm(delta[6]+delta[7]),1e-30))
        interaction=delta[6]-delta[2]-delta[5];pred_interaction=forecasts[6]-forecasts[2]-forecasts[5]
        balance=rec[:,:,7]-rec[0:1,:,7];energy=[]
        for j,c in enumerate(cases):
            if c['amplitude']:
                incident=rec[0,j,7]-rec[0,c['baseline'],7]
                energy.append(float(np.max(abs(balance[:,j]-balance[:,c['baseline']]))/incident))
        metrics[label]={'trace_prediction_relative':errs,'interval_cycles':records,'predicted_interval_cycles':pmrecords,
           'markers_valid':bool(marker_valid),'markers_missing':bool(marker_missing),'sign_odd_fraction':odd,'pair_sign_odd_fraction':pair_odd,'weak_slope':slope,
           'amplitude_normalized_difference':scale,'interaction_prediction_relative':relative(pred_interaction,interaction),
           'interaction_rms':float(np.sqrt(np.mean(interaction**2))),
           'charge_error':float(np.max(abs(rec[:,:,8]/rec[0:1,:,8]-1))),
           'matched_energy_residual_over_incident':max(energy),
           'single_signal_rms':float(np.sqrt(np.mean(delta[2]**2)))}
        if label=='base':
            data=np.load(raw/f'receiver-{label}.npz');fields=data['fields'];rr=data['r']
            for ti in range(len(fields)):
                for j in (2,5,6):
                    for ri,r in enumerate(rr):spatial.append({'time':float(ti),'radius':float(r),'case':cases[j]['name'],'a':float(fields[ti,0,j,ri]),'invariant':float(fields[ti,1,j,ri])})
            sur=np.load(raw/'surface-base.npz')['records'];R=p['upstream_radius']
            for ti in range(len(sur)):
                for j in range(2):
                    tt,a,at,ar=sur[ti,j];inc=(R*at+a+R*ar)/2;out=(R*at-a-R*ar)/2
                    surfaces.append({'time':float(tt),'pulse':j,'a':float(a),'a_t':float(at),'a_r':float(ar),'incoming':float(inc),'outgoing':float(out)})
    selected=(2,5,6,9);controls={};record_budgets={};trace_budgets={}
    for j in selected:
        d=arrays['finer']['delta'][j]
        trace_error=sum(np.linalg.norm(arrays[a]['delta'][j]-arrays[b]['delta'][j]) for a,b in [('finer','fine'),('base','time'),('base','wide')])+p['field_noise_floor']*np.sqrt(len(d))
        trace_budgets[str(j)]=float(trace_error/np.linalg.norm(d))
        record=arrays['finer']['records'][j]
        valid=all(arrays[k]['records'][j] is not None for k in arrays)
        error=(sum(abs(arrays[a]['records'][j]-arrays[b]['records'][j]) for a,b in [('finer','fine'),('base','time'),('base','wide')])+p['cycle_noise_floor']) if valid else None
        record_budgets[str(j)]={'signal':record,'absolute_error':error,'signal_to_error':abs(record)/error if valid else None,
           'prediction_error':abs(record-arrays['finer']['predicted_records'][j]) if valid and arrays['finer']['predicted_records'][j] is not None else None}
        controls[str(j)]={k:relative(arrays[k]['delta'][j],arrays['base']['delta'][j]) for k in ('fine','time','wide')}
        controls[str(j)]['finer_vs_fine']=relative(arrays['finer']['delta'][j],arrays['fine']['delta'][j])
    resolved=all(v['signal_to_error'] is not None and v['signal_to_error']>5 for v in record_budgets.values())
    check('record-resolution',resolved,record_budgets,not resolved)
    check('surface-prediction',all(metrics['finer']['trace_prediction_relative'][j]<max(.05,trace_budgets[str(j)]) for j in selected),{'relative_errors':metrics['finer']['trace_prediction_relative'],'trace_error_budget':trace_budgets})
    marker_ok=all(v['prediction_error'] is not None and v['prediction_error']<=max(.05*abs(v['signal']),v['absolute_error']) for v in record_budgets.values())
    check('marker-prediction',marker_ok,record_budgets,not resolved)
    check('local-markers',all(m['markers_valid'] for m in metrics.values()),{k:m['markers_valid'] for k,m in metrics.items()},any(m['markers_missing'] for m in metrics.values()))
    check('sign-even',all(m['sign_odd_fraction']<1e-5 and m['pair_sign_odd_fraction']<1e-5 for m in metrics.values()),{k:[m['sign_odd_fraction'],m['pair_sign_odd_fraction']] for k,m in metrics.items()})
    check('amplitude-square',all(m['amplitude_normalized_difference']<.05 and abs(m['weak_slope']-2)<.1 for m in metrics.values()),{k:[m['weak_slope'],m['amplitude_normalized_difference']] for k,m in metrics.items()})
    interaction=arrays['finer']['delta'][6]-arrays['finer']['delta'][2]-arrays['finer']['delta'][5]
    inter_error=sum(np.linalg.norm((arrays[a]['delta'][6]-arrays[a]['delta'][2]-arrays[a]['delta'][5])-(arrays[b]['delta'][6]-arrays[b]['delta'][2]-arrays[b]['delta'][5])) for a,b in [('finer','fine'),('base','time'),('base','wide')])+p['field_noise_floor']*np.sqrt(len(interaction))
    iratio=float(np.linalg.norm(interaction)/inter_error)
    check('pulse-overlap',metrics['finer']['interaction_prediction_relative']<max(.05,1/iratio),{'signal_to_error':iratio,'prediction_relative':metrics['finer']['interaction_prediction_relative']},iratio<=5)
    frozen=np.load(raw/'frozen-core.npz')['records'];null=float(np.max(abs(frozen[:,:,9:11])))
    check('frozen-core-control',null<1e-15 and metrics['finer']['single_signal_rms']>5*p['field_noise_floor'],{'incomplete_prediction_max':null,'full_signal_rms':metrics['finer']['single_signal_rms']})
    check('numerical-controls',all(v<.05 for d in controls.values() for v in d.values()),controls)
    check('conservation',all(m['charge_error']<1e-5 and m['matched_energy_residual_over_incident']<.01 for m in metrics.values()),{k:[m['charge_error'],m['matched_energy_residual_over_incident']] for k,m in metrics.items()})
    summary={'metrics':metrics,'record_error_budgets':record_budgets,'trace_error_budgets':trace_budgets,'numerical_controls':controls,
       'checks':{c['id']:c['status'] for c in checks},'cases':cases,'interaction_signal_to_error':iratio,
       'marker_definition':'first rising and last falling |a|=1e-4 at r=0.1 in t=0..100; matched quiet phase sampled at these counterfactual local times'}
    for name,rows in [('traces',traces),('markers',markrows),('spacetime',spatial),('surface',surfaces)]:save_csv(derived/f'{name}.csv',rows)
    write_json(derived/'summary.json',summary);out={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',out)
    return {'raw_source':paths[0].relative_to(run_path).as_posix(),'checks':out,'summary':summary}
