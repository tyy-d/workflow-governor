from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol

from workflow_governor.core.errors import ContractValidationError
from workflow_governor.core.models import (
    EvidenceRef,
    ExecutionStatus,
    ExecutorType,
    PlanStatus,
    TaskContext,
    TaskResult,
    TaskSpec,
)
from workflow_governor.core.persistence_json import json_text
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
    completion_criteria: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    created_at: datetime


@dataclass(frozen=True, slots=True)
class HumanResponse:
    handoff_id: str
    workflow_id: str
    plan_id: str
    plan_version: int
    task_id: str
    decision: str
    authority_verified: bool
    rationale: str | None = None
    output: Mapping[str, Any] = field(default_factory=dict)


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
    _EXECUTOR_TERMINAL = {
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.BLOCKED,
    }

    def __init__(self, executors: Mapping[ExecutorType, TaskExecutor]) -> None:
        self._executors = dict(executors)

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
        serialized_plan = json_text(plan.to_dict())
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
                    handoff = self.create_handoff(plan_record, run_state.workflow_id, task)
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
                context = context_provider.get_context(task, run_state)
                self._transition(run_state, state, ExecutionStatus.IN_PROGRESS, event_sink)
                state.attempts += 1
                state.started_at = state.started_at or datetime.now(timezone.utc)
                try:
                    result = executor.execute(task, context)
                    result = self._validated_result(task, result)
                except Exception as exc:
                    result = self._failed_result(task, f"executor raised {type(exc).__name__}: {exc}")
                state.result = result
                state.error = result.error
                state.finished_at = datetime.now(timezone.utc)
                self._transition(run_state, state, result.status, event_sink, result=result)
                progress = True
        if json_text(plan.to_dict()) != serialized_plan:
            raise RuntimeError("approved plan changed during execution")
        return run_state

    @staticmethod
    def handoff_id(workflow_id: str, plan_id: str, plan_version: int, task_id: str) -> str:
        correlation = f"{workflow_id}\0{plan_id}\0{plan_version}\0{task_id}".encode("utf-8")
        return f"handoff-{hashlib.sha256(correlation).hexdigest()[:32]}"

    @classmethod
    def create_handoff(
        cls,
        plan_record: PlanRecord,
        workflow_id: str,
        task: TaskSpec,
        *,
        created_at: datetime | None = None,
    ) -> HumanHandoff:
        plan = plan_record.plan
        return HumanHandoff(
            cls.handoff_id(workflow_id, plan.plan_id, plan.version, task.task_id),
            workflow_id,
            plan.plan_id,
            plan.version,
            task.task_id,
            task.objective,
            task.evidence_requirements + task.policy_requirements,
            task.authority_requirement,
            task.completion_criteria,
            plan.unresolved_questions,
            created_at or datetime.now(timezone.utc),
        )

    def apply_human_response(
        self,
        plan_record: PlanRecord,
        run_state: RunState,
        response: HumanResponse | object,
        event_sink: ExecutionEventSink,
    ) -> bool:
        """Apply only a correlated, externally authorized response.

        Authentication and authority verification are deliberately outside this
        boundary. Invalid input leaves the pending task unchanged.
        """
        if plan_record.status is not PlanStatus.APPROVED or not isinstance(response, HumanResponse):
            return False
        task = next((item for item in plan_record.plan.tasks if item.task_id == response.task_id), None)
        if task is None or task.executor_type is not ExecutorType.HUMAN:
            return False
        state = run_state.task_states.get(task.task_id)
        if state is None or state.status is not ExecutionStatus.PENDING_HUMAN:
            return False
        expected = self.create_handoff(plan_record, run_state.workflow_id, task)
        correlations_match = (
            response.handoff_id == expected.handoff_id
            and response.workflow_id == expected.workflow_id
            and response.plan_id == expected.plan_id
            and response.plan_version == expected.plan_version
            and response.task_id == expected.task_id
        )
        if (
            not correlations_match
            or response.authority_verified is not True
            or not isinstance(response.decision, str)
            or not response.decision.strip()
            or (response.rationale is not None and not isinstance(response.rationale, str))
            or not isinstance(response.output, Mapping)
        ):
            return False
        try:
            result = TaskResult(
                task.task_id,
                ExecutionStatus.COMPLETED,
                ExecutorType.HUMAN,
                evidence_refs=expected.evidence_refs,
                rationale=response.rationale,
                output={"decision": response.decision, "response": dict(response.output)},
            )
            result.to_dict()
        except (ContractValidationError, TypeError, ValueError):
            return False
        state.result = result
        state.error = None
        state.finished_at = datetime.now(timezone.utc)
        state.human_handoff = state.human_handoff or expected
        self._transition(run_state, state, ExecutionStatus.COMPLETED, event_sink, result=result)
        return True

    @classmethod
    def _validated_result(cls, task: TaskSpec, result: object) -> TaskResult:
        if not isinstance(result, TaskResult):
            return cls._failed_result(task, "executor contract violation: expected TaskResult")
        violations = []
        if result.task_id != task.task_id:
            violations.append("task ID mismatch")
        if result.executor_type is not task.executor_type:
            violations.append("executor type mismatch")
        if result.status not in cls._EXECUTOR_TERMINAL:
            violations.append(f"invalid terminal status {result.status}")
        if violations:
            return cls._failed_result(task, f"executor contract violation: {', '.join(violations)}")
        return result

    @staticmethod
    def _failed_result(task: TaskSpec, error: str) -> TaskResult:
        return TaskResult(
            task.task_id,
            ExecutionStatus.FAILED,
            task.executor_type,
            evidence_refs=task.evidence_requirements + task.policy_requirements,
            error=error,
        )

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
