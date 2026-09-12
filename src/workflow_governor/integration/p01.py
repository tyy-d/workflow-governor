from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from workflow_governor.core.models import EvidenceContent, WorkspaceMap
from workflow_governor.execution.runner import (
    ExecutionEventSink,
    HumanHandoffSink,
    MinimalTaskRunner,
    RunState,
    TaskContextProvider,
)
from workflow_governor.planning.lifecycle import PlanLifecycle, PlanRecord
from workflow_governor.planning.planner import Planner, PlanningRequest


@dataclass(frozen=True, slots=True)
class WorkspaceBundle:
    workspace_map: WorkspaceMap
    targeted_evidence: tuple[EvidenceContent, ...]
    relevant_policy: tuple[EvidenceContent, ...]


class WorkspaceProvider(Protocol):
    def prepare(self, objective: str) -> WorkspaceBundle: ...


class P01Coordinator:
    """Thin composition boundary; it contains no case-specific business logic."""

    def __init__(
        self,
        *,
        planner: Planner,
        lifecycle: PlanLifecycle,
        runner: MinimalTaskRunner,
    ) -> None:
        self._planner = planner
        self._lifecycle = lifecycle
        self._runner = runner

    def run(
        self,
        *,
        workflow_id: str,
        objective: str,
        workspace_provider: WorkspaceProvider,
        context_provider: TaskContextProvider,
        event_sink: ExecutionEventSink,
        handoff_sink: HumanHandoffSink | None,
        approver: str,
        mock_assisted: bool = True,
    ) -> tuple[PlanRecord, RunState]:
        bundle = workspace_provider.prepare(objective)
        request = PlanningRequest(
            objective,
            bundle.workspace_map,
            bundle.targeted_evidence,
            bundle.relevant_policy,
        )
        plan = self._planner.plan(request)
        proposed = self._lifecycle.register(plan)
        history = self._lifecycle.approve(proposed, actor=approver)
        approved = history.current
        state = RunState(workflow_id, mock_assisted=mock_assisted)
        return approved, self._runner.run(
            approved, state, context_provider, event_sink, handoff_sink
        )
