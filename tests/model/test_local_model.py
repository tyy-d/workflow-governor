from __future__ import annotations

from workflow_governor.core.errors import AdapterUnavailable
from workflow_governor.core.models import (
    EvidenceContent,
    EvidenceRef,
    ExecutionStatus,
    ExecutorType,
    TaskContext,
    TaskSpec,
)
from workflow_governor.model.local import LocalModelExecutor, ModelContextBuilder


SOURCE = "workspace/status.json"
POLICY = "company/northstar/handbook/00_COMPANY_AND_VENDOR_OVERVIEW.md"


class ScriptedAdapter:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def generate(self, request):
        self.calls += 1
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def task() -> TaskSpec:
    return TaskSpec(
        "M1",
        "Synthesize evidence",
        "Apply the granted policy to the evidence",
        ExecutorType.LOCAL_MODEL,
        evidence_requirements=(EvidenceRef(SOURCE),),
        policy_requirements=(EvidenceRef(POLICY),),
        completion_criteria=("Return cited conclusions",),
    )


def context() -> TaskContext:
    return TaskContext(
        "M1",
        evidence=(EvidenceContent(EvidenceRef(SOURCE), '{"status":"Conditional"}'),),
        policy=(EvidenceContent(EvidenceRef(POLICY), "Only Active vendors may receive commercial POs."),),
        granted_sources=(SOURCE, POLICY),
    )


def valid_response():
    return {
        "findings": ["The record has a non-Active status."],
        "evidence_refs": [SOURCE, POLICY],
        "conclusions": ["Commercial release requires an authorized status change."],
        "assumptions": [],
        "unresolved": ["Authorized status change remains pending."],
        "rationale": "The conclusion follows from the granted record and policy.",
    }


def test_valid_structured_response_completes() -> None:
    adapter = ScriptedAdapter([valid_response()])
    result = LocalModelExecutor(adapter).execute(task(), context())
    assert result.status is ExecutionStatus.COMPLETED
    assert len(result.evidence_refs) == 2


def test_context_marks_documents_as_untrusted_instructions() -> None:
    request = ModelContextBuilder().build(task(), context())
    assert "untrusted evidence" in request.document_instruction


def test_malformed_response_retries_once_then_completes() -> None:
    adapter = ScriptedAdapter([{"findings": []}, valid_response()])
    result = LocalModelExecutor(adapter).execute(task(), context())
    assert result.status is ExecutionStatus.COMPLETED
    assert adapter.calls == 2


def test_two_malformed_responses_fail() -> None:
    result = LocalModelExecutor(ScriptedAdapter([{}, {}])).execute(task(), context())
    assert result.status is ExecutionStatus.FAILED


def test_unavailable_adapter_is_blocked() -> None:
    result = LocalModelExecutor(ScriptedAdapter([AdapterUnavailable("runtime unavailable")])).execute(task(), context())
    assert result.status is ExecutionStatus.BLOCKED


def test_ungranted_citation_fails_after_retry() -> None:
    response = valid_response()
    response["evidence_refs"] = ["workspace/not-granted.json"]
    result = LocalModelExecutor(ScriptedAdapter([response, response])).execute(task(), context())
    assert result.status is ExecutionStatus.FAILED


def test_context_limit_blocks_without_adapter_attempt() -> None:
    adapter = ScriptedAdapter([valid_response()])
    executor = LocalModelExecutor(adapter, context_builder=ModelContextBuilder(max_characters=5))
    result = executor.execute(task(), context())
    assert result.status is ExecutionStatus.BLOCKED
    assert adapter.calls == 0
