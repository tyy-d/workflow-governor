from __future__ import annotations

import json
from pathlib import Path

import pytest

from workflow_governor.core.models import DecisionAuthorityScope
from workflow_governor.human.contracts import AuthorityStatus, AuthorityValidation, HumanTaskResponse, ResponseDisposition
from workflow_governor.operator_model import (
    AcceptedObservationNotification,
    OperatorEvidenceLedger,
    OperatorProfileProjector,
    OperatorProfileStore,
    OperatorSchemaValidationError,
    OperatorSchemaValidator,
    accepted_response_event,
)


ROOT = Path(__file__).resolve().parents[2]
NOW = "2026-09-12T14:00:00+00:00"


def schema():
    return OperatorSchemaValidator(ROOT)


def response():
    return HumanTaskResponse(
        "R001", "H001", "W001", "P001", 1, "T001", "P001", ResponseDisposition.COMPLETE,
        DecisionAuthorityScope.NO_DECISION, AuthorityValidation(AuthorityStatus.NOT_REQUIRED, None),
        {"outcome": "reviewed"}, "Completed bounded review.", submitted_at=NOW,
    )


def verified_event(*, event_id="EV-VERIFY", effect="POSITIVE", attribution="NO_ERROR", capability="document_comparison", knowledge=()):
    return {
        "event_id": event_id,
        "operator_id": "P001",
        "timestamp": NOW,
        "event_type": "TASK_VERIFIED_CORRECT" if effect == "POSITIVE" else "TASK_VERIFIED_INCORRECT",
        "source": "SYSTEM_OBSERVATION",
        "observation": "Deterministic comparison verified the submitted result.",
        "task_context": {"workflow_id": "W001", "task_id": "T001", "difficulty": "MODERATE", "scaffolding_level": "LIGHT"},
        "capability_implications": [{"capability_id": capability, "effect": effect, "strength": "MODERATE", "rationale": "The comparison was materially exercised."}],
        "knowledge_implications": list(knowledge),
        "attribution": attribution,
        "verification": {"status": "VERIFIED", "method": "DETERMINISTIC", "verifier": "comparison-check"},
        "profile_significance": "MEDIUM",
        "source_refs": ["response_id:R001", f"verification_id:{event_id}"],
    }


def test_cold_start_is_unknown_in_canonical_order() -> None:
    validator = schema()
    profile = OperatorProfileProjector(validator).cold_start("P001", NOW)
    assert len(profile["capabilities"]) == len(validator.dimension_order) == 19
    assert profile["capabilities"] == [0.5] * 19
    assert profile["capability_evidence"] == [0.0] * 19


def test_accepted_observation_is_unverified_and_does_not_move_capability() -> None:
    validator = schema()
    event = accepted_response_event(response(), AcceptedObservationNotification("R001", "H001", "W001", "T001", NOW), event_id="EV-ACCEPT")
    profile = OperatorProfileProjector(validator).reconstruct("P001", [event], timestamp=NOW)
    assert profile["capabilities"] == [0.5] * 19
    assert profile["capability_evidence"] == [0.0] * 19
    assert profile["evidence_stats"]["total_events"] == 1


def test_verified_success_moves_only_exercised_dimension() -> None:
    validator = schema()
    profile = OperatorProfileProjector(validator).reconstruct("P001", [verified_event()], timestamp=NOW)
    index = validator.dimension_order.index("document_comparison")
    assert profile["capabilities"][index] > 0.5
    assert profile["capability_evidence"][index] > 0
    assert all(value == 0.5 for position, value in enumerate(profile["capabilities"]) if position != index)


def test_negative_movement_requires_verified_operator_error() -> None:
    validator = schema()
    projector = OperatorProfileProjector(validator)
    ai_error = verified_event(effect="NEGATIVE", attribution="AI_ERROR")
    operator_error = verified_event(event_id="EV-OPERATOR", effect="NEGATIVE", attribution="OPERATOR_ERROR")
    unchanged = projector.reconstruct("P001", [ai_error], timestamp=NOW)
    changed = projector.reconstruct("P001", [operator_error], timestamp=NOW)
    index = validator.dimension_order.index("document_comparison")
    assert unchanged["capabilities"][index] == 0.5
    assert changed["capabilities"][index] < 0.5


def test_contradictory_knowledge_is_preserved_with_both_events() -> None:
    validator = schema()
    supports = verified_event(event_id="EV-K1", knowledge=({"topic": "vendor activation", "effect": "SUPPORTS", "strength": "MODERATE"},))
    contradicts = verified_event(event_id="EV-K2", knowledge=({"topic": "vendor activation", "effect": "CONTRADICTS", "strength": "STRONG"},))
    profile = OperatorProfileProjector(validator).reconstruct("P001", [supports, contradicts], timestamp=NOW)
    record = profile["knowledge"][0]
    assert record["status"] == "CONTRADICTED"
    assert record["basis_event_ids"] == ["EV-K1", "EV-K2"]


def test_ledger_and_profile_store_are_idempotent_and_reconstructable(tmp_path) -> None:
    validator = schema()
    ledger = OperatorEvidenceLedger(tmp_path, validator)
    event = verified_event()
    assert ledger.append(event) is True
    assert ledger.append(event) is False
    profile = OperatorProfileProjector(validator).reconstruct("P001", ledger.read("P001"), timestamp=NOW)
    path = OperatorProfileStore(tmp_path, validator).write(profile)
    assert json.loads(path.read_text(encoding="utf-8"))["operator_id"] == "P001"


def test_duplicate_accepted_observation_for_response_is_rejected_even_with_new_event_id(tmp_path) -> None:
    validator = schema()
    ledger = OperatorEvidenceLedger(tmp_path, validator)
    notification = AcceptedObservationNotification("R001", "H001", "W001", "T001", NOW)
    first = accepted_response_event(response(), notification, event_id="EV-A1")
    second = accepted_response_event(response(), notification, event_id="EV-A2")
    assert ledger.append(first) is True
    with pytest.raises(ValueError, match="duplicate evidence identity"):
        ledger.append(second)


@pytest.mark.parametrize("verification", ["UNVERIFIED", "DISPUTED"])
def test_unsupported_verification_causes_no_capability_movement(verification) -> None:
    validator = schema()
    event = verified_event()
    event["verification"]["status"] = verification
    profile = OperatorProfileProjector(validator).reconstruct("P001", [event], timestamp=NOW)
    assert profile["capabilities"] == [0.5] * 19
    assert profile["capability_evidence"] == [0.0] * 19


def test_schema_rejects_malformed_event() -> None:
    with pytest.raises(OperatorSchemaValidationError):
        schema().validate_event({"event_id": "broken"})
