from __future__ import annotations

import pytest

from workflow_governor.artifacts.state import WorkflowStateLoader
from workflow_governor.artifacts.store import ArtifactStore
from workflow_governor.core.config import RuntimeConfig
from workflow_governor.core.errors import ContractValidationError
from workflow_governor.core.models import (
    ExecutionStatus,
    ExecutorType,
    PlanStatus,
    TaskResult,
    TaskSpec,
    WorkflowPlan,
)
from workflow_governor.integration.resume import reconstruct_persisted_run


def make_store(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    store = ArtifactStore(RuntimeConfig(repo, tmp_path / "runtime"))
    store.create_workflow("W", "Resume work", ())
    return store


def make_plan():
    return WorkflowPlan(
        "P",
        1,
        "Resume work",
        (
            TaskSpec("pending", "Pending", "Pending", ExecutorType.DETERMINISTIC),
            TaskSpec("completed", "Completed", "Completed", ExecutorType.DETERMINISTIC),
            TaskSpec("failed", "Failed", "Failed", ExecutorType.LOCAL_MODEL),
            TaskSpec("blocked", "Blocked", "Blocked", ExecutorType.DETERMINISTIC),
            TaskSpec("human", "Human", "Human", ExecutorType.HUMAN),
        ),
    )


def persist_plan(store, plan):
    store.save_plan("W", plan, status=PlanStatus.APPROVED)
    for task in plan.tasks:
        store.save_task("W", task)


def test_reconstructs_approved_plan_and_exact_persisted_states(tmp_path) -> None:
    store = make_store(tmp_path)
    plan = make_plan()
    persist_plan(store, plan)
    for task_id, status, executor_type in (
        ("completed", ExecutionStatus.COMPLETED, ExecutorType.DETERMINISTIC),
        ("failed", ExecutionStatus.FAILED, ExecutorType.LOCAL_MODEL),
        ("blocked", ExecutionStatus.BLOCKED, ExecutorType.DETERMINISTIC),
    ):
        result = TaskResult(task_id, status, executor_type, output={"preserved": task_id})
        store.save_task_status("W", task_id, status)
        store.save_result("W", result)
    store.save_task_status("W", "human", ExecutionStatus.PENDING_HUMAN)

    fresh_store = ArtifactStore(RuntimeConfig(store.config.repository_root, store.config.runtime_root))
    snapshot = WorkflowStateLoader(fresh_store).load("W")
    record, state = reconstruct_persisted_run(snapshot, snapshot.current_plan)
    assert record.plan == plan
    assert state.mock_assisted is True
    assert state.task_states["pending"].status is ExecutionStatus.PENDING
    assert state.task_states["completed"].result.output == {"preserved": "completed"}
    assert state.task_states["failed"].status is ExecutionStatus.FAILED
    assert state.task_states["blocked"].status is ExecutionStatus.BLOCKED
    assert state.task_states["human"].status is ExecutionStatus.PENDING_HUMAN
    assert state.task_states["human"].result is None


@pytest.mark.parametrize("status", [ExecutionStatus.READY, ExecutionStatus.IN_PROGRESS])
def test_rejects_non_resumable_checkpoint_states(tmp_path, status) -> None:
    store = make_store(tmp_path)
    plan = make_plan()
    persist_plan(store, plan)
    store.save_task_status("W", "pending", status)
    snapshot = WorkflowStateLoader(store).load("W")
    with pytest.raises(ContractValidationError, match="non-resumable"):
        reconstruct_persisted_run(snapshot, snapshot.current_plan)


def test_rejects_nonapproved_current_plan(tmp_path) -> None:
    store = make_store(tmp_path)
    plan = make_plan()
    store.save_plan("W", plan, status=PlanStatus.PROPOSED)
    for task in plan.tasks:
        store.save_task("W", task)
    snapshot = WorkflowStateLoader(store).load("W")
    with pytest.raises(ContractValidationError, match="approved"):
        reconstruct_persisted_run(snapshot, snapshot.current_plan)


def test_rejects_unknown_persisted_status(tmp_path) -> None:
    store = make_store(tmp_path)
    plan = make_plan()
    persist_plan(store, plan)
    store.save_task_status("W", "pending", "UNKNOWN_STATE")
    snapshot = WorkflowStateLoader(store).load("W")
    with pytest.raises(ContractValidationError, match="Unknown persisted"):
        reconstruct_persisted_run(snapshot, snapshot.current_plan)


def test_rejects_persisted_result_executor_mismatch(tmp_path) -> None:
    store = make_store(tmp_path)
    plan = make_plan()
    persist_plan(store, plan)
    store.save_task_status("W", "completed", ExecutionStatus.COMPLETED)
    store.save_result(
        "W", TaskResult("completed", ExecutionStatus.COMPLETED, ExecutorType.LOCAL_MODEL)
    )
    snapshot = WorkflowStateLoader(store).load("W")
    with pytest.raises(ContractValidationError, match="executor mismatch"):
        reconstruct_persisted_run(snapshot, snapshot.current_plan)


def test_rejects_foreign_task_state(tmp_path) -> None:
    store = make_store(tmp_path)
    plan = make_plan()
    persist_plan(store, plan)
    store.save_task_status("W", "foreign", ExecutionStatus.BLOCKED)
    snapshot = WorkflowStateLoader(store).load("W")
    with pytest.raises(ContractValidationError, match="unknown approved-plan tasks"):
        reconstruct_persisted_run(snapshot, snapshot.current_plan)


def test_rejects_task_definition_mismatch(tmp_path) -> None:
    store = make_store(tmp_path)
    plan = make_plan()
    persist_plan(store, plan)
    store.save_task("W", TaskSpec("pending", "Changed", "Changed", ExecutorType.DETERMINISTIC))
    snapshot = WorkflowStateLoader(store).load("W")
    with pytest.raises(ContractValidationError, match="differs"):
        reconstruct_persisted_run(snapshot, snapshot.current_plan)


def test_rejects_status_result_conflict_and_missing_completed_result(tmp_path) -> None:
    store = make_store(tmp_path)
    plan = make_plan()
    persist_plan(store, plan)
    store.save_task_status("W", "completed", ExecutionStatus.COMPLETED)
    snapshot = WorkflowStateLoader(store).load("W")
    with pytest.raises(ContractValidationError, match="missing"):
        reconstruct_persisted_run(snapshot, snapshot.current_plan)

    store.save_result(
        "W", TaskResult("completed", ExecutionStatus.FAILED, ExecutorType.DETERMINISTIC)
    )
    snapshot = WorkflowStateLoader(store).load("W")
    with pytest.raises(ContractValidationError, match="conflict"):
        reconstruct_persisted_run(snapshot, snapshot.current_plan)
