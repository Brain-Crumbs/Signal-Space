"""Separate inspected-history diagnostic and locked held-out order-four checks."""
import hashlib
import json
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import brentq
from signal_space.analysis.reception import markers, interval, phase
from signal_space.analysis.clock import save_csv
from signal_space.runtime.io import read_json, write_json
from signal_space.numerics.prereception import ROOT
from signal_space.numerics.prereception import RadialSystem
from signal_space.numerics.reception import rk4


def quadratures(jet, A):
    z0=jet[:,1]-1j*jet[:,2]/OMEGA
    z2=jet[:,3]-1j*jet[:,4]/OMEGA
    z4=jet[:,5]-1j*jet[:,6]/OMEGA
    d2=A*A*np.imag(z2/z0)
    d4=A**4*np.imag(z4/z0-.5*(z2/z0)**2)
    return d2,d4


def hermite_markers(t,a,adot,threshold):
    """Actual derivative at the SAME local point; first rise and last fall."""
    spline=CubicHermiteSpline(t,a,adot); roots=[]
    for i in range(len(t)-1):
        for sign in (-1,1):
            left=sign*a[i]-threshold;right=sign*a[i+1]-threshold
            if left*right<0:
                root=brentq(lambda x:sign*float(spline(x))-threshold,t[i],t[i+1])
                roots.append((root,right>left))
    ups=[x for x,rising in roots if rising];downs=[x for x,rising in roots if not rising]
    return (ups[0],downs[-1]) if ups and downs and downs[-1]>ups[0] else None


def evaluate(jet, full, A, threshold, sample):
    t=jet[:,0];d2,d4=quadratures(jet,A);forecast=d2+d4
    actual=phase(full[:,1,1],full[:,1,2],OMEGA)-phase(full[:,0,1],full[:,0,2],OMEGA)
    observed_linear=markers(t,full[:,1,3],threshold)
    observed_hermite=hermite_markers(t,full[:,1,3],full[:,1,4],threshold)
    neutral=A*jet[:,7]+A**3*jet[:,9]
    neutral_dot=A*jet[:,8]+A**3*jet[:,10]
    forecast_linear=markers(t,neutral,threshold)
    forecast_hermite=hermite_markers(t,neutral,neutral_dot,threshold)
    zero=interval(t,actual,observed_linear)
    P2=interval(t,d2,forecast_linear);P4=interval(t,forecast,forecast_linear)
    # Compare decimated linear/Hermite reconstruction to full-resolution markers.
    down=round(.1/sample);t_coarse=t[::down];a_coarse=full[::down,1,3];d_coarse=full[::down,1,4]
    return {'actual':zero,'order2':P2,'order4':P4,
        'marker_actual_linear':observed_linear,'marker_actual_hermite':observed_hermite,
        'marker_pred_linear':forecast_linear,'marker_pred_hermite':forecast_hermite,
        'marker_decimated_linear':markers(t_coarse,a_coarse,threshold),
        'marker_decimated_hermite':hermite_markers(t_coarse,a_coarse,d_coarse,threshold),
        'trace2_relative':float(np.linalg.norm(actual-d2)/np.linalg.norm(actual)),
        'trace4_relative':float(np.linalg.norm(actual-forecast)/np.linalg.norm(actual)),
        'quartic_interval_at_actual_events':interval(t,d4,observed_linear),
        'residual_order2_at_actual_events':interval(t,actual-d2,observed_linear),
        'predicted_neutral_at_probe':neutral,
        'actual_phase':actual,'order2_phase':d2,'order4_phase':forecast}


def linear_probe(system,u,b,v,dt,duration,sample):
    """Independent known-Z neutral transfer for the saved vacuum-inverse control."""
    Z=1+system.eps*abs(u/system.r)**2
    y=np.asarray([b,Z*v]);out=[];stride=round(sample/dt)
    ix=round(.1/system.h)-1
    def rhs(q):
        return np.asarray([q[1]/Z,-system.transpose((1+system.eps*system.faces(abs(u/system.r)**2))*system.gradient(q[0]))])
    for k in range(round(duration/dt)+1):
        if k%stride==0:out.append(y[0,ix]/system.r[ix])
        if k<round(duration/dt):y=rk4(y,dt,rhs)
    return np.asarray(out)


def analyze(run_path, output, config):
    global OMEGA
    p=config['parameters'];OMEGA=p['omega_chi'];raw=next((run_path/'attempts').glob('*/raw'))
    prior=ROOT/p['prior_raw'];old=np.load(prior/'receiver-finer.npz')['records'];old_t=old[:,0,0]
    derived=output/'derived';derived.mkdir(parents=True)
    locks=read_json(raw/'prediction-lock.json')
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    events=[json.loads(x) for x in (raw.parent/'events.jsonl').read_text().splitlines()]
    valid=all(sha(raw/f'{key}-{x["grid"]}.npz')==x[key] for x in locks for key in ('surface','input','prediction'))
    boundary=next(i for i,x in enumerate(events) if x['type']=='all-predictions-locked')
    valid=valid and boundary<min(i for i,x in enumerate(events) if x['type']=='receiver-started')
    valid=valid and all(sha(ROOT/f['path'])==f['sha256'] for f in p['frozen_inputs']+p['prior_inputs'])
    diagnostic=[]
    with np.load(raw/'diagnostic-finer.npz') as d: jet=d['records'][::2]
    old=old[:len(jet)]
    fixed_old_events=markers(jet[:,0],old[:,2,3],p['marker_threshold'])
    for A,j in ((.002,1),(.004,2),(.008,3)):
        t=jet[:,0];theta=phase(old[:,j,1],old[:,j,2],OMEGA)-phase(old[:,0,1],old[:,0,2],OMEGA)
        d2,d4=quadratures(jet,A)
        diagnostic.append({'amplitude':A,'actual_minus_second_at_fixed_nominal_markers':interval(t,theta-d2,fixed_old_events),
            'derived_fourth_at_fixed_nominal_markers':interval(t,d4,fixed_old_events),
            'actual_minus_fourth_at_fixed_nominal_markers':interval(t,theta-d2-d4,fixed_old_events),
            'status':'diagnostic: inspected Test 7 data and fixed nominal marker times; no held-out acceptance'})
    checks=[]
    def check(key,condition,value,unresolved=False):
        checks.append({'id':key,'status':'unresolved' if unresolved else ('pass' if condition else 'fail'),
            'value':value,'evidence':'derived/summary.json'})
    check('prediction-first',valid,{'hashes_and_order':valid})
    traces=[]; metrics={};threshold=p['marker_threshold']
    for variant in p['variants']:
        name=variant['name'];jet=np.load(raw/f'prediction-{name}.npz')['records'];rec=np.load(raw/f'receiver-{name}.npz')['records']
        metrics[name]=[]
        for j,A in enumerate(p['amplitudes'],1):
            evaluation=evaluate(jet,rec[:,[0,j]],A,threshold,p['sample_interval'])
            data={k:v for k,v in evaluation.items() if not isinstance(v,np.ndarray)}
            data['amplitude']=A;data['energy_relative']=float(np.max(abs(rec[:,j,5]-rec[0,j,5]))/(rec[0,j,5]-rec[0,0,5]))
            data['charge_relative']=float(np.max(abs(rec[:,j,6]-rec[0,j,6]))/abs(rec[0,j,6]))
            metrics[name].append(data)
            if j==1:
                for k,t in enumerate(jet[:,0]):traces.append({'grid':name,'time':float(t),'actual_cycles':float(evaluation['actual_phase'][k]/(2*np.pi)),
                    'second_cycles':float(evaluation['order2_phase'][k]/(2*np.pi)),
                    'fourth_cycles':float(evaluation['order4_phase'][k]/(2*np.pi)),
                    'local_a':float(rec[k,j,3]),'predicted_a':float(evaluation['predicted_neutral_at_probe'][k])})
    chosen=metrics['finer'][0]; coarse=metrics['base'][0]; fine=metrics['fine'][0]
    with np.load(raw/'profile-0.900.npz') as d:r=d['r'];u=d['u']
    sys=RadialSystem(r,p['epsilon'])
    with np.load(raw/'input-base.npz') as d:vac_b=d['vacuum_b'][1:-1];vac_v=d['vacuum_v'][1:-1]
    vacuum_trace=linear_probe(sys,u,vac_b,vac_v,p['variants'][0]['dt'],p['duration'],p['sample_interval'])
    base_jet=np.load(raw/'prediction-base.npz')['records'];base_rec=np.load(raw/'receiver-base.npz')['records']
    vacuum_events=markers(base_jet[:,0],p['amplitudes'][0]*vacuum_trace,threshold)
    optical_events=markers(base_jet[:,0],p['amplitudes'][0]*base_jet[:,7],threshold)
    actual_events=coarse['marker_actual_linear']
    inversion={'vacuum_linear':vacuum_events,'known_Z_optical_linear':optical_events,
        'heldout_actual_linear':actual_events,
        'vacuum_max_error':max(abs(np.array(vacuum_events)-actual_events)) if vacuum_events else None,
        'known_Z_max_error':max(abs(np.array(optical_events)-actual_events)) if optical_events else None,
        'status':'post-hoc control on held-out receiver; optical fourth-order forecast was locked before receiver'}
    temporal={name:{'coarse_linear_vs_fine_hermite':max(abs(np.array(v['marker_decimated_linear'])-v['marker_actual_hermite'])),
                    'coarse_hermite_vs_fine_hermite':max(abs(np.array(v['marker_decimated_hermite'])-v['marker_actual_hermite'])),
                    'fine_linear_vs_fine_hermite':max(abs(np.array(v['marker_actual_linear'])-v['marker_actual_hermite']))}
              for name,v in [('base',coarse),('fine',fine),('finer',chosen)]}
    # Direct numerical differences are measured in the same event convention.
    budget=abs(chosen['actual']-fine['actual'])+abs(coarse['actual']-metrics['time'][0]['actual'])+p['cycle_noise_floor']
    record_ok=chosen['actual'] is not None and abs(chosen['actual'])>5*budget
    check('record-resolution',record_ok,{'signal':chosen['actual'],'budget':budget},not record_ok)
    rel=lambda x:abs(x['actual']-x['order4'])
    allowed=max(.05*abs(chosen['actual']),budget)
    check('heldout-interval',record_ok and rel(chosen)<=allowed,
          {'actual':chosen['actual'],'second':chosen['order2'],'fourth':chosen['order4'],
           'second_error':abs(chosen['actual']-chosen['order2']),'fourth_error':rel(chosen),'allowance':allowed},not record_ok)
    check('heldout-waveform',chosen['trace4_relative']<min(.05,chosen['trace2_relative']),
          {'second':chosen['trace2_relative'],'fourth':chosen['trace4_relative']})
    marker_errors={}
    for name,rows in metrics.items():
        for item in rows:
            if item['marker_actual_linear'] and item['marker_pred_linear']:
                marker_errors[f'{name}:{item["amplitude"]}']=max(abs(np.array(item['marker_actual_linear'])-item['marker_pred_linear']))
    markers_present=len(marker_errors)==len(p['variants'])*len(p['amplitudes'])
    check('marker-timing',markers_present and max(marker_errors.values())<=p['marker_time_tolerance'],
          marker_errors,not markers_present)
    check('sign-even',all(np.isclose(a,b,rtol=1e-6,atol=1e-12) for a,b in zip(metrics['finer'][0]['marker_actual_linear'],metrics['finer'][1]['marker_actual_linear'])) and
          abs(metrics['finer'][0]['actual']-metrics['finer'][1]['actual'])<1e-10,
          {'positive':metrics['finer'][0]['actual'],'negative':metrics['finer'][1]['actual']})
    energy=max(v['energy_relative'] for rows in metrics.values() for v in rows)
    charge=max(v['charge_relative'] for rows in metrics.values() for v in rows)
    check('conservation',energy<.01 and charge<1e-5,{'energy_relative':energy,'charge_relative':charge})
    summary={'prior_inspected_diagnostic':diagnostic,'heldout':metrics,'marker_error':marker_errors,
        'inversion_control':inversion,'temporal_interpolation':temporal,
        'numerical_budget_cycles':budget,'checks':{c['id']:c['status'] for c in checks},
        'model':'unchanged SS OCF 1 radial discrete Hamiltonian; calibrated omega and mode',
        'sample':'0.05; retrospective first-rise last-fall; quiet interval is counterfactual'}
    save_csv(derived/'traces.csv',traces);write_json(derived/'summary.json',summary)
    out={'schema_version':'research-checks-v1','checks':checks};write_json(output/'checks.json',out)
    return {'raw_source':str(raw.relative_to(run_path)/'execution.json'),'checks':out,'summary':summary}
