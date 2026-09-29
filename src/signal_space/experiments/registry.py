"""GROSS-only registry. Load one plugin on demand; never import solvers here."""
from functools import lru_cache
from importlib import import_module
from signal_space.experiments.base import ExperimentPlugin

_PLUGINS = {
    'gross.operator-identities.v1': ('operators', 'OperatorExperiment', ()),
    'gross.reciprocal-events.v1': ('reciprocal', 'ReciprocalExperiment', ()),
    'gross.router-propagation.v1': ('router', 'RouterExperiment', ()),
    'gross.full-spectrum.v1': ('floquet', 'FloquetExperiment', ()),
    'gross.continuum-action.v1': ('continuum', 'ContinuumExperiment', ()),
    'gross.bound-clock.v1': ('clock', 'ClockExperiment', ()),
    'gross.reception.v1': ('reception', 'ReceptionExperiment', ()),
    'gross.reception-order4.v1': ('reception_order4', 'ReceptionOrder4Experiment', ()),
    'gross.reception-transfer.v1': ('reception_transfer', 'ReceptionTransferExperiment', ()),
    'gross.reconstruction.v1': ('reconstruction', 'ReconstructionExperiment', ()),
    'gross.boundary-memory.v1': ('boundary_memory', 'BoundaryMemoryExperiment', ()),
    'gross.reception-acceptance.v1': ('reception_acceptance', 'ReceptionAcceptanceExperiment', ()),
    'gross.two-object-calibration.v1': ('two_object', 'TwoObjectCalibrationExperiment', ()),
    'gross.two-object-quiet-calibration.v1': ('two_object_quiet', 'TwoObjectQuietExperiment', ()),
    "gross.clock-longevity.v1": ("prereception", "PrereceptionExperiment", ("longevity",)),
    "gross.clock-response.v1": ("prereception", "PrereceptionExperiment", ("response",)),
}

@lru_cache(maxsize=None)
def get_experiment(experiment_id: str) -> ExperimentPlugin:
    try:
        module, name, arguments = _PLUGINS[experiment_id]
    except KeyError as error:
        raise ValueError(f"unregistered GROSS experiment id: {experiment_id}") from error
    return getattr(import_module(f"signal_space.experiments.{module}"), name)(*arguments)

def list_experiments() -> list[dict[str, object]]:
    return [get_experiment(key).describe() for key in sorted(_PLUGINS)]
