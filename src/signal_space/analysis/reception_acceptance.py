"""Frozen Program 15.7 gates on a fresh known-incident receiver suite."""
import json
import numpy as np
from signal_space.numerics.prereception import digest
from signal_space.analysis.clock import save_csv
from signal_space.runtime.io import read_json,write_json


def phase_series(jet,receiver,baseline,amplitude,omega):
    z0=jet[:,1]-1j*jet[:,2]/omega;z2=jet[:,3]-1j*jet[:,4]/omega;z4=jet[:,5]-1j*jet[:,6]/omega
    zr=receiver[:,1]-1j*receiver[:,2]/omega;zq=baseline[:,1]-1j*baseline[:,2]/omega
    if min(np.min(abs(z0)),np.min(abs(zq)))<1e-12:raise ValueError('undefined local phase')
    actual=np.unwrap(np.angle(zr/zq))/(2*np.pi)
    second=amplitude**2*np.imag(z2/z0)/(2*np.pi)
    fourth=second+amplitude**4*np.imag(z4/z0-.5*(z2/z0)**2)/(2*np.pi)
    return actual,second,fourth


def interval(t,cycles,events):
    if not t[0]<=events[0]<events[1]<=t[-1]:raise ValueError('events outside acquisition')
    return float(np.interp(events[1],t,cycles)-np.interp(events[0],t,cycles))


def budget(values,noise):
    return abs(values['finer']-values['fine'])+abs(values['fine']-values['time'])+abs(values['base']-values['wide'])+noise


def analyze(run_path,output,config):
    p=config['parameters'];raw=next((run_path/'attempts').glob('*/raw'));derived=output/'derived';derived.mkdir(parents=True)
    checks=[];arrays={};metrics={};traces=[];surfaces=[];spatial=[]
    def check(key,ok,value,unresolved=False):
        checks.append({'id':key,'status':'unresolved' if unresolved else ('pass' if ok else 'fail'),'value':value,'evidence':'derived/summary.json'})
    valid=all(digest(raw/x['name'])==x['sha256'] for x in p['frozen_inputs'])
    check('frozen-calibration',valid,{'hashes_valid':valid})
    log=[json.loads(x) for x in (raw.parent/'events.jsonl').read_text().splitlines()]
    lock=read_json(raw/'prediction-lock.json');li=next(i for i,x in enumerate(log) if x['type']=='all-predictions-locked')
    ri=min(i for i,x in enumerate(log) if x['type']=='receiver-started')
    integrity=all(digest(raw/f'{key}-{item["variant"]}.npz')==item[key] for item in lock['forecasts'] for key in ('calibration','input','surface','prediction'))
    integrity &= digest(raw/'frozen-core.npz')==lock['frozen_core'] and digest(raw/'prediction-lock.json')==log[li]['payload']['sha256']
    check('prediction-first',integrity and li<ri,{'hashes_valid':integrity,'lock_event':li,'first_receiver':ri})
    for variant in p['variants']:
        name=variant['name'];jet=np.load(raw/f'prediction-{name}.npz')['records']
        with np.load(raw/f'receiver-{name}.npz') as data:rec=data['records'];fields=data['fields'];rr=data['r']
        if not np.isfinite(rec).all() or not np.isfinite(jet).all():raise ValueError('nonfinite saved evidence')
        t=rec[:,0,0];metrics[name]={};arrays[name]={}
        for j,c in enumerate(p['cases']):
            b=rec[:,c['baseline']];q=jet[:,c['prediction']];A=c['amplitude']
            actual,second,pred=phase_series(q,rec[:,j],b,A,p['omega_chi'])
            d=rec[:,j,1]-b[:,1];pd=A*A*q[:,3]+A**4*q[:,5]
            density=rec[:,j,5]-b[:,5];density_pred=A*A*q[:,11]+A**4*q[:,12]
            norm=lambda x:float(np.linalg.norm(x))
            rel=lambda x,y:norm(x-y)/max(norm(y),1e-30)
            N=interval(t,actual,p['event_times']);PN=interval(t,pred,p['event_times'])
            initial=rec[0,j,7]-b[0,7]
            energy=float(np.max(abs((rec[:,j,7]-rec[0,j,7])-(b[:,7]-b[0,7])))/initial) if A else 0.
            metrics[name][c['name']]={'actual':N,'prediction':PN,'second':interval(t,second,p['event_times']),
                'absolute_error':abs(N-PN),'relative_error':abs(N-PN)/max(abs(N),1e-30),
                'phase_trace_relative':rel(pred,actual) if A else 0.,'chi_trace_relative':rel(pd,d) if A else 0.,
                'density_trace_relative':rel(density_pred,density) if A else 0.,'second_trace_relative':rel(second,actual) if A else 0.,
                'charge_error':float(np.max(abs(rec[:,j,8]/rec[0,j,8]-1))),
                'matched_energy_over_incident':energy,'total_energy_relative':float(np.max(abs(rec[:,j,7]/rec[0,j,7]-1))),
                'output_sampling':abs(N-interval(t[::2],actual[::2],p['event_times']))+abs(PN-interval(t[::2],pred[::2],p['event_times']))}
            arrays[name][c['name']]={'actual':actual,'prediction':pred,'chi':d,'predicted_chi':pd}
            if name=='finer':
                for k,time in enumerate(t):traces.append({'case':c['name'],'amplitude':A,'time':float(time),
                    'actual_cycles':float(actual[k]),'second_cycles':float(second[k]),'predicted_cycles':float(pred[k]),
                    'chi':float(rec[k,j,1]),'quiet_chi':float(b[k,1]),'delta_chi':float(d[k]),'predicted_chi':float(pd[k]),
                    'density_response':float(density[k]),'predicted_density':float(density_pred[k]),
                    'local_a':float(rec[k,j,3]),'local_invariant':float(rec[k,j,6]),'predicted_invariant2':float(A*A*q[k,13])})
        if name=='base':
            for k,field in enumerate(fields):
                for j in (2,5,6):
                    for ix,r in enumerate(rr):spatial.append({'time':float(k),'radius':float(r),'case':p['cases'][j]['name'],
                        'a':float(field[0,j,ix]),'invariant':float(field[1,j,ix])})
            sur=np.load(raw/f'surface-{name}.npz')['records']
            for k in range(0,len(sur),round(p['sample_interval']/variant['dt'])):
                for j in range(2):
                    time,a,at,ar=sur[k,j];surfaces.append({'time':float(time),'pulse':j,'a':float(a),'a_t':float(at),'a_r':float(ar),'invariant':float(at*at-ar*ar)})
    names=[c['name'] for c in p['cases'] if c['amplitude']];budgets={};convergence={};trace_budgets={}
    for name in names:
        m=metrics['finer'][name]
        parts={key:budget({g:metrics[g][name][key] for g in metrics},0.) for key in ('actual','prediction')}
        B=sum(parts.values())+m['output_sampling']+p['cycle_noise_floor']
        budgets[name]={'signal':m['actual'],'prediction':m['prediction'],'error':m['absolute_error'],'budget':B,
            'actual_numerics':parts['actual'],'forecast_numerics':parts['prediction'],'sampling':m['output_sampling'],
            'signal_to_budget':abs(m['actual'])/B,'allowance':max(.05*abs(m['actual']),B)}
        changes={}
        for kind in ('actual','prediction'):
            norm=lambda a,b:float(np.linalg.norm(arrays[a][name][kind]-arrays[b][name][kind]))
            fine=norm('finer','fine');coarse=norm('fine','base');extra=norm('fine','time')+norm('base','wide')+p['cycle_noise_floor']*np.sqrt(len(t))
            changes[kind]={'fine_change':fine,'coarse_change':coarse,'nonspatial':float(extra),'contracts':bool(fine<=.75*coarse+extra)}
        convergence[name]=changes
        trace_budgets[name]=sum(x['fine_change']+x['nonspatial'] for x in changes.values())/max(float(np.linalg.norm(arrays['finer'][name]['actual'])),1e-30)
    resolved=all(x['signal_to_budget']>5 for x in budgets.values())
    check('record-resolution',resolved,budgets,not resolved)
    check('interval-prediction',all(x['error']<=x['allowance'] for x in budgets.values()),budgets,not resolved)
    check('response-traces',all(max(metrics['finer'][n]['phase_trace_relative'],metrics['finer'][n]['chi_trace_relative'],metrics['finer'][n]['density_trace_relative'])<=max(.05,trace_budgets[n]) for n in names),{'metrics':metrics['finer'],'phase_numerical_budgets':trace_budgets})
    parity={};scaling={}
    for g in arrays:
        a=arrays[g];norm=lambda x:float(np.linalg.norm(x))
        parity[g]=max(norm(a[x]['actual']-a[y]['actual'])/max(norm(a[x]['actual'])+norm(a[y]['actual']),1e-30) for x,y in [('single','negative'),('both','both-negative')])
        slope=float(np.log(norm(a['single']['chi'])/norm(a['half']['chi']))/np.log(2))
        normalized=max(norm(a[n]['chi']/factor**2-a['half']['chi']/.5**2)/norm(a['half']['chi']/.5**2) for n,factor in [('single',1),('double',2)])
        scaling[g]={'weak_exponent':slope,'normalized_trace_difference':normalized,'weak_second_order_phase_error':metrics[g]['half']['second_trace_relative']}
    check('sign-even',max(parity.values())<=1e-5,parity)
    check('weak-amplitude-law',all(abs(x['weak_exponent']-2)<=.1 and x['normalized_trace_difference']<=.05 and x['weak_second_order_phase_error']<=.05 for x in scaling.values()),scaling,not resolved)
    inter={g:{k:arrays[g]['both'][k]-arrays[g]['single'][k]-arrays[g]['second'][k] for k in ('actual','prediction')} for g in arrays}
    effect=inter['finer']['actual'];forecast=inter['finer']['prediction'];norm=lambda x:float(np.linalg.norm(x))
    IB=sum(norm(inter[a][k]-inter[b][k]) for k in ('actual','prediction') for a,b in [('finer','fine'),('fine','time'),('base','wide')])+p['cycle_noise_floor']*np.sqrt(len(t))
    ratio=norm(effect)/IB;err=norm(forecast-effect)/max(norm(effect),1e-30)
    check('pulse-overlap',err<=max(.05,1/ratio),{'signal_to_budget':ratio,'prediction_relative':err},ratio<=5)
    null=np.load(raw/'frozen-core.npz')['records'];nullmax=float(np.max(abs(null[:,:,3:7])))
    quiet_names=[c['name'] for c in p['cases'] if c['amplitude']==0]
    quiet_records={g:{n:metrics[g][n]['actual'] for n in quiet_names} for g in metrics}
    check('quiet-and-frozen-core',nullmax<=1e-15 and all(abs(value)<1e-15 for rows in quiet_records.values() for value in rows.values()),{'frozen_response_max':nullmax,'quiet_records':quiet_records})
    conv=all(c['contracts'] for v in convergence.values() for c in v.values())
    check('numerical-convergence',conv and max(trace_budgets.values())<.2,{'convergence':convergence,'trace_budgets':trace_budgets},not conv or max(trace_budgets.values())>=.2)
    em=max(v['matched_energy_over_incident'] for rows in metrics.values() for v in rows.values());qm=max(v['charge_error'] for rows in metrics.values() for v in rows.values());tm=max(v['total_energy_relative'] for rows in metrics.values() for v in rows.values())
    check('conservation',em<.01 and qm<1e-5 and tm<1e-5,{'matched_energy_over_incident':em,'charge_relative':qm,'total_energy_relative':tm})
    summary={'metrics':metrics,'record_budgets':budgets,'trace_budgets':trace_budgets,'convergence':convergence,
        'sign_parity':parity,'amplitude_scaling':scaling,'overlap':{'signal_to_budget':ratio,'prediction_relative':err},
        'event_times':p['event_times'],'cases':p['cases'],'checks':{c['id']:c['status'] for c in checks},
        'scope':'Program 15.7 known-incident, fixed-local-time, fourth-order radial acceptance; old surface-only classifications unchanged'}
    for name,rows in [('traces',traces),('surface',surfaces),('spacetime',spatial)]:save_csv(derived/f'{name}.csv',rows)
    write_json(derived/'summary.json',summary);out={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',out)
    return {'raw_source':str(raw.relative_to(run_path)/'execution.json'),'checks':out,'summary':summary}
