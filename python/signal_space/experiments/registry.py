from __future__ import annotations

from signal_space.experiments.base import ExperimentPlugin
from signal_space.experiments.synthetic import SyntheticExperiment
from signal_space.experiments.charged import ChargedExperiment
from signal_space.experiments.operators import OperatorExperiment
from signal_space.experiments.reciprocal import ReciprocalExperiment
from signal_space.experiments.router import RouterExperiment
from signal_space.experiments.floquet import FloquetExperiment
from signal_space.experiments.continuum import ContinuumExperiment
from signal_space.experiments.clock import ClockExperiment
from signal_space.experiments.prereception import PrereceptionExperiment
from signal_space.experiments.reception import ReceptionExperiment
from signal_space.experiments.reception_order4 import ReceptionOrder4Experiment
from signal_space.experiments.reception_transfer import ReceptionTransferExperiment

_PLUGINS: dict[str, ExperimentPlugin] = {
    SyntheticExperiment.experiment_id: SyntheticExperiment(),
    ChargedExperiment.experiment_id: ChargedExperiment(),
    OperatorExperiment.experiment_id: OperatorExperiment(),
    ReciprocalExperiment.experiment_id: ReciprocalExperiment(),
    RouterExperiment.experiment_id: RouterExperiment(),
    FloquetExperiment.experiment_id: FloquetExperiment(),
    ContinuumExperiment.experiment_id: ContinuumExperiment(),
    ClockExperiment.experiment_id: ClockExperiment(),
    "gross.clock-longevity.v1": PrereceptionExperiment("longevity"),
    "gross.clock-response.v1": PrereceptionExperiment("response"),
    ReceptionExperiment.experiment_id: ReceptionExperiment(),
    ReceptionOrder4Experiment.experiment_id: ReceptionOrder4Experiment(),
    ReceptionTransferExperiment.experiment_id: ReceptionTransferExperiment(),
}


def get_experiment(experiment_id: str) -> ExperimentPlugin:
    try:
        return _PLUGINS[experiment_id]
    except KeyError as error:
        raise ValueError(f"unregistered experiment id: {experiment_id}") from error


def list_experiments() -> list[dict[str, object]]:
    return [plugin.describe() for plugin in _PLUGINS.values()]
