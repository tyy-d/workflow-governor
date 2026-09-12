from __future__ import annotations

from dataclasses import replace

import pytest

from workflow_governor.core.models import DecisionAuthorityScope, EvidenceRef
from workflow_governor.execution.runner import HumanHandoff
from workflow_governor.human.contracts import (
    AuthorityStatus,
    AuthorityValidation,
    Correction,
    HumanTaskResponse,
    ResponseDisposition,
    ValidationIssueCode,
    ValidationStatus,
)
from workflow_governor.human.interaction import FileHumanInteractionStore
from workflow_governor.human.validation import BoundIdentityProvider, HumanResponseValidator


GRANT = EvidenceRef("workspace/document.txt")
AUTHORITY_BASIS = EvidenceRef("trusted/authority.json")


class Authority:
    def __init__(self, status: AuthorityStatus):
        self.status = status

    def validate(self, actor_id, requirement):
        return AuthorityValidation(self.status if requirement else AuthorityStatus.NOT_REQUIRED, requirement, (AUTHORITY_BASIS,), "trusted fixture")


def handoff(scope=DecisionAuthorityScope.AUTHORITY_DECISION):
    return HumanHandoff(
        handoff_id="H001",
        workflow_id="W001",
        plan_id="P001",
        plan_version=1,
        task_id="T001",
        objective="Review the bounded evidence",
        evidence_refs=(GRANT,),
        authority_requirement="vendor activation authority" if scope is DecisionAuthorityScope.AUTHORITY_DECISION else None,
        requested_decision_authority_scope=scope,
        completion_criteria=("Return a decision and rationale",),
        unresolved_questions=(),
        created_at="2026-09-12T14:00:00+00:00",
    )


def response(
    *,
    response_id="R001",
    disposition=ResponseDisposition.COMPLETE,
    scope=DecisionAuthorityScope.AUTHORITY_DECISION,
    authority=AuthorityStatus.SATISFIED,
    evidence=(GRANT,),
    unresolved=(),
):
    return HumanTaskResponse(
        response_id=response_id,
        handoff_id="H001",
        workflow_id="W001",
        task_id="T001",
        actor_id="P001",
        response_disposition=disposition,
        actual_decision_authority_scope=scope,
        authority_validation=AuthorityValidation(authority, "vendor activation authority", (AUTHORITY_BASIS,), "trusted fixture"),
        decision={"outcome": "REJECTED"},
        rationale="The review is complete from the evidence provided.",
        evidence_refs=evidence,
        unresolved_questions=unresolved,
        submitted_at="2026-09-12T14:01:00+00:00",
    )


def validator(authority=AuthorityStatus.SATISFIED, artifacts=None):
    return HumanResponseValidator(BoundIdentityProvider({"S001": "P001"}), Authority(authority), artifacts)


def codes(result):
    return {issue.code for issue in result.issues}


def test_completed_review_keeps_business_rejection_separate_from_task_status() -> None:
    result = validator().validate(handoff(), response(), session_id="S001")
    assert result.status is ValidationStatus.ACCEPTED
    assert result.response.decision["outcome"] == "REJECTED"
    assert not hasattr(result, "task_status")


def test_safe_authority_decline_is_accepted_without_decision_authority() -> None:
    submitted = response(
        disposition=ResponseDisposition.AUTHORITY_DECLINED,
        scope=DecisionAuthorityScope.NO_DECISION,
        authority=AuthorityStatus.NOT_SATISFIED,
        unresolved=("An authorized Vendor Compliance reviewer is required.",),
    )
    result = validator(AuthorityStatus.NOT_SATISFIED).validate(handoff(), submitted, session_id="S001")
    assert result.status is ValidationStatus.ACCEPTED


def test_protected_complete_response_cannot_self_downgrade() -> None:
    submitted = response(scope=DecisionAuthorityScope.ANALYSIS_OR_RECOMMENDATION)
    result = validator().validate(handoff(), submitted, session_id="S001")
    assert ValidationIssueCode.INVALID_DECISION_SCOPE in codes(result)


def test_protected_decision_requires_satisfied_authority() -> None:
    submitted = response(authority=AuthorityStatus.UNVERIFIED)
    result = validator(AuthorityStatus.UNVERIFIED).validate(handoff(), submitted, session_id="S001")
    assert ValidationIssueCode.AUTHORITY_UNVERIFIED in codes(result)


@pytest.mark.parametrize("requested,actual", [
    (DecisionAuthorityScope.NO_DECISION, DecisionAuthorityScope.NO_DECISION),
    (DecisionAuthorityScope.ANALYSIS_OR_RECOMMENDATION, DecisionAuthorityScope.ANALYSIS_OR_RECOMMENDATION),
])
def test_non_authority_scopes_are_accepted_without_authority(requested, actual) -> None:
    current_handoff = handoff(requested)
    submitted = replace(
        response(scope=actual),
        authority_validation=AuthorityValidation(AuthorityStatus.NOT_REQUIRED, None, (AUTHORITY_BASIS,), "trusted fixture"),
    )
    result = validator().validate(current_handoff, submitted, session_id="S001")
    assert result.status is ValidationStatus.ACCEPTED


def test_response_cannot_escalate_above_declared_scope() -> None:
    current_handoff = handoff(DecisionAuthorityScope.NO_DECISION)
    submitted = replace(
        response(scope=DecisionAuthorityScope.ANALYSIS_OR_RECOMMENDATION),
        authority_validation=AuthorityValidation(AuthorityStatus.NOT_REQUIRED, None, (AUTHORITY_BASIS,), "trusted fixture"),
    )
    result = validator().validate(current_handoff, submitted, session_id="S001")
    assert ValidationIssueCode.INVALID_DECISION_SCOPE in codes(result)


@pytest.mark.parametrize("disposition", [
    ResponseDisposition.NEEDS_INFORMATION,
    ResponseDisposition.REASSIGNMENT_REQUESTED,
    ResponseDisposition.AUTHORITY_DECLINED,
])
def test_no_decision_boundary_dispositions_are_accepted(disposition) -> None:
    submitted = response(
        disposition=disposition,
        scope=DecisionAuthorityScope.NO_DECISION,
        authority=AuthorityStatus.NOT_SATISFIED,
        unresolved=("An authorized owner or additional evidence is required.",),
    )
    assert validator(AuthorityStatus.NOT_SATISFIED).validate(handoff(), submitted, session_id="S001").status is ValidationStatus.ACCEPTED


@pytest.mark.parametrize("disposition", [ResponseDisposition.PARTIAL, ResponseDisposition.TASK_NARROWED])
def test_partial_or_narrowed_analysis_preserves_protected_decision(disposition) -> None:
    submitted = response(
        disposition=disposition,
        scope=DecisionAuthorityScope.ANALYSIS_OR_RECOMMENDATION,
        authority=AuthorityStatus.NOT_SATISFIED,
        unresolved=("The protected activation decision remains unresolved.",),
    )
    assert validator(AuthorityStatus.NOT_SATISFIED).validate(handoff(), submitted, session_id="S001").status is ValidationStatus.ACCEPTED


def test_identity_correlation_and_grant_failures_are_typed() -> None:
    submitted = replace(response(), workflow_id="OTHER", evidence_refs=(EvidenceRef("workspace/secret.txt"),))
    result = validator().validate(handoff(), submitted, session_id="wrong-session")
    assert {
        ValidationIssueCode.CORRELATION_MISMATCH,
        ValidationIssueCode.UNIDENTIFIED_RESPONDER,
        ValidationIssueCode.EVIDENCE_OUTSIDE_GRANT,
    }.issubset(codes(result))


def test_file_adapter_keeps_submissions_distinct_and_idempotent(tmp_path) -> None:
    store = FileHumanInteractionStore(tmp_path)
    first = response(response_id="R001")
    second = response(response_id="R002")
    assert store.write_submission(first) == store.write_submission(first)
    payload = store.read_submission("W001", "H001", "R001")
    assert validator().validate_payload(handoff(), payload, session_id="S001").status is ValidationStatus.ACCEPTED
    assert store.write_submission(second).name == "R002.json"
    artifact = store.register_artifact(first, "note.txt", b"bounded human note")
    assert store.is_registered("W001", "H001", "R001", artifact)
    accepted = response(response_id="R001", evidence=(GRANT, artifact))
    result = validator(artifacts=store).validate(handoff(), accepted, session_id="S001")
    assert result.status is ValidationStatus.ACCEPTED


def test_artifact_registration_is_bound_to_exact_workflow_path(tmp_path) -> None:
    store = FileHumanInteractionStore(tmp_path)
    artifact = store.register_artifact(response(), "note.txt", b"bounded human note")
    assert not store.is_registered("OTHER", "H001", "R001", artifact)

    misleading = tmp_path / "workflows/OTHER/artifacts/human/H001/responses/R001/artifacts"
    misleading.mkdir(parents=True)
    misleading_path = misleading / f"{artifact.artifact_id}-note.txt"
    misleading_path.write_bytes(b"unrelated workflow artifact")
    misleading_ref = EvidenceRef(
        misleading_path.relative_to(tmp_path).as_posix(),
        artifact_id=artifact.artifact_id,
    )
    assert not store.is_registered("W001", "H001", "R001", misleading_ref)


def test_file_adapter_rejects_symlinked_interaction_paths(tmp_path) -> None:
    store = FileHumanInteractionStore(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    linked = tmp_path / "workflows/W001/artifacts/human"
    linked.parent.mkdir(parents=True)
    linked.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="unsafe human interaction path"):
        store.write_submission(response())


def test_malformed_wire_payload_returns_typed_rejection() -> None:
    result = validator().validate_payload(handoff(), {"response_id": "R001"}, session_id="S001")
    assert result.status is ValidationStatus.REJECTED
    assert codes(result) == {ValidationIssueCode.MALFORMED_RESPONSE}


def test_correction_supporting_evidence_obeys_grant_boundary() -> None:
    submitted = replace(
        response(),
        corrections=(Correction("prior finding", "corrected", "The supplied record differs.", supporting_refs=(EvidenceRef("workspace/secret.txt"),)),),
    )
    result = validator().validate(handoff(), submitted, session_id="S001")
    assert ValidationIssueCode.EVIDENCE_OUTSIDE_GRANT in codes(result)
