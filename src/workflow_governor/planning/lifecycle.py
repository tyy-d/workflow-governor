from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Callable

from workflow_governor.core.models import EvidenceRef, PlanStatus, WorkflowPlan


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class LifecycleTransition:
    plan_id: str
    plan_version: int
    from_status: PlanStatus | None
    to_status: PlanStatus
    actor: str
    timestamp: datetime
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class PlanRevisionRequest:
    plan_id: str
    plan_version: int
    reason: str
    evidence_refs: tuple[EvidenceRef, ...]
    requester: str
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class PlanRecord:
    plan: WorkflowPlan
    status: PlanStatus


@dataclass(frozen=True, slots=True)
class PlanHistory:
    records: tuple[PlanRecord, ...]
    transitions: tuple[LifecycleTransition, ...]
    revision_requests: tuple[PlanRevisionRequest, ...] = ()

    @property
    def current(self) -> PlanRecord:
        return max(self.records, key=lambda record: record.plan.version)


class PlanLifecycle:
    def __init__(self, clock: Callable[[], datetime] = _utc_now) -> None:
        self._clock = clock

    def register(self, plan: WorkflowPlan, *, actor: str = "planner") -> PlanRecord:
        return PlanRecord(plan=plan, status=PlanStatus.PROPOSED)

    def approve(self, record: PlanRecord, *, actor: str) -> PlanHistory:
        if record.status is not PlanStatus.PROPOSED:
            raise ValueError("only a proposed plan can be approved")
        approved = replace(record, status=PlanStatus.APPROVED)
        transition = self._transition(record, PlanStatus.APPROVED, actor)
        return PlanHistory((approved,), (transition,))

    def request_revision(
        self,
        plan_state: PlanRecord | PlanHistory,
        *,
        reason: str,
        evidence_refs: tuple[EvidenceRef, ...],
        requester: str,
    ) -> PlanHistory:
        history = (
            plan_state
            if isinstance(plan_state, PlanHistory)
            else PlanHistory((plan_state,), ())
        )
        record = history.current
        if record.status is not PlanStatus.APPROVED:
            raise ValueError("revision can be requested only for an approved plan")
        if not reason.strip():
            raise ValueError("revision reason must not be empty")
        requested = replace(record, status=PlanStatus.REVISION_REQUESTED)
        timestamp = self._clock()
        revision = PlanRevisionRequest(
            record.plan.plan_id,
            record.plan.version,
            reason,
            evidence_refs,
            requester,
            timestamp,
        )
        transition = LifecycleTransition(
            record.plan.plan_id,
            record.plan.version,
            record.status,
            PlanStatus.REVISION_REQUESTED,
            requester,
            timestamp,
            reason,
        )
        records = tuple(requested if item is record else item for item in history.records)
        return replace(
            history,
            records=records,
            transitions=history.transitions + (transition,),
            revision_requests=history.revision_requests + (revision,),
        )

    def cancel_revision(self, history: PlanHistory, *, actor: str) -> PlanHistory:
        current = max(history.records, key=lambda record: record.plan.version)
        if current.status is not PlanStatus.REVISION_REQUESTED:
            raise ValueError("no revision request is active")
        restored = replace(current, status=PlanStatus.APPROVED)
        records = tuple(restored if record is current else record for record in history.records)
        transition = self._transition(current, PlanStatus.APPROVED, actor, "revision cancelled")
        return replace(history, records=records, transitions=history.transitions + (transition,))

    def approve_replacement(
        self,
        history: PlanHistory,
        replacement: WorkflowPlan,
        *,
        actor: str,
    ) -> PlanHistory:
        previous = max(history.records, key=lambda record: record.plan.version)
        if previous.status is not PlanStatus.REVISION_REQUESTED:
            raise ValueError("replacement requires an active revision request")
        if replacement.plan_id != previous.plan.plan_id:
            raise ValueError("replacement must retain plan_id")
        if replacement.version <= previous.plan.version:
            raise ValueError("replacement version must increase")
        superseded = replace(previous, status=PlanStatus.SUPERSEDED)
        approved = PlanRecord(replacement, PlanStatus.APPROVED)
        records = tuple(superseded if record is previous else record for record in history.records)
        transitions = history.transitions + (
            self._transition(previous, PlanStatus.SUPERSEDED, actor),
            LifecycleTransition(
                replacement.plan_id,
                replacement.version,
                PlanStatus.PROPOSED,
                PlanStatus.APPROVED,
                actor,
                self._clock(),
                "replacement approved",
            ),
        )
        return replace(history, records=records + (approved,), transitions=transitions)

    def _transition(
        self,
        record: PlanRecord,
        to_status: PlanStatus,
        actor: str,
        reason: str | None = None,
    ) -> LifecycleTransition:
        return LifecycleTransition(
            record.plan.plan_id,
            record.plan.version,
            record.status,
            to_status,
            actor,
            self._clock(),
            reason,
        )
