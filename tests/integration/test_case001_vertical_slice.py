from __future__ import annotations

from pathlib import Path
import json
import re
from datetime import datetime

from workflow_governor.core.models import (
    EvidenceContent,
    EvidenceRef,
    ExecutionStatus,
    ExecutorType,
    FileRecord,
    TaskContext,
    TaskSpec,
    WorkflowPlan,
    WorkspaceMap,
)
from workflow_governor.execution.deterministic import DeterministicExecutor
from workflow_governor.execution.runner import MinimalTaskRunner
from workflow_governor.integration.p01 import P01Coordinator, WorkspaceBundle
from workflow_governor.planning.lifecycle import PlanLifecycle
from workflow_governor.planning.planner import Planner
from workflow_governor.planning.validation import PlanValidator


ROOT = Path(__file__).resolve().parents[2]
CASE_ROOT = ROOT / "cases" / "CASE_001_VENDOR_ACTIVATION"
STATUS = "workspace/documents/VENDORLINK_STATUS_NVID-10482.json"
COI = "workspace/documents/COI_NVID-10482_2026.txt"
PO = "workspace/documents/PO_78431_DRAFT.md"
POLICY = "company/northstar/handbook/00_COMPANY_AND_VENDOR_OVERVIEW.md"


class AuthorizedCaseWorkspace:
    def prepare(self, objective):
        evidence = tuple(
            EvidenceContent(EvidenceRef(source), (CASE_ROOT / source).read_text(encoding="utf-8"))
            for source in (STATUS, COI, PO)
        )
        policy_path = ROOT / POLICY
        policy = (EvidenceContent(EvidenceRef(POLICY), policy_path.read_text(encoding="utf-8")),)
        files = tuple(FileRecord(item.ref.source, Path(item.ref.source).name, size=len(item.content)) for item in evidence)
        return WorkspaceBundle(WorkspaceMap("authorized-case-workspace", files), evidence, policy)


class ReviewedPlanBackend:
    """Test-local plan shape; factual values remain executor inputs, not plan conclusions."""

    def create_plan(self, request):
        return WorkflowPlan(
            "P01-PLAN",
            1,
            request.objective,
            (
                TaskSpec("standing", "Inspect standing", "Extract selected status fields", ExecutorType.DETERMINISTIC, evidence_requirements=(EvidenceRef(STATUS),), completion_criteria=("Return cited status fields",), operation="extract_fields"),
                TaskSpec("insurance", "Check evidence date", "Compare the supplied expiration and review dates", ExecutorType.DETERMINISTIC, evidence_requirements=(EvidenceRef(COI), EvidenceRef(STATUS)), completion_criteria=("Return the exact date relationship",), operation="compare_dates"),
                TaskSpec("po", "Inspect transmission state", "Check whether a transmission identifier is present", ExecutorType.DETERMINISTIC, evidence_requirements=(EvidenceRef(PO),), completion_criteria=("Return the exact transmission comparison",), operation="structured_equal"),
                TaskSpec("activate", "Complete authorized activation", "Review the evidence and perform only the authorized status action", ExecutorType.HUMAN, dependencies=("standing", "insurance", "po"), evidence_requirements=(EvidenceRef(STATUS), EvidenceRef(COI), EvidenceRef(PO)), policy_requirements=(EvidenceRef(POLICY),), completion_criteria=("Record an authorized decision",), authority_requirement="Vendor Compliance activation authority"),
            ),
            unresolved_questions=("Whether acceptable replacement evidence will be provided",),
        )


class ContextProvider:
    def __init__(self, bundle):
        self.bundle = bundle

    def get_context(self, task, run_state):
        available = {item.ref.source: item for item in self.bundle.targeted_evidence + self.bundle.relevant_policy}
        evidence = tuple(available[ref.source] for ref in task.evidence_requirements)
        policy = tuple(available[ref.source] for ref in task.policy_requirements)
        status_record = json.loads(available[STATUS].content)
        expiration_match = re.search(r"Policy expiration date:\s*([^\r\n]+)", available[COI].content)
        transmission_match = re.search(r"VendorLink transmission ID:\*\*\s*([^\r\n]+)", available[PO].content)
        assert expiration_match and transmission_match
        inputs = {
            "standing": {"format": "json", "content": available[STATUS].content, "fields": ["status", "commercial_po_eligible"]},
            "insurance": {
                "left": datetime.strptime(expiration_match.group(1).strip(), "%B %d, %Y").date().isoformat(),
                "right": status_record["exported_at"][:10],
            },
            "po": {"left": transmission_match.group(1).strip().lower(), "right": "none"},
        }.get(task.task_id, {})
        return TaskContext(task.task_id, evidence=evidence, policy=policy, operation_inputs=inputs, granted_sources=tuple(available))


class Events:
    def __init__(self): self.items = []
    def record(self, event): self.items.append(event)


class Handoffs:
    def __init__(self): self.items = []
    def emit(self, handoff): self.items.append(handoff)


def test_case001_expected_results_emerge_from_authorized_evidence() -> None:
    workspace = AuthorizedCaseWorkspace()
    bundle = workspace.prepare("Can you figure out what we need to do to get this vendor live by Friday?")
    deterministic = DeterministicExecutor()
    validator = PlanValidator(
        allowed_evidence_sources={STATUS, COI, PO, POLICY},
        supported_operations=deterministic.supported_operations,
    )
    coordinator = P01Coordinator(
        planner=Planner(ReviewedPlanBackend(), validator),
        lifecycle=PlanLifecycle(),
        runner=MinimalTaskRunner({ExecutorType.DETERMINISTIC: deterministic}),
    )
    events, handoffs = Events(), Handoffs()
    approved, state = coordinator.run(
        workflow_id="P01-TEST",
        objective="Can you figure out what we need to do to get this vendor live by Friday?",
        workspace_provider=workspace,
        context_provider=ContextProvider(bundle),
        event_sink=events,
        handoff_sink=handoffs,
        approver="integration-reviewer",
    )

    standing = state.task_states["standing"].result.output["result"]["values"]
    expiration = state.task_states["insurance"].result.output["result"]
    release = state.task_states["po"].result.output["result"]
    assert standing == {"status": "Conditional", "commercial_po_eligible": False}
    assert expiration == {"relation": "before", "days": -9}
    assert release["equal"] is True
    assert state.task_states["activate"].status is ExecutionStatus.PENDING_HUMAN
    assert handoffs.items[0].authority_requirement == "Vendor Compliance activation authority"
    assert approved.plan.plan_id == "P01-PLAN"
    assert state.mock_assisted is True
    assert all("ground_truth" not in ref.source for task in approved.plan.tasks for ref in task.evidence_requirements)


def test_production_modules_contain_no_case_specific_identifiers() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src").rglob("*.py"))
    for forbidden in ("CASE_001", "NVID-10482", "Harbor Finch", "78431", "MCS-884201"):
        assert forbidden not in source
