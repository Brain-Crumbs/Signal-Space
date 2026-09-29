"""Causal exterior elimination using two measured surface sites.

No source initial data enters replay. An auxiliary exterior solve is a
state-space realization of the exact causal boundary-memory convolution.
"""
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import brentq
from signal_space.numerics.prereception import ROOT, RadialSystem, digest
from signal_space.numerics.reception_transfer import incident
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event


def coefficients(system, u):
    r=system.r; mass=1+system.eps*abs(u/r)**2
    faces=(1+system.eps*system.faces(abs(u/r)**2))*(system.rf/system.h)**2
    diagonal=(faces[:-1]+faces[1:])/r**2
    diagonal[0]-=faces[0]/r[0]**2
    off=-faces[1:-1]/(r[:-1]*r[1:])
    return mass,diagonal,off


def stiffness(b,diagonal,off):
    out=diagonal*b
    out[...,1:]+=off*b[...,:-1]
    out[...,:-1]+=off*b[...,1:]
    return out


def advance(y,t,dt,rhs):
    k1=rhs(t,y);k2=rhs(t+dt/2,y+dt*k1/2)
    k3=rhs(t+dt/2,y+dt*k2/2);k4=rhs(t+dt,y+dt*k3)
    return y+dt*(k1+2*k2+2*k3+k4)/6


def source(system,u,b,v,dt,duration,sample,radius,local_radius,local=False):
    """Acquisition exports surface data only; local=True is a later audit."""
    M,D,O=coefficients(system,u);y=np.asarray([b,M*v]);rows=[]
    ix=round(radius/system.h)-1;probe=round(local_radius/system.h)-1
    stride=round(sample/dt);steps=round(duration/dt)
    def rhs(t,q):return np.asarray([q[1]/M,-stiffness(q[0],D,O)])
    def energy(q):return .5*np.sum(q[1]**2/M+q[0]*stiffness(q[0],D,O),axis=-1)
    initial=energy(y)
    for k in range(steps+1):
        if k%stride==0:
            if local: rows.append(np.stack((y[0,:,probe],y[1,:,probe]/M[probe]),axis=-1))
            else: rows.append(np.stack((y[0,:,ix],y[1,:,ix]/M[ix],y[0,:,ix+1],y[1,:,ix+1]/M[ix+1]),axis=-1))
        if k<steps:y=advance(y,k*dt,dt,rhs)
    return np.asarray(rows),abs(energy(y)-initial)/initial


def replay(system,u,t,surface,dt,duration,sample,radius,local_radius,cutoff):
    """Recover free exterior drive, then propagate with exterior memory.

    States: exterior response to measured interior surface x; full memory;
    memory with incoming drive cut at cutoff; Dirichlet no-memory control.
    No values of the original interior or source initial state are accepted.
    """
    M,D,O=coefficients(system,u);ix=round(radius/system.h)-1;edge=ix+1
    probe=round(local_radius/system.h)-1;link=O[ix]
    curve=CubicHermiteSpline(t,surface[:,:,[0,2]],surface[:,:,[1,3]],axis=0)
    y=np.zeros((4,2,surface.shape[1],len(M)));rows=[];drives=[]
    steps=round(duration/dt);stride=round(sample/dt)
    def rhs(time,q,short_drive):
        measured=curve(time);incoming=measured[:,1]-q[0,0,:,edge]
        out=np.stack((q[:,1]/M,-stiffness(q[:,0],D,O)),axis=1)
        out[0,:,:,:edge]=0
        out[0,1,:,edge]-=link*measured[:,0]
        out[1,1,:,ix]-=link*incoming
        if short_drive:out[2,1,:,ix]-=link*incoming
        out[3,:,:,edge:]=0
        out[3,1,:,ix]-=link*incoming
        return out
    for k in range(steps+1):
        if k%stride==0:
            rows.append(np.stack((y[1:,0,:,probe],y[1:,1,:,probe]/M[probe]),axis=-1))
            measured=curve(k*dt);drives.append(np.stack((measured[:,1],y[0,0,:,edge],measured[:,1]-y[0,0,:,edge]),axis=-1))
        if k<steps:
            # At the cutoff the final driven RK stage is included, exactly as
            # piecewise integration on [0,cutoff], [cutoff,duration] requires.
            short_drive=k<round(cutoff/dt)
            y=advance(y,k*dt,dt,lambda tt,qq:rhs(tt,qq,short_drive))
    return np.asarray(rows),np.asarray(drives)


def events(t,a,adot,rule='excursion'):
    """First local threshold rise, then first fall (or historical last fall)."""
    curve=CubicHermiteSpline(t,a,adot);crossings=[]
    for sign in (-1,1):
        q=sign*a-1e-4
        for i in np.flatnonzero(q[:-1]*q[1:]<0):
            root=brentq(lambda s:sign*float(curve(s))-1e-4,t[i],t[i+1])
            crossings.append((root,sign*float(curve(root,1))>0))
    crossings.sort();rises=[x for x,up in crossings if up]
    if not rises:return None
    falls=[x for x,up in crossings if not up and x>rises[0]]
    if not falls:return None
    return [float(rises[0]),float(falls[0] if rule=='excursion' else falls[-1])]


def execute(request_path):
    req=read_json(request_path);p=req['config']['parameters'];raw=Path(req['attempt_path'])/'raw';raw.mkdir(exist_ok=True)
    log=raw.parent/'events.jsonl'
    append_event(log,'worker-started','run',{'algorithm':'causal-exterior-memory-v1'})
    for item in p['frozen_inputs']:
        if digest(ROOT/item['path'])!=item['sha256']:raise ValueError('frozen input changed')
    write_json(raw/'rng-start.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    for variant in p['variants']:
        name=variant['name'];dt=variant['dt']
        with np.load(ROOT/variant['profile']) as data:r=data['r'];u=data['u']
        system=RadialSystem(r,p['epsilon']);waves=[incident(system.r,w,system.h) for w in p['waveforms']]
        b=np.asarray([w[0] for w in waves]);v=np.asarray([w[1] for w in waves])
        surface,energy=source(system,u,b,v,dt,p['duration'],p['sample_interval'],p['upstream_radius'],p['local_radius'])
        t=np.arange(len(surface))*p['sample_interval']
        np.savez_compressed(raw/f'surface-{name}.npz',t=t,records=surface)
        append_event(log,'surface-acquired','run',{'variant':name})
        prediction,drives=replay(system,u,t,surface,dt,p['duration'],p['sample_interval'],p['upstream_radius'],p['local_radius'],p['cutoff'])
        decimated,_=replay(system,u,t[::2],surface[::2],dt,p['duration'],p['sample_interval'],p['upstream_radius'],p['local_radius'],p['cutoff'])
        np.savez_compressed(raw/f'forecast-{name}.npz',t=t,records=prediction,decimated=decimated,drives=drives)
        lock={'surface_sha256':digest(raw/f'surface-{name}.npz'),'forecast_sha256':digest(raw/f'forecast-{name}.npz')}
        write_json(raw/f'lock-{name}.json',lock)
        append_event(log,'prediction-locked','run',{'variant':name,'sha256':digest(raw/f'lock-{name}.json')})
        append_event(log,'source-audit-started','run',{'variant':name})
        audit,drift=source(system,u,b,v,dt,p['duration'],p['sample_interval'],p['upstream_radius'],p['local_radius'],local=True)
        np.savez_compressed(raw/f'audit-{name}.npz',t=t,records=audit)
        write_json(raw/f'audit-{name}.json',{'relative_energy_drift':drift.tolist(),'acquisition_energy_drift':energy.tolist()})
        append_event(log,'source-audit-completed','run',{'variant':name})
    write_json(raw/'execution.json',{'algorithm':'causal-exterior-memory-v1','nonlinear_receiver_executed':False,
        'acquisition':'two-site frozen linear surface through t=60, acquired before replay; cutoff=16 diagnostic',
        'primary_events':'first complete local |a|=1e-4 threshold excursion',
        'legacy_events':'first rise and last fall retained as diagnostics',
        'known_limit':'same-discretization linear calibration; no physical noise model or nonlinear forecast'})
    write_json(raw/'rng-end.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    append_event(log,'worker-completed','run',{})
    return 0
