from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AcceptedObservationNotification:
    response_id: str
    handoff_id: str
    workflow_id: str
    task_id: str
    accepted_at: str
