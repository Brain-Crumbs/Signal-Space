"""Nonresetting full-direction C1 proof producer; not an experiment runner.

A bounded engineering caller may demonstrate one AB cycle. Campaign admission,
registration and scientific locks belong to #96, confirmation to #97.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
from time import monotonic

from signal_space.numerics.dyadic import Interval as I
from signal_space.numerics import validated_linked_memory as local
from signal_space.numerics.record_certificate_math import (
    dump, forced, identity, load, matrix, mm, opnorm, point, record_terms,
    residual, transport, up,
)

BUDGETS = {'preparation':'1/4000', 'numerical':'1/4000', 'readout':'1/4000',
           'omitted_law':'1/4000', 'total':'1/1000'}
SOURCES = ('src/signal_space/numerics/dyadic.py',
           'src/signal_space/numerics/validated_linked_memory.py',
           'src/signal_space/numerics/record_certificate_math.py',
           'src/signal_space/numerics/record_tubes.py',
           'src/signal_space/numerics/record_certificate_check.py',
           'docs/research/gross-local-record-theorem.md',
           'research/papers/gross-operator-program-v0.2.md',
           'requirements-validated-lock.txt')


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def sources():
    root = Path(__file__).resolve().parents[3]
    return {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCES}


def configuration(seed, bits, gates):
    if seed not in ('active-plus', 'active-minus') or bits not in (64,96,128):
        raise ValueError('unsupported seed/precision')
    if type(gates) is not int or not 1 <= gates <= 64:
        raise ValueError('ordered gate ceiling is 64')
    return dict(seed=seed, bits=bits, gates=gates, epsilon='1/1000000',
                coupling='exact-pi/2', word=[n % 2 for n in range(gates)],
                budgets=dict(BUDGETS), model='signal-space.ss-ops-1.v1')


def produce(seed='active-plus', *, bits=96, gates=2, wall_seconds=30):
    """Return complete checked-prefix evidence, preserving any later obstruction.

    Explicit sequential bootstrap: the previous proved alpha/beta/Q determine
    the full input ball before its H is evaluated. No convergence-tolerance
    fixed-point assumption and no resets are used.
    """
    config = configuration(seed,bits,gates)
    if type(wall_seconds) not in (int,float) or not 0 < wall_seconds <= 60:
        raise ValueError('bounded producer wall ceiling must be <=60 seconds')
    local.require_runtime()
    deadline = monotonic()+wall_seconds
    source = local.source_contract(bits)
    initial_values = [load(x,bits) for x in source['seeds'][seed]['values']]
    center = [point(x,bits) for x in initial_values]
    alpha0 = residual(initial_values,center,bits)
    ec = load(source['chart_radius'],bits).upper()
    q0 = Q(source['chart_remainder_upper'])
    tangent = [[I.exact(x,bits) for x in row] for row in source['J0']]
    alpha,beta,q = alpha0,Q(0),q0
    factors = [identity(bits)]
    af,bf,qf = [],[],[]
    packet = dict(format='gross.record-tube-proof.v1', config=config,
                  config_sha256=digest(config), source_sha256=sources(), source=source,
                  initial_center=[x.data() for x in center], steps=[])
    try:
        for n,event in enumerate(config['word']):
            if monotonic() >= deadline:
                raise TimeoutError('producer aggregate wall ceiling')
            V = opnorm(tangent,bits)
            W = up(V+beta,bits)
            R = up(ec*W+q,bits)
            input_required = up(alpha+R,bits)
            domain = local.ball_box(center,input_required,bits)
            if any(x.magnitude() > 4 for x in domain):
                raise ArithmeticError('full bootstrap domain exceeds qualified backend')
            bounds = local.curvature(domain,event,Q(1))
            H = Q(bounds['gate_hessian_upper'])
            result = local.evaluate(center,event,bits=bits,
                                    wall_seconds=min(30,deadline-monotonic()))
            if result['status'] != 'enclosed':
                raise ArithmeticError(result['reason'])
            out = [load(x,bits) for x in result['gate']['values']]
            next_center = [point(x,bits) for x in out]
            D = matrix(result['gate']['derivatives'],bits,18,18)
            A = [[point(x,bits) for x in row] for row in D]
            eta = residual([x for row in D for x in row],[x for row in A for x in row],bits)
            d = residual(out,next_center,bits)
            e = up(eta+H*alpha,bits)
            # Each local forcing is retained and transported intact to every
            # later endpoint. Interval products include their own rounding.
            af.append(up(d+eta*alpha+H*alpha**2/2,bits))
            bf.append(up(e*W,bits))
            qf.append(up(e*q+H*R**2/2,bits))
            factors,norms = transport(factors,A,bits)
            tangent = mm(A,tangent)
            raw_alpha = norms[0]*alpha0+sum((n*f for n,f in zip(norms[1:],af)),Q(0))
            raw_beta = sum((n*f for n,f in zip(norms[1:],bf)),Q(0))
            raw_q = norms[0]*q0+sum((n*f for n,f in zip(norms[1:],qf)),Q(0))
            alpha = forced(norms,alpha0,af,bits)
            beta = forced(norms,Q(0),bf,bits)
            q = forced(norms,q0,qf,bits)
            Rnext = up(ec*up(opnorm(tangent,bits)+beta,bits)+q,bits)
            endpoint_domain = local.ball_box(next_center,up(alpha+Rnext,bits),bits)
            if any(x.magnitude() > 4 for x in endpoint_domain):
                raise ArithmeticError('endpoint bootstrap domain exceeds qualified backend')
            rbounds = local.curvature(endpoint_domain,event,Q(0))
            records = local.pack(local.record_jets(local.variables(next_center),event),bits)
            rows = record_terms(records,tangent,beta,alpha,q,ec,Rnext,rbounds,bits)
            def domain_margin(box, mid, required):
                return min(min(m.midpoint()-Q(x.lo,1 << bits),x.upper()-m.midpoint())
                           for x,m in zip(box,mid))-required
            margins = dict(alpha=str(alpha-raw_alpha),beta=str(beta-raw_beta),Q=str(q-raw_q))
            # input alpha/R are the previous proven values, saved before update.
            margins['input_domain'] = str(domain_margin(domain,center,input_required))
            margins['endpoint_domain'] = str(domain_margin(endpoint_domain,next_center,up(alpha+Rnext,bits)))
            margins['records'] = []
            for row in rows:
                c = up(Q(row['gamma'])+Q(row['B'])*alpha,bits)
                wn = up(opnorm(tangent,bits)+beta,bits)
                raw_p = ec*(Q(row['K'])+Q(row['G'])*beta+c*wn)+(Q(row['G'])+c)*q+Q(row['B'])*Rnext**2/2
                raw_n = (Q(row['G'])+Q(row['gamma']))*alpha+Q(row['B'])*alpha**2/2
                margins['records'].append(dict(
                    preparation_inequality=str(Q(row['preparation'])-raw_p),
                    numerical_inequality=str(Q(row['numerical'])-raw_n),
                    total_inequality=str(Q(row['total'])-Q(row['preparation'])-Q(row['numerical'])-Q(row['readout'])),
                    budgets={k:str(Q(BUDGETS[k])-Q(row[k])) for k in BUDGETS}))
            packet['steps'].append(dict(index=n+1,event=event,local=result,
                center=[x.data() for x in next_center], A=dump(A), tangent=dump(tangent),
                input_domain=[x.data() for x in domain], endpoint_domain=[x.data() for x in endpoint_domain],
                bounds=bounds,record_bounds=rbounds,records=records,record_terms=rows,margins=margins,
                transition_norms=list(map(str,norms)),
                majorants={k:str(v) for k,v in dict(alpha=alpha,beta=beta,Q=q,R=Rnext,
                           input_R=R,H=H,d=d,eta=eta,e=e,
                           alpha_forcing=af[-1],beta_forcing=bf[-1],Q_forcing=qf[-1]).items()}))
            center = next_center
        packet['termination'] = 'completed'
    except (ArithmeticError,ValueError,TimeoutError,MemoryError) as exc:
        packet['termination'] = 'unresolved'
        packet['obstruction'] = str(exc)
    return packet
