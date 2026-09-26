"""Discrete surface observability inverse followed by locked Taylor forecasts.

Only the acquisition function knows the pulse shape. The inverse receives two
surface traces, frozen Z, support, and the declared incoming rule v=D_h b.
It fits initial data, never a clock-response coefficient.
"""
from pathlib import Path
import numpy as np
from scipy.linalg import lstsq
from signal_space.numerics.prereception import RadialSystem, ROOT, digest, packet
from signal_space.numerics.reception import rk4, profile as frozen_profile
from signal_space.numerics.clock import profile, eigenproblem
from signal_space.numerics.reception_order4 import evolve_jet, evolve_full
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event


def derivative(x, h):
    """Centered skew-adjoint derivative with zero endpoint extension."""
    y=np.zeros_like(x); y[..., :-1]+=x[..., 1:]; y[..., 1:]-=x[..., :-1]
    return y/(2*h)


def frozen_operator(system, u):
    density=abs(u/system.r)**2
    mass=1+system.eps*density
    faces=1+system.eps*system.faces(density)
    def stiffness(x):
        return system.transpose(faces*system.gradient(x))
    return mass, stiffness


def incident(r, wave, h):
    b,_=packet(r,wave['center'],wave['width'])
    b*=np.cos(wave['carrier']*(r-wave['center']))
    return b, derivative(b,h)


def acquire_surface(system,u,b,v,dt,duration,sample,R):
    mass,K=frozen_operator(system,u); y=np.asarray([b,mass*v]);rows=[]
    index=round(R/system.h)-1;stride=round(sample/dt)
    def rhs(q):return np.asarray([q[1]/mass,-K(q[0])])
    for k in range(round(duration/dt)+1):
        if k%stride==0:rows.append([k*dt,y[0,index],y[1,index]/mass[index]])
        if k<round(duration/dt):y=rk4(y,dt,rhs)
    return np.asarray(rows)


def observation_matrix(system,u,dt,duration,sample,R,support):
    """Rows C R(dt F)^k B via R(dt F.T)^k C.T; no pulse input.

    F=[0,M^-1;-K,0], B=[I;M D]. RK4 is a matrix polynomial,
    so this is the exact transpose of the acquisition time discretization.
    """
    mass,K=frozen_operator(system,u);n=len(mass);index=round(R/system.h)-1
    y=np.zeros((2,2,n));y[0,0,index]=1;y[1,1,index]=1/mass[index]
    inside=(system.r>=support[0]-1e-9)&(system.r<=support[1]+1e-9)
    rows=[];stride=round(sample/dt)
    def rhs(q):return np.asarray([-K(q[1]),q[0]/mass])
    for k in range(round(duration/dt)+1):
        if k%stride==0:
            rows.append((y[0]-derivative(mass*y[1],system.h))[:,inside])
        if k<round(duration/dt):y=rk4(y,dt,rhs)
    return np.asarray(rows).reshape(-1,int(inside.sum())),inside


def invert_surface(system,H,inside,surface,cutoff):
    target=surface[:,1:].reshape(-1)
    coeff,residual,rank,singular=lstsq(H,target,cond=cutoff,lapack_driver='gelsd')
    b=np.zeros(len(system.r));b[inside]=coeff;v=derivative(b,system.h)
    info={'cutoff':cutoff,'rank':int(rank),'columns':H.shape[1],'rows':H.shape[0],
          'relative_surface_residual':float(np.linalg.norm(H@coeff-target)/np.linalg.norm(target)),
          'singular_values':singular.tolist()}
    return b,v,info


def forecast_record(jet,A,omega,threshold):
    from signal_space.analysis.reception_order4 import hermite_markers
    from scipy.interpolate import CubicSpline
    z0=jet[:,1]-1j*jet[:,2]/omega;z2=jet[:,3]-1j*jet[:,4]/omega;z4=jet[:,5]-1j*jet[:,6]/omega
    second=A*A*np.imag(z2/z0)/(2*np.pi)
    fourth=second+A**4*np.imag(z4/z0-.5*(z2/z0)**2)/(2*np.pi)
    times=hermite_markers(jet[:,0],A*jet[:,7]+A**3*jet[:,9],A*jet[:,8]+A**3*jet[:,10],threshold)
    def delta(q):
        if times is None:return None
        curve=CubicSpline(jet[:,0],q);return float(curve(times[1])-curve(times[0]))
    return {'amplitude':A,'markers':times,'second':delta(second),'fourth':delta(fourth)}


def execute(request_path):
    req=read_json(request_path);p=req['config']['parameters'];raw=Path(req['attempt_path'])/'raw';raw.mkdir(exist_ok=True)
    events=raw.parent/'events.jsonl'
    append_event(events,'worker-started','run',{'algorithm':'discrete-adjoint-surface-transfer-v1'})
    for src in p['frozen_inputs']:
        if digest(ROOT/src['path'])!=src['sha256']:raise ValueError('frozen source changed')
    write_json(raw/'rng-start.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    profiles={};prepared=[];locks=[];forecasts=[]
    for variant in p['variants']:
        name=variant['name'];h=variant['h'];dt=variant['dt'];radius=variant['radius']
        key=(h,radius,variant['profile'])
        if key not in profiles:
            if variant['profile']=='independent':
                r,u,attempts=profile(p['omega_Q'],radius,h)
                if u is None:raise ValueError('independent profile failed')
                eigen,mode,_=eigenproblem(r,u,h,.4)
                info={'attempts':attempts,'eigenvalues':eigen.tolist(),'method':'independent BVP and discrete Newton; independent eigenproblem; fixed readout omega'}
            else:
                source=p['frozen_inputs'][1]
                r,u,mode=frozen_profile(ROOT/Path(source['path']).parent,Path(source['path']).name,h)
                info={'method':'interpolated prior fine profile, diagnostic only'}
            profiles[key]=(r,u,mode,info)
        r,u,mode,info=profiles[key];system=RadialSystem(r,p['epsilon'])
        np.savez_compressed(raw/f'profile-{name}.npz',r=r,u=u,mode=mode,Z=1+p['epsilon']*abs(u/system.r)**2)
        write_json(raw/f'profile-{name}.json',info)
        H,inside=observation_matrix(system,u,dt,p['acquisition_duration'],p['surface_sample_interval'],p['upstream_radius'],p['support'])
        for wave in p['waveforms']:
            tag=name+'-'+wave['name'];b,v=incident(system.r,wave,h)
            surface=acquire_surface(system,u,b,v,dt,p['acquisition_duration'],p['surface_sample_interval'],p['upstream_radius'])
            np.savez_compressed(raw/f'surface-{tag}.npz',records=surface)
            recovered,velocity,inverse=invert_surface(system,H,inside,surface,variant['cutoff'])
            np.savez_compressed(raw/f'input-{tag}.npz',b=recovered,v=velocity)
            write_json(raw/f'inverse-{tag}.json',inverse)
            jet=evolve_jet(system,u,mode,dt,p['duration'],p['sample_interval'],p['clock_amplitude'],p['omega_chi'],0,recovered,velocity)
            np.savez_compressed(raw/f'prediction-{tag}.npz',records=jet)
            records=[forecast_record(jet,A,p['omega_chi'],p['marker_threshold']) for A in p['amplitudes']]
            forecasts.append({'case':tag,'records':records})
            locks.append({'case':tag,**{x:digest(raw/f'{x}-{tag}.npz') for x in ('surface','input','prediction')},'profile':digest(raw/f'profile-{name}.npz')})
            prepared.append((variant,wave,r,u,mode))
            append_event(events,'prediction-saved','run',{'case':tag,'forecasts':records})
    write_json(raw/'forecast-markers-and-intervals.json',forecasts)
    write_json(raw/'prediction-lock.json',{'files':locks,'forecast_sha256':digest(raw/'forecast-markers-and-intervals.json')})
    append_event(events,'all-predictions-locked','run',{'sha256':digest(raw/'prediction-lock.json')})
    for variant,wave,r,u,mode in prepared:
        tag=variant['name']+'-'+wave['name'];system=RadialSystem(r,p['epsilon']);b,v=incident(system.r,wave,variant['h'])
        append_event(events,'receiver-started','run',{'case':tag})
        rec=evolve_full(system,u,mode,variant['dt'],p['duration'],p['sample_interval'],p['clock_amplitude'],p['omega_chi'],0,b,v,p['amplitudes'])
        np.savez_compressed(raw/f'receiver-{tag}.npz',records=rec)
        # Source-shape audit is downstream of every prediction lock.
        with np.load(raw/f'input-{tag}.npz') as d:
            audit={'b_relative_error':float(np.linalg.norm(d['b']-b)/np.linalg.norm(b)),
                   'v_relative_error':float(np.linalg.norm(d['v']-v)/np.linalg.norm(v))}
        write_json(raw/f'input-audit-{tag}.json',audit)
        append_event(events,'receiver-completed','run',{'case':tag})
    write_json(raw/'execution.json',{'algorithm':'discrete-adjoint-surface-transfer-v1','variants':p['variants'],'waveforms':p['waveforms'],
        'preparation':'compact incoming b; v=D_h b, known support only passed to inverse','receiver_use_in_prediction':False})
    write_json(raw/'rng-end.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    append_event(events,'worker-completed','run',{})
    return 0
