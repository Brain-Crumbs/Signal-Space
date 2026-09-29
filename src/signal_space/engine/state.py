"""Typed canonical quiet state. Snapshots own their arrays; views are explicit."""
from dataclasses import dataclass
import numpy as np


@dataclass
class FieldState:
    phi: np.ndarray
    pi: np.ndarray
    chi: np.ndarray
    pchi: np.ndarray
    a: np.ndarray
    pia: np.ndarray
    energy_sink: float = 0.
    charge_sink: float = 0.

    @classmethod
    def from_tuple(cls, state, *, copy=False):
        if len(state)!=8: raise ValueError('six canonical fields and two sinks required')
        result=cls(*(np.array(x,copy=True) if copy else x for x in state[:6]),float(state[6]),float(state[7]))
        result.validate()
        return result

    def as_tuple(self):
        return (self.phi,self.pi,self.chi,self.pchi,self.a,self.pia,self.energy_sink,self.charge_sink)

    def snapshot(self):
        return self.from_tuple(self.as_tuple(),copy=True)

    def validate(self):
        for i,value in enumerate(self.as_tuple()[:6]):
            if value.ndim!=2 or value.shape!=self.phi.shape or value.dtype!=np.dtype('complex128' if i<2 else 'float64') or not np.isfinite(value).all():
                raise ValueError('canonical fields require common 2D shape and finite complex128/float64 values')
        if not np.isfinite((self.energy_sink,self.charge_sink)).all(): raise ValueError('nonfinite integrated sinks')
