"""Common host admission. Locked run ceilings are never silently increased."""
from pathlib import Path

from signal_space.runtime import execution
from signal_space.runtime.errors import ResourceRejected


def admit(resources, workspace: Path, policy=None, *, extra_output_mb=0):
    policy = policy or execution.ExecutionPolicy()
    capacity = {'cpu_slots': execution.cpu_capacity(),
                'memory_mb': execution.memory_capacity_mb(),
                'output_mb': execution.disk_capacity_mb(Path(workspace).resolve())}
    requested = {'cpu_slots': policy.cpu_slots,
                 'memory_mb': resources['max_memory_mb'],
                 'output_mb': resources['max_output_mb'] + extra_output_mb}
    rejected = [key for key in requested if requested[key] > capacity[key]]
    if rejected:
        raise ResourceRejected('host admission rejected ' + ', '.join(
            f'{key}: requires {requested[key]}, available {capacity[key]}' for key in rejected))
    return {'requested': requested, 'available': capacity,
            'retention': 'available disk is after existing attempts; reserve a full new attempt plus stated export headroom'}
