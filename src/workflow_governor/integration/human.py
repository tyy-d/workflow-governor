"""Track B-owned application of already validated Track C response facts."""

from __future__ import annotations

from datetime import datetime, timezone

from workflow_governor.core.errors import ContractValidationError
from workflow_governor.core.models import ExecutionStatus, ExecutorType, PlanStatus, TaskResult
from workflow_governor.core.serialization import to_primitive
from workflow_governor.execution.runner import ExecutionEvent, ExecutionEventSink, MinimalTaskRunner, RunState
from workflow_governor.human.contracts import ResponseDisposition, ResponseValidationResult, ValidationStatus
from workflow_governor.planning.lifecycle import PlanRecord


def apply_validated_human_response(
    runner: MinimalTaskRunner,
    plan_record: PlanRecord,
    run_state: RunState,
    validation: ResponseValidationResult,
    event_sink: ExecutionEventSink,
) -> bool:
    """Apply only an accepted, complete, fully correlated human response."""

    response = validation.response
    if validation.status is not ValidationStatus.ACCEPTED or response is None:
        return False
    if response.response_disposition is not ResponseDisposition.COMPLETE:
        return False
    if plan_record.status is not PlanStatus.APPROVED:
        return False
    task = next((item for item in plan_record.plan.tasks if item.task_id == response.task_id), None)
    if task is None or task.executor_type is not ExecutorType.HUMAN:
        return False
    state = run_state.task_states.get(task.task_id)
    if state is None or state.status is not ExecutionStatus.PENDING_HUMAN:
        return False
    expected = state.human_handoff or runner.create_handoff(plan_record, run_state.workflow_id, task)
    if any(
        (
            response.handoff_id != expected.handoff_id,
            response.workflow_id != expected.workflow_id,
            response.plan_id != expected.plan_id,
            response.plan_version != expected.plan_version,
            response.task_id != expected.task_id,
        )
    ):
        return False
    try:
        result = TaskResult(
            task.task_id,
            ExecutionStatus.COMPLETED,
            ExecutorType.HUMAN,
            evidence_refs=response.evidence_refs,
            unresolved=response.unresolved_questions,
            rationale=response.rationale,
            output={
                "response_id": response.response_id,
                "response_disposition": response.response_disposition.value,
                "decision": to_primitive(response.decision),
                "authority_validation": to_primitive(response.authority_validation),
                "corrections": to_primitive(response.corrections),
            },
        )
        result.to_dict()
    except (ContractValidationError, TypeError, ValueError):
        return False

    timestamp = datetime.now(timezone.utc)
    event_sink.record(ExecutionEvent(run_state.workflow_id, task.task_id, ExecutionStatus.COMPLETED, timestamp, result))
    state.result = result
    state.error = None
    state.finished_at = timestamp
    state.human_handoff = state.human_handoff or expected
    state.status = ExecutionStatus.COMPLETED
    return True


__all__ = ["apply_validated_human_response"]
