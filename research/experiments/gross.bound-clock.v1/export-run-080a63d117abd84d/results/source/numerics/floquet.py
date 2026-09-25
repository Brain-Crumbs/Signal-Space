"""Bounded physical tangent calculation; all results are saved before analysis."""
import os
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from signal_space.models.floquet import LABELS, N, stages, bloch, background, apply_tangent, perturb, ray
from signal_space.models.reciprocal import exact_gate, rhs
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event


def ode(state):
    r=solve_ivp(rhs,(0,1),state.ravel(),args=(np.pi/2,0,False),method='DOP853',rtol=2e-12,atol=2e-14,max_step=.05)
    if not r.success: raise ValueError(r.message)
    return r.y[:,-1].reshape(3,2)


def execute(request_path):
    request=read_json(request_path); attempt=Path(request['attempt_path']); raw=attempt/'raw'; raw.mkdir(exist_ok=True)
    events=attempt/'events.jsonl'; p=request['config']['parameters']
    append_event(events,'worker-started','run',{'pid':os.getpid(),'algorithm':'physical-ray-tangent-v1'})
    rng=np.random.Generator(np.random.PCG64(request['seed_ledger']['initialization']))
    write_json(raw/'rng-start.json',rng.bit_generator.state)
    directions=np.array(p['directions'],float); directions/=np.linalg.norm(directions,axis=1)[:,None]
    q=np.concatenate([r*directions for r in p['radii']]); data={'q':q,'directions':directions}
    grid=np.linspace(-np.pi,np.pi,p['path_points'])
    path=np.concatenate([grid[:,None]*d for d in directions[[13,16,25]]])
    data['path']=path; data['path_parameter']=np.tile(grid,3)
    # Staged inputs/outputs and both differential resolutions remain raw evidence.
    for label in LABELS:
        if (attempt/'cancel.request').exists(): return 130
        for hi,h in enumerate(p['steps']):
            inputs,outputs,blocks=stages(label,h)
            data[f'{label}_inputs']=inputs; data[f'{label}_outputs']=outputs
            data[f'{label}_blocks_{hi}']=blocks
            data[f'{label}_maps_{hi}']=np.array([bloch(blocks,k) for k in q])
        _,_,frozen=stages(label,p['steps'][-1],True)
        data[f'{label}_frozen_blocks']=frozen
        data[f'{label}_path_maps']=np.array([bloch(blocks,k) for k in path])
        data[f'{label}_frozen_maps']=np.array([bloch(frozen,k) for k in q])
        oi,oo,ob=stages(label,p['steps'][-1],solver=ode)
        data[f'{label}_ode_outputs']=oo; data[f'{label}_ode_blocks']=ob
        # Exact map gates tested on off-background normalized random states.
        controls=[]
        for _ in range(8):
            state=rng.normal(size=(3,2))+1j*rng.normal(size=(3,2)); state[2]/=np.linalg.norm(state[2])
            controls.append([state,exact_gate(state,np.pi/2,0)])
        data[f'{label}_conservation']=np.array(controls)
        # Physical memory phase null and overlap-changing tangent control.
        base=inputs[0]; phase=base.copy()
        phase[2]=base[2]*np.exp(.731j)
        data[f'{label}_phase_control']=np.array([exact_gate(base,np.pi/2,0),exact_gate(phase,np.pi/2,0)])
        data[f'{label}_physical_probe']=np.array([base[2],perturb(base,8,.01)[2]])
        # Local impulse at each box center, same observation before boundary wrap.
        for size in p['box_sizes']:
            field=np.zeros((size,size,size,N)); center=size//2
            field[center,center,center,8]=1
            history=[field.copy()]
            for _ in range(p['cycles']):
                field=apply_tangent(field,blocks); history.append(field.copy())
            data[f'{label}_impulse_{size}']=np.array(history)
        append_event(events,'background-completed','run',{'background':label,'physical_dimensions':N})
    np.savez_compressed(raw/'floquet.npz',**data)
    write_json(raw/'rng-end.json',rng.bit_generator.state)
    write_json(raw/'execution.json',{'seed_ledger':request['seed_ledger'],'algorithm':'exact-gate-centered-physical-ray-v1','backgrounds':list(LABELS),'memory_phase_quotient':True})
    append_event(events,'worker-completed','run',{'backgrounds':3})
    return 0
