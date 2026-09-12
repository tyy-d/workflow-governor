"""Shared P00-compatible contracts used by the parallel tracks.

These are cross-track interfaces. Change them only through an explicit interface
change request during parallel development.
"""

from .models import (
    DecisionAuthorityScope,
    EvidenceContent,
    EvidenceRef,
    ExecutionStatus,
    ExecutorType,
    FileRecord,
    PlanStatus,
    TaskContext,
    TaskResult,
    TaskSpec,
    WorkflowPlan,
    WorkspaceMap,
)

__all__ = [
    "DecisionAuthorityScope",
    "EvidenceContent",
    "EvidenceRef",
    "ExecutionStatus",
    "ExecutorType",
    "FileRecord",
    "PlanStatus",
    "TaskContext",
    "TaskResult",
    "TaskSpec",
    "WorkflowPlan",
    "WorkspaceMap",
]
