"""Finite-gate analytic controls; interval guarantees and floating diagnostics differ."""
from fractions import Fraction as Q
import copy
import json
from pathlib import Path

from signal_space.numerics.dyadic import Interval as I
from signal_space.numerics import validated_linked_memory as v
from signal_space.numerics.record_certificate_check import check


def unpack(p):
    return [I(int(x['lo']),int(x['hi']),x['bits']) for x in p['gate']['values']]


def invariants(x):
    n=sum((a.square() for a in x[:12]),I.exact(0))
    j=[x[12+k]+x[15+k] for k in range(3)]
    for k in (0,4,8):
        ar,ai,br,bi=x[k:k+4]
        j[0]+=ar*br+ai*bi
        j[1]+=ar*bi-ai*br
        j[2]+=(ar.square()+ai.square()-br.square()-bi.square())/2
    constraints=[sum((a.square() for a in x[k:k+3]),I.exact(0))-Q(1,4) for k in (12,15)]
    return [n,*j],constraints


def transform(x,swap=False):
    y=list(x)
    for k in (0,4,8):
        y[k:k+4]=x[k+2:k+4]+x[k:k+2] if swap else [-x[k+1],x[k],-x[k+3],x[k+2]]
    if swap:
        for k in (12,15):y[k:k+3]=[x[k],-x[k+1],-x[k+2]]
    return y


def evaluate_controls(proofs, destination, saved=None):
    """All new science calls are inside the registered, bounded worker."""
    import numpy as np
    from scipy.integrate import solve_ivp
    from signal_space.models import linked_memory as f
    from signal_space.models.operators import SIGMA
    directory=Path(destination);directory.mkdir(parents=True,exist_ok=True)
    results=[];calls=[]
    saved_calls=json.loads((Path(saved)/'local-controls.json').read_text()) if saved else None
    def gate(box,event,duration='1'):
        if saved_calls is None:
            out=v.evaluate(box,event,duration=duration)
        else:
            matches=[x for x in saved_calls if x['domain']==[a.data() for a in box]
                     and x['event']==event and x['duration']==str(Q(duration))]
            if not matches:raise ValueError('missing saved analytic-control request')
            out=matches[0]
            if not v.check_local_output(out,box,event,duration=duration):
                raise ValueError('corrupt saved local-control enclosure')
        if out['status']!='enclosed':raise ValueError(out['reason'])
        calls.append(out);return out
    def add(name,residual,valid=True,kind='outward-enclosure',limit=Q(1,10**12)):
        results.append(dict(id=name,kind=kind,upper=str(residual),limit=str(limit),
                            status='pass' if valid and residual<=limit else 'unresolved'))
    # Dark full word, and separately isolated commuting A and B (not linked).
    dark=[I.exact(0) for _ in range(18)]
    for k in (0,4,8):dark[k]=I.exact(Q(1,2))
    dark[14]=I.exact(Q(1,2));dark[17]=I.exact(Q(-1,2))
    x=list(dark)
    for event in (0,1):x=unpack(gate(x,event))
    add('dark-word',max((a-b).magnitude() for a,b in zip(x,dark)))
    residual=Q(0)
    for event in (0,1):
        x=[I.exact(0) for _ in range(18)];x[14]=I.exact(Q(1,2));x[17]=I.exact(Q(-1,2))
        start=4*event+2*event;x[start]=I.exact(1)
        y=unpack(gate(x,event))
        expected=list(x);expected[start]=I.exact(0);expected[start+4]=I.exact(1)
        residual=max(residual,max((a-b).magnitude() for a,b in zip(y,expected)))
    add('isolated-commuting',residual)
    # Exact quantities are enclosed throughout the complete input/output boxes.
    source=v.source_chart();initial,_=invariants(source)
    worst=Q(0);valid=True
    for event in (0,1):
        before=list(source);h0=v.record_jets(v.variables(before),event)[2][0]
        for duration in ('1/2','1'):
            y=unpack(gate(before,event,duration));ledger,cons=invariants(y)
            for a,b in zip(ledger,initial):
                error=a-b;worst=max(worst,error.magnitude());valid &= error.contains(0)
            for c in cons:worst=max(worst,c.magnitude());valid &= c.contains(0)
            h=v.record_jets(v.variables(y),event)[2][0]-h0
            worst=max(worst,h.magnitude());valid &= h.contains(0)
        source=y
    add('conservation-r3-memory',worst,valid)
    # Exact rational common phase i and U(2) swap, no fitted port phases.
    source=v.source_chart();worst=Q(0)
    for event in (0,1):
        base=unpack(gate(source,event))
        for swap in (False,True):
            actual=unpack(gate(transform(source,swap),event))
            worst=max(worst,max((a-b).magnitude() for a,b in zip(actual,transform(base,swap))))
    add('description-covariance',worst)
    # Independent physical variational ODE diagnostic, never an interval proof.
    available=bool(proofs and proofs[0].get("steps"))
    if available:
        if saved is None:
            state=f.preparations()['active-plus'];basis=f.tangent_basis(state)
            sol=solve_ivp(f.variational_rhs,(0,1),np.concatenate((state[None],basis)).ravel(),
                          args=(0,np.pi/2,16),method='DOP853',rtol=2e-12,atol=2e-14,max_step=1/16)
            if not sol.success:raise ValueError('variational diagnostic failed')
            out=sol.y[:,-1].reshape(17,5,2);cols=[]
            for delta in out[1:]:
                dp=[np.outer(dw,w.conj())+np.outer(w,dw.conj()) for w,dw in zip(out[0,3:],delta[3:])]
                cols.append(np.r_[np.stack((delta[:3].real,delta[:3].imag),axis=-1).ravel(),
                                  [np.trace(p@s).real/2 for p in dp for s in SIGMA]])
            diagnostic={'ode_physical_columns':np.array(cols).T.tolist(),
                        'method':'DOP853','rtol':2e-12,'atol':2e-14,'max_step':1/16}
        else:
            diagnostic=json.loads((Path(saved)/'variational.json').read_text())
            if {k:diagnostic[k] for k in ('method','rtol','atol','max_step')}!={'method':'DOP853','rtol':2e-12,'atol':2e-14,'max_step':1/16}:
                raise ValueError('changed saved variational diagnostic')
        reference=np.array(diagnostic['ode_physical_columns'])
        if reference.shape!=(18,16) or not np.all(np.isfinite(reference)):
            raise ValueError('missing variational physical directions')
        local=proofs[0]['steps'][0]['local']
        jac=np.array([[float(Q(x)) for x in row] for row in local['gate']['derivative_centers']])
        error=float(np.max(abs(jac@np.array(v.source_contract()['J0'])-reference)))
        (directory/'variational.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
        add('variational-diagnostic',Q.from_float(error),kind='floating-independent-formulation',limit=Q(1,10**8))
    else:
        results.append(dict(id='variational-diagnostic',kind='floating-independent-formulation',upper=None,limit='1/100000000',status='unresolved',reason='no qualified source gate in zero-prefix proof'))
    # Identity after anisotropic expansion/contraction, and exact reachable norm.
    from signal_space.numerics.record_certificate_math import identity,mm,opnorm
    a,b=identity(96),identity(96)
    a[0][0]=I.exact(4);a[1][1]=I.exact(Q(1,4));b[0][0]=I.exact(Q(1,4));b[1][1]=I.exact(4)
    add('linear-majorant',abs(opnorm(mm(b,a),96)-1),limit=Q(0))
    good=proofs[0];loaded=json.loads(json.dumps(good));corrupt=copy.deepcopy(loaded)
    if corrupt['steps']:corrupt['steps'][0]['majorants']['Q']='0'
    else:corrupt['source']['J0'][0].pop()
    add('corrupt-certificate',Q(0),not check(corrupt)['verified'],kind='negative-control',limit=Q(0))
    add('serialization',Q(0),check(loaded)['verified'],limit=Q(0))
    # A known exact derivative law / full gate diagnostic, not changed physics.
    (directory/'local-controls.json').write_text(json.dumps(calls,sort_keys=True,indent=2)+'\n')
    return results
