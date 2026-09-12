from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
from typing import Any, Iterable

from workflow_governor.operator_model.schema import OperatorSchemaValidator


@dataclass(frozen=True, slots=True)
class ProjectionPolicy:
    """Uncalibrated, conservative operator-profile-v1 projection constants."""

    version: str = "provisional-v1"
    capability_step: dict[str, float] = field(default_factory=lambda: {"WEAK": 0.01, "MODERATE": 0.02, "STRONG": 0.04})
    evidence_step: dict[str, float] = field(default_factory=lambda: {"WEAK": 0.02, "MODERATE": 0.04, "STRONG": 0.08})
    verification_factor: dict[str, float] = field(default_factory=lambda: {"UNVERIFIED": 0.0, "PARTIALLY_VERIFIED": 0.5, "VERIFIED": 1.0, "DISPUTED": 0.0})
    difficulty_factor: dict[str | None, float] = field(default_factory=lambda: {None: 0.5, "LOW": 0.5, "MODERATE": 0.75, "HIGH": 1.0})
    scaffolding_factor: dict[str | None, float] = field(default_factory=lambda: {None: 0.5, "NONE": 1.0, "LIGHT": 0.85, "STRUCTURED": 0.6, "STEP_BY_STEP": 0.35})
    method_factor: dict[str, float] = field(default_factory=lambda: {"DETERMINISTIC": 1.0, "AUTHORITATIVE_SOURCE": 1.0, "CROSS_CHECK": 0.9, "HUMAN_REVIEW": 0.8, "MODEL_REVIEW": 0.5, "NONE": 0.0})


class OperatorProfileProjector:
    def __init__(self, validator: OperatorSchemaValidator, policy: ProjectionPolicy | None = None) -> None:
        self._validator = validator
        self._policy = policy or ProjectionPolicy()
        self._index = {dimension: index for index, dimension in enumerate(validator.dimension_order)}

    def cold_start(self, operator_id: str, timestamp: str) -> dict[str, Any]:
        profile = {
            "profile_version": "operator-profile-v1",
            "operator_id": operator_id,
            "company_id": "northstar-regional-markets",
            "capability_schema_version": "northstar-operator-v1",
            "capabilities": [0.5] * 19,
            "capability_evidence": [0.0] * 19,
            "stable_summary": "Evidence is currently insufficient to characterize this operator's task capabilities.",
            "recent_notes": "",
            "knowledge": [],
            "authority": [],
            "access": [],
            "evidence_stats": {"total_events": 0},
            "recent_evidence_ids": [],
            "last_updated": timestamp,
        }
        self._validator.validate_profile(profile)
        return profile

    def reconstruct(self, operator_id: str, events: Iterable[dict[str, Any]], *, timestamp: str) -> dict[str, Any]:
        profile = self.cold_start(operator_id, timestamp)
        for event in events:
            self._validator.validate_event(event)
            if event["operator_id"] != operator_id:
                raise ValueError("cannot project another operator's evidence")
            self._apply(profile, event)
        profile["last_updated"] = timestamp
        self._refresh_narrative(profile)
        self._validator.validate_profile(profile)
        return profile

    def _apply(self, profile: dict[str, Any], event: dict[str, Any]) -> None:
        verification = event["verification"]
        verification_status = verification["status"]
        task = event.get("task_context", {})
        factor = (
            self._policy.verification_factor[verification_status]
            * self._policy.difficulty_factor.get(task.get("difficulty"), 0.5)
            * self._policy.scaffolding_factor.get(task.get("scaffolding_level"), 0.5)
            * self._policy.method_factor[verification["method"]]
        )
        for implication in event["capability_implications"]:
            effect = implication["effect"]
            if effect == "NEUTRAL" or factor == 0:
                continue
            if effect == "NEGATIVE" and not (verification_status == "VERIFIED" and event["attribution"] == "OPERATOR_ERROR"):
                continue
            index = self._index[implication["capability_id"]]
            sign = 1 if effect == "POSITIVE" else -1
            strength = implication["strength"]
            profile["capabilities"][index] = _clamp(profile["capabilities"][index] + sign * self._policy.capability_step[strength] * factor)
            profile["capability_evidence"][index] = _clamp(profile["capability_evidence"][index] + self._policy.evidence_step[strength] * factor)

        self._apply_knowledge(profile, event)
        stats = profile["evidence_stats"]
        stats["total_events"] += 1
        if event["event_type"] == "TASK_VERIFIED_CORRECT" and verification_status == "VERIFIED":
            stats["verified_successes"] = stats.get("verified_successes", 0) + 1
        if event["event_type"] == "TASK_VERIFIED_INCORRECT" and verification_status == "VERIFIED":
            stats["verified_errors"] = stats.get("verified_errors", 0) + 1
        if event["event_type"] in {"TASK_RETURNED", "TASK_NARROWED", "REASSIGNMENT_REQUESTED", "AUTHORITY_DECLINED"}:
            stats["task_returns"] = stats.get("task_returns", 0) + 1
        if event["event_type"] == "CLARIFICATION_REQUESTED":
            stats["clarification_requests"] = stats.get("clarification_requests", 0) + 1
        if event["event_type"] == "OPERATOR_CORRECTED_AI":
            stats["operator_corrected_ai"] = stats.get("operator_corrected_ai", 0) + 1
        stats["last_event_id"] = event["event_id"]
        profile["recent_evidence_ids"] = (profile["recent_evidence_ids"] + [event["event_id"]])[-50:]

    @staticmethod
    def _apply_knowledge(profile: dict[str, Any], event: dict[str, Any]) -> None:
        by_topic = {item["topic"]: item for item in profile["knowledge"]}
        for implication in event["knowledge_implications"]:
            if implication["effect"] == "NO_CHANGE":
                continue
            topic = implication["topic"]
            record = by_topic.get(topic, {
                "topic": topic,
                "level": "UNKNOWN",
                "confidence": "LOW",
                "status": "UNCERTAIN",
                "basis_type": "OBSERVED_TASK",
                "basis_event_ids": [],
            })
            if implication["effect"] == "SUPPORTS":
                record["level"] = {"WEAK": "VAGUE", "MODERATE": "GENERAL", "STRONG": "DETAILED"}[implication["strength"]]
                record["confidence"] = "HIGH" if event["verification"]["status"] == "VERIFIED" else "MEDIUM"
                record["status"] = "CURRENT" if event["verification"]["status"] == "VERIFIED" else "UNCERTAIN"
            elif implication["effect"] == "CONTRADICTS":
                record["status"] = "CONTRADICTED"
                record["confidence"] = "HIGH" if event["verification"]["status"] == "VERIFIED" else "MEDIUM"
            else:
                record["confidence"] = "LOW"
                record["status"] = "UNCERTAIN"
            record["basis_event_ids"] = (record["basis_event_ids"] + [event["event_id"]])[-50:]
            record["last_observed"] = event["timestamp"]
            by_topic[topic] = record
        profile["knowledge"] = list(by_topic.values())

    def _refresh_narrative(self, profile: dict[str, Any]) -> None:
        observed = [
            (dimension, profile["capabilities"][index], profile["capability_evidence"][index])
            for dimension, index in self._index.items()
            if profile["capability_evidence"][index] > 0
        ]
        if not observed:
            profile["stable_summary"] = "Evidence is currently insufficient to characterize this operator's task capabilities."
            profile["recent_notes"] = ""
            return
        strongest = sorted(observed, key=lambda item: item[2], reverse=True)[:4]
        details = "; ".join(f"{name}={capability:.3f} (evidence {confidence:.3f})" for name, capability, confidence in strongest)
        profile["stable_summary"] = (f"Provisional evidence-backed observations under {self._policy.version}: {details}. Authority and access remain independent hard constraints.")[:1600]
        profile["recent_notes"] = f"Projected from {profile['evidence_stats']['total_events']} ledger event(s); unobserved dimensions remain unknown."[:500]


class OperatorProfileStore:
    def __init__(self, runtime_root: Path, validator: OperatorSchemaValidator) -> None:
        self._root = runtime_root.resolve()
        self._validator = validator

    def write(self, profile: dict[str, Any]) -> Path:
        self._validator.validate_profile(profile)
        operator_id = profile["operator_id"]
        if not re.fullmatch(r"[A-Za-z0-9._-]+", operator_id):
            raise ValueError(f"unsafe operator_id: {operator_id!r}")
        path = self._root / "operators" / operator_id / "profile.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with temporary.open("r+b") as stream:
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        return path


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)
