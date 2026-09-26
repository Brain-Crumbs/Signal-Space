"""Unfitted A^4 Taylor response of the registered radial discrete Hamiltonian.

The first ten channels are the exact Test 7 quiet, odd-neutral and even-order
tangent system. Six appended channels evolve neutral order three and charged /
clock order four. Coefficients are derivatives divided by factorials, not fits.
"""
from pathlib import Path
import shutil
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.integrate import cumulative_trapezoid
from signal_space.numerics.prereception import RadialSystem, packet, ROOT, digest
from signal_space.numerics.reception import profile, acquire, reconstruct, rk4
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event
from signal_space.models.clock import core_force, clock_mass


def jet_rhs(system, y):
    """Exact formal coefficient extraction through A^4, at each RK4 stage."""
    r=system.r; eps=system.eps
    u,v,w,z,b,p,d,e,f,k,b3,p3,d4,e4,f4,k4=y
    base=system.rhs(y[:10], True)
    s0=abs(u/r)**2; s2=2*np.real(np.conj(u)*d)/r**2
    s4=(abs(d)**2+2*np.real(np.conj(u)*d4))/r**2
    c0=w.real/r; c2=f.real/r; c4=f4.real/r
    Z0=1+eps*s0; Z2=eps*s2
    bt1=p.real/Z0; bt3=p3.real/Z0-Z2*p.real/Z0**2
    g1=system.gradient(b.real); g3=system.gradient(b3.real)
    j2=(bt1**2-system.face_adjoint(g1**2))/r**2
    j4=(2*bt1*bt3-2*system.face_adjoint(g1*g3))/r**2
    C0=core_force(s0)+.5*(-.4+.4*s0)*c0**2
    C2=(-2+6*s0+.2*c0**2)*s2+(-.4+.4*s0)*c0*c2
    C4=(-2+6*s0+.2*c0**2)*s4+3*s2**2+.4*s2*c0*c2+(-.4+.4*s0)*(c0*c4+.5*c2**2)
    M0=clock_mass(s0); M2=(-.4+.4*s0)*s2
    M4=(-.4+.4*s0)*s4+.2*s2**2
    return np.concatenate((base, np.asarray([
        bt3,
        -system.transpose((1+eps*system.faces(s0))*g3+eps*system.faces(s2)*g1),
        e4,
        system_lap(system,d4)-C0*d4-C2*d-C4*u+.5*eps*(j2*d+j4*u),
        k4,
        system_lap(system,f4)-M0*f4-M2*f-M4*w-.1*(3*c0**2*f4+3*c0*c2*f),
    ])))


def system_lap(system, x):
    from signal_space.numerics.prereception import lap
    return lap(x, system.h)


def evolve_jet(system,u,mode,dt,duration,sample,clock_amp,omega,phase,b1,v1):
    r=system.r; y=np.zeros((16,len(r)),complex)
    y[0]=u;y[1]=-.9j*u
    y[2]=clock_amp*mode/np.max(mode/r)*np.cos(phase)
    y[3]=-omega*clock_amp*mode/np.max(mode/r)*np.sin(phase)
    y[4]=b1;y[5]=(1+system.eps*abs(u/r)**2)*v1
    local=round(.1/system.h)-1; rows=[]; stride=round(sample/dt)
    for step in range(round(duration/dt)+1):
        if step%stride==0:
            s=abs(y[0]/r)**2; Z=1+system.eps*s
            rows.append([step*dt,y[2,local].real/r[local],y[3,local].real/r[local],
                y[8,local].real/r[local],y[9,local].real/r[local],
                y[14,local].real/r[local],y[15,local].real/r[local],
                y[4,local].real/r[local],y[5,local].real/Z[local]/r[local],
                y[10,local].real/r[local],
                (y[11,local].real/Z[local]-system.eps*(2*np.real(np.conj(y[0,local])*y[6,local])/r[local]**2)*y[5,local].real/Z[local]**2)/r[local]])
        if step==round(duration/dt):break
        y=rk4(y,dt,lambda q:jet_rhs(system,q))
        if not np.isfinite(y).all():raise ValueError('nonfinite order-four jet')
    return np.asarray(rows)


def evolve_full(system,u,mode,dt,duration,sample,clock_amp,omega,phase,b,v,amps):
    r=system.r; n=len(r); y=np.zeros((6,len(amps)+1,n),complex)
    y[0]=u;y[1]=-.9j*u
    y[2]=clock_amp*mode/np.max(mode/r)*np.cos(phase)
    y[3]=-omega*clock_amp*mode/np.max(mode/r)*np.sin(phase)
    for j,A in enumerate(amps,1):y[4,j]=A*b;y[5,j]=A*(1+system.eps*abs(u/r)**2)*v
    local=round(.1/system.h)-1; stride=round(sample/dt);rows=[]
    for step in range(round(duration/dt)+1):
        if step%stride==0:
            s=abs(y[0]/r)**2; Z=1+system.eps*s
            E,Q=system.energy_charge(y)
            rows.append(np.stack((np.full(len(amps)+1,step*dt),y[2,:,local].real/r[local],
                y[3,:,local].real/r[local],y[4,:,local].real/r[local],
                (y[5].real/Z)[:,local]/r[local],E,Q),axis=-1))
        if step==round(duration/dt):break
        y=rk4(y,dt,lambda q:system.rhs(q,False))
        if not np.isfinite(y).all():raise ValueError('nonfinite heldout receiver')
    return np.asarray(rows)


def reconstruct_optical(surface, r, u, eps, R):
    """Leading WKB inversion using the known exterior Z(r), with no receiver data.

    The omitted reflection/dispersion of the discrete transfer remains an
    independently tested limitation; this is not called an exact inverse.
    """
    interior=r[1:-1]; Z=1+eps*abs(u/interior)**2
    time=surface[:,0];a,at,ar=surface[:,1:].T
    ix=round(R/(r[1]-r[0]))-1; speed=np.sqrt(Z[ix])
    incoming=(R*at+speed*(a+R*ar))/2
    curve=CubicSpline(time,incoming);anti=curve.antiderivative()
    closure=float(anti(time[-1])-anti(time[0]))
    travel=cumulative_trapezoid(1/np.sqrt(Z),interior,initial=0)
    x=travel-travel[ix];valid=(x>=time[0])&(x<=time[-1]);b=np.zeros_like(interior);v=b.copy()
    scale=(Z[ix]/Z)**.25
    b[valid]=scale[valid]*(anti(x[valid])-anti(time[0])-closure*x[valid]/time[-1])
    v[valid]=scale[valid]*(curve(x[valid])-closure/time[-1])
    return b,v,{'surface_Z':float(Z[ix]),'closure':closure,
                'optical_distance_to_edge':float(travel[-1]-travel[ix])}


def execute(request_path):
    req=read_json(request_path);p=req['config']['parameters'];raw=Path(req['attempt_path'])/'raw';raw.mkdir(exist_ok=True)
    events=raw.parent/'events.jsonl'
    append_event(events,'worker-started','run',{'algorithm':'formal-order-four-reception-v1'})
    for src in p['frozen_inputs']:
        if digest(ROOT/src['path'])!=src['sha256']:raise ValueError('calibration changed')
        shutil.copy2(ROOT/src['path'],raw/src['name'])
    write_json(raw/'rng-start.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    prior=ROOT/p['prior_raw'];prepared=[];locks=[]
    for variant in p['variants']:
        label=variant['name'];h=variant['h'];dt=variant['dt'];r,u,mode=profile(raw,variant['profile'],h)
        sys=RadialSystem(r,p['epsilon'])
        # Diagnostic uses already inspected Test 7 data. No new claim of blindness.
        if label=='finer':
            with np.load(prior/f'input-{label}.npz') as old:b0=old['b'][0].copy();v0=old['v'][0].copy()
            diag=evolve_jet(sys,u,mode,dt,p['duration'],p['sample_interval'],p['clock_amplitude'],p['omega_chi'],0,b0,v0)
            np.savez_compressed(raw/f'diagnostic-{label}.npz',records=diag)
        # Held-out excitation is chosen in the locked plan, after the old-data diagnostic.
        center=p['heldout_center'];width=p['heldout_width']
        def wave(rr):return packet(rr,center,width)
        # Acquisition produces only upstream field/derivative histories.
        spec=dict(packet_centers=[center,center],packet_width=width,upstream_radius=p['upstream_radius'],acquisition_duration=p['acquisition_duration'])
        surface=acquire(sys,u,dt,spec)[:,0,:]
        np.savez_compressed(raw/f'surface-{label}.npz',records=surface)
        window=surface[surface[:,0]<=p['incoming_window']]
        vacuum_b,vacuum_v,vacuum_info=reconstruct(window,r,p['upstream_radius'])
        b1,v1,info=reconstruct_optical(window,r,u,p['epsilon'],p['upstream_radius'])
        # Known exterior Z profile gives a separate travel-time correction.
        # Keep the original vacuum inversion as the registered primary forecast.
        write_json(raw/f'optical-{label}.json',info|{'vacuum_closure':vacuum_info['closure']})
        np.savez_compressed(raw/f'input-{label}.npz',b=b1,v=v1,vacuum_b=vacuum_b,vacuum_v=vacuum_v)
        jet=evolve_jet(sys,u,mode,dt,p['duration'],p['sample_interval'],p['clock_amplitude'],p['omega_chi'],0,b1,v1)
        np.savez_compressed(raw/f'prediction-{label}.npz',records=jet)
        locks.append({x:digest(raw/f'{x}-{label}.npz') for x in ('surface','input','prediction')}|{'grid':label})
        append_event(events,'prediction-saved','run',{'grid':label})
        prepared.append((variant,r,u,mode))
    write_json(raw/'prediction-lock.json',locks)
    append_event(events,'all-predictions-locked','run',{'sha256':digest(raw/'prediction-lock.json')})
    for variant,r,u,mode in prepared:
        label=variant['name'];sys=RadialSystem(r,p['epsilon']);b,v=wave(sys.r)
        append_event(events,'receiver-started','run',{'grid':label})
        rec=evolve_full(sys,u,mode,variant['dt'],p['duration'],p['sample_interval'],p['clock_amplitude'],p['omega_chi'],0,b,v,p['amplitudes'])
        np.savez_compressed(raw/f'receiver-{label}.npz',records=rec)
        append_event(events,'receiver-completed','run',{'grid':label})
    write_json(raw/'execution.json',{'algorithm':'formal-order-four-reception-v1','prior_run':'run-b1677e67610c5870',
        'prior_role':'inspected diagnostic only','amplitudes':p['amplitudes'],'variants':p['variants']})
    write_json(raw/'rng-end.json',{'seed':req['seed_ledger'],'stochastic_use':'none'})
    append_event(events,'worker-completed','run',{})
    return 0
