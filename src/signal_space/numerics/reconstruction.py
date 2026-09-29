"""Linear Test 7 observability audit. No nonlinear receiver is evolved.

The two-site causal control uses [K,P]b forcing through the acquisition cutoff.
Its additional link measurement and finite acquisition are explicit assumptions.
"""
from pathlib import Path
import numpy as np
from scipy.linalg import svd
from scipy.interpolate import CubicHermiteSpline
from signal_space.numerics.prereception import ROOT, RadialSystem, digest
from signal_space.numerics.reception import rk4
from signal_space.numerics.reception_transfer import (
    derivative, frozen_operator, observation_matrix, incident)
from signal_space.analysis.reception_order4 import hermite_markers
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event


def acquisition(system, u, b, v, dt, duration, sample, radius):
    """Only two adjacent surface sites are exported to the predictor."""
    mass, K = frozen_operator(system, u)
    state = np.asarray([b, mass*v]); ix = round(radius/system.h)-1
    rows = []; stride = round(sample/dt)
    def rhs(x): return np.asarray([x[1]/mass, -K(x[0])])
    for k in range(round(duration/dt)+1):
        if k % stride == 0:
            rows.append([k*dt, state[0,ix], state[1,ix]/mass[ix],
                         state[0,ix+1], state[1,ix+1]/mass[ix+1]])
        if k < round(duration/dt): state = rk4(state,dt,rhs)
    return np.asarray(rows), state


def causal_capture(system, u, surface, dt, duration, sample, radius, local_radius):
    """Reconstruct P x(T) from commutator forcing, then freely propagate.

    At T the omitted exterior state remains a separately audited uncertainty.
    RK4 evaluates Hermite surface data at its actual stage times.
    """
    mass, K = frozen_operator(system,u); n = len(mass)
    ix = round(radius/system.h)-1; local = round(local_radius/system.h)-1
    e = np.zeros(n); e[ix] = 1; link = float(K(e)[ix+1])
    curve = CubicHermiteSpline(surface[:,0],surface[:,[1,3]],surface[:,[2,4]])
    end = surface[-1,0]; y = np.zeros((2,n)); rows=[]; capture=None
    def rhs(t,x,drive):
        z = np.asarray([x[1]/mass,-K(x[0])])
        if drive:
            a = curve(t)
            z[1,ix] -= link*a[1]
            z[1,ix+1] += link*a[0]
        return z
    steps=round(duration/dt); stop=round(end/dt); stride=round(sample/dt)
    for k in range(steps+1):
        if k==stop: capture=y.copy()
        if k%stride==0: rows.append([k*dt,y[0,local],y[1,local]/mass[local]])
        if k==steps: break
        t=k*dt; drive=k<stop
        k1=rhs(t,y,drive);k2=rhs(t+dt/2,y+dt*k1/2,drive)
        k3=rhs(t+dt/2,y+dt*k2/2,drive);k4=rhs(t+dt,y+dt*k3,drive)
        y += dt*(k1+2*k2+2*k3+k4)/6
    return np.asarray(rows), capture


def markers(t, local, p, stride=1):
    scale=p['amplitude']/p['local_radius']
    return hermite_markers(t[::stride],scale*local[::stride,0],
                          scale*local[::stride,1],p['marker_threshold'])


def singular_audit(H, L, qhat, U, s, Vt, keep, target, times, t, p):
    """Conditional linear sensitivities plus finite admissible witnesses.

    eta bounds the surface l2 perturbation. rho bounds the initial q l2
    perturbation. These are declared tolerances, not measured detector noise.
    """
    eta=p['surface_relative_tolerance']*np.linalg.norm(target)
    fit_residual=np.linalg.norm(H@qhat-target)
    witness_margin=max(0.,eta-fit_residual)
    rho=p['input_radius_factor']*np.linalg.norm(qhat)
    local=(L@qhat).reshape(-1,2);scale=p['amplitude']/p['local_radius']
    rows=[];witnesses=[]
    if times is None: return rows,witnesses
    lc=CubicHermiteSpline(t,L[0::2],L[1::2],axis=0)
    for event,time in zip(('first','last'),times):
        row=scale*lc(time); slope=float(scale*lc(time,1)@qhat)
        coeff=Vt@row; retained=keep; discarded=~keep
        field_r=(eta+fit_residual)*np.linalg.norm(coeff[retained]/s[retained])
        field_d=rho*np.linalg.norm(coeff[discarded])
        record={'event':event,'time':float(time),'slope':slope,
                'eta':float(eta),'rho':float(rho),
                'surface_fit_residual':float(fit_residual),
                'retained_field_bound':float(field_r),'discarded_field_bound':float(field_d),
                'linear_timing_sensitivity':float((field_r+field_d)/max(abs(slope),1e-300)),
                'singular_event_coefficients':coeff.tolist(),
                'bound_scope':'conditional first-order root sensitivity, not a nonlinear event certificate'}
        for name,mask in [('retained',retained),('discarded',discarded)]:
            weights=np.zeros_like(s)
            if name=='retained': weights[mask]=coeff[mask]/s[mask]**2
            else: weights[mask]=coeff[mask]
            direction=Vt.T@weights; norm=np.linalg.norm(direction)
            if norm==0: continue
            direction/=norm
            step=min(rho,witness_margin/max(np.linalg.norm(H@direction),1e-300))
            delta=step*direction
            for sign in (-1,1):
                changed=(L@(qhat+sign*delta)).reshape(-1,2)
                mt=markers(t,changed,p)
                witnesses.append({'event':event,'subspace':name,'sign':sign,
                    'surface_relative_change':float(np.linalg.norm(H@delta)/np.linalg.norm(target)),
                    'surface_relative_residual':float(np.linalg.norm(H@(qhat+sign*delta)-target)/np.linalg.norm(target)),
                    'input_relative_change':float(np.linalg.norm(delta)/np.linalg.norm(qhat)),
                    'markers':mt,'marker_shift':None if mt is None else (np.asarray(mt)-times).tolist()})
        rows.append(record)
    return rows,witnesses


def execute(request_path):
    req=read_json(request_path);p=req['config']['parameters']
    raw=Path(req['attempt_path'])/'raw';raw.mkdir(exist_ok=True);events=raw.parent/'events.jsonl'
    append_event(events,'worker-started','run',{'algorithm':'linear-reconstruction-observability-v1'})
    for item in p['frozen_inputs']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('frozen input changed')
    write_json(raw/'rng-start.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    locks=[]; summaries=[]
    # One variant's forecast is locked before its source audit. Source waveforms
    # are fixed by the plan, never adapted to an observed reconstruction result.
    for variant in p['variants']:
        name=variant['name'];dt=variant['dt'];h=variant['h']
        with np.load(ROOT/variant['profile']) as d:r=d['r'];u=d['u']
        system=RadialSystem(r,p['epsilon'])
        H,inside=observation_matrix(system,u,dt,p['acquisition_duration'],p['sample_interval'],p['upstream_radius'],p['support'])
        L,local_inside=observation_matrix(system,u,dt,p['duration'],p['sample_interval'],p['local_radius'],p['support'])
        if not np.array_equal(inside,local_inside):raise ValueError('input spaces disagree')
        U,s,Vt=svd(H,full_matrices=False,lapack_driver='gesdd');keep=s>p['cutoff']*s[0]
        t=np.arange(L.shape[0]//2)*p['sample_interval']
        np.savez_compressed(raw/f'operators-{name}.npz',H=H,s=s,Vt=Vt,inside=inside)
        pending=[]
        for wave in p['waveforms']:
            tag=name+'-'+wave['name'];b,v=incident(system.r,wave,h)
            surface,endstate=acquisition(system,u,b,v,dt,p['acquisition_duration'],p['sample_interval'],p['upstream_radius'])
            target=surface[:,1:3].reshape(-1)
            qhat=Vt[keep].T@((U[:,keep].T@target)/s[keep])
            qalt=Vt[s>p['alternate_cutoff']*s[0]].T@((U[:,s>p['alternate_cutoff']*s[0]].T@target)/s[s>p['alternate_cutoff']*s[0]])
            local=(L@qhat).reshape(-1,2);alternate=(L@qalt).reshape(-1,2)
            causal,captured=causal_capture(system,u,surface,dt,p['duration'],p['sample_interval'],p['upstream_radius'],p['local_radius'])
            coarse,_=causal_capture(system,u,surface[::2],dt,p['duration'],p['sample_interval'],p['upstream_radius'],p['local_radius'])
            times=markers(t,local,p)
            sensitivity,witnesses=singular_audit(H,L,qhat,U,s,Vt,keep,target,times,t,p)
            prediction={'case':tag,'rank':int(keep.sum()),'columns':len(s),
                'relative_surface_residual':float(np.linalg.norm(H@qhat-target)/np.linalg.norm(target)),
                'inverse_markers':times,'alternate_markers':markers(t,alternate,p),
                'causal_markers':markers(t,causal[:,1:],p),
                'causal_surface_decimated_markers':markers(t,coarse[:,1:],p),
                'sensitivity':sensitivity,'witnesses':witnesses}
            np.savez_compressed(raw/f'forecast-{tag}.npz',t=t,inverse=local,alternate=alternate,causal=causal[:,1:],
                causal_surface_decimated=coarse[:,1:],surface=surface,qhat=qhat,captured=captured)
            write_json(raw/f'forecast-{tag}.json',prediction)
            locks.append({'case':tag,'npz':digest(raw/f'forecast-{tag}.npz'),'json':digest(raw/f'forecast-{tag}.json')})
            pending.append((tag,b,v,endstate,prediction,qhat,captured))
        write_json(raw/f'prediction-lock-{name}.json',locks[-len(p['waveforms']):])
        append_event(events,'variant-predictions-locked','run',{'variant':name,'sha256':digest(raw/f'prediction-lock-{name}.json')})
        for tag,b,v,endstate,prediction,qhat,captured in pending:
            append_event(events,'source-audit-started','run',{'case':tag})
            source=(L@b[inside]).reshape(-1,2)
            qerr=b[inside]-qhat;coordinates=Vt@qerr
            retained=(L@(Vt[keep].T@coordinates[keep])).reshape(-1,2)
            discarded=(L@(Vt[~keep].T@coordinates[~keep])).reshape(-1,2)
            projection=endstate.copy();projection[:,round(p['upstream_radius']/h):]=0
            M,K=frozen_operator(system,u)
            def energy(x):return .5*float(np.sum(x[1]**2/M+x[0]*K(x[0])))
            capture_error=captured-projection
            audit={'source_markers':markers(t,source,p),
                'source_energy_relative_drift':abs(energy(endstate)-energy(np.asarray([b,M*v])))/max(energy(np.asarray([b,M*v])),1e-300),
                'capture_energy_error_relative':energy(capture_error)/max(energy(projection),1e-300),
                'omitted_exterior_energy_relative':energy(endstate-projection)/max(energy(endstate),1e-300),
                'source_norm_relative_to_recovered':float(np.linalg.norm(b[inside])/np.linalg.norm(qhat)),
                'retained_input_error_norm':float(np.linalg.norm(coordinates[keep])),
                'discarded_input_error_norm':float(np.linalg.norm(coordinates[~keep])),
                'decomposition_residual':float(np.linalg.norm(source-(L@qhat).reshape(-1,2)-retained-discarded))}
            np.savez_compressed(raw/f'audit-{tag}.npz',source=source,retained_error=retained,discarded_error=discarded)
            write_json(raw/f'audit-{tag}.json',audit)
            summaries.append({'case':tag,**prediction,**audit})
            append_event(events,'source-audit-completed','run',{'case':tag})
        del H,L,U,s,Vt
    write_json(raw/'execution.json',{'algorithm':'linear-reconstruction-observability-v1','summaries':summaries,
        'nonlinear_receiver_executed':False,'causal_control':'two-site measured b and b_t; finite capture at t=16',
        'frozen_inputs':p['frozen_inputs']})
    write_json(raw/'rng-end.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    append_event(events,'worker-completed','run',{})
    return 0
