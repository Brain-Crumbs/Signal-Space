"""Saved-proof checker, independent of the trajectory producer.

Never calls produce(), chooses a new reference state, or runs a trajectory
solver. It revalidates local algebra at the SAVED centers using the qualified
#94 gate arithmetic, then reconstructs every transition and proof inequality.
Trusted base: CPython exact integers/Fraction/isqrt, dyadic/local enclosure
kernel and the stated chart/curvature theorem. This is not formal verification
or an independent implementation of the gate-enclosure kernel.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

from signal_space.numerics.dyadic import Interval as I, norm_upper
from signal_space.numerics import validated_linked_memory as local
from signal_space.numerics.record_certificate_math import (
    dump, identity, load, matrix, mm, opnorm, point, residual, up,
)


def _same(actual, expected, obligation):
    if actual != expected:
        raise ValueError(obligation)


def _local(saved, box, event, bits):
    # Validate each independent local obligation, not a newly evolved path.
    expected = local.evaluate(box,event,bits=bits)
    if expected['status'] != 'enclosed':
        raise ValueError('local arithmetic unavailable: '+expected['reason'])
    for key in ('python','platform'):
        expected['proof'].pop(key)
    candidate = dict(saved)
    candidate['proof'] = dict(saved['proof'])
    for key in ('python','platform'):
        candidate['proof'].pop(key)
    _same(candidate,expected,'local value/derivative/tail enclosure')


def _configuration(p):
    c = p['config']
    bits,gates,seed = c['bits'],c['gates'],c['seed']
    if type(bits) is not int or bits not in (64,96,128):
        raise ValueError('precision')
    if type(gates) is not int or not 1 <= gates <= 64:
        raise ValueError('gate ceiling')
    if seed not in ('active-plus','active-minus'):
        raise ValueError('seed')
    expected = dict(seed=seed,bits=bits,gates=gates,epsilon='1/1000000',
                    coupling='exact-pi/2',word=[n % 2 for n in range(gates)],
                    budgets={'preparation':'1/4000','numerical':'1/4000','readout':'1/4000',
                             'omitted_law':'1/4000','total':'1/1000'},
                    model='signal-space.ss-ops-1.v1')
    _same(c,expected,'fixed model, order, preparation and budgets')
    encoded = json.dumps(c,sort_keys=True,separators=(',',':')).encode()
    _same(p['config_sha256'],hashlib.sha256(encoded).hexdigest(),'config hash')
    return c


def _check(p):
    local.require_runtime()
    _same(p['format'],'gross.record-tube-proof.v1','format')
    c = _configuration(p)
    bits,seed = c['bits'],c['seed']
    root = Path(__file__).resolve().parents[3]
    # Explicit source inventory: do not accept a producer-chosen subset.
    paths = ('src/signal_space/numerics/dyadic.py',
             'src/signal_space/numerics/validated_linked_memory.py',
             'src/signal_space/numerics/record_certificate_math.py',
             'src/signal_space/numerics/record_tubes.py',
             'src/signal_space/numerics/record_certificate_check.py',
             'docs/research/gross-local-record-theorem.md',
             'research/papers/gross-operator-program-v0.2.md',
             'requirements-validated-lock.txt')
    _same(p['source_sha256'],{s:hashlib.sha256((root/s).read_bytes()).hexdigest() for s in paths},
          'source versions; check under the recorded source revision')
    source = local.source_contract(bits)
    _same(p['source'],source,'exact chart, all 16 columns, source constants')
    x0 = [load(x,bits) for x in source['seeds'][seed]['values']]
    center = [load(x,bits) for x in p['initial_center']]
    if len(center) != 18 or any(x.lo != x.hi for x in center):
        raise ValueError('initial reference dimension / exact storage')
    alpha0 = residual(x0,center,bits)
    alpha,beta,q = alpha0,Q(0),Q(source['chart_remainder_upper'])
    q0 = q
    ec = load(source['chart_radius'],bits).upper()
    tangent = [[I.exact(x,bits) for x in row] for row in source['J0']]
    products = [identity(bits)]
    aterms,bterms,qterms = [],[],[]
    horizons = [0,0,0]
    obstruction_terms = []
    if len(p['steps']) > c['gates']:
        raise ValueError('extra endpoints')
    for n,step in enumerate(p['steps']):
        event = c['word'][n]
        _same((step['index'],step['event']),(n+1,event),'ordered prefix / cycle reset')
        V = opnorm(tangent,bits)
        W = up(V+beta,bits)
        R = up(ec*W+q,bits)
        input_required = up(alpha+R,bits)
        domain = local.ball_box(center,input_required,bits)
        if any(x.magnitude() > 4 for x in domain):
            raise ValueError('unqualified bootstrap domain')
        _same(step['input_domain'],[x.data() for x in domain],'complete input tube')
        Hbounds = local.curvature(domain,event,Q(1))
        _same(step['bounds'],Hbounds,'full-domain gate Hessian')
        _local(step['local'],center,event,bits)
        out = [load(x,bits) for x in step['local']['gate']['values']]
        new = [load(x,bits) for x in step['center']]
        if len(new) != 18 or any(x.lo != x.hi for x in new):
            raise ValueError('stored reference is not a point')
        derivatives = matrix(step['local']['gate']['derivatives'],bits,18,18)
        a = matrix(step['A'],bits,18,18)
        _same(a,[[point(x,bits) for x in row] for row in derivatives],'stored derivative center')
        d = residual(out,new,bits)
        eta = residual([x for row in derivatives for x in row],[x for row in a for x in row],bits)
        H = Q(Hbounds['gate_hessian_upper'])
        e = up(eta+H*alpha,bits)
        # Separate reconstruction of the variation-of-constants sums. All old
        # forcing is retained; no saved Q/alpha/beta is used as a new initial value.
        aterms.append(up(d+eta*alpha+H*alpha**2/2,bits))
        bterms.append(up(e*W,bits))
        qterms.append(up(e*q+H*R**2/2,bits))
        products = [mm(a,p) for p in products]+[identity(bits)]
        norms = [opnorm(p,bits) for p in products]
        _same(step['transition_norms'],list(map(str,norms)),'intact transition products')
        tangent = mm(a,tangent)
        _same(step['tangent'],dump(tangent),'full 18x16 tangent/product rounding')
        raw_alpha = norms[0]*alpha0+sum((norms[k+1]*f for k,f in enumerate(aterms)),Q(0))
        raw_beta = sum((norms[k+1]*f for k,f in enumerate(bterms)),Q(0))
        raw_q = norms[0]*q0+sum((norms[k+1]*f for k,f in enumerate(qterms)),Q(0))
        alpha,beta,q = (up(v,bits) for v in (raw_alpha,raw_beta,raw_q))
        rn = up(ec*up(opnorm(tangent,bits)+beta,bits)+q,bits)
        _same(step['majorants'],{k:str(v) for k,v in dict(alpha=alpha,beta=beta,Q=q,R=rn,
              input_R=R,H=H,d=d,eta=eta,e=e,alpha_forcing=aterms[-1],
              beta_forcing=bterms[-1],Q_forcing=qterms[-1]).items()},'nonresetting forcing/majorants')
        rd = local.ball_box(new,up(alpha+rn,bits),bits)
        if any(x.magnitude() > 4 for x in rd):
            raise ValueError('unqualified readout domain')
        _same(step['endpoint_domain'],[x.data() for x in rd],'complete record tube')
        rb = local.curvature(rd,event,Q(0))
        _same(step['record_bounds'],rb,'record curvature / domain')
        records = local.pack(local.record_jets(local.variables(new),event),bits)
        _same(step['records'],records,'gradient/readout enclosure')
        # Reconstruct theorem (B) independently: do not call the producer's
        # record_terms formula. Only elementary interval/norm operations are shared.
        terms = []
        margins = dict(alpha=str(alpha-raw_alpha),beta=str(beta-raw_beta),Q=str(q-raw_q),records=[])
        def clearance(box, mid, required):
            return min(min(y.midpoint()-Q(x.lo,1 << bits),x.upper()-y.midpoint())
                       for x,y in zip(box,mid))-required
        margins['input_domain'] = str(clearance(domain,center,input_required))
        margins['endpoint_domain'] = str(clearance(rd,new,up(alpha+rn,bits)))
        for l in range(3):
            gradient = [load(x,bits) for x in records['derivatives'][l]]
            h = [point(x,bits) for x in gradient]
            gamma = norm_upper([x-y for x,y in zip(gradient,h)],bits)
            G = norm_upper(h,bits)
            transported = mm([h],tangent)[0]
            K = norm_upper(transported,bits)
            B = Q(rb['record_hessian_upper'][l])
            cerror = up(gamma+B*alpha,bits)
            wbound = up(opnorm(tangent,bits)+beta,bits)
            raw_linear = ec*(K+G*beta+cerror*wbound)
            raw_remainder = (G+cerror)*q+B*rn**2/2
            linear,remainder = up(raw_linear,bits),up(raw_remainder,bits)
            preparation = up(linear+remainder,bits)
            raw_numerical = (G+gamma)*alpha+B*alpha**2/2
            numerical = up(raw_numerical,bits)
            value = load(records['values'][l],bits)
            nu = (value-point(value,bits)).magnitude()
            total = up(preparation+numerical+nu,bits)
            row = {k:str(v) for k,v in dict(G=G,K=K,gamma=gamma,nu=nu,B=B,
                   readout_center=point(value,bits).midpoint(),linear=linear,
                   remainder=remainder,preparation=preparation,numerical=numerical,
                   readout=nu,omitted_law=Q(0),total=total).items()}
            terms.append(row)
            margins['records'].append(dict(preparation_inequality=str(preparation-raw_linear-raw_remainder),
                numerical_inequality=str(numerical-raw_numerical),
                total_inequality=str(total-preparation-numerical-nu),
                budgets={k:str(Q(c['budgets'][k])-Q(row[k])) for k in c['budgets']}))
        _same(step['record_terms'],terms,'separate allocations / readout products')
        _same(step['margins'],margins,'proof inequality/domain/budget margins')
        for k in ('alpha','beta','Q','input_domain','endpoint_domain'):
            if Q(margins[k]) < 0:
                raise ValueError('negative proof/domain margin')
        for row in margins['records']:
            if any(Q(row[k]) < 0 for k in ('preparation_inequality','numerical_inequality','total_inequality')):
                raise ValueError('negative readout proof margin')
        for l,row in enumerate(terms):
            within = all(Q(row[k]) <= Q(c['budgets'][k]) for k in c['budgets'])
            if horizons[l] == n and within:
                horizons[l] += 1
            obstruction_terms.append(dict(endpoint=n+1,event=event,record=l+1,
                                           **{k:float(Q(row[k])) for k in
                                              ('linear','remainder','preparation','numerical','readout','total')}))
        center = new
    if p['termination'] == 'completed':
        _same(len(p['steps']),c['gates'],'missing completed endpoint')
    elif p['termination'] != 'unresolved' or not isinstance(p.get('obstruction'),str):
        raise ValueError('termination evidence')
    prefix = min(horizons)
    return dict(verified=True,seed=seed,verified_endpoints=len(p['steps']),
                record_endpoint_horizons=horizons,record_cycle_horizons=[h//2 for h in horizons],
                endpoint_horizon=prefix,cycle_horizon=prefix//2,
                classification='certified-prefix' if prefix else 'unresolved',
                target_met=prefix == c['gates'],terms=obstruction_terms,
                limitation='gate endpoints only; no 32-cycle campaign or physical detector claim')


def check(packet):
    """Fail closed: malformed/undersized evidence never returns a horizon."""
    try:
        return _check(packet)
    except (KeyError,TypeError,ValueError,ArithmeticError,MemoryError,RecursionError) as exc:
        return dict(verified=False,classification='unresolved',endpoint_horizon=0,
                    cycle_horizon=0,reason=str(exc))


def check_file(path):
    path = Path(path)
    if path.stat().st_size > 128*1024*1024:
        return dict(verified=False,classification='unresolved',reason='proof file size ceiling')
    def pairs(items):
        result = {}
        for k,v in items:
            if k in result:
                raise ValueError('duplicate JSON key')
            result[k] = v
        return result
    try:
        return check(json.loads(path.read_text(),object_pairs_hook=pairs))
    except (ValueError,RecursionError) as exc:
        return dict(verified=False,classification='unresolved',reason=str(exc))


def separation_bounds(differences):
    """Interval lower bounds; only checked physical witnesses may use a fail verdict."""
    lower = [Q(0) if x.lo <= 0 <= x.hi else
             min(abs(Q(x.lo,1 << x.bits)),abs(x.upper())) for x in differences]
    return lower, any(x > Q(1,4000) for x in lower)


def check_witness(witness):
    """A failure needs a physical in-ball source and enclosed record separation.

    Saved gate obligations enclose both exact trajectories, without numerical
    reference centers. Excessive certificate upper bounds are never inputs here.
    """
    try:
        _same(witness['format'],'gross.record-witness.v1','witness format')
        seed,bits = witness['seed'],witness['bits']
        if seed not in ('active-plus','active-minus') or type(bits) is not int or bits not in (64,96,128):
            raise ValueError('witness seed/precision')
        u = witness['u']
        if len(u) != 16 or any(type(x) is not str or len(x)>256 for x in u):
            raise ValueError('full bounded source chart required')
        # Also applies the exact-input syntax/size restrictions.
        for x in u:
            I.exact(x,bits)
        u = list(map(Q,u))
        t2 = [sum((v*v for v in u[a:a+2]),Q(0)) for a in (12,14)]
        chord2 = sum((v*v for v in u[:12]),Q(0))+sum((t/(1+t) for t in t2),Q(0))
        if chord2 > Q(1,10**12):
            raise ValueError('counterexample source outside physical radius')
        word = witness['steps']
        if not 1 <= len(word) <= 64:
            raise ValueError('witness gate ceiling')
        boxes = [local.source_chart(seed,bits=bits),local.source_chart(seed,u,bits=bits)]
        for n,step in enumerate(word):
            _same(step['event'],n % 2,'witness order')
            for k,key in enumerate(('nominal','perturbed')):
                _local(step[key],boxes[k],n % 2,bits)
                boxes[k] = [load(x,bits) for x in step[key]['gate']['values']]
        rs = [local.record_jets(local.variables(b), (len(word)-1) % 2) for b in boxes]
        differences = [b[0]-a[0] for a,b in zip(*rs)]
        lower,failed = separation_bounds(differences)
        return dict(verified=True,classification='fail' if failed else 'unresolved',
                    failed_allocation='preparation' if failed else None,
                    endpoint=len(word),physical_chord_squared=str(chord2),
                    record_difference_lower=list(map(str,lower)),
                    record_differences=[x.data() for x in differences])
    except (KeyError,TypeError,ValueError,ArithmeticError,MemoryError,RecursionError) as exc:
        return dict(verified=False,classification='unresolved',reason=str(exc))
