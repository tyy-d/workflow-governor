from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from workflow_governor.core.models import EvidenceContent, WorkflowPlan, WorkspaceMap
from workflow_governor.planning.validation import PlanValidator


@dataclass(frozen=True, slots=True)
class PlanningRequest:
    objective: str
    workspace_map: WorkspaceMap
    targeted_evidence: tuple[EvidenceContent, ...] = ()
    relevant_policy: tuple[EvidenceContent, ...] = ()
    prior_plan_id: str | None = None


class PlannerBackend(Protocol):
    def create_plan(self, request: PlanningRequest) -> WorkflowPlan: ...


class Planner:
    def __init__(self, backend: PlannerBackend, validator: PlanValidator) -> None:
        self._backend = backend
        self._validator = validator

    def plan(self, request: PlanningRequest) -> WorkflowPlan:
        if not request.objective.strip():
            raise ValueError("planning objective must not be empty")
        plan = self._backend.create_plan(request)
        if plan.objective.strip() != request.objective.strip():
            raise ValueError("planner changed the requested objective")
        self._validator.validate(plan).require_valid()
        return plan

