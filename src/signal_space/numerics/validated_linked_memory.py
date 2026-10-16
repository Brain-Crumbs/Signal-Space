"""Local C1 enclosures, not a trajectory certificate or registered experiment.

See docs/research/gross-validated-local-backend.md for proofs and API contract.
Coordinates: interleaved Re/Im waves (12), Pauli xA (3), xB (3).
"""
from dataclasses import dataclass
from fractions import Fraction
from math import factorial
import platform
import sys
from time import monotonic

from signal_space.numerics.dyadic import Interval as I, norm_upper, pi_interval

BACKEND = "dyadic-taylor-v1"
PYTHON = ((3, 12, 14), (3, 12, 10))
TERMS = 32
SQUARINGS = 8


@dataclass(frozen=True)
class Complex:
    re: I
    im: I

    def coerce(self, x):
        return x if isinstance(x, Complex) else Complex(self.re.coerce(x), self.re.coerce(0))

    def __add__(self, x):
        x = self.coerce(x)
        return Complex(self.re+x.re, self.im+x.im)
    __radd__ = __add__

    def __neg__(self):
        return Complex(-self.re, -self.im)

    def __sub__(self, x):
        return self + -self.coerce(x)

    def __rsub__(self, x):
        return self.coerce(x) - self

    def __mul__(self, x):
        x = self.coerce(x)
        return Complex(self.re*x.re-self.im*x.im, self.re*x.im+self.im*x.re)
    __rmul__ = __mul__

    def __truediv__(self, x):
        return Complex(self.re/x, self.im/x)

    def conj(self):
        return Complex(self.re, -self.im)

    def magnitude(self):
        # Component one-norm dominates complex modulus.
        return self.re.magnitude()+self.im.magnitude()

    def widen(self, r):
        return Complex(self.re.widen(r), self.im.widen(r))


@dataclass(frozen=True)
class Jet:
    value: Complex
    derivative: tuple

    def coerce(self, x):
        if isinstance(x, Jet):
            return x
        return Jet(self.value.coerce(x), tuple(self.value.coerce(0) for _ in self.derivative))

    def __add__(self, x):
        x = self.coerce(x)
        return Jet(self.value+x.value, tuple(a+b for a,b in zip(self.derivative,x.derivative)))
    __radd__ = __add__

    def __neg__(self):
        return Jet(-self.value, tuple(-a for a in self.derivative))

    def __sub__(self, x):
        return self + -self.coerce(x)

    def __rsub__(self, x):
        return self.coerce(x) - self

    def __mul__(self, x):
        x = self.coerce(x)
        return Jet(self.value*x.value, tuple(a*x.value+self.value*b
                    for a,b in zip(self.derivative,x.derivative)))
    __rmul__ = __mul__

    def __truediv__(self, x):
        return Jet(self.value/x, tuple(a/x for a in self.derivative))

    def conj(self):
        return Jet(self.value.conj(), tuple(a.conj() for a in self.derivative))


def mm(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))), 0)
             for j in range(len(b[0]))] for i in range(len(a))]


def adjoint(a):
    return [[a[j][i].conj() for j in range(len(a))] for i in range(len(a[0]))]


def matrix_norm(a):
    return max(sum(x.magnitude() for x in row) for row in a)


def exponential(a, deadline, proofs):
    """Differentiated Taylor polynomial + explicit value/Frechet tails."""
    n = len(a)
    if n not in (1, 2) or any(len(row) != n for row in a):
        raise ValueError("only 1x1 and 2x2 exponentials supported")
    b = [[x/(1 << SQUARINGS) for x in row] for row in a]
    radius = matrix_norm([[x.value for x in row] for row in b])
    if radius > Fraction(1, 4):
        raise ArithmeticError("exponential domain exceeds fixed work envelope")
    zero = a[0][0].coerce(0)
    ident = [[zero.coerce(int(i == j)) for j in range(n)] for i in range(n)]
    total, term = ident, ident
    for k in range(1, TERMS+1):
        if monotonic() > deadline:
            raise TimeoutError("local arithmetic wall ceiling")
        term = [[x/k for x in row] for row in mm(term, b)]
        total = [[total[i][j]+term[i][j] for j in range(n)] for i in range(n)]
    tail = radius**(TERMS+1)/factorial(TERMS+1)/(1-radius/Fraction(TERMS+2))
    derivative_tail_factor = radius**TERMS/factorial(TERMS)/(1-radius/Fraction(TERMS+1))
    tails = [derivative_tail_factor*matrix_norm([[x.derivative[k] for x in row] for row in b])
             for k in range(len(zero.derivative))]
    proofs.append({"scaled_norm": str(radius), "terms": TERMS, "squarings": SQUARINGS,
                   "value_tail": str(tail), "derivative_tails": list(map(str, tails))})
    total = [[Jet(x.value.widen(tail), tuple(d.widen(t) for d,t in zip(x.derivative,tails)))
              for x in row] for row in total]
    for _ in range(SQUARINGS):
        if monotonic() > deadline:
            raise TimeoutError("local arithmetic wall ceiling")
        total = mm(total, total)
    return total


def variables(box, count=18):
    bits = box[0].bits
    zero = Complex(I.exact(0,bits),I.exact(0,bits))
    return [Jet(Complex(x,zero.im), tuple(zero.coerce(int(i == j)) for j in range(count)))
            for i,x in enumerate(box)]


def coordinates(x):
    imaginary = Complex(x[0].value.re.coerce(0), x[0].value.re.coerce(1))
    waves = [[x[4*i]+x[4*i+1]*imaginary, x[4*i+2]+x[4*i+3]*imaginary] for i in range(3)]
    memories = []
    for k in (12,15):
        memories.append([[x[k+2]+Fraction(1,2), x[k]-x[k+1]*imaginary],
                         [x[k]+x[k+1]*imaginary, Fraction(1,2)-x[k+2]]])
    return waves, memories, imaginary


def flatten(waves, memories):
    result = []
    for row in waves:
        for z in row:
            result.extend([(z.value.re,tuple(d.re for d in z.derivative)),
                           (z.value.im,tuple(d.im for d in z.derivative))])
    for p in memories:
        for z, part in ((p[0][1],"re"),(-p[0][1],"im"),((p[0][0]-p[1][1])/2,"re")):
            result.append((getattr(z.value,part),tuple(getattr(d,part) for d in z.derivative)))
    return result


def gate_jets(x, event, duration, deadline, proofs):
    waves, ps, imaginary = coordinates(x)
    i,j,a = ((0,1,0),(1,2,1))[event]
    d = [[waves[i][k]-waves[j][k]] for k in range(2)]
    b = [waves[i][k]+waves[j][k] for k in range(2)]
    dd = mm(d,adjoint(d))
    q = mm(adjoint(d),d)[0][0]
    t = pi_interval(x[0].value.re.bits)*duration/2
    # Multiplication must dispatch through Jet so every ambient column survives.
    generator = [[(dd[k][l]+2*ps[a][k][l])*(-imaginary)*t for l in range(2)] for k in range(2)]
    u = exponential(generator,deadline,proofs)
    phase = exponential([[q*imaginary*t]],deadline,proofs)[0][0]
    evolved = mm(u,d)
    for k in range(2):
        waves[i][k] = (b[k]+phase*evolved[k][0])/2
        waves[j][k] = (b[k]-phase*evolved[k][0])/2
    ps[a] = mm(mm(u,ps[a]),adjoint(u))
    return flatten(waves,ps)


def record_jets(x,event):
    waves, ps, _ = coordinates(x)
    i,j,a = ((0,1,0),(1,2,1))[event]
    result = []
    for row in (waves[i],waves[j],[waves[i][k]-waves[j][k] for k in range(2)]):
        v = [[z] for z in row]
        r = mm(mm(adjoint(v),ps[a]),v)[0][0]
        result.append((r.value.re,tuple(d.re for d in r.derivative)))
    return result


def curvature(box,event,duration):
    """Global-on-box Hermitian Frechet bounds in the #93 Euclidean norm."""
    bits = box[0].bits
    def c(x): return I.exact(x,bits)
    n = sum((x.square() for x in box[:12]),c(0))
    a = 12+3*event
    p = c(Fraction(1,2))+sum((x.square() for x in box[a:a+3]),c(0)).sqrt()
    d, root2 = (2*n).sqrt(), c(2).sqrt()
    t = pi_interval(bits)*duration/2
    l = 2*d*root2+2
    u1 = t*l
    u2 = 4*t+u1.square()
    f1 = 2*t*d*root2
    f2 = 4*t+f1.square()
    hd = (f2+2*f1*u1+u2)*d+2*(f1+u1)*root2
    hp = 2*p*(u2+u1.square())+4*u1
    h = (hd.square()/2+hp.square()).sqrt().upper()
    rb = (p+(p.square()+4*n).sqrt()).upper()
    return {"wave_weight_upper":str(n.upper()), "memory_op_upper":str(p.upper()),
            "gate_hessian_upper":str(h), "record_hessian_upper":[str(rb),str(rb),str(2*rb)],
            "memory_trace":"1", "memory_spectrum_abs_upper":str(p.upper()),
            "physicality_assumed":False}


def pack(rows,bits):
    values = [x for x,_ in rows]
    derivatives = [list(ds) for _,ds in rows]
    return {"values":[x.data() for x in values],
            "centers":list(map(lambda x:str(x.midpoint()),values)),
            "radii":list(map(lambda x:str(x.radius()),values)),
            "value_error_norm_upper":str(norm_upper([x.radius() for x in values],bits)),
            "derivatives":[[x.data() for x in row] for row in derivatives],
            "derivative_centers":[[str(x.midpoint()) for x in row] for row in derivatives],
            "derivative_operator_error_upper":str(norm_upper([x.radius() for row in derivatives for x in row],bits))}


def evaluate(box, event=0, *, bits=96, duration="1", coupling="exact-pi/2", wall_seconds=30):
    """Enclose F, DF and records/gradients at every point of an 18D box.

    A ball is accepted via ball_box(center,radius). Records are evaluated on
    the INPUT box; call separately at an endpoint. Failure has no payload.
    All successful numeric payloads are exact rational strings/dyadic integers.
    """
    try:
        require_runtime()
        if type(event) is not int or event not in (0,1) or bits not in (64,96,128):
            raise ValueError("unsupported event or precision")
        if coupling != "exact-pi/2":
            raise ValueError("only mathematical pi/2 coupling supported")
        if type(wall_seconds) not in (int,float) or not 0 < wall_seconds <= 30:
            raise ValueError("invalid local wall ceiling")
        I.exact(duration,bits)  # reject undeclared float conversion and oversized input
        s = Fraction(duration)
        if not 0 <= s <= 1:
            raise ValueError("duration must be in [0,1]")
        if len(box) != 18:
            raise ValueError("expected 18 ambient coordinates")
        box = [I.exact(x,bits) for x in box]
        if any(x.magnitude() > 4 for x in box):
            raise ValueError("box exceeds bounded backend domain")
        deadline = monotonic()+wall_seconds
        x, proofs = variables(box), []
        gate = gate_jets(x,event,s,deadline,proofs)
        records = record_jets(x,event)
        bounds = curvature(box,event,s)
        result = {"status":"enclosed", "backend":BACKEND, "bits":bits,
                "coupling":coupling, "duration":str(s), "event":event,
                "domain":[x.data() for x in box], "gate":pack(gate,bits),
                "records":pack(records,bits), "bounds":bounds,
                "proof":{"exponentials":proofs,"arithmetic":"integer-floor-ceiling",
                         "python":platform.python_version(),"implementation":platform.python_implementation(),
                         "platform":platform.platform(),"norm":"18D Euclidean / Pauli", "law":"SS OPS 1 lambda=0"}}
        if monotonic() > deadline:
            raise TimeoutError("local arithmetic wall ceiling")
        return result
    except (ValueError, TypeError, ArithmeticError, MemoryError, TimeoutError) as exc:
        return {"status":"unresolved", "reason":str(exc), "backend":BACKEND}


def ball_box(center, radius, bits=96):
    """A full Euclidean ball lies in this axis-aligned box; no sampling."""
    r = I.exact(radius,bits)
    if r.lo < 0 or len(center) != 18:
        raise ValueError("invalid ambient ball")
    return [I.exact(x,bits).widen(r) for x in center]


def require_runtime():
    if platform.python_implementation() != "CPython" or sys.version_info[:3] not in PYTHON:
        raise ValueError("unsupported arithmetic runtime (requires CPython 3.12.14 or 3.12.10)")


def source_chart(seed="active-plus", u=None, *, bits=96):
    """Exact active seeds and their full 16-coordinate chart, without spinor sqrt.

    P=(w+eta)(w+eta)^dagger/(1+|eta|^2) evaluates the identical normalized
    spinor chart. No normalization is applied to the evolved state.
    """
    require_runtime()
    if seed not in ("active-plus","active-minus"):
        raise ValueError("unsupported source seed")
    if u is None: u = [0]*16
    if len(u) != 16: raise ValueError("expected 16 chart coordinates")
    u = [I.exact(v,bits) for v in u]
    if any(v.magnitude() > Fraction(1,4) for v in u):
        raise ValueError("chart exceeds bounded domain")
    c = lambda v: I.exact(v,bits)
    wave = [c(0) for _ in range(12)]
    wave[0] = wave[6] = 1/c(3).sqrt()
    wave[8] = 1/c(6).sqrt()
    wave[11] = (1 if seed == "active-plus" else -1)/c(6).sqrt()
    out = [a+b for a,b in zip(wave,u[:12])]
    for a,sign in ((12,1),(14,-1)):
        re,im = u[a:a+2]
        t2 = re.square()+im.square()
        den = 1+t2
        # w=e1,v=e2; w=e2,v=-e1 respectively.
        out.extend([sign*re/den,im/den,sign*(1-t2)/(2*den)])
    return out


def source_contract(bits=96):
    require_runtime()
    epsilon = I.exact("0.000001",bits)
    ec = epsilon/(1-epsilon.square()).sqrt()
    # J0 columns: all waves, then xA,yA and -xB,yB.
    j0 = [[int(i == j) if j < 12 else
           (int(i == 12) if j == 12 else int(i == 13) if j == 13 else
            -int(i == 15) if j == 14 else int(i == 16)) for j in range(16)] for i in range(18)]
    return {"pi":pi_interval(bits).data(), "chart_radius":ec.data(),
            "chart_remainder_upper":str(ec.square().upper()),"J0":j0,
            "J0_error":"0","seeds":{s:pack([(x,()) for x in source_chart(s,bits=bits)],bits)
                                       for s in ("active-plus","active-minus")}}


def check_local_output(candidate, box, event=0, **kwargs):
    """Deterministic local recomputation guard, not #95's saved-tube checker.

    Refuses incomplete/tampered tail obligations as well as corrupted output.
    Independent analytic tests remain necessary to qualify the implementation.
    """
    expected = evaluate(box,event,**kwargs)
    return expected["status"] == "enclosed" and candidate == expected
