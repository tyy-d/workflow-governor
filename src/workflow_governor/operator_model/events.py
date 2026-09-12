from __future__ import annotations

from typing import Any

from workflow_governor.human.contracts import HumanTaskResponse, ResponseDisposition
from workflow_governor.operator_model.contracts import AcceptedObservationNotification


_EVENT_TYPE = {
    ResponseDisposition.COMPLETE: "TASK_COMPLETED",
    ResponseDisposition.NEEDS_INFORMATION: "CLARIFICATION_REQUESTED",
    ResponseDisposition.PARTIAL: "TASK_COMPLETED",
    ResponseDisposition.TASK_NARROWED: "TASK_NARROWED",
    ResponseDisposition.REASSIGNMENT_REQUESTED: "REASSIGNMENT_REQUESTED",
    ResponseDisposition.AUTHORITY_DECLINED: "AUTHORITY_DECLINED",
}


def accepted_response_event(
    response: HumanTaskResponse,
    notification: AcceptedObservationNotification,
    *,
    event_id: str,
) -> dict[str, Any]:
    for field in ("response_id", "handoff_id", "workflow_id", "task_id"):
        if getattr(response, field) != getattr(notification, field):
            raise ValueError(f"accepted-observation {field} does not match response")
    return {
        "event_id": event_id,
        "operator_id": response.actor_id,
        "timestamp": notification.accepted_at,
        "event_type": _EVENT_TYPE[response.response_disposition],
        "source": "TASK_EXECUTION",
        "observation": _observation(response),
        "task_context": {
            "workflow_id": response.workflow_id,
            "task_id": response.task_id,
        },
        "capability_implications": [],
        "knowledge_implications": [],
        "attribution": "NO_ERROR",
        "verification": {
            "status": "UNVERIFIED",
            "method": "NONE",
            "verifier": "workflow-acceptance",
            "details": "Accepted as a workflow observation; correctness not established.",
        },
        "profile_significance": "LOW",
        "source_refs": [
            f"response_id:{response.response_id}",
            f"handoff_id:{response.handoff_id}",
        ],
    }


def _observation(response: HumanTaskResponse) -> str:
    text = f"Accepted {response.response_disposition.value} response from {response.actor_id}. {response.rationale.strip()}"
    if response.corrections:
        text += f" Included {len(response.corrections)} explicit correction(s)."
    return text[:2000]
