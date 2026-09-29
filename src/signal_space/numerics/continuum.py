"""Bounded seeded local jet audit; every input and unsummarized output saved."""
import os
from pathlib import Path
import numpy as np
from signal_space.models.continuum import metric, lagrangian, quartic_control
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event


def directions(n):
    i=np.arange(n,dtype=float)
    z=1-2*(i+.5)/n
    angle=np.pi*(3-np.sqrt(5))*i
    return np.column_stack([np.sqrt(1-z*z)*np.cos(angle),np.sqrt(1-z*z)*np.sin(angle),z])


def hessian(fields,inv):
    """Polarize evaluations of the action in independent derivative directions."""
    basis=np.eye(24).reshape(24,6,4)
    zero=np.zeros((6,4))
    origin=lagrangian(fields,zero,inv)
    diagonals=np.array([2*(lagrangian(fields,u,inv)-origin) for u in basis])
    result=np.diag(diagonals)
    for j in range(24):
        for k in range(j):
            plus=lagrangian(fields,basis[j]+basis[k],inv)
            mixed=plus-origin-diagonals[j]/2-diagonals[k]/2
            result[k,j]=result[j,k]=mixed
    return result.reshape(6,4,6,4)


def gravity_control():
    """Independent linearized Einstein tensor for a flat harmonic-gauge TT jet."""
    eta=np.diag([1.,-1.,-1.,-1.])
    worst=0.
    for k in directions(20):
        transverse=np.cross(k,[0,0,1.]) if abs(k[2])<.9 else np.cross(k,[0,1.,0])
        transverse/=np.linalg.norm(transverse)
        other=np.cross(k,transverse)
        spatial=np.outer(transverse,transverse)-np.outer(other,other)
        spatial+=.37*(np.outer(transverse,other)+np.outer(other,transverse))
        h=np.zeros((4,4));h[1:,1:]=spatial
        xi=np.r_[1.3,k]
        raised=eta@xi
        xi2=xi@raised
        tr=np.einsum('ab,ab->',eta,h)
        contract=raised@h
        ricci=(np.outer(xi,contract)+np.outer(contract,xi)-xi2*h-np.outer(xi,xi)*tr)/2
        scalar=np.einsum('ab,ab->',eta,ricci)
        einstein=ricci-eta*scalar/2
        bar=h-eta*tr/2
        harmonic=raised@bar
        expected=-xi2*bar/2
        hamiltonian=k@spatial@k-np.trace(spatial)
        momentum=k@spatial-np.trace(spatial)*k
        worst=max(worst,float(np.max(abs(einstein-expected))),float(np.max(abs(harmonic))),abs(hamiltonian),float(np.max(abs(momentum))))
    return worst


def orientation_control(p=.6,kappa=.4):
    """Separate SS OCF 1 + quartic control evaluated from its own action."""
    inv=np.diag([1.,-1.,-1.,-1.]); n=np.array([0.,0.,1.]); base=np.zeros((4,3));base[1,0]=p
    a=np.zeros((4,3));a[0,1]=1
    b=np.zeros((4,3));b[1,1]=1
    def local(dn):
        return np.einsum('ai,ab,bi->',dn,inv,dn)/2+quartic_control(n,dn,inv,kappa)
    l0=local(base)
    kt=local(base+a)+local(base-a)-2*l0
    kx=-(local(base+b)+local(base-b)-2*l0)
    return kt,kx,np.sqrt(kx/kt)


def execute(request_path):
    request=read_json(request_path)
    if request.get('resume_checkpoint'): raise ValueError('atomic Test 5 does not resume')
    attempt=Path(request['attempt_path']);raw=attempt/'raw';raw.mkdir(exist_ok=True)
    events=attempt/'events.jsonl';config=request['config'];p=config['parameters']
    rng=np.random.Generator(np.random.PCG64(request['seed_ledger']['sampling']))
    write_json(raw/'rng-start.json',rng.bit_generator.state)
    append_event(events,'worker-started','run',{'pid':os.getpid(),'algorithm':'local-action-polarization-v1'})
    coframes=[];fields=[];gradients=[];jets=[];hessians=[];roots=[]
    kdirs=directions(p['directions'])
    for index in range(p['samples']):
        if (attempt/'cancel.request').exists():
            append_event(events,'cancellation-observed','run',{'completed':index})
            return 130
        lapse=rng.uniform(.8,1.2); shift=rng.uniform(-.2,.2,size=3)
        spatial=np.eye(3)+rng.uniform(-.15,.15,size=(3,3))
        e=np.zeros((4,4));e[0,0]=lapse;e[1:,0]=spatial@shift;e[1:,1:]=spatial
        g=metric(e);inv=np.linalg.inv(g)
        q=rng.uniform(-1,1,size=4)
        f=np.r_[q,rng.uniform(-1,1,size=2)]
        d=rng.uniform(-.5,.5,size=(6,4));second=rng.uniform(-.5,.5,size=(6,4,4));second=(second+second.transpose(0,2,1))/2
        block=hessian(f,inv)
        a0=inv[0,0];cross=np.einsum('i,di->d',inv[0,1:],kdirs)
        spatial_form=np.einsum('di,ij,dj->d',kdirs,inv[1:,1:],kdirs)
        discriminant=cross*cross-a0*spatial_form
        if min(discriminant)<=0 or np.linalg.cond(e)>3: raise ValueError('sampled coframe outside locked domain')
        one=np.stack([(-cross-np.sqrt(discriminant))/a0,(-cross+np.sqrt(discriminant))/a0],axis=-1)
        coframes.append(e);fields.append(f);gradients.append(d);jets.append(second);hessians.append(block)
        roots.append(np.repeat(one[:,None,:],6,axis=1))
        if index%50==49: append_event(events,'samples-completed','run',{'count':index+1})
    arrays={'coframes':np.array(coframes),'fields':np.array(fields),'gradients':np.array(gradients),
            'second_jets':np.array(jets),'derivative_hessians':np.array(hessians),'roots':np.array(roots),'directions':kdirs}
    np.savez_compressed(raw/'continuum.npz',**arrays)
    kt,kx,speed=orientation_control()
    write_json(raw/'controls.json',{'negative_z':-0.5,'orientation_model_id':'signal-space.ss-ocf-1.orientation-quartic-control.v1',
                                   'orientation_p':.6,'orientation_kappa':.4,'orientation_kt':kt,'orientation_kx':kx,
                                   'orientation_speed':speed,'gravity_gauge':'linearized harmonic/de Donder, flat TT',
                                   'gravity_symbol_constraint_residual':gravity_control()})
    write_json(raw/'rng-end.json',rng.bit_generator.state)
    write_json(raw/'execution.json',{'seed_ledger':request['seed_ledger'],'algorithm':'local-action-polarization-v1',
        'sample_count':p['samples'],'backgrounds':'arbitrary smooth local jets, not on-shell Einstein solutions',
        'connection':'flat A=0 local trivialization','gravity':'linearized flat harmonic TT symbol and constraints only'})
    append_event(events,'worker-completed','run',{'samples':p['samples'],'directions':p['directions']})
    return 0
