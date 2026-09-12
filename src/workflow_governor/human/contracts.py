from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from workflow_governor.core.models import DecisionAuthorityScope, EvidenceRef


class ResponseDisposition(StrEnum):
    COMPLETE = "COMPLETE"
    NEEDS_INFORMATION = "NEEDS_INFORMATION"
    PARTIAL = "PARTIAL"
    TASK_NARROWED = "TASK_NARROWED"
    REASSIGNMENT_REQUESTED = "REASSIGNMENT_REQUESTED"
    AUTHORITY_DECLINED = "AUTHORITY_DECLINED"


class AuthorityStatus(StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    UNVERIFIED = "UNVERIFIED"


class ValidationStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ValidationIssueCode(StrEnum):
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    CORRELATION_MISMATCH = "CORRELATION_MISMATCH"
    UNIDENTIFIED_RESPONDER = "UNIDENTIFIED_RESPONDER"
    INVALID_DECISION_SCOPE = "INVALID_DECISION_SCOPE"
    AUTHORITY_NOT_SATISFIED = "AUTHORITY_NOT_SATISFIED"
    AUTHORITY_UNVERIFIED = "AUTHORITY_UNVERIFIED"
    EVIDENCE_OUTSIDE_GRANT = "EVIDENCE_OUTSIDE_GRANT"
    INVALID_ARTIFACT_ATTRIBUTION = "INVALID_ARTIFACT_ATTRIBUTION"


@dataclass(frozen=True, slots=True)
class AuthorityValidation:
    status: AuthorityStatus
    declared_requirement: str | None
    basis_refs: tuple[EvidenceRef, ...] = ()
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class Correction:
    target: str
    corrected_value: Any
    rationale: str
    prior_value: Any | None = None
    supporting_refs: tuple[EvidenceRef, ...] = ()


@dataclass(frozen=True, slots=True)
class HumanTaskResponse:
    response_id: str
    handoff_id: str
    workflow_id: str
    task_id: str
    actor_id: str
    response_disposition: ResponseDisposition
    actual_decision_authority_scope: DecisionAuthorityScope
    authority_validation: AuthorityValidation
    decision: Any
    rationale: str
    evidence_refs: tuple[EvidenceRef, ...] = ()
    corrections: tuple[Correction, ...] = ()
    unresolved_questions: tuple[str, ...] = ()
    submitted_at: str = ""


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: ValidationIssueCode
    message: str
    field: str | None = None


@dataclass(frozen=True, slots=True)
class ResponseValidationResult:
    status: ValidationStatus
    response: HumanTaskResponse | None = None
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

    @classmethod
    def accepted(cls, response: HumanTaskResponse) -> "ResponseValidationResult":
        return cls(ValidationStatus.ACCEPTED, response=response)

    @classmethod
    def rejected(cls, *issues: ValidationIssue) -> "ResponseValidationResult":
        return cls(ValidationStatus.REJECTED, issues=tuple(issues))


def human_response_from_mapping(value: Mapping[str, Any]) -> HumanTaskResponse:
    """Parse the canonical wire form without accepting silent extra fields."""

    required = {
        "response_id", "handoff_id", "workflow_id", "task_id", "actor_id",
        "response_disposition", "actual_decision_authority_scope",
        "authority_validation", "decision", "rationale", "submitted_at",
    }
    optional = {"evidence_refs", "corrections", "unresolved_questions"}
    missing = required - set(value)
    extra = set(value) - required - optional
    if missing or extra:
        raise ValueError(f"invalid response fields; missing={sorted(missing)}, extra={sorted(extra)}")
    authority = value["authority_validation"]
    if not isinstance(authority, Mapping):
        raise ValueError("authority_validation must be an object")
    authority_validation = AuthorityValidation(
        status=AuthorityStatus(authority["status"]),
        declared_requirement=authority.get("declared_requirement"),
        basis_refs=tuple(_evidence_ref(item) for item in authority.get("basis_refs", ())),
        reason=authority.get("reason"),
    )
    corrections = tuple(_correction(item) for item in value.get("corrections", ()))
    return HumanTaskResponse(
        response_id=value["response_id"],
        handoff_id=value["handoff_id"],
        workflow_id=value["workflow_id"],
        task_id=value["task_id"],
        actor_id=value["actor_id"],
        response_disposition=ResponseDisposition(value["response_disposition"]),
        actual_decision_authority_scope=DecisionAuthorityScope(value["actual_decision_authority_scope"]),
        authority_validation=authority_validation,
        decision=value["decision"],
        rationale=value["rationale"],
        evidence_refs=tuple(_evidence_ref(item) for item in value.get("evidence_refs", ())),
        corrections=corrections,
        unresolved_questions=tuple(value.get("unresolved_questions", ())),
        submitted_at=value["submitted_at"],
    )


def _evidence_ref(value: Mapping[str, Any]) -> EvidenceRef:
    if not isinstance(value, Mapping):
        raise ValueError("evidence reference must be an object")
    allowed = {"source", "location", "artifact_id", "label"}
    if "source" not in value or set(value) - allowed:
        raise ValueError("invalid evidence reference")
    return EvidenceRef(value["source"], value.get("location"), value.get("artifact_id"), value.get("label"))


def _correction(value: Mapping[str, Any]) -> Correction:
    if not isinstance(value, Mapping):
        raise ValueError("correction must be an object")
    required = {"target", "corrected_value", "rationale"}
    allowed = required | {"prior_value", "supporting_refs"}
    if required - set(value) or set(value) - allowed:
        raise ValueError("invalid correction")
    return Correction(
        target=value["target"],
        corrected_value=value["corrected_value"],
        rationale=value["rationale"],
        prior_value=value.get("prior_value"),
        supporting_refs=tuple(_evidence_ref(item) for item in value.get("supporting_refs", ())),
    )


__all__ = [
    "AuthorityStatus",
    "AuthorityValidation",
    "Correction",
    "DecisionAuthorityScope",
    "HumanTaskResponse",
    "ResponseDisposition",
    "ResponseValidationResult",
    "ValidationIssue",
    "ValidationIssueCode",
    "ValidationStatus",
    "human_response_from_mapping",
]
