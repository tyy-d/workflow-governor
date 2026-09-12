class WorkflowGovernorError(Exception):
    """Base class for expected workflow errors."""


class ContractValidationError(WorkflowGovernorError):
    """A shared contract is malformed or inconsistent."""


class WorkspaceAccessError(WorkflowGovernorError):
    """Requested evidence is outside the authorized workspace."""


class ExecutionError(WorkflowGovernorError):
    """An executor attempted work and failed."""


class BlockedExecution(WorkflowGovernorError):
    """Execution cannot start because an input or capability is unavailable."""


class AdapterUnavailable(BlockedExecution):
    """The configured local-model adapter is unavailable."""

