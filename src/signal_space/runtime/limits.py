"""Apply process limits before importing experiment or numerical libraries."""
from typing import Any

def _resource_limiter(resources: dict[str, Any]):
    def limit() -> None:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (int(resources["max_cpu_seconds"]), int(resources["max_cpu_seconds"])))
        bytes_limit = int(resources["max_memory_mb"]) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (bytes_limit, bytes_limit))
        file_limit = int(resources["max_output_mb"]) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
    return limit

