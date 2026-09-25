"""Frozen input baseline and O(A²) prediction followed by reciprocal evolution.

Neutral discretization comes from a positive discrete Hamiltonian. No fitted
response coefficient enters the prediction. The tangent fields are Taylor
coefficients multiplying A², not differences of nonlinear experiments.
"""
from pathlib import Path
import hashlib
import shutil
import numpy as np
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event
from signal_space.numerics.clock import evolution
from signal_space.models.clock import core_force, clock_mass

ROOT = Path(__file__).resolve().parents[3]

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def lap(x, h):
    y = -2*x.copy()
    y[..., 1:] += x[..., :-1]
    y[..., :-1] += x[..., 1:]
    return y/h**2

class RadialSystem:
    def __init__(self, r, eps):
        self.r = r[1:-1]; self.h = r[1]-r[0]; self.eps = eps
        self.rf = (r[:-1]+r[1:])/2
    def gradient(self, b):
        a = b/self.r
        full = np.concatenate((a[..., :1], a, np.zeros_like(a[..., :1])), axis=-1)
        return np.diff(full, axis=-1)*self.rf/self.h
    def transpose(self, g):
        # G^T; the regular origin face has identically zero gradient.
        return (self.rf[:-1]*g[..., :-1]-self.rf[1:]*g[..., 1:])/(self.h*self.r)
    def faces(self, s):
        full = np.concatenate((s[..., :1], s, np.zeros_like(s[..., :1])), axis=-1)
        return (full[..., :-1]+full[..., 1:])/2
    def face_adjoint(self, g2):
        # g[0]=0, so the doubled regular-origin endpoint contributes zero.
        return (g2[..., :-1]+g2[..., 1:])/2
    def rhs(self, y, tangent=False):
        u, v, w, z, b, p = y[:6]
        w=w.real; z=z.real; b=b.real; p=p.real
        s=abs(u/self.r)**2; chi=w/self.r; Z=1+self.eps*s
        g=self.gradient(b); neutral_v=p/Z
        invariant=(neutral_v**2-self.face_adjoint(g*g))/self.r**2
        C=core_force(s)+.5*(-.4+.4*s)*chi**2
        dv=lap(u,self.h)-C*u
        if not tangent: dv += .5*self.eps*invariant*u
        out=[v,dv,z,lap(w,self.h)-clock_mass(s)*w-.1*chi**2*w,
             neutral_v,-self.transpose((1+self.eps*self.faces(s))*g)]
        if tangent:
            d,e,f,k=y[6:]; f=f.real; k=k.real
            ds=2*np.real(np.conj(u)*d)/self.r**2
            dc=(-2+6*s+.2*chi**2)*ds+(-.4+.4*s)*chi*f/self.r
            out.extend([e,lap(d,self.h)-C*d-dc*u+.5*self.eps*invariant*u,
                        k,lap(f,self.h)-(clock_mass(s)+.3*chi**2)*f-(-.4+.4*s)*ds*w])
        return np.asarray(out)
    def energy_charge(self,y):
        u,v,w,z,b,p=y[:6];w=w.real;z=z.real;b=b.real;p=p.real
        s=abs(u/self.r)**2
        du=np.diff(np.pad(u,((0,0),(1,1))),axis=-1)/self.h
        dw=np.diff(np.pad(w,((0,0),(1,1))),axis=-1)/self.h
        g=self.gradient(b)
        H=(np.sum(abs(v)**2+.5*z*z+self.r**2*(s-s*s+s**3+.5*clock_mass(s)*(w/self.r)**2+.025*(w/self.r)**4)+.5*p*p/(1+self.eps*s),axis=-1)
           +np.sum(abs(du)**2+.5*dw*dw+.5*(1+self.eps*self.faces(s))*g*g,axis=-1))
        Q=-2*np.sum(np.imag(np.conj(u)*v),axis=-1)
        return 4*np.pi*self.h*H,4*np.pi*self.h*Q

def packet(r, center, width):
    x=(r-center)/width; inside=abs(x)<1
    value=np.zeros_like(r);derivative=value.copy()
    c=np.cos(np.pi*x[inside]/2);sn=np.sin(np.pi*x[inside]/2)
    value[inside]=center*c**4
    derivative[inside]=-2*np.pi*center/width*c**3*sn
    return value,derivative

def integrate(system, u, mode, dt, duration, amplitudes, patterns, tangent):
    r=system.r; n=len(r); count=len(amplitudes)
    state=np.zeros((10 if tangent else 6,count,n),complex)
    state[0]=u;state[1]=-.9j*u
    state[2]=.001*mode/np.max(mode/r)
    incoming,iv=packet(r,18.,3.);outgoing,ov=packet(r,4.,2.)
    for j,(amp,pattern) in enumerate(zip(amplitudes,patterns)):
        state[4,j]=amp*(incoming+(outgoing if pattern=='counter' else 0))
        velocity=amp*(iv-(ov if pattern=='counter' else 0))
        state[5,j]=(1+system.eps*abs(u/r)**2)*velocity
    steps=round(duration/dt);stride=round(.1/dt)
    local=round(.1/system.h)-1;upstream=round(14/system.h)-1
    rows=[];spatial=[]
    for step in range(steps+1):
        if step%stride==0:
            E,Q=system.energy_charge(state)
            s=abs(state[0]/r)**2
            rows.append(np.array([np.full(count,step*dt),state[2,:,local].real/r[local],
               state[4,:,upstream].real/r[upstream], E,Q,
               state[8,:,local].real/r[local] if tangent else np.zeros(count),
               state[0,:,local].real, s[:,local]]).T)
        if step%round(2/dt)==0:
            spatial.append(np.stack((state[4,:,::4].real/r[::4],state[2,:,::4].real/r[::4])))
        if step==steps:break
        k1=system.rhs(state,tangent);k2=system.rhs(state+dt*k1/2,tangent)
        k3=system.rhs(state+dt*k2/2,tangent);k4=system.rhs(state+dt*k3,tangent)
        state += dt/6*(k1+2*k2+2*k3+k4)
        if not np.isfinite(state).all():raise ValueError(f'nonfinite state at {step*dt}')
    return np.asarray(rows),np.asarray(spatial),r[::4]

def execute(request_path):
    req=read_json(request_path);cfg=req['config'];p=cfg['parameters'];kind=p['kind']
    attempt=Path(req['attempt_path']);raw=attempt/'raw';raw.mkdir(exist_ok=True)
    events=attempt/'events.jsonl'
    append_event(events,'worker-started','run',{'algorithm':'frozen-profile-prereception-v1','kind':kind})
    frozen=[]
    for source in p['frozen_inputs']:
        origin=ROOT/source['path']
        if digest(origin)!=source['sha256']:raise ValueError('frozen profile hash changed')
        shutil.copy2(origin,raw/source['name']);frozen.append(source)
    write_json(raw/'frozen-inputs.json',frozen)
    write_json(raw/'rng-start.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    details=[]
    if kind=='longevity':
        for label,source,h,dt in [('base','profile-0.900.npz',.1,.04),('fine','profile-fine.npz',.05,.02),('time','profile-0.900.npz',.1,.02)]:
            with np.load(raw/source) as d:
                r=d['r'];u=d['u'];mode=d['mode'];eig=float(d['eigenvalues'][0])
            # Fixed physical duration from frozen nominal eigenfrequency.
            cycles=100*np.sqrt(eig)/p['omega_chi']
            rows,info=evolution(r,u,mode,.9,eig,.001,h,dt,cycles,round(.2/dt),60,round(.1/h)-1)
            np.savez_compressed(raw/f'longevity-{label}.npz',records=rows)
            details.append({'label':label,**info,'readout_radius':.1})
            append_event(events,'longevity-completed','run',{'label':label,'steps':info['steps']})
    else:
        # ALL predictions are saved and hashed before ANY full nonlinear receiver run.
        variants=[('base','profile-0.900.npz',.02),('fine','profile-fine.npz',.01),
                  ('time','profile-0.900.npz',.01),('wide','profile-wide.npz',.02)]
        prepared=[]
        for label,source,dt in variants:
            with np.load(raw/source) as d:r=d['r'];u=d['u'];mode=d['mode']
            sys=RadialSystem(r,p['epsilon'])
            records,fields,rr=integrate(sys,u,mode,dt,p['duration'],[1,1],['single','counter'],True)
            path=raw/f'prediction-{label}.npz'
            np.savez_compressed(path,records=records,fields=fields,r=rr)
            prepared.append((label,source,dt));details.append({'label':label,'prediction_sha256':digest(path),'dt':dt})
            append_event(events,'prediction-saved','run',{'label':label,'sha256':digest(path)})
        write_json(raw/'prediction-lock.json',details)
        append_event(events,'all-predictions-locked','run',{'sha256':digest(raw/'prediction-lock.json')})
        for label,source,dt in prepared:
            with np.load(raw/source) as d:r=d['r'];u=d['u'];mode=d['mode']
            sys=RadialSystem(r,p['epsilon'])
            amps=p['amplitudes'];patterns=p['patterns']
            records,fields,rr=integrate(sys,u,mode,dt,p['duration'],amps,patterns,False)
            np.savez_compressed(raw/f'receiver-{label}.npz',records=records,fields=fields,r=rr)
            append_event(events,'receiver-completed','run',{'label':label})
    write_json(raw/'execution.json',{'kind':kind,'details':details,'frozen_inputs_verified':True,
        'source_run':'run-080a63d117abd84d','calibration':{'omega_Q':.9,'omega_chi':p['omega_chi'],'readout_radius':.1},
        'geometry':'spherical flat decoupling; concentric shells; no recoil'})
    write_json(raw/'rng-end.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    append_event(events,'worker-completed','run',{'kind':kind})
    return 0
