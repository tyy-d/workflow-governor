from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from workflow_governor.artifacts.state import WorkflowStateLoader
from workflow_governor.artifacts.store import ArtifactStore
from workflow_governor.core.models import EvidenceContent, WorkspaceMap
from workflow_governor.core.substrate import RetrievedEvidence, WorkspaceGrant
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
    retrieved_evidence: tuple[RetrievedEvidence, ...] = ()


class WorkspaceProvider(Protocol):
    def prepare(self, objective: str) -> WorkspaceBundle: ...


class PersistableWorkspaceProvider(WorkspaceProvider, Protocol):
    @property
    def grants(self) -> tuple[WorkspaceGrant, ...]: ...


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

    def start_persisted(
        self,
        *,
        workflow_id: str,
        objective: str,
        workspace_provider: PersistableWorkspaceProvider,
        context_provider_factory: Callable[[WorkspaceBundle], TaskContextProvider],
        store: ArtifactStore,
        handoff_sink: HumanHandoffSink | None,
        approver: str,
    ) -> tuple[PlanRecord, RunState]:
        """Start the explicitly mock-assisted, durable integration path."""
        from workflow_governor.integration.adapters import (
            ArtifactExecutionEventSink,
            PersistingTaskContextProvider,
        )

        store.create_workflow(workflow_id, objective, workspace_provider.grants)
        bundle = workspace_provider.prepare(objective)
        store.save_workspace_map(workflow_id, bundle.workspace_map)
        store.save_evidence(workflow_id, bundle.retrieved_evidence)
        request = PlanningRequest(
            objective,
            bundle.workspace_map,
            bundle.targeted_evidence,
            bundle.relevant_policy,
        )
        plan = self._planner.plan(request)
        proposed = self._lifecycle.register(plan)
        approved = self._lifecycle.approve(proposed, actor=approver).current
        store.save_plan(workflow_id, approved.plan, status=approved.status)
        for task in approved.plan.tasks:
            store.save_task(workflow_id, task)
        context_provider = PersistingTaskContextProvider(
            context_provider_factory(bundle), store, workflow_id
        )
        state = RunState(workflow_id, mock_assisted=True)
        return approved, self._runner.run(
            approved,
            state,
            context_provider,
            ArtifactExecutionEventSink(store),
            handoff_sink,
        )

    def resume_persisted(
        self,
        *,
        workflow_id: str,
        store: ArtifactStore,
        context_provider: TaskContextProvider,
        handoff_sink: HumanHandoffSink | None,
    ) -> tuple[PlanRecord, RunState]:
        """Resume persisted facts without replanning, reapproval, or retries."""
        from workflow_governor.integration.adapters import (
            ArtifactExecutionEventSink,
            PersistingTaskContextProvider,
        )
        from workflow_governor.integration.resume import reconstruct_persisted_run

        snapshot = WorkflowStateLoader(store).load(workflow_id)
        if snapshot.current_plan is None:
            raise ValueError("persisted workflow has no current plan")
        approved, state = reconstruct_persisted_run(snapshot, snapshot.current_plan)
        provider = PersistingTaskContextProvider(context_provider, store, workflow_id)
        return approved, self._runner.run(
            approved,
            state,
            provider,
            ArtifactExecutionEventSink(store),
            handoff_sink,
        )
