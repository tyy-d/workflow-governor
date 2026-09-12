from __future__ import annotations

import pytest
from dataclasses import fields
from datetime import datetime, timezone

from workflow_governor.core.models import (
    ExecutionStatus,
    ExecutorType,
    PlanStatus,
    TaskContext,
    TaskResult,
    TaskSpec,
    WorkflowPlan,
)
from workflow_governor.core.persistence_json import json_text
from workflow_governor.execution.runner import (
    HumanHandoff,
    HumanResponse,
    MinimalTaskRunner,
    RunState,
    TaskExecutionState,
)
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
    state = MinimalTaskRunner({ExecutorType.DETERMINISTIC: executor}).run(
        record, RunState("W"), Contexts(), events, handoffs
    )
    assert state.task_states["fails"].status is ExecutionStatus.FAILED
    assert state.task_states["dependent"].status is ExecutionStatus.BLOCKED
    assert state.task_states["independent"].status is ExecutionStatus.COMPLETED
    assert state.task_states["human"].status is ExecutionStatus.PENDING_HUMAN
    assert executor.calls == ["fails", "independent"]
    assert handoffs.handoffs[0].authority_requirement == "Vendor Compliance activation authority"
    assert events.events


def test_runner_rejects_unapproved_plan() -> None:
    plan = WorkflowPlan("P", 1, "Execute", (spec("one"),))
    try:
        MinimalTaskRunner({}).run(PlanRecord(plan, PlanStatus.PROPOSED), RunState("W"), Contexts(), RecordingSink(), HandoffSink())
    except ValueError as exc:
        assert "approved" in str(exc)
    else:
        raise AssertionError("unapproved plan should be rejected")


@pytest.mark.parametrize(
    "status",
    [
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.BLOCKED,
        ExecutionStatus.PENDING_HUMAN,
    ],
)
def test_runner_never_redispatches_terminal_resume_states(status) -> None:
    task = spec("one")
    executor = Executor({})
    events = RecordingSink()
    state = RunState("W", {"one": TaskExecutionState("one", status=status)})
    MinimalTaskRunner({ExecutorType.DETERMINISTIC: executor}).run(
        PlanRecord(WorkflowPlan("P", 1, "Execute", (task,)), PlanStatus.APPROVED),
        state,
        Contexts(),
        events,
        HandoffSink(),
    )
    assert executor.calls == []
    assert events.events == []


def test_runner_routes_only_to_declared_executor() -> None:
    deterministic = Executor({})
    local = Executor({})
    task = spec("model", ExecutorType.LOCAL_MODEL)
    MinimalTaskRunner(
        {ExecutorType.DETERMINISTIC: deterministic, ExecutorType.LOCAL_MODEL: local}
    ).run(
        PlanRecord(WorkflowPlan("P", 1, "Execute", (task,)), PlanStatus.APPROVED),
        RunState("W"),
        Contexts(),
        RecordingSink(),
        HandoffSink(),
    )
    assert deterministic.calls == []
    assert local.calls == ["model"]


@pytest.mark.parametrize(
    "result",
    [
        TaskResult("wrong", ExecutionStatus.COMPLETED, ExecutorType.DETERMINISTIC),
        TaskResult("one", ExecutionStatus.COMPLETED, ExecutorType.LOCAL_MODEL),
        TaskResult("one", ExecutionStatus.PENDING, ExecutorType.DETERMINISTIC),
        TaskResult("one", ExecutionStatus.READY, ExecutorType.DETERMINISTIC),
        TaskResult("one", ExecutionStatus.IN_PROGRESS, ExecutorType.DETERMINISTIC),
        TaskResult("one", ExecutionStatus.PENDING_HUMAN, ExecutorType.DETERMINISTIC),
    ],
)
def test_runner_converts_invalid_executor_results_to_failure(result) -> None:
    class InvalidExecutor:
        def execute(self, task, context):
            return result

    events = RecordingSink()
    state = MinimalTaskRunner({ExecutorType.DETERMINISTIC: InvalidExecutor()}).run(
        PlanRecord(WorkflowPlan("P", 1, "Execute", (spec("one"),)), PlanStatus.APPROVED),
        RunState("W"),
        Contexts(),
        events,
        HandoffSink(),
    )
    assert state.task_states["one"].status is ExecutionStatus.FAILED
    assert "contract violation" in state.task_states["one"].result.error
    assert [event.status for event in events.events] == [
        ExecutionStatus.READY,
        ExecutionStatus.IN_PROGRESS,
        ExecutionStatus.FAILED,
    ]


def test_runner_records_executor_exception_and_continues_independent_work() -> None:
    class RaisingExecutor(Executor):
        def execute(self, task, context):
            self.calls.append(task.task_id)
            if task.task_id == "raises":
                raise RuntimeError("boom")
            return TaskResult(task.task_id, ExecutionStatus.COMPLETED, task.executor_type)

    executor = RaisingExecutor({})
    tasks = (spec("raises"), spec("dependent", dependencies=("raises",)), spec("independent"))
    state = MinimalTaskRunner({ExecutorType.DETERMINISTIC: executor}).run(
        PlanRecord(WorkflowPlan("P", 1, "Execute", tasks), PlanStatus.APPROVED),
        RunState("W"),
        Contexts(),
        RecordingSink(),
        HandoffSink(),
    )
    assert state.task_states["raises"].status is ExecutionStatus.FAILED
    assert "RuntimeError: boom" in state.task_states["raises"].result.error
    assert state.task_states["dependent"].status is ExecutionStatus.BLOCKED
    assert state.task_states["independent"].status is ExecutionStatus.COMPLETED


def test_missing_executor_is_ready_then_blocked_without_in_progress() -> None:
    events = RecordingSink()
    state = MinimalTaskRunner({}).run(
        PlanRecord(WorkflowPlan("P", 1, "Execute", (spec("one"),)), PlanStatus.APPROVED),
        RunState("W"),
        Contexts(),
        events,
        HandoffSink(),
    )
    assert state.task_states["one"].attempts == 0
    assert [event.status for event in events.events] == [ExecutionStatus.READY, ExecutionStatus.BLOCKED]


@pytest.mark.parametrize(
    "predecessor_status",
    [ExecutionStatus.FAILED, ExecutionStatus.BLOCKED, ExecutionStatus.PENDING_HUMAN],
)
def test_unsuccessful_predecessors_block_only_descendants(predecessor_status) -> None:
    executor = Executor({})
    tasks = (spec("root"), spec("dependent", dependencies=("root",)), spec("independent"))
    state = RunState("W", {"root": TaskExecutionState("root", status=predecessor_status)})
    MinimalTaskRunner({ExecutorType.DETERMINISTIC: executor}).run(
        PlanRecord(WorkflowPlan("P", 1, "Execute", tasks), PlanStatus.APPROVED),
        state,
        Contexts(),
        RecordingSink(),
        HandoffSink(),
    )
    assert state.task_states["dependent"].status is ExecutionStatus.BLOCKED
    assert state.task_states["independent"].status is ExecutionStatus.COMPLETED
    assert executor.calls == ["independent"]


def test_human_event_order_and_resume_do_not_duplicate_handoff() -> None:
    task = spec("human", ExecutorType.HUMAN, authority="authorized reviewer")
    record = PlanRecord(WorkflowPlan("P", 1, "Decide", (task,)), PlanStatus.APPROVED)
    events, handoffs = RecordingSink(), HandoffSink()
    runner = MinimalTaskRunner({})
    state = runner.run(record, RunState("W"), Contexts(), events, handoffs)
    assert [event.status for event in events.events] == [ExecutionStatus.READY, ExecutionStatus.PENDING_HUMAN]
    assert len(handoffs.handoffs) == 1
    assert handoffs.handoffs[0].workflow_id == "W"
    assert handoffs.handoffs[0].plan_id == "P"
    runner.run(record, state, Contexts(), events, handoffs)
    assert len(handoffs.handoffs) == 1


def test_human_handoff_has_only_minimal_correlation_boundary() -> None:
    assert [item.name for item in fields(HumanHandoff)] == [
        "handoff_id",
        "workflow_id",
        "plan_id",
        "plan_version",
        "task_id",
        "objective",
        "evidence_refs",
        "authority_requirement",
        "completion_criteria",
        "unresolved_questions",
        "created_at",
    ]
    task = spec("human", ExecutorType.HUMAN, authority="authorized reviewer")
    record = PlanRecord(WorkflowPlan("P", 2, "Decide", (task,)), PlanStatus.APPROVED)
    first = MinimalTaskRunner.create_handoff(
        record, "W", task, created_at=datetime(2020, 1, 1, tzinfo=timezone.utc)
    )
    second = MinimalTaskRunner.create_handoff(
        record, "W", task, created_at=datetime(2021, 1, 1, tzinfo=timezone.utc)
    )
    assert first.handoff_id == second.handoff_id
    assert first.created_at != second.created_at


@pytest.mark.parametrize("decision", ["approved", "rejected"])
def test_authorized_human_decision_completes_task_even_when_rejected(decision) -> None:
    task = spec("human", ExecutorType.HUMAN, authority="authorized reviewer")
    record = PlanRecord(WorkflowPlan("P", 1, "Decide", (task,)), PlanStatus.APPROVED)
    runner, events = MinimalTaskRunner({}), RecordingSink()
    state = runner.run(record, RunState("W"), Contexts(), events, HandoffSink())
    handoff = state.task_states["human"].human_handoff
    accepted = runner.apply_human_response(
        record,
        state,
        HumanResponse(
            handoff.handoff_id,
            "W",
            "P",
            1,
            "human",
            decision,
            True,
            rationale="Reviewed by the external authority boundary",
            output={"comment": "bounded response"},
        ),
        events,
    )
    assert accepted is True
    assert state.task_states["human"].status is ExecutionStatus.COMPLETED
    assert state.task_states["human"].result.output["decision"] == decision
    assert events.events[-1].status is ExecutionStatus.COMPLETED


@pytest.mark.parametrize(
    "variation", ["malformed", "unauthorized", "mismatched", "nondurable_output"]
)
def test_invalid_human_response_leaves_pending_state_unchanged(variation) -> None:
    task = spec("human", ExecutorType.HUMAN, authority="authorized reviewer")
    record = PlanRecord(WorkflowPlan("P", 1, "Decide", (task,)), PlanStatus.APPROVED)
    runner, events = MinimalTaskRunner({}), RecordingSink()
    state = runner.run(record, RunState("W"), Contexts(), events, HandoffSink())
    handoff = state.task_states["human"].human_handoff
    if variation == "malformed":
        response = {"decision": "approved"}
    else:
        response = HumanResponse(
            "wrong" if variation == "mismatched" else handoff.handoff_id,
            "W",
            "P",
            1,
            "human",
            "approved",
            variation != "unauthorized",
            output={"invalid": {1, 2}} if variation == "nondurable_output" else {},
        )
    count = len(events.events)
    assert runner.apply_human_response(record, state, response, events) is False
    assert state.task_states["human"].status is ExecutionStatus.PENDING_HUMAN
    assert state.task_states["human"].result is None
    assert len(events.events) == count
    assert len(events.events) == 2


def test_approved_plan_canonical_serialization_is_unchanged() -> None:
    plan = WorkflowPlan("P", 1, "Execute", (spec("one"),))
    before = json_text(plan.to_dict())
    MinimalTaskRunner({ExecutorType.DETERMINISTIC: Executor({})}).run(
        PlanRecord(plan, PlanStatus.APPROVED),
        RunState("W"),
        Contexts(),
        RecordingSink(),
        HandoffSink(),
    )
    assert json_text(plan.to_dict()) == before
