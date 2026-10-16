"""Outward dyadic intervals. Only integer/Fraction arithmetic is trusted.

No binary floating operation participates in an enclosure. Each result is
rounded down/up to a fixed binary grid; sqrt uses integer square root.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
import re


@dataclass(frozen=True)
class Interval:
    lo: int
    hi: int
    bits: int = 96

    def __post_init__(self):
        if type(self.lo) is not int or type(self.hi) is not int or self.lo > self.hi:
            raise ValueError("invalid interval")
        if self.bits not in (64, 96, 128):
            raise ValueError("unsupported precision")
        if max(abs(self.lo), abs(self.hi)).bit_length() > self.bits + 512:
            raise ArithmeticError("interval magnitude resource ceiling")

    @classmethod
    def exact(cls, value, bits=96):
        if isinstance(value, cls):
            if value.bits != bits:
                raise ValueError("mixed precision")
            return value
        # Floats are deliberately rejected: caller must declare their exact
        # rational value using Fraction.from_float, or use decimal strings.
        if type(value) not in (int, str, Fraction):
            raise ValueError("expected exact rational input")
        if isinstance(value, str) and (len(value) > 256 or not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|[0-9]+/[0-9]+)", value)):
            raise ValueError("expected bounded decimal or rational string (no exponent)")
        q = Fraction(value)
        if max(q.numerator.bit_length(), q.denominator.bit_length()) > 16384:
            raise ValueError("input size ceiling")
        n, d = q.numerator << bits, q.denominator
        return cls(n // d, -((-n) // d), bits)

    def coerce(self, x):
        return Interval.exact(x, self.bits)

    def __add__(self, x):
        x = self.coerce(x)
        return Interval(self.lo + x.lo, self.hi + x.hi, self.bits)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo, self.bits)

    def __sub__(self, x):
        return self + -self.coerce(x)

    def __rsub__(self, x):
        return self.coerce(x) - self

    def __mul__(self, x):
        x = self.coerce(x)
        products = (self.lo*x.lo, self.lo*x.hi, self.hi*x.lo, self.hi*x.hi)
        return Interval(min(products) >> self.bits,
                        -((-max(products)) >> self.bits), self.bits)

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ArithmeticError("division interval contains zero")
        scale = 1 << (2*self.bits)
        return Interval(scale // self.hi, -((-scale) // self.lo), self.bits)

    def __truediv__(self, x):
        return self * self.coerce(x).reciprocal()

    def __rtruediv__(self, x):
        return self.coerce(x) / self

    def square(self):
        low = 0 if self.lo <= 0 <= self.hi else min(self.lo**2, self.hi**2)
        high = max(self.lo**2, self.hi**2)
        return Interval(low >> self.bits, -((-high) >> self.bits), self.bits)

    def sqrt(self):
        if self.lo < 0:
            raise ArithmeticError("negative square-root domain")
        lo = isqrt(self.lo << self.bits)
        h = self.hi << self.bits
        hi = isqrt(h)
        return Interval(lo, hi + (hi*hi != h), self.bits)

    def upper(self):
        return Fraction(self.hi, 1 << self.bits)

    def magnitude(self):
        return Fraction(max(abs(self.lo), abs(self.hi)), 1 << self.bits)

    def midpoint(self):
        return Fraction(self.lo + self.hi, 1 << (self.bits+1))

    def radius(self):
        return Fraction(self.hi-self.lo, 1 << (self.bits+1))

    def widen(self, radius):
        r = self.coerce(radius)
        if r.lo < 0:
            raise ValueError("negative radius")
        return Interval(self.lo-r.hi, self.hi+r.hi, self.bits)

    def contains(self, value):
        q = Fraction(value)
        return Fraction(self.lo, 1 << self.bits) <= q <= self.upper()

    def data(self):
        return {"lo": str(self.lo), "hi": str(self.hi), "bits": self.bits}


def norm_upper(values, bits=96):
    """Euclidean/Frobenius upper bound, including all arithmetic."""
    total = sum((Interval.exact(v, bits).magnitude()**2 for v in values), Fraction(0))
    scaled = (total.numerator << (2*bits)) // total.denominator
    root = isqrt(scaled)
    if Fraction(root*root, 1 << (2*bits)) < total:
        root += 1
    return Fraction(root, 1 << bits)



def pi_interval(bits=96):
    """Machin identity; alternating arctan series with exact rational tails."""
    def atan_inverse(q):
        n = bits  # deliberately over-resolved, fixed bounded work
        partial = sum((Fraction((-1)**k, (2*k+1)*q**(2*k+1))
                       for k in range(n)), Fraction(0))
        remainder = Fraction(1, (2*n+1)*q**(2*n+1))
        return Interval.exact(partial, bits).widen(remainder)
    return 16*atan_inverse(5) - 4*atan_inverse(239)
