class ResearchRuntimeError(RuntimeError):
    code = "RUNTIME_ERROR"


class ResourceRejected(ResearchRuntimeError):
    code = "RESOURCE_REJECTED"


class RunNotFound(ResearchRuntimeError):
    code = "RUN_NOT_FOUND"


class InvalidState(ResearchRuntimeError):
    code = "INVALID_STATE"


class CheckpointMismatch(ResearchRuntimeError):
    code = "CHECKPOINT_MISMATCH"


class IntegrityError(ResearchRuntimeError):
    code = "CORRUPT_ARTIFACT"
