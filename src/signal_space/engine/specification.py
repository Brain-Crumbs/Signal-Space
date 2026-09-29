"""High-level engine specification: unsupported physics fails before evolution."""
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class ModelSpec:
    model_id: str = 'signal-space.ss-ocf-1.flat-axisymmetric-neutral-clock.v1'
    candidate: str = 'B'
    units: str = 'c=hbar=m=1'
    reduction: str = 'fixed-internal-direction-axisymmetric'
    gravity: str = 'decoupled'


@dataclass(frozen=True)
class GeometrySpec:
    h: float
    radius: float
    half_length: float
    absorber_width: float
    absorber_strength: float


@dataclass(frozen=True)
class SimulationSpec:
    geometry: GeometrySpec
    model: ModelSpec = field(default_factory=ModelSpec)
    backend: str = 'numpy'
    neutral_mode: str = 'full'
    detectors: tuple[str, ...] = ('quiet-clock', 'energy-charge')

    def validate(self):
        import math
        if self.model != ModelSpec():
            raise ValueError('unsupported model/reduction; a new physical action requires an explicit registered implementation')
        if self.backend not in {'numpy','numba'} or self.neutral_mode not in {'full','exact-zero'}:
            raise ValueError('unsupported engine backend or neutral sector')
        if self.neutral_mode == 'exact-zero' and self.backend != 'numba':
            raise ValueError('exact-zero is a compiled, exact-null capability')
        if set(self.detectors)-{'quiet-clock','energy-charge'}:
            raise ValueError('detector capability unavailable; worldtubes, proper-time markers and momentum exchange require separate qualification')
        g=self.geometry
        if any(not math.isfinite(v) or v<=0 for v in (g.h,g.radius,g.half_length,g.absorber_width)) or not math.isfinite(g.absorber_strength) or g.absorber_strength<0:
            raise ValueError('finite positive geometry and nonnegative absorber strength required')
        if g.absorber_width>=min(g.radius,g.half_length): raise ValueError('absorber does not fit domain')
        for length in (g.radius,2*g.half_length):
            if abs(round(length/g.h)*g.h-length)>1e-8: raise ValueError('geometry extents must be exact cell multiples')
        return self

    def record(self):
        return asdict(self)


def capabilities():
    return {'engine_version':'1', 'model':asdict(ModelSpec()),
            'supported':['axisymmetric-flat-fv','rk4','numpy-reference','numba-strict',
                         'frozen-profile-preparation','free-superposed-pair','quiet-clock',
                         'energy-charge','absorber-sinks','complete-quiet-restart'],
            'unavailable':['joint-relaxed-pair','embedded-spatial-mode-solve','physical-source-exchange',
                           'momentum-worldtube-flux','proper-time-marker-tracking','Test9-reconstruction',
                           'dynamical-gravity','protected-topology'],
            'candidate_A':'separate registered event/projector implementations; no continuum identification',
            'scientific_acceptance':'owned by each locked experiment, not inferred from engine availability'}
