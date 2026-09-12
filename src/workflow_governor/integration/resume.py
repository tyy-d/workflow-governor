from __future__ import annotations

from workflow_governor.artifacts.state import WorkflowSnapshot
from workflow_governor.artifacts.store import StoredPlan
from workflow_governor.core.errors import ContractValidationError
from workflow_governor.core.models import ExecutionStatus, ExecutorType, PlanStatus
from workflow_governor.execution.runner import RunState, TaskExecutionState
from workflow_governor.planning.lifecycle import PlanRecord


_NON_RESUMABLE = {ExecutionStatus.READY, ExecutionStatus.IN_PROGRESS}


def reconstruct_persisted_run(
    snapshot: WorkflowSnapshot,
    stored_plan: StoredPlan,
) -> tuple[PlanRecord, RunState]:
    """Map persisted facts to runtime state without scheduling or recovery policy."""
    if snapshot.current_plan is None or snapshot.current_plan != stored_plan:
        raise ContractValidationError("Resume requires the current persisted plan")
    if stored_plan.status is not PlanStatus.APPROVED:
        raise ContractValidationError("Resume requires an approved current plan")
    plan = stored_plan.plan
    plan_tasks = {task.task_id: task for task in plan.tasks}
    if len(plan_tasks) != len(plan.tasks):
        raise ContractValidationError("Approved plan contains duplicate task IDs")

    buckets = {
        "task definition": snapshot.tasks,
        "status": snapshot.statuses,
        "context": snapshot.contexts,
        "result": snapshot.results,
    }
    for name, bucket in buckets.items():
        foreign = set(bucket) - set(plan_tasks)
        if foreign:
            raise ContractValidationError(
                f"Persisted {name} references unknown approved-plan tasks: {', '.join(sorted(foreign))}"
            )
    if set(snapshot.tasks) != set(plan_tasks):
        missing = set(plan_tasks) - set(snapshot.tasks)
        raise ContractValidationError(
            f"Approved plan task definitions are missing: {', '.join(sorted(missing))}"
        )
    for task_id, task in plan_tasks.items():
        if snapshot.tasks[task_id] != task:
            raise ContractValidationError(f"Persisted task definition differs from approved plan: {task_id}")
    errors = [
        item.code
        for item in snapshot.diagnostics
        if item.severity in {"error", "fatal"}
    ]
    if errors:
        raise ContractValidationError(
            f"Persisted workflow contains unresolved diagnostics: {', '.join(errors)}"
        )

    states: dict[str, TaskExecutionState] = {}
    for task_id, task in plan_tasks.items():
        raw_status = snapshot.statuses.get(task_id)
        try:
            status = ExecutionStatus.PENDING if raw_status is None else ExecutionStatus(raw_status)
        except (TypeError, ValueError) as exc:
            raise ContractValidationError(f"Unknown persisted execution status for {task_id}") from exc
        if status in _NON_RESUMABLE:
            raise ContractValidationError(
                f"Task {task_id} has non-resumable checkpoint state {status.value}"
            )
        result = snapshot.results.get(task_id)
        if result is not None:
            if result.task_id != task_id:
                raise ContractValidationError(f"Persisted result identity mismatch for {task_id}")
            if result.executor_type is not task.executor_type:
                raise ContractValidationError(f"Persisted result executor mismatch for {task_id}")
            if result.status is not status:
                raise ContractValidationError(f"Persisted status/result conflict for {task_id}")
        elif status is ExecutionStatus.COMPLETED:
            # WorkflowStateLoader and ArtifactStore require completed work to
            # retain its result; FAILED/BLOCKED may be status-only checkpoints.
            raise ContractValidationError(f"Completed task {task_id} is missing its persisted result")
        if status in {ExecutionStatus.PENDING, ExecutionStatus.PENDING_HUMAN} and result is not None:
            raise ContractValidationError(f"Non-result state {status.value} has a persisted result for {task_id}")
        if status is ExecutionStatus.PENDING_HUMAN and task.executor_type is not ExecutorType.HUMAN:
            raise ContractValidationError(f"Non-human task {task_id} is persisted as PENDING_HUMAN")
        states[task_id] = TaskExecutionState(
            task_id,
            status=status,
            result=result,
            error=result.error if result is not None else None,
        )

    return PlanRecord(plan, PlanStatus.APPROVED), RunState(
        snapshot.manifest.workflow_id,
        states,
        mock_assisted=True,
    )
