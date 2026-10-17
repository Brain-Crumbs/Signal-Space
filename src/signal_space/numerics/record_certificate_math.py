"""Exact/outward linear algebra shared by certificate producer and checker.

The local gate enclosure and integer dyadic kernel are the trusted arithmetic
base. No floating operation contributes to a proof bound.
"""
from fractions import Fraction as Q

from signal_space.numerics.dyadic import Interval as I, norm_upper
from signal_space.numerics.validated_linked_memory import mm


def up(x, bits):
    if x < 0:
        raise ValueError('negative majorant')
    return I.exact(x, bits).upper()


def point(x, bits):
    """Choose a representable center; never silently normalize a memory."""
    return I((x.lo+x.hi)//2, (x.lo+x.hi)//2, bits)


def load(x, bits):
    if set(x) != {'lo', 'hi', 'bits'} or x['bits'] != bits:
        raise ValueError('interval serialization/precision')
    for k in ('lo', 'hi'):
        if type(x[k]) is not str or len(x[k]) > 200 or str(int(x[k])) != x[k]:
            raise ValueError('noncanonical interval endpoint')
    return I(int(x['lo']), int(x['hi']), bits)


def matrix(data, bits, rows, cols):
    if len(data) != rows or any(len(row) != cols for row in data):
        raise ValueError('matrix dimensions / dropped directions')
    return [[load(x, bits) for x in row] for row in data]


def dump(a):
    return [[x.data() for x in row] for row in a]


def identity(bits):
    return [[I.exact(int(i == j), bits) for j in range(18)] for i in range(18)]


def opnorm(a, bits):
    """min(Frobenius,sqrt(||A||1 ||A||inf)) encloses the spectral norm."""
    one = max(sum(x.magnitude() for x in col) for col in zip(*a))
    infinity = max(sum(x.magnitude() for x in row) for row in a)
    return min(norm_upper([x for row in a for x in row], bits),
               I.exact(one*infinity, bits).sqrt().upper())


def residual(values, centers, bits):
    return norm_upper([x-y for x, y in zip(values, centers)], bits)


def transport(factors, a, bits):
    # Phi(n+1,k)=A_n Phi(n,k), Phi(n+1,n+1)=I. No inverses.
    products = [mm(a, p) for p in factors]+[identity(bits)]
    return products, [opnorm(p, bits) for p in products]


def forced(norms, initial, forcing, bits):
    if len(norms) != len(forcing)+1:
        raise ValueError('missing forcing or reset prefix')
    return up(norms[0]*initial+sum((n*f for n, f in zip(norms[1:], forcing)), Q(0)), bits)


def record_terms(records, tangent, beta, alpha, q, ec, radius, bounds, bits):
    """Theorem (B), with all 16 entries of every record row transported."""
    rows = []
    for l in range(3):
        g = [load(x, bits) for x in records['derivatives'][l]]
        if len(g) != 18:
            raise ValueError('record gradient dimensions')
        h = [point(x, bits) for x in g]
        gamma = residual(g, h, bits)
        value = load(records['values'][l], bits)
        readout_center = point(value,bits).midpoint()
        nu = (value-readout_center).magnitude()
        G = norm_upper(h, bits)
        K = norm_upper(mm([h], tangent)[0], bits)
        W = up(opnorm(tangent, bits)+beta, bits)
        B = Q(bounds['record_hessian_upper'][l])
        c = up(gamma+B*alpha, bits)
        linear = up(ec*(K+G*beta+c*W), bits)
        remainder = up((G+c)*q+B*radius**2/2, bits)
        preparation = up(linear+remainder, bits)
        numerical = up((G+gamma)*alpha+B*alpha**2/2, bits)
        total = up(preparation+numerical+nu, bits)
        rows.append({k: str(v) for k, v in dict(G=G,K=K,gamma=gamma,nu=nu,B=B,
                    readout_center=readout_center,linear=linear,remainder=remainder,preparation=preparation,
                    numerical=numerical,readout=nu,omitted_law=Q(0),total=total).items()})
    return rows
