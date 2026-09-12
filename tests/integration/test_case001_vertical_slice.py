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
from workflow_governor.core.config import RuntimeConfig
from workflow_governor.core.persistence_json import json_text
from workflow_governor.core.substrate import WorkspaceGrant
from workflow_governor.artifacts.state import WorkflowStateLoader
from workflow_governor.artifacts.store import ArtifactStore
from workflow_governor.execution.deterministic import DeterministicExecutor
from workflow_governor.execution.runner import MinimalTaskRunner
from workflow_governor.integration.adapters import AuthorizedWorkspaceProvider
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
PERSISTED_STATUS = "cases/CASE_001_VENDOR_ACTIVATION/workspace/documents/VENDORLINK_STATUS_NVID-10482.json"
PERSISTED_COI = "cases/CASE_001_VENDOR_ACTIVATION/workspace/documents/COI_NVID-10482_2026.txt"
PERSISTED_PO = "cases/CASE_001_VENDOR_ACTIVATION/workspace/documents/PO_78431_DRAFT.md"
PERSISTED_POLICY = "company/northstar/handbook/00_COMPANY_AND_VENDOR_OVERVIEW.md"


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


class PersistedReviewedPlanBackend:
    """Reviewed test input describes work only; executors derive the findings."""

    def create_plan(self, request):
        return WorkflowPlan(
            "P01-PERSISTED",
            1,
            request.objective,
            (
                TaskSpec(
                    "standing",
                    "Inspect standing",
                    "Extract selected status fields",
                    ExecutorType.DETERMINISTIC,
                    evidence_requirements=(EvidenceRef(PERSISTED_STATUS),),
                    completion_criteria=("Return cited status fields",),
                    operation="extract_fields",
                ),
                TaskSpec(
                    "insurance",
                    "Check evidence date",
                    "Compare supplied dates",
                    ExecutorType.DETERMINISTIC,
                    evidence_requirements=(EvidenceRef(PERSISTED_COI), EvidenceRef(PERSISTED_STATUS)),
                    completion_criteria=("Return the date relationship",),
                    operation="compare_dates",
                ),
                TaskSpec(
                    "po",
                    "Inspect transmission state",
                    "Compare the selected transmission value",
                    ExecutorType.DETERMINISTIC,
                    evidence_requirements=(EvidenceRef(PERSISTED_PO),),
                    completion_criteria=("Return the exact comparison",),
                    operation="structured_equal",
                ),
                TaskSpec(
                    "activate",
                    "Complete authorized activation review",
                    "Make the bounded decision requiring external authority",
                    ExecutorType.HUMAN,
                    dependencies=("standing", "insurance", "po"),
                    evidence_requirements=(
                        EvidenceRef(PERSISTED_STATUS),
                        EvidenceRef(PERSISTED_COI),
                        EvidenceRef(PERSISTED_PO),
                    ),
                    policy_requirements=(EvidenceRef(PERSISTED_POLICY),),
                    completion_criteria=("Record an authorized decision",),
                    authority_requirement="Vendor Compliance activation authority",
                ),
            ),
            unresolved_questions=("Whether acceptable replacement evidence will be provided",),
        )


class PersistedContexts:
    def __init__(self, bundle):
        self.available = {
            item.ref.source: item
            for item in bundle.targeted_evidence + bundle.relevant_policy
        }

    def get_context(self, task, run_state):
        evidence = tuple(self.available[ref.source] for ref in task.evidence_requirements)
        policy = tuple(self.available[ref.source] for ref in task.policy_requirements)
        status_record = json.loads(self.available[PERSISTED_STATUS].content)
        expiration_match = re.search(
            r"Policy expiration date:\s*([^\r\n]+)", self.available[PERSISTED_COI].content
        )
        transmission_match = re.search(
            r"VendorLink transmission ID:\*\*\s*([^\r\n]+)", self.available[PERSISTED_PO].content
        )
        assert expiration_match and transmission_match
        inputs = {
            "standing": {
                "format": "json",
                "content": self.available[PERSISTED_STATUS].content,
                "fields": ["status", "commercial_po_eligible"],
            },
            "insurance": {
                "left": datetime.strptime(expiration_match.group(1).strip(), "%B %d, %Y").date().isoformat(),
                "right": status_record["exported_at"][:10],
            },
            "po": {"left": transmission_match.group(1).strip().lower(), "right": "none"},
        }.get(task.task_id, {})
        return TaskContext(
            task.task_id,
            evidence=evidence,
            policy=policy,
            operation_inputs=inputs,
            granted_sources=tuple(self.available),
        )


class ContextMustNotRun:
    def get_context(self, task, run_state):
        raise AssertionError("terminal tasks must not request context after restart")


def test_case001_persisted_mock_assisted_start_and_fresh_restart(tmp_path) -> None:
    config = RuntimeConfig(ROOT, tmp_path / "runtime")
    grants = (
        WorkspaceGrant("case-workspace", "cases/CASE_001_VENDOR_ACTIVATION/workspace"),
        WorkspaceGrant("northstar-policy", "company/northstar/handbook"),
    )
    provider = AuthorizedWorkspaceProvider(
        config,
        grants,
        primary_grant_id="case-workspace",
        evidence_selections={
            "case-workspace": (
                "documents/VENDORLINK_STATUS_NVID-10482.json",
                "documents/COI_NVID-10482_2026.txt",
                "documents/PO_78431_DRAFT.md",
            )
        },
        policy_selections={"northstar-policy": ("00_COMPANY_AND_VENDOR_OVERVIEW.md",)},
    )
    deterministic = DeterministicExecutor()
    validator = PlanValidator(
        allowed_evidence_sources={PERSISTED_STATUS, PERSISTED_COI, PERSISTED_PO, PERSISTED_POLICY},
        supported_operations=deterministic.supported_operations,
    )
    coordinator = P01Coordinator(
        planner=Planner(PersistedReviewedPlanBackend(), validator),
        lifecycle=PlanLifecycle(),
        runner=MinimalTaskRunner({ExecutorType.DETERMINISTIC: deterministic}),
    )
    store = ArtifactStore(config)
    handoffs = Handoffs()
    approved, state = coordinator.start_persisted(
        workflow_id="P01-DURABLE",
        objective="Can you figure out what we need to do to get this vendor live by Friday?",
        workspace_provider=provider,
        context_provider_factory=PersistedContexts,
        store=store,
        handoff_sink=handoffs,
        approver="integration-reviewer",
    )
    serialized = json_text(approved.plan.to_dict())
    assert state.mock_assisted is True
    assert state.task_states["standing"].result.output["result"]["values"] == {
        "status": "Conditional",
        "commercial_po_eligible": False,
    }
    assert state.task_states["insurance"].result.output["result"] == {
        "relation": "before",
        "days": -9,
    }
    assert state.task_states["po"].result.output["result"]["equal"] is True
    assert state.task_states["activate"].status is ExecutionStatus.PENDING_HUMAN
    assert len(handoffs.items) == 1

    snapshot = WorkflowStateLoader(store).load("P01-DURABLE")
    assert snapshot.workspace_map.root == "cases/CASE_001_VENDOR_ACTIVATION/workspace"
    assert len(snapshot.evidence) == 4
    assert all(item.status == "unchanged" for item in snapshot.evidence)
    assert all(item.reference.artifact_id == f"sha256:{item.sha256}" for item in snapshot.evidence)
    for task_id in ("standing", "insurance", "po"):
        assert snapshot.contexts[task_id] == store.load_context("P01-DURABLE", task_id)
    assert json_text(snapshot.current_plan.plan.to_dict()) == serialized

    fresh_store = ArtifactStore(RuntimeConfig(ROOT, tmp_path / "runtime"))
    fresh_coordinator = P01Coordinator(
        planner=Planner(PersistedReviewedPlanBackend(), validator),
        lifecycle=PlanLifecycle(),
        runner=MinimalTaskRunner({ExecutorType.DETERMINISTIC: DeterministicExecutor()}),
    )
    resumed_handoffs = Handoffs()
    resumed_plan, resumed = fresh_coordinator.resume_persisted(
        workflow_id="P01-DURABLE",
        store=fresh_store,
        context_provider=ContextMustNotRun(),
        handoff_sink=resumed_handoffs,
    )
    assert resumed.mock_assisted is True
    assert {key: value.status for key, value in resumed.task_states.items()} == {
        key: value.status for key, value in state.task_states.items()
    }
    assert resumed_handoffs.items == []
    assert json_text(resumed_plan.plan.to_dict()) == serialized
    resumed_human_task = next(task for task in resumed_plan.plan.tasks if task.task_id == "activate")
    reconstructed_handoff = MinimalTaskRunner.create_handoff(
        resumed_plan, "P01-DURABLE", resumed_human_task
    )
    assert reconstructed_handoff.handoff_id == handoffs.items[0].handoff_id
