from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping, Protocol
from uuid import uuid4

from workflow_governor.core.models import (
    EvidenceRef,
    DecisionAuthorityScope,
    ExecutionStatus,
    ExecutorType,
    PlanStatus,
    TaskContext,
    TaskResult,
    TaskSpec,
)
from workflow_governor.planning.lifecycle import PlanRecord


@dataclass(slots=True)
class TaskExecutionState:
    task_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    attempts: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    result: TaskResult | None = None
    error: str | None = None
    human_handoff: "HumanHandoff | None" = None


@dataclass(slots=True)
class RunState:
    workflow_id: str
    task_states: dict[str, TaskExecutionState] = field(default_factory=dict)
    mock_assisted: bool = False


@dataclass(frozen=True, slots=True)
class ExecutionEvent:
    workflow_id: str
    task_id: str
    status: ExecutionStatus
    timestamp: datetime
    result: TaskResult | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class HumanHandoff:
    handoff_id: str
    workflow_id: str
    plan_id: str
    plan_version: int
    task_id: str
    objective: str
    evidence_refs: tuple[EvidenceRef, ...]
    authority_requirement: str | None
    requested_decision_authority_scope: DecisionAuthorityScope
    completion_criteria: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    created_at: str


class ExecutionEventSink(Protocol):
    def record(self, event: ExecutionEvent) -> None: ...


class HumanHandoffSink(Protocol):
    def emit(self, handoff: HumanHandoff) -> None: ...


class TaskContextProvider(Protocol):
    def get_context(self, task: TaskSpec, run_state: RunState) -> TaskContext: ...


class TaskExecutor(Protocol):
    def execute(self, task: TaskSpec, context: TaskContext) -> TaskResult: ...


class MinimalTaskRunner:
    _TERMINAL = {
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.BLOCKED,
        ExecutionStatus.PENDING_HUMAN,
    }

    def __init__(
        self,
        executors: Mapping[ExecutorType, TaskExecutor],
        *,
        handoff_id_factory=None,
        clock=None,
    ) -> None:
        self._executors = dict(executors)
        self._handoff_id_factory = handoff_id_factory or (lambda: f"H-{uuid4()}")
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def run(
        self,
        plan_record: PlanRecord,
        run_state: RunState,
        context_provider: TaskContextProvider,
        event_sink: ExecutionEventSink,
        handoff_sink: HumanHandoffSink | None,
    ) -> RunState:
        if plan_record.status is not PlanStatus.APPROVED:
            raise ValueError("minimal task runner requires an approved plan")
        plan = plan_record.plan
        states = run_state.task_states
        for task in plan.tasks:
            states.setdefault(task.task_id, TaskExecutionState(task.task_id))

        progress = True
        while progress:
            progress = False
            for task in plan.tasks:
                state = states[task.task_id]
                if state.status in self._TERMINAL or state.status is ExecutionStatus.IN_PROGRESS:
                    continue
                dependency_states = [states[dependency].status for dependency in task.dependencies]
                if any(status in {ExecutionStatus.FAILED, ExecutionStatus.BLOCKED, ExecutionStatus.PENDING_HUMAN} for status in dependency_states):
                    self._finish_blocked(run_state, task, state, event_sink, "required predecessor did not complete")
                    progress = True
                    continue
                if not all(status is ExecutionStatus.COMPLETED for status in dependency_states):
                    continue
                self._transition(run_state, state, ExecutionStatus.READY, event_sink)
                if task.executor_type is ExecutorType.HUMAN:
                    handoff = HumanHandoff(
                        handoff_id=self._handoff_id_factory(),
                        workflow_id=run_state.workflow_id,
                        plan_id=plan.plan_id,
                        plan_version=plan.version,
                        task_id=task.task_id,
                        objective=task.objective,
                        evidence_refs=task.evidence_requirements + task.policy_requirements,
                        authority_requirement=task.authority_requirement,
                        requested_decision_authority_scope=task.requested_decision_authority_scope,
                        completion_criteria=task.completion_criteria,
                        unresolved_questions=plan.unresolved_questions,
                        created_at=self._clock().isoformat(),
                    )
                    state.human_handoff = handoff
                    if handoff_sink is not None:
                        handoff_sink.emit(handoff)
                    self._transition(run_state, state, ExecutionStatus.PENDING_HUMAN, event_sink)
                    progress = True
                    continue
                executor = self._executors.get(task.executor_type)
                if executor is None:
                    self._finish_blocked(run_state, task, state, event_sink, f"executor unavailable: {task.executor_type}")
                    progress = True
                    continue
                self._transition(run_state, state, ExecutionStatus.IN_PROGRESS, event_sink)
                state.attempts += 1
                state.started_at = state.started_at or datetime.now(timezone.utc)
                result = executor.execute(task, context_provider.get_context(task, run_state))
                state.result = result
                state.error = result.error
                state.finished_at = datetime.now(timezone.utc)
                self._transition(run_state, state, result.status, event_sink, result=result)
                progress = True
        return run_state

    @staticmethod
    def _transition(
        run_state: RunState,
        state: TaskExecutionState,
        status: ExecutionStatus,
        event_sink: ExecutionEventSink,
        *,
        result: TaskResult | None = None,
        message: str | None = None,
    ) -> None:
        state.status = status
        event_sink.record(
            ExecutionEvent(run_state.workflow_id, state.task_id, status, datetime.now(timezone.utc), result, message)
        )

    def _finish_blocked(
        self,
        run_state: RunState,
        task: TaskSpec,
        state: TaskExecutionState,
        event_sink: ExecutionEventSink,
        message: str,
    ) -> None:
        state.finished_at = datetime.now(timezone.utc)
        state.result = TaskResult(
            state.task_id,
            ExecutionStatus.BLOCKED,
            task.executor_type,
            unresolved=(message,),
        )
        self._transition(run_state, state, ExecutionStatus.BLOCKED, event_sink, result=state.result, message=message)
