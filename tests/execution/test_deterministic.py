from __future__ import annotations

import pytest

from workflow_governor.core.models import (
    EvidenceContent,
    EvidenceRef,
    ExecutionStatus,
    ExecutorType,
    TaskContext,
    TaskSpec,
)
from workflow_governor.execution.deterministic import DeterministicExecutor


SOURCE = "workspace/data.json"


def run(operation: str, inputs: dict, *, with_evidence: bool = True):
    ref = EvidenceRef(SOURCE)
    task = TaskSpec(
        "T1",
        "Calculate",
        "Run an exact operation",
        ExecutorType.DETERMINISTIC,
        evidence_requirements=(ref,),
        completion_criteria=("Return exact result",),
        operation=operation,
    )
    evidence = (EvidenceContent(ref, "{}"),) if with_evidence else ()
    context = TaskContext("T1", evidence=evidence, operation_inputs=inputs, granted_sources=(SOURCE,))
    return DeterministicExecutor().execute(task, context)


def test_percentage_is_decimal_and_exact() -> None:
    result = run("percentage", {"numerator": 900, "denominator": 1000, "places": 1})
    assert result.status is ExecutionStatus.COMPLETED
    assert result.output["result"]["percentage"] == "90.0"


def test_zero_denominator_is_failed_after_attempt() -> None:
    result = run("percentage", {"numerator": 1, "denominator": 0})
    assert result.status is ExecutionStatus.FAILED
    assert "zero" in result.error


def test_missing_evidence_is_blocked_before_attempt() -> None:
    result = run("structured_equal", {"left": 1, "right": 1}, with_evidence=False)
    assert result.status is ExecutionStatus.BLOCKED


def test_latest_authorized_revision_and_case_002_rates() -> None:
    selected = run(
        "select_latest_authorized_revision",
        {"records": [{"revision": 1, "authorized": True}, {"revision": 2, "authorized": True}]},
    )
    on_time = run("percentage", {"numerator": 900, "denominator": 1000, "places": 1})
    fill = run("reconcile_quantity", {"ordered": 1000, "received": 900})
    assert selected.output["result"]["revision"] == 2
    assert on_time.output["result"]["percentage"] == "90.0"
    assert fill.output["result"]["fill_percentage"] == "90.00"


def test_json_schema_validation() -> None:
    result = run(
        "validate_json_schema",
        {"instance": {"count": 2}, "schema": {"type": "object", "required": ["count"], "properties": {"count": {"type": "integer"}}}},
    )
    assert result.status is ExecutionStatus.COMPLETED

    invalid = run(
        "validate_json_schema",
        {"instance": {"count": "two"}, "schema": {"properties": {"count": {"type": "integer"}}}},
    )
    assert invalid.status is ExecutionStatus.FAILED

