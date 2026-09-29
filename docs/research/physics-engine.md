# Incremental GROSS physics engine

`signal_space.engine` is the extracted existing SS OCF 1 flat, axisymmetric,
fixed-internal-direction sector. It reuses the registered finite-volume and RK4
arithmetic. The current experiment adapters use this core; this is executable
code, not a new alternative law or a full multiphysics framework.

| Interface | Responsibility |
| --- | --- |
| `ModelSpec` | Exact model version, Candidate B, units and supported reduction |
| `GeometrySpec`, `SimulationSpec` | Explicit grid, outer damping intervention, backend and detectors |
| `FieldState` | Six canonical arrays and two integrated sinks; validated dtype/shape, owned snapshots |
| `prepare` | Frozen isolated or freely superposed pair data |
| `Simulation` | NumPy reference or strict compiled advance, energy/charge and quiet-clock observations |
| `checkpoint_fields`, `restore_fields` | Complete field/sink payload; runtime adds hashes, accumulated diagnostics and producer identity |
| `capabilities()` | Implemented and missing combinations; experiment-owned acceptance remains distinct |

The pure `axisymmetric` module does not read repository files, write events,
choose campaign cases or export reports. Existing adapters retain those tasks.
Charge density and fixed profile representation are shared within each detector
sample; moving centroids and interpolated mode shapes remain dynamic. Compiled
and reference kernels remain separate implementations so their agreement is a
useful numerical control. Frozen physical coefficients have not changed.

A high-level bounded engineering preparation can be composed as follows. A real
research experiment must additionally lock its source profile hash, parameters,
controls, acceptance criteria and retention through the registered runtime.

```python
from signal_space.engine import GeometrySpec, SimulationSpec
from signal_space.engine.simulation import prepare, Simulation

spec = SimulationSpec(
    geometry=GeometrySpec(h=0.2, radius=24, half_length=64,
                          absorber_width=4, absorber_strength=0.12),
    backend="numba", neutral_mode="full",
    detectors=("quiet-clock", "energy-charge"),
)
# profile is the already verified frozen radial profile/mode mapping.
initial = prepare(spec, profile, separation=72, pair=True)
simulation = Simulation(spec, initial)
simulation.advance(0.01)
observation = simulation.observe_quiet_clocks(profile, (-36, 36), 72)
owned_snapshot = simulation.snapshot()
```

Unsupported model/reduction, gravity, backend and detector requests fail before
advancement. A superposed pair is not a relaxed joint solution. A frozen clock
projection is not an independent spatial mode solve or an autonomous proper-time
detector. `signal-space capabilities` records these boundaries explicitly.

The next experiment should specify its question and action, identify the smallest
missing capability, add analytical/manufactured and independent-reference controls,
then register and lock the new experiment. Only after measured feasibility and
scientific dependency gates pass should its physics campaign run. Preserve negative
results and numerical limits alongside reusable components.

Full Test 8 needs joint preparation, embedded spatial calibration, physical source
initial data, momentum/worldtube flux, local timelike tracking, proper-time markers
and Test 9 retention. These remain scientific implementation work, with the
prospective 127-evolution design blocked. New action terms require a model version;
new diagnostics/discretizations require numerical and protocol provenance. Engine
availability never establishes physical truth. Candidate A event/projector laws
remain separately versioned; scheduling and evidence can be shared without
identifying them with Candidate B continuum fields.
