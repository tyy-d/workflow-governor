from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class ExecutorType(StrEnum):
    DETERMINISTIC = "DETERMINISTIC"
    LOCAL_MODEL = "LOCAL_MODEL"
    HUMAN = "HUMAN"


class ExecutionStatus(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    PENDING_HUMAN = "PENDING_HUMAN"


class PlanStatus(StrEnum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    SUPERSEDED = "SUPERSEDED"


class DecisionAuthorityScope(StrEnum):
    """Maximum authority-bearing scope requested by an approved task."""

    NO_DECISION = "NO_DECISION"
    ANALYSIS_OR_RECOMMENDATION = "ANALYSIS_OR_RECOMMENDATION"
    AUTHORITY_DECISION = "AUTHORITY_DECISION"


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    source: str
    location: str | None = None
    artifact_id: str | None = None
    label: str | None = None


@dataclass(frozen=True, slots=True)
class EvidenceContent:
    ref: EvidenceRef
    content: str
    untrusted_document: bool = True


@dataclass(frozen=True, slots=True)
class FileRecord:
    relative_path: str
    name: str
    media_type: str | None = None
    size: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    extractable: bool | None = None


@dataclass(frozen=True, slots=True)
class WorkspaceMap:
    root: str
    files: tuple[FileRecord, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TaskSpec:
    task_id: str
    objective: str
    description: str
    executor_type: ExecutorType
    dependencies: tuple[str, ...] = ()
    evidence_requirements: tuple[EvidenceRef, ...] = ()
    policy_requirements: tuple[EvidenceRef, ...] = ()
    completion_criteria: tuple[str, ...] = ()
    consequence: str | None = None
    risk: str | None = None
    authority_requirement: str | None = None
    requested_decision_authority_scope: DecisionAuthorityScope = DecisionAuthorityScope.NO_DECISION
    operation: str | None = None


@dataclass(frozen=True, slots=True)
class TaskContext:
    task_id: str
    evidence: tuple[EvidenceContent, ...] = ()
    policy: tuple[EvidenceContent, ...] = ()
    deterministic_results: tuple["TaskResult", ...] = ()
    workflow_state: Mapping[str, Any] = field(default_factory=dict)
    operation_inputs: Mapping[str, Any] = field(default_factory=dict)
    granted_sources: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TaskResult:
    task_id: str
    status: ExecutionStatus
    executor_type: ExecutorType
    findings: tuple[str, ...] = ()
    evidence_refs: tuple[EvidenceRef, ...] = ()
    artifacts: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    rationale: str | None = None
    error: str | None = None
    output: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkflowPlan:
    plan_id: str
    version: int
    objective: str
    tasks: tuple[TaskSpec, ...]
    assumptions: tuple[str, ...] = ()
    unresolved_questions: tuple[str, ...] = ()
