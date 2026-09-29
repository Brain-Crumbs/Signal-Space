"""Known-incident Test 7: all formal forecasts precede every coupled receiver."""
from pathlib import Path
import shutil
import numpy as np
from signal_space.numerics.prereception import ROOT, RadialSystem, packet, digest
from signal_space.numerics.reception import profile, acquire, evolve, rk4
from signal_space.numerics.reception_order4 import jet_rhs
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event


JET_COLUMNS = ['time','chi0','chi0_dot','chi2','chi2_dot','chi4','chi4_dot',
               'a1','a1_dot','a3','a3_dot','density2','density4','invariant2']


def incident(r, parameters, weights):
    waves=[packet(r,c,parameters['packet_width']) for c in parameters['packet_centers']]
    return tuple(sum(w*waves[j][k] for j,w in enumerate(weights)) for k in range(2))


def forecast(system,u,mode,dt,p,cases,frozen=False):
    """Batched unfitted Taylor coefficients; no receiver observations accepted."""
    r=system.r;n=len(r);y=np.zeros((16,len(cases),n),complex)
    y[0]=u;y[1]=-1j*p['omega_Q']*u
    clock=p['clock_amplitude']*mode/np.max(mode/r)
    for j,c in enumerate(cases):
        y[2,j]=clock*np.cos(c['phase']);y[3,j]=-p['omega_chi']*clock*np.sin(c['phase'])
        b,v=incident(r,p,c['weights']);y[4,j]=b;y[5,j]=(1+system.eps*abs(u/r)**2)*v
    probe=round(p['local_radius']/system.h)-1;stride=round(p['sample_interval']/dt)
    rows=[]
    def rhs(q):
        out=jet_rhs(system,q)
        if frozen:out[6:]=0
        return out
    for step in range(round(p['duration']/dt)+1):
        if step%stride==0:
            s0=abs(y[0]/r)**2;Z=1+system.eps*s0
            s2=2*np.real(np.conj(y[0])*y[6])/r**2
            s4=(abs(y[6])**2+2*np.real(np.conj(y[0])*y[12]))/r**2
            v1=y[5].real/Z;v3=y[11].real/Z-system.eps*s2*y[5].real/Z**2
            inv=(v1*v1-system.face_adjoint(system.gradient(y[4].real)**2))/r**2
            rows.append(np.stack((np.full(len(cases),step*dt),y[2,:,probe].real/r[probe],
                y[3,:,probe].real/r[probe],y[8,:,probe].real/r[probe],y[9,:,probe].real/r[probe],
                y[14,:,probe].real/r[probe],y[15,:,probe].real/r[probe],y[4,:,probe].real/r[probe],
                v1[:,probe]/r[probe],y[10,:,probe].real/r[probe],v3[:,probe]/r[probe],
                s2[:,probe],s4[:,probe],inv[:,probe]),axis=-1))
        if step==round(p['duration']/dt):break
        y=rk4(y,dt,rhs)
        if not np.isfinite(y).all():raise ValueError('nonfinite acceptance forecast')
    return np.asarray(rows)


def execute(request_path):
    req=read_json(request_path);p=req['config']['parameters'];raw=Path(req['attempt_path'])/'raw';raw.mkdir(exist_ok=True)
    log=raw.parent/'events.jsonl';append_event(log,'worker-started','run',{'algorithm':'known-incident-order4-acceptance-v1'})
    for item in p['frozen_inputs']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('frozen calibration changed')
        shutil.copy2(ROOT/item['path'],raw/item['name'])
    write_json(raw/'rng-start.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    locks=[]
    for variant in p['variants']:
        label=variant['name'];r,u,mode=profile(raw,variant['profile'],variant['h']);system=RadialSystem(r,p['epsilon'])
        np.savez_compressed(raw/f'calibration-{label}.npz',r=r,u=u,mode=mode)
        b,v=zip(*(incident(system.r,p,c['weights']) for c in p['prediction_cases']))
        np.savez_compressed(raw/f'input-{label}.npz',b=np.asarray(b),v=np.asarray(v))
        surface=acquire(system,u,variant['dt'],p)
        np.savez_compressed(raw/f'surface-{label}.npz',records=surface)
        append_event(log,'surface-acquired','run',{'variant':label})
        pred=forecast(system,u,mode,variant['dt'],p,p['prediction_cases'])
        np.savez_compressed(raw/f'prediction-{label}.npz',records=pred)
        locks.append({'variant':label,**{key:digest(raw/f'{key}-{label}.npz') for key in ('calibration','input','surface','prediction')}})
        append_event(log,'prediction-saved','run',{'variant':label})
    base=p['variants'][0];r,u,mode=profile(raw,base['profile'],base['h'])
    null=forecast(RadialSystem(r,p['epsilon']),u,mode,base['dt'],p,[p['prediction_cases'][0]],True)
    np.savez_compressed(raw/'frozen-core.npz',records=null)
    write_json(raw/'prediction-lock.json',{'forecasts':locks,'frozen_core':digest(raw/'frozen-core.npz')})
    append_event(log,'all-predictions-locked','run',{'sha256':digest(raw/'prediction-lock.json')})
    for variant in p['variants']:
        label=variant['name'];r,u,mode=profile(raw,variant['profile'],variant['h']);system=RadialSystem(r,p['epsilon'])
        def initial(c,rr):return tuple(c['amplitude']*x for x in incident(rr,p,c['weights']))
        append_event(log,'receiver-started','run',{'variant':label})
        rec,fields,rr=evolve(system,u,mode,variant['dt'],p,p['cases'],initial)
        np.savez_compressed(raw/f'receiver-{label}.npz',records=rec,fields=fields,r=rr)
        append_event(log,'receiver-completed','run',{'variant':label})
    write_json(raw/'execution.json',{'algorithm':'known-incident-order4-acceptance-v1','jet_columns':JET_COLUMNS,
        'primary_events':p['event_times'],'information_boundary':'known preparation and frozen calibration; no coupled receiver output',
        'surface_role':'independent frozen-linear incident record; no surface inverse used',
        'scope':'Program 15.7 known-incident radial acceptance; previous surface-only protocols unchanged'})
    write_json(raw/'rng-end.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    append_event(log,'worker-completed','run',{})
    return 0
