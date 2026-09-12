"""Semantic integration checks for the quiet workbench and Track C boundary."""

import time
from unittest.mock import patch

import pytest

from governor.service import Service
from governor.store import Store
from governor.workspace import Workspace
from workflow_governor.core.models import DecisionAuthorityScope
from workflow_governor.human.contracts import AuthorityStatus, AuthorityValidation
from workflow_governor.human.interaction import FileHumanInteractionStore
from workflow_governor.human.validation import BoundIdentityProvider, HumanResponseValidator


class NoAuthorityRequired:
    def validate(self, actor_id, requirement):
        return AuthorityValidation(AuthorityStatus.NOT_REQUIRED, requirement)


def settle(service, workflow_id):
    for _ in range(200):
        workflow = service.store.read(workflow_id)
        if not workflow.get("operation"):
            return workflow
        time.sleep(.01)
    raise AssertionError("background operation did not finish")


def prepared_service(tmp_path, *, binding="actor-1"):
    (tmp_path / "workspace").mkdir()
    (tmp_path / "workspace" / "status.json").write_text('{"status":"Pending"}', encoding="utf-8")
    grants = {"selected": {"root": "workspace", "label": "Selected workspace", "policies": []}}
    store = Store(tmp_path / "runtime" / "workflows", tmp_path, grants)
    validator = HumanResponseValidator(BoundIdentityProvider({"session-1": binding}), NoAuthorityRequired())
    service = Service(
        store,
        Workspace(tmp_path, grants),
        human_validator=validator,
        human_interactions=FileHumanInteractionStore(tmp_path / "runtime"),
    )
    source_id = service.workspace.inventory("selected")[0]["id"]
    workflow = service.create({"workspace": "selected", "objective": "Review selected evidence", "sourceIds": [source_id]})
    tasks = [
        {"id": "T1", "title": "Human review", "objective": "Make a bounded recommendation", "executor": "Human", "dependencyIds": [], "evidenceIds": [source_id], "rationale": "Judgment required", "expectedOutput": "A bounded decision", "authorityRequirement": None, "requestedDecisionAuthorityScope": "ANALYSIS_OR_RECOMMENDATION"},
        {"id": "T2", "title": "Extract facts", "objective": "Inspect the selected record", "executor": "Deterministic", "dependencyIds": ["T1"], "evidenceIds": [source_id], "rationale": "Structured record", "expectedOutput": "Facts", "authorityRequirement": None, "requestedDecisionAuthorityScope": "NO_DECISION"},
        {"id": "T3", "title": "Synthesize", "objective": "Synthesize the results", "executor": "Local AI", "dependencyIds": ["T1", "T2"], "evidenceIds": [source_id], "rationale": "Synthesis", "expectedOutput": "Summary", "authorityRequirement": None, "requestedDecisionAuthorityScope": "NO_DECISION"},
    ]
    with patch("governor.compact_plan.generate", return_value={"tasks": tasks, "assumptions": [], "questions": []}):
        service.plan(workflow["id"])
        workflow = settle(service, workflow["id"])
    service.approve(workflow["id"])
    return service, service.store.read(workflow["id"])


def response(handoff, *, actor="actor-1", response_id="R-1"):
    return {
        "response_id": response_id,
        "handoff_id": handoff.handoff_id,
        "workflow_id": handoff.workflow_id,
        "plan_id": handoff.plan_id,
        "plan_version": handoff.plan_version,
        "task_id": handoff.task_id,
        "actor_id": actor,
        "response_disposition": "COMPLETE",
        "actual_decision_authority_scope": DecisionAuthorityScope.ANALYSIS_OR_RECOMMENDATION.value,
        "authority_validation": {"status": "NOT_REQUIRED", "declared_requirement": None, "basis_refs": [], "reason": None},
        "decision": {"outcome": "REJECTED"},
        "rationale": "The reviewed evidence does not support proceeding.",
        "evidence_refs": [],
        "corrections": [],
        "unresolved_questions": [],
        "submitted_at": "2026-09-12T12:00:00+00:00",
    }


def test_canonical_handoff_is_deterministic_and_persisted(tmp_path):
    service, workflow = prepared_service(tmp_path)
    first = service.human_handoff(workflow["id"], "T1")
    second = service.human_handoff(workflow["id"], "T1")
    assert first == second
    assert first.requested_decision_authority_scope is DecisionAuthorityScope.ANALYSIS_OR_RECOMMENDATION
    assert (tmp_path / "runtime" / "workflows" / workflow["id"] / "artifacts" / "human" / first.handoff_id / "handoff.json").is_file()


def test_validated_business_rejection_completes_execution_task(tmp_path):
    service, workflow = prepared_service(tmp_path)
    handoff = service.human_handoff(workflow["id"], "T1")
    updated = service.human(workflow["id"], "T1", response(handoff), session_id="session-1")
    task = updated["tasks"][0]
    assert task["status"] == "Completed"
    assert task["humanState"] == "COMPLETE"
    assert service.store.loader.load(workflow["id"], strict=True).results["T1"].output["decision"]["outcome"] == "REJECTED"


def test_unbound_responder_cannot_change_pending_human_state(tmp_path):
    service, workflow = prepared_service(tmp_path)
    handoff = service.human_handoff(workflow["id"], "T1")
    unchanged = service.human(workflow["id"], "T1", response(handoff, actor="other", response_id="R-2"), session_id="session-1")
    assert unchanged["tasks"][0]["status"] == "Needs Human"
    assert "T1" not in service.store.loader.load(workflow["id"]).results


def test_persisted_handoff_must_still_match_approved_plan(tmp_path):
    service, workflow = prepared_service(tmp_path)
    service.human_handoff(workflow["id"], "T1")
    workflow = service.store.read(workflow["id"])
    workflow["tasks"][0]["humanHandoff"]["plan_id"] = "tampered-plan"
    service.store.save(workflow)
    try:
        service.human_handoff(workflow["id"], "T1")
    except ValueError as exc:
        assert "does not match the approved plan" in str(exc)
    else:
        raise AssertionError("tampered handoff was accepted")


def test_tampered_persisted_handoff_is_rejected(tmp_path):
    service, workflow = prepared_service(tmp_path)
    workflow["tasks"][0]["humanHandoff"]["plan_id"] = "OTHER"
    service.store.save(workflow)
    with pytest.raises(ValueError, match="does not match the approved plan"):
        service.human_handoff(workflow["id"], "T1")
