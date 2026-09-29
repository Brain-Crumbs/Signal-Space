"""Composable existing physics with explicit state ownership and detector scope."""
from signal_space.engine.specification import SimulationSpec
from signal_space.engine.state import FieldState


class Simulation:
    def __init__(self, spec: SimulationSpec, initial: FieldState):
        from signal_space.engine.axisymmetric import AbsorbingGrid
        spec.validate(); initial.validate()
        self.spec=spec
        g=spec.geometry
        self.grid=AbsorbingGrid(g.h,g.radius,g.half_length,g.absorber_width,g.absorber_strength)
        if initial.phi.shape!=(self.grid.nr,self.grid.nz): raise ValueError('state and geometry differ')
        self._state=initial.snapshot().as_tuple()
        self._compiled=None
        if spec.backend=='numba':
            from signal_space.numerics.two_object_compiled import CompiledStepper
            self._compiled=CompiledStepper(self.grid,self._state,exact_zero=spec.neutral_mode=='exact-zero')
            self._state=self._compiled.state

    @property
    def state(self):
        """Live view. Use snapshot() to retain an independent observation."""
        return FieldState(*self._state)

    def snapshot(self):
        return FieldState.from_tuple(self._state,copy=True)

    def advance(self, dt):
        import math
        from signal_space.engine.axisymmetric import step
        if not math.isfinite(dt) or dt<=0: raise ValueError('positive finite timestep required')
        self._state=self._compiled.advance(dt) if self._compiled else step(self.grid,self._state,dt)
        return self.state

    def energy_charge(self):
        return self.grid.energy_charge(self._state[:6])

    def observe_quiet_clocks(self, profile, centers, separation):
        from signal_space.engine.axisymmetric import local_observables
        if 'quiet-clock' not in self.spec.detectors: raise ValueError('quiet-clock detector not selected')
        return local_observables(self.grid,self._state,profile,centers,separation)


def prepare(spec, profile, separation, *, pair=False, amplitude=.001):
    from signal_space.engine.axisymmetric import AbsorbingGrid, initial_state
    spec.validate(); g=spec.geometry
    grid=AbsorbingGrid(g.h,g.radius,g.half_length,g.absorber_width,g.absorber_strength)
    return FieldState.from_tuple((*initial_state(grid,profile,separation,amplitude,pair),0.,0.))


def checkpoint_fields(state):
    """Complete canonical field payload; runtime adds identity and diagnostics."""
    state.validate()
    return {key:getattr(state,key).copy() for key in ('phi','pi','chi','pchi','a','pia')} | {
        'energy_sink':state.energy_sink,'charge_sink':state.charge_sink}


def restore_fields(payload):
    return FieldState.from_tuple(tuple(payload[key] for key in ('phi','pi','chi','pchi','a','pia','energy_sink','charge_sink')),copy=True)
