from __future__ import annotations

from dataclasses import replace

import pytest

from workflow_governor.core.models import DecisionAuthorityScope, ExecutionStatus, ExecutorType, PlanStatus, TaskContext, TaskSpec, WorkflowPlan
from workflow_governor.execution.runner import MinimalTaskRunner, RunState
from workflow_governor.human.contracts import AuthorityStatus, AuthorityValidation, HumanTaskResponse, ResponseDisposition, ResponseValidationResult
from workflow_governor.integration.human import apply_validated_human_response
from workflow_governor.planning.lifecycle import PlanRecord


class Contexts:
    def get_context(self, task, run_state):
        return TaskContext(task.task_id)


class Events:
    def __init__(self):
        self.items = []

    def record(self, event):
        self.items.append(event)


def setup_pending():
    task = TaskSpec(
        "human",
        "Review",
        "Return an authorized decision",
        ExecutorType.HUMAN,
        completion_criteria=("Return a decision",),
        authority_requirement="authorized reviewer",
        requested_decision_authority_scope=DecisionAuthorityScope.AUTHORITY_DECISION,
    )
    record = PlanRecord(WorkflowPlan("P", 1, "Decide", (task,)), PlanStatus.APPROVED)
    events = Events()
    runner = MinimalTaskRunner({}, clock=lambda: "2026-09-12T14:00:00+00:00")
    state = runner.run(record, RunState("W"), Contexts(), events, None)
    return runner, record, state, events, state.task_states["human"].human_handoff


def response(handoff, disposition=ResponseDisposition.COMPLETE):
    scope = DecisionAuthorityScope.AUTHORITY_DECISION if disposition is ResponseDisposition.COMPLETE else DecisionAuthorityScope.NO_DECISION
    unresolved = () if disposition is ResponseDisposition.COMPLETE else ("Protected decision remains unresolved.",)
    return HumanTaskResponse(
        response_id="R001",
        handoff_id=handoff.handoff_id,
        workflow_id=handoff.workflow_id,
        plan_id=handoff.plan_id,
        plan_version=handoff.plan_version,
        task_id=handoff.task_id,
        actor_id="P001",
        response_disposition=disposition,
        actual_decision_authority_scope=scope,
        authority_validation=AuthorityValidation(AuthorityStatus.SATISFIED, "authorized reviewer"),
        decision={"outcome": "REJECTED" if disposition is ResponseDisposition.COMPLETE else "NO_DECISION"},
        rationale="Bounded review returned.",
        unresolved_questions=unresolved,
        submitted_at="2026-09-12T14:01:00+00:00",
    )


def test_completed_business_rejection_completes_human_task() -> None:
    runner, record, state, events, handoff = setup_pending()
    accepted = apply_validated_human_response(
        runner, record, state, ResponseValidationResult.accepted(response(handoff)), events
    )
    assert accepted is True
    assert state.task_states["human"].status is ExecutionStatus.COMPLETED
    assert state.task_states["human"].result.output["decision"]["outcome"] == "REJECTED"


@pytest.mark.parametrize("disposition", [
    ResponseDisposition.NEEDS_INFORMATION,
    ResponseDisposition.PARTIAL,
    ResponseDisposition.TASK_NARROWED,
    ResponseDisposition.REASSIGNMENT_REQUESTED,
    ResponseDisposition.AUTHORITY_DECLINED,
])
def test_noncomplete_validated_responses_remain_pending(disposition) -> None:
    runner, record, state, events, handoff = setup_pending()
    assert apply_validated_human_response(
        runner, record, state, ResponseValidationResult.accepted(response(handoff, disposition)), events
    ) is False
    assert state.task_states["human"].status is ExecutionStatus.PENDING_HUMAN


@pytest.mark.parametrize("field,value", [("handoff_id", "OTHER"), ("plan_id", "OTHER"), ("plan_version", 2)])
def test_correlation_mismatch_remains_pending(field, value) -> None:
    runner, record, state, events, handoff = setup_pending()
    validation = ResponseValidationResult.accepted(replace(response(handoff), **{field: value}))
    assert apply_validated_human_response(runner, record, state, validation, events) is False
    assert state.task_states["human"].status is ExecutionStatus.PENDING_HUMAN


def test_persistence_failure_does_not_mutate_in_memory_state() -> None:
    runner, record, state, _, handoff = setup_pending()

    class FailingEvents:
        def record(self, event):
            raise OSError("persistence unavailable")

    with pytest.raises(OSError, match="persistence unavailable"):
        apply_validated_human_response(
            runner, record, state, ResponseValidationResult.accepted(response(handoff)), FailingEvents()
        )
    assert state.task_states["human"].status is ExecutionStatus.PENDING_HUMAN
