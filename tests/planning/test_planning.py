from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from workflow_governor.core.models import (
    EvidenceRef,
    ExecutorType,
    PlanStatus,
    TaskSpec,
    WorkflowPlan,
)
from workflow_governor.core.serialization import to_json
from workflow_governor.planning.lifecycle import PlanLifecycle
from workflow_governor.planning.validation import PlanValidator


def task(task_id: str, *, dependencies: tuple[str, ...] = (), source: str = "workspace/a.json") -> TaskSpec:
    return TaskSpec(
        task_id,
        "Check evidence",
        "Check the provided evidence",
        ExecutorType.DETERMINISTIC,
        dependencies=dependencies,
        evidence_requirements=(EvidenceRef(source),),
        completion_criteria=("Return a cited result",),
        operation="structured_equal",
    )


def plan(*tasks: TaskSpec, version: int = 1) -> WorkflowPlan:
    return WorkflowPlan("PLAN-1", version, "Review the authorized workspace", tuple(tasks))


def test_task_spec_has_no_runtime_status() -> None:
    assert "status" not in TaskSpec.__dataclass_fields__


def test_validator_accepts_minimal_acyclic_plan() -> None:
    candidate = plan(task("A"), task("B", dependencies=("A",)))
    result = PlanValidator(
        allowed_evidence_sources={"workspace/a.json"},
        supported_operations={"structured_equal"},
    ).validate(candidate)
    assert result.valid


@pytest.mark.parametrize(
    "candidate,code",
    [
        (plan(task("A"), task("A")), "DUPLICATE_TASK_ID"),
        (plan(task("A", dependencies=("MISSING",))), "UNKNOWN_DEPENDENCY"),
        (plan(task("A", dependencies=("B",)), task("B", dependencies=("A",))), "DEPENDENCY_CYCLE"),
        (plan(replace(task("A"), completion_criteria=())), "MISSING_COMPLETION_CRITERIA"),
        (plan(task("A", source="cases/X/ground_truth/a.json")), "FORBIDDEN_SOURCE"),
    ],
)
def test_validator_rejects_invalid_plans(candidate: WorkflowPlan, code: str) -> None:
    result = PlanValidator().validate(candidate)
    assert code in {issue.code for issue in result.issues}


def test_lifecycle_preserves_immutable_plan_contents() -> None:
    clock = lambda: datetime(2026, 9, 12, tzinfo=timezone.utc)
    lifecycle = PlanLifecycle(clock)
    original = plan(task("A"))
    original_json = to_json(original)
    proposed = lifecycle.register(original)
    history = lifecycle.approve(proposed, actor="reviewer")
    assert history.current.status is PlanStatus.APPROVED
    assert to_json(history.current.plan) == original_json

    history = lifecycle.request_revision(
        history,
        reason="new authorized evidence",
        evidence_refs=(EvidenceRef("workspace/new.json"),),
        requester="coordinator",
    )
    assert history.current.status is PlanStatus.REVISION_REQUESTED
    assert to_json(history.current.plan) == original_json
    assert len(history.transitions) == 2

    replacement = replace(original, version=2, assumptions=("new evidence reviewed",))
    history = lifecycle.approve_replacement(history, replacement, actor="reviewer")
    assert [record.status for record in history.records] == [PlanStatus.SUPERSEDED, PlanStatus.APPROVED]
    assert to_json(history.records[0].plan) == original_json


def test_revision_can_be_cancelled_without_changing_plan() -> None:
    lifecycle = PlanLifecycle(lambda: datetime(2026, 9, 12, tzinfo=timezone.utc))
    original = plan(task("A"))
    approved_history = lifecycle.approve(lifecycle.register(original), actor="reviewer")
    history = lifecycle.request_revision(
        approved_history,
        reason="inspect new evidence",
        evidence_refs=(EvidenceRef("workspace/new.json"),),
        requester="coordinator",
    )
    restored = lifecycle.cancel_revision(history, actor="reviewer")
    assert restored.current.status is PlanStatus.APPROVED
    assert restored.current.plan is original
    assert len(restored.transitions) == 3
