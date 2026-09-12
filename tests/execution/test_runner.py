from __future__ import annotations

from workflow_governor.core.models import (
    DecisionAuthorityScope,
    ExecutionStatus,
    ExecutorType,
    PlanStatus,
    TaskContext,
    TaskResult,
    TaskSpec,
    WorkflowPlan,
)
from workflow_governor.execution.runner import MinimalTaskRunner, RunState
from workflow_governor.planning.lifecycle import PlanRecord


class RecordingSink:
    def __init__(self):
        self.events = []

    def record(self, event):
        self.events.append(event)


class HandoffSink:
    def __init__(self):
        self.handoffs = []

    def emit(self, handoff):
        self.handoffs.append(handoff)


class Contexts:
    def get_context(self, task, run_state):
        return TaskContext(task.task_id)


class Executor:
    def __init__(self, statuses):
        self.statuses = statuses
        self.calls = []

    def execute(self, task, context):
        self.calls.append(task.task_id)
        status = self.statuses.get(task.task_id, ExecutionStatus.COMPLETED)
        return TaskResult(task.task_id, status, task.executor_type, error="attempt failed" if status is ExecutionStatus.FAILED else None)


def spec(task_id, executor=ExecutorType.DETERMINISTIC, dependencies=(), authority=None):
    return TaskSpec(
        task_id,
        task_id,
        f"Execute {task_id}",
        executor,
        dependencies=dependencies,
        completion_criteria=("Return a result",),
        authority_requirement=authority,
        requested_decision_authority_scope=(
            DecisionAuthorityScope.AUTHORITY_DECISION if authority else DecisionAuthorityScope.NO_DECISION
        ),
        operation="structured_equal" if executor is ExecutorType.DETERMINISTIC else None,
    )


def test_runner_continues_independent_work_and_preserves_states() -> None:
    tasks = (
        spec("fails"),
        spec("dependent", dependencies=("fails",)),
        spec("independent"),
        spec("human", ExecutorType.HUMAN, authority="Vendor Compliance activation authority"),
    )
    plan = WorkflowPlan("P", 1, "Execute bounded work", tasks)
    record = PlanRecord(plan, PlanStatus.APPROVED)
    executor = Executor({"fails": ExecutionStatus.FAILED})
    events, handoffs = RecordingSink(), HandoffSink()
    state = MinimalTaskRunner(
        {ExecutorType.DETERMINISTIC: executor},
        handoff_id_factory=lambda: "H-001",
    ).run(
        record, RunState("W"), Contexts(), events, handoffs
    )
    assert state.task_states["fails"].status is ExecutionStatus.FAILED
    assert state.task_states["dependent"].status is ExecutionStatus.BLOCKED
    assert state.task_states["independent"].status is ExecutionStatus.COMPLETED
    assert state.task_states["human"].status is ExecutionStatus.PENDING_HUMAN
    assert executor.calls == ["fails", "independent"]
    assert handoffs.handoffs[0].authority_requirement == "Vendor Compliance activation authority"
    assert handoffs.handoffs[0].handoff_id == "H-001"
    assert handoffs.handoffs[0].requested_decision_authority_scope is DecisionAuthorityScope.AUTHORITY_DECISION
    assert events.events


def test_runner_rejects_unapproved_plan() -> None:
    plan = WorkflowPlan("P", 1, "Execute", (spec("one"),))
    try:
        MinimalTaskRunner({}).run(PlanRecord(plan, PlanStatus.PROPOSED), RunState("W"), Contexts(), RecordingSink(), HandoffSink())
    except ValueError as exc:
        assert "approved" in str(exc)
    else:
        raise AssertionError("unapproved plan should be rejected")
