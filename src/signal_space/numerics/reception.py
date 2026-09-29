"""Test 7: surface-only input inversion, locked Taylor predictions, held-out receiver.

The predictor never receives prescribed packet parameters or receiver interiors.
The neutral acquisition evolves only a linear field on a frozen core background.
"""
from pathlib import Path
import shutil
import numpy as np
from scipy.interpolate import CubicSpline
from signal_space.numerics.prereception import RadialSystem, packet, digest, ROOT
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event

# Columns are stable raw contracts, in natural units.
COLUMNS = ['time','chi','chi_dot','a','a_dot','density','invariant','energy','charge',
           'delta_chi_2','delta_chi_dot_2','delta_density_2']
VARIANTS = [('base','profile-0.900.npz',.1,.02),
            ('fine','profile-fine.npz',.05,.01),
            ('finer','profile-fine.npz',.025,.005),
            ('time','profile-0.900.npz',.1,.01),
            ('wide','profile-wide.npz',.1,.02)]

def profile(raw, source, h):
    with np.load(raw/source) as d:
        r=d['r'].copy();u=d['u'].copy();mode=d['mode'].copy()
    if abs(r[1]-h)>1e-10:
        target=np.arange(round(r[-1]/h)+1)*h
        # Interpolate the SAME frozen calibration, without a new eigenproblem.
        u=CubicSpline(r,np.r_[0,u,0],bc_type='natural')(target)[1:-1]
        mode=CubicSpline(r,np.r_[0,mode,0],bc_type='natural')(target)[1:-1]
        r=target
    return r,u,mode

def rk4(y,dt,rhs):
    a=rhs(y);b=rhs(y+dt*a/2);c=rhs(y+dt*b/2);d=rhs(y+dt*c)
    return y+dt*(a+2*b+2*c+d)/6

def acquire(system,u,dt,p):
    """Return ONLY surface data for two prescribed incoming pulses; no interior export."""
    r=system.r;s=abs(u/r)**2;Z=1+system.eps*s
    y=np.zeros((2,2,len(r)))
    for j,center in enumerate(p['packet_centers']):
        b,v=packet(r,center,p['packet_width']);y[0,j]=b;y[1,j]=Z*v
    def rhs(state):
        return np.array([state[1]/Z,-system.transpose((1+system.eps*system.faces(s))*system.gradient(state[0]))])
    ix=round(p['upstream_radius']/system.h)-1;rows=[]
    for k in range(round(p['acquisition_duration']/dt)+1):
        # b=r*a; b_r=a+r*a_r. Both radial and temporal derivatives are recorded.
        b=y[0,:,ix];bt=y[1,:,ix]/Z[ix];br=(y[0,:,ix+1]-y[0,:,ix-1])/(2*system.h)
        R=r[ix]
        rows.append(np.array([np.full(2,k*dt),b/R,bt/R,(br-b/R)/R]).T)
        y=rk4(y,dt,rhs)
    return np.asarray(rows)

def reconstruct(surface,r,R):
    """Invert vacuum incoming characteristic I=(r*a_t+a+r*a_r)/2.

For b=F(t+r-R)+G(t-r+R), I=F'. A cubic antiderivative
with F(0)=0 reconstructs F; compact endpoint closure removes a measured
linear drift. This is an explicit exterior vacuum approximation.
"""
    t=surface[:,0];a=surface[:,1];at=surface[:,2];ar=surface[:,3]
    incoming=(R*at+a+R*ar)/2;outgoing=(R*at-a-R*ar)/2
    curve=CubicSpline(t,incoming);primitive=curve.antiderivative()
    closure=float(primitive(t[-1])-primitive(t[0]));x=r-R
    valid=(x>=t[0])&(x<=t[-1]);b=np.zeros_like(r);v=b.copy()
    b[valid]=primitive(x[valid])-primitive(t[0])-closure*x[valid]/t[-1]
    v[valid]=curve(x[valid])-closure/t[-1]
    return b,v,{'incoming':incoming,'outgoing':outgoing,'closure':closure}

def evolve(system,u,mode,dt,p,cases,neutral,tangent=False,frozen_core=False):
    r=system.r;n=len(r);count=len(cases);y=np.zeros((10 if tangent else 6,count,n),complex)
    y[0]=u;y[1]=-.9j*u
    amp=p['clock_amplitude'];omega=p['omega_chi'];clock=amp*mode/np.max(mode/r)
    for j,c in enumerate(cases):
        y[2,j]=clock*np.cos(c['phase']);y[3,j]=-omega*clock*np.sin(c['phase'])
        b,v=neutral(c,r);y[4,j]=b;y[5,j]=(1+system.eps*abs(u/r)**2)*v
    local=round(p['local_radius']/system.h)-1;rows=[];fields=[]
    def rhs(state):
        out=system.rhs(state,tangent)
        if frozen_core:
            # Deliberately incomplete Taylor replay: remove the neutral core source.
            out[6:]=0
        return out
    stride=round(p['sample_interval']/dt)
    for step in range(round(p['duration']/dt)+1):
        if step%stride==0:
            E,Q=system.energy_charge(y);s=abs(y[0]/r)**2;bt=y[5].real/(1+system.eps*s)
            inv=(bt*bt-system.face_adjoint(system.gradient(y[4].real)**2))/r**2
            ds=2*np.real(np.conj(y[0])*y[6])/r**2 if tangent else np.zeros((count,n))
            rows.append(np.array([np.full(count,step*dt),y[2,:,local].real/r[local],
                y[3,:,local].real/r[local],y[4,:,local].real/r[local],bt[:,local]/r[local],s[:,local],inv[:,local],E,Q,
                y[8,:,local].real/r[local] if tangent else np.zeros(count),
                y[9,:,local].real/r[local] if tangent else np.zeros(count),ds[:,local]]).T)
        if step%round(1/dt)==0:
            ix=(r<=35)&(np.arange(n)%max(1,round(.2/system.h))==0)
            fields.append(np.stack((y[4,:,ix].real.T/r[ix],inv[:,ix] if step%stride==0 else np.zeros((count,np.sum(ix))))))
        if step==round(p['duration']/dt):break
        y=rk4(y,dt,rhs)
        if not np.isfinite(y).all():raise ValueError('nonfinite reception state')
    return np.asarray(rows),np.asarray(fields),r[ix]

def execute(request_path):
    req=read_json(request_path);p=req['config']['parameters'];attempt=Path(req['attempt_path']);raw=attempt/'raw';raw.mkdir(exist_ok=True)
    events=attempt/'events.jsonl'
    for src in p['frozen_inputs']:
        if digest(ROOT/src['path'])!=src['sha256']:raise ValueError('frozen calibration changed')
        shutil.copy2(ROOT/src['path'],raw/src['name'])
    write_json(raw/'rng-start.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    locks=[]
    for label,source,h,dt in VARIANTS:
        r,u,mode=profile(raw,source,h);sys=RadialSystem(r,p['epsilon'])
        np.savez_compressed(raw/f'calibration-{label}.npz',r=r,u=u,mode=mode)
        surface=acquire(sys,u,dt,p);np.savez_compressed(raw/f'surface-{label}.npz',records=surface)
        # Cross the information barrier: reload only the surface artifact.
        surface=np.load(raw/f'surface-{label}.npz')['records'];replays=[];characteristics=[]
        for j in range(2):
            b,v,info=reconstruct(surface[surface[:,j,0]<=p['incoming_window'],j],sys.r,p['upstream_radius']);replays.append((b,v));characteristics.append(info)
        np.savez_compressed(raw/f'input-{label}.npz',b=np.array([x[0] for x in replays]),v=np.array([x[1] for x in replays]),
            incoming=np.array([x['incoming'] for x in characteristics]),outgoing=np.array([x['outgoing'] for x in characteristics]),closure=np.array([x['closure'] for x in characteristics]))
        def measured(c,rr):
            return tuple(sum(c['weights'][j]*replays[j][k] for j in range(2)) for k in range(2))
        # Prediction cases use unit neutral coefficient; scale by A² only downstream.
        pcases=[dict(c,amplitude=1.) for c in p['prediction_cases']]
        rec,fields,rr=evolve(sys,u,mode,dt,p,pcases,measured,True)
        np.savez_compressed(raw/f'prediction-{label}.npz',records=rec,fields=fields,r=rr)
        # Frozen core gives identically zero clock perturbation in this action.
        locks.append({'label':label,'prediction_sha256':digest(raw/f'prediction-{label}.npz'),
                      'surface_sha256':digest(raw/f'surface-{label}.npz'),'input_sha256':digest(raw/f'input-{label}.npz'),
                      'calibration_sha256':digest(raw/f'calibration-{label}.npz')})
        append_event(events,'prediction-saved','run',{'label':label})
    write_json(raw/'prediction-lock.json',locks)
    append_event(events,'all-predictions-locked','run',{'sha256':digest(raw/'prediction-lock.json')})
    for label,source,h,dt in VARIANTS:
        append_event(events,'receiver-started','run',{'label':label})
        r,u,mode=profile(raw,source,h);sys=RadialSystem(r,p['epsilon'])
        def prescribed(c,rr):
            packets=[packet(rr,center,p['packet_width']) for center in p['packet_centers']]
            return tuple(c['amplitude']*sum(c['weights'][j]*packets[j][k] for j in range(2)) for k in range(2))
        rec,fields,rr=evolve(sys,u,mode,dt,p,p['cases'],prescribed)
        np.savez_compressed(raw/f'receiver-{label}.npz',records=rec,fields=fields,r=rr)
        append_event(events,'receiver-completed','run',{'label':label})
    # Actually execute the deliberately incomplete replay on the base mesh.
    r,u,mode=profile(raw,'profile-0.900.npz',.1);sys=RadialSystem(r,p['epsilon'])
    inp=np.load(raw/'input-base.npz')
    def incomplete(c,rr):return inp['b'][0],inp['v'][0]
    rec,_,_=evolve(sys,u,mode,.02,p,[p['prediction_cases'][0]],incomplete,True,True)
    np.savez_compressed(raw/'frozen-core.npz',records=rec)
    write_json(raw/'execution.json',{'algorithm':'surface-only-reception-v1','columns':COLUMNS,'variants':VARIANTS,
       'source_run':'run-82cb109afa4e14c2','prediction_cases':p['prediction_cases'],'cases':p['cases'],
       'limitations':['spherical reflected shells, not opposing planar beams','flat fixed receiver; no recoil or transformed history',
                       'finer grid interpolates frozen fine profile, not a newly solved branch','surface acquisition is linear on frozen background']})
    write_json(raw/'rng-end.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    append_event(events,'worker-completed','run',{})
    return 0
