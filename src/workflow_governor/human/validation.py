from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any, Mapping, Protocol

from workflow_governor.core.models import DecisionAuthorityScope, EvidenceRef
from workflow_governor.execution.runner import HumanHandoff
from workflow_governor.human.contracts import (
    AuthorityStatus,
    AuthorityValidation,
    Correction,
    HumanTaskResponse,
    ResponseDisposition,
    ResponseValidationResult,
    ValidationIssue,
    ValidationIssueCode,
    human_response_from_mapping,
)


class IdentityProvider(Protocol):
    def is_bound(self, session_id: str, actor_id: str) -> bool: ...


class AuthorityProvider(Protocol):
    def validate(self, actor_id: str, requirement: str | None) -> AuthorityValidation: ...


class HumanArtifactRegistry(Protocol):
    def is_registered(self, handoff_id: str, response_id: str, evidence_ref: EvidenceRef) -> bool: ...


@dataclass(frozen=True, slots=True)
class BoundIdentityProvider:
    bindings: dict[str, str]

    def is_bound(self, session_id: str, actor_id: str) -> bool:
        return self.bindings.get(session_id) == actor_id


class EmptyArtifactRegistry:
    def is_registered(self, handoff_id: str, response_id: str, evidence_ref: EvidenceRef) -> bool:
        return False


_SCOPE_RANK = {
    DecisionAuthorityScope.NO_DECISION: 0,
    DecisionAuthorityScope.ANALYSIS_OR_RECOMMENDATION: 1,
    DecisionAuthorityScope.AUTHORITY_DECISION: 2,
}

_NO_DECISION_DISPOSITIONS = {
    ResponseDisposition.NEEDS_INFORMATION,
    ResponseDisposition.REASSIGNMENT_REQUESTED,
    ResponseDisposition.AUTHORITY_DECLINED,
}


class HumanResponseValidator:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        authority_provider: AuthorityProvider,
        artifact_registry: HumanArtifactRegistry | None = None,
    ) -> None:
        self._identity = identity_provider
        self._authority = authority_provider
        self._artifacts = artifact_registry or EmptyArtifactRegistry()

    def validate_payload(
        self,
        handoff: HumanHandoff,
        payload: Mapping[str, Any],
        *,
        session_id: str,
    ) -> ResponseValidationResult:
        try:
            response = human_response_from_mapping(payload)
        except (KeyError, TypeError, ValueError) as exc:
            return ResponseValidationResult.rejected(
                self._issue(ValidationIssueCode.MALFORMED_RESPONSE, str(exc), "response")
            )
        return self.validate(handoff, response, session_id=session_id)

    def validate(
        self,
        handoff: HumanHandoff,
        response: HumanTaskResponse,
        *,
        session_id: str,
    ) -> ResponseValidationResult:
        issues: list[ValidationIssue] = []
        self._validate_shape(response, issues)

        for field in ("handoff_id", "workflow_id", "task_id"):
            if getattr(response, field) != getattr(handoff, field):
                issues.append(self._issue(ValidationIssueCode.CORRELATION_MISMATCH, f"{field} does not match the handoff", field))

        if not self._identity.is_bound(session_id, response.actor_id):
            issues.append(self._issue(ValidationIssueCode.UNIDENTIFIED_RESPONDER, "actor is not bound to this session", "actor_id"))

        granted = set(handoff.evidence_refs)
        submitted_refs = [(ref, "evidence_refs") for ref in response.evidence_refs]
        submitted_refs.extend(
            (ref, "corrections.supporting_refs")
            for correction in response.corrections
            if isinstance(correction, Correction)
            for ref in correction.supporting_refs
        )
        for ref, field in submitted_refs:
            if not isinstance(ref, EvidenceRef):
                issues.append(self._issue(ValidationIssueCode.MALFORMED_RESPONSE, "evidence collections must contain canonical EvidenceRef values", field))
                continue
            if ref not in granted and not self._artifacts.is_registered(handoff.handoff_id, response.response_id, ref):
                code = ValidationIssueCode.INVALID_ARTIFACT_ATTRIBUTION if ref.artifact_id else ValidationIssueCode.EVIDENCE_OUTSIDE_GRANT
                issues.append(self._issue(code, f"evidence is not granted or attributable: {ref.source}", field))

        requested_scope = handoff.requested_decision_authority_scope
        actual_scope = response.actual_decision_authority_scope
        scopes_valid = isinstance(requested_scope, DecisionAuthorityScope) and isinstance(actual_scope, DecisionAuthorityScope)
        disposition_valid = isinstance(response.response_disposition, ResponseDisposition)
        if not scopes_valid or not disposition_valid:
            issues.append(self._issue(ValidationIssueCode.MALFORMED_RESPONSE, "disposition and authority scopes must use canonical values", "response_disposition"))
        elif _SCOPE_RANK[actual_scope] > _SCOPE_RANK[requested_scope]:
            issues.append(self._issue(ValidationIssueCode.INVALID_DECISION_SCOPE, "response exceeds the handoff decision-authority scope", "actual_decision_authority_scope"))

        if disposition_valid and response.response_disposition in _NO_DECISION_DISPOSITIONS and actual_scope is not DecisionAuthorityScope.NO_DECISION:
            issues.append(self._issue(ValidationIssueCode.INVALID_DECISION_SCOPE, "boundary-safe disposition must not assert a decision", "actual_decision_authority_scope"))

        if (
            scopes_valid
            and disposition_valid
            and requested_scope is DecisionAuthorityScope.AUTHORITY_DECISION
            and response.response_disposition is ResponseDisposition.COMPLETE
            and actual_scope is not DecisionAuthorityScope.AUTHORITY_DECISION
        ):
            issues.append(self._issue(ValidationIssueCode.INVALID_DECISION_SCOPE, "a completed protected decision cannot be self-downgraded", "actual_decision_authority_scope"))

        if disposition_valid and response.response_disposition in {ResponseDisposition.PARTIAL, ResponseDisposition.TASK_NARROWED} and not response.unresolved_questions:
            issues.append(self._issue(ValidationIssueCode.MALFORMED_RESPONSE, "partial or narrowed work must identify what remains unresolved", "unresolved_questions"))

        authority = self._authority.validate(response.actor_id, handoff.authority_requirement)
        if authority.declared_requirement != handoff.authority_requirement:
            issues.append(self._issue(ValidationIssueCode.MALFORMED_RESPONSE, "authority provider evaluated a different requirement", "authority_validation"))
        elif authority != response.authority_validation:
            issues.append(self._issue(ValidationIssueCode.MALFORMED_RESPONSE, "submitted authority facts do not match the trusted provider", "authority_validation"))

        if scopes_valid and actual_scope is DecisionAuthorityScope.AUTHORITY_DECISION and handoff.authority_requirement:
            if authority.status is AuthorityStatus.NOT_SATISFIED:
                issues.append(self._issue(ValidationIssueCode.AUTHORITY_NOT_SATISFIED, "responder lacks the declared authority", "authority_validation"))
            elif authority.status is not AuthorityStatus.SATISFIED:
                issues.append(self._issue(ValidationIssueCode.AUTHORITY_UNVERIFIED, "declared authority could not be verified", "authority_validation"))

        return ResponseValidationResult.rejected(*issues) if issues else ResponseValidationResult.accepted(response)

    @staticmethod
    def _validate_shape(response: HumanTaskResponse, issues: list[ValidationIssue]) -> None:
        for field in ("response_id", "handoff_id", "workflow_id", "task_id", "actor_id", "rationale", "submitted_at"):
            value = getattr(response, field)
            if not isinstance(value, str) or not value.strip():
                issues.append(HumanResponseValidator._issue(ValidationIssueCode.MALFORMED_RESPONSE, f"{field} must be a non-empty string", field))
        if isinstance(response.submitted_at, str):
            try:
                datetime.fromisoformat(response.submitted_at.replace("Z", "+00:00"))
            except ValueError:
                issues.append(HumanResponseValidator._issue(ValidationIssueCode.MALFORMED_RESPONSE, "submitted_at must be an ISO-8601 timestamp", "submitted_at"))
        try:
            encoded = json.dumps(response.decision)
            if response.decision in (None, "", [], {}) or not encoded:
                raise ValueError
        except (TypeError, ValueError):
            issues.append(HumanResponseValidator._issue(ValidationIssueCode.MALFORMED_RESPONSE, "decision must be non-empty JSON-serializable data", "decision"))
        for question in response.unresolved_questions:
            if not isinstance(question, str) or not question.strip():
                issues.append(HumanResponseValidator._issue(ValidationIssueCode.MALFORMED_RESPONSE, "unresolved questions must be non-empty strings", "unresolved_questions"))
        for correction in response.corrections:
            if not isinstance(correction, Correction):
                issues.append(HumanResponseValidator._issue(ValidationIssueCode.MALFORMED_RESPONSE, "corrections must use the canonical Correction type", "corrections"))
                continue
            if not isinstance(correction.target, str) or not correction.target.strip() or not isinstance(correction.rationale, str) or not correction.rationale.strip():
                issues.append(HumanResponseValidator._issue(ValidationIssueCode.MALFORMED_RESPONSE, "corrections require a target and rationale", "corrections"))
            try:
                json.dumps(correction.corrected_value)
                json.dumps(correction.prior_value)
            except (TypeError, ValueError):
                issues.append(HumanResponseValidator._issue(ValidationIssueCode.MALFORMED_RESPONSE, "correction values must be JSON-serializable", "corrections"))
        if response.response_disposition in _NO_DECISION_DISPOSITIONS and not response.unresolved_questions:
            issues.append(HumanResponseValidator._issue(ValidationIssueCode.MALFORMED_RESPONSE, "boundary-safe response must explain what remains unresolved", "unresolved_questions"))

    @staticmethod
    def _issue(code: ValidationIssueCode, message: str, field: str) -> ValidationIssue:
        return ValidationIssue(code, message, field)
