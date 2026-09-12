from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from io import StringIO
import json
from typing import Any, Callable, Mapping

from workflow_governor.core.errors import BlockedExecution, ExecutionError
from workflow_governor.core.models import (
    ExecutionStatus,
    ExecutorType,
    TaskContext,
    TaskResult,
    TaskSpec,
)


Operation = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class DeterministicExecutor:
    def __init__(self) -> None:
        self._operations: dict[str, Operation] = {
            "compare_dates": self._compare_dates,
            "compare_threshold": self._compare_threshold,
            "percentage": self._percentage,
            "reconcile_quantity": self._reconcile_quantity,
            "select_latest_authorized_revision": self._latest_revision,
            "structured_equal": self._structured_equal,
            "extract_fields": self._extract_fields,
            "join_records": self._join_records,
            "validate_json_schema": self._validate_json_schema,
        }

    @property
    def supported_operations(self) -> frozenset[str]:
        return frozenset(self._operations)

    def execute(self, task: TaskSpec, context: TaskContext) -> TaskResult:
        if task.executor_type is not ExecutorType.DETERMINISTIC:
            return self._failed(task, "deterministic executor received a different executor type")
        if task.task_id != context.task_id:
            return self._failed(task, "task and context IDs do not match")
        missing = self._missing_required_sources(task, context)
        if missing:
            return TaskResult(
                task.task_id,
                ExecutionStatus.BLOCKED,
                task.executor_type,
                unresolved=(f"missing required sources: {', '.join(sorted(missing))}",),
            )
        operation = self._operations.get(task.operation or "")
        if operation is None:
            return self._failed(task, f"unsupported deterministic operation: {task.operation}")
        try:
            output = operation(context.operation_inputs)
        except BlockedExecution as exc:
            return TaskResult(
                task.task_id,
                ExecutionStatus.BLOCKED,
                task.executor_type,
                evidence_refs=task.evidence_requirements,
                unresolved=(str(exc),),
            )
        except Exception as exc:
            return self._failed(task, str(exc))
        return TaskResult(
            task.task_id,
            ExecutionStatus.COMPLETED,
            task.executor_type,
            evidence_refs=task.evidence_requirements + task.policy_requirements,
            rationale=f"executed deterministic operation {task.operation}",
            output={"operation": task.operation, "inputs": dict(context.operation_inputs), "result": output},
        )

    @staticmethod
    def _missing_required_sources(task: TaskSpec, context: TaskContext) -> set[str]:
        granted = set(context.granted_sources)
        present = {item.ref.source for item in context.evidence + context.policy}
        available = granted & present if granted else present
        required = {ref.source for ref in task.evidence_requirements + task.policy_requirements}
        return required - available

    @staticmethod
    def _failed(task: TaskSpec, error: str) -> TaskResult:
        return TaskResult(
            task.task_id,
            ExecutionStatus.FAILED,
            ExecutorType.DETERMINISTIC,
            evidence_refs=task.evidence_requirements + task.policy_requirements,
            error=error,
        )

    @staticmethod
    def _decimal(value: Any, name: str) -> Decimal:
        try:
            return Decimal(str(value))
        except Exception as exc:
            raise ExecutionError(f"{name} must be numeric") from exc

    @staticmethod
    def _compare_dates(inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            left = date.fromisoformat(str(inputs["left"]))
            right = date.fromisoformat(str(inputs["right"]))
        except (KeyError, ValueError) as exc:
            raise ExecutionError("compare_dates requires ISO left and right dates") from exc
        relation = "equal" if left == right else ("before" if left < right else "after")
        return {"relation": relation, "days": (left - right).days}

    @classmethod
    def _compare_threshold(cls, inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        value = cls._decimal(inputs.get("value"), "value")
        threshold = cls._decimal(inputs.get("threshold"), "threshold")
        operator = str(inputs.get("operator", "gte"))
        comparisons = {
            "lt": value < threshold,
            "lte": value <= threshold,
            "gt": value > threshold,
            "gte": value >= threshold,
            "eq": value == threshold,
        }
        if operator not in comparisons:
            raise ExecutionError(f"unsupported threshold operator: {operator}")
        return {"value": str(value), "threshold": str(threshold), "operator": operator, "passes": comparisons[operator]}

    @classmethod
    def _percentage(cls, inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        numerator = cls._decimal(inputs.get("numerator"), "numerator")
        denominator = cls._decimal(inputs.get("denominator"), "denominator")
        if denominator == 0:
            raise ExecutionError("percentage denominator must not be zero")
        places = int(inputs.get("places", 2))
        if places < 0 or places > 12:
            raise ExecutionError("places must be between 0 and 12")
        raw = numerator / denominator * Decimal("100")
        quantum = Decimal(1).scaleb(-places)
        rounded = raw.quantize(quantum, rounding=ROUND_HALF_UP)
        return {"numerator": str(numerator), "denominator": str(denominator), "percentage": str(rounded)}

    @classmethod
    def _reconcile_quantity(cls, inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        ordered = cls._decimal(inputs.get("ordered"), "ordered")
        received = cls._decimal(inputs.get("received"), "received")
        if ordered <= 0:
            raise ExecutionError("ordered quantity must be positive")
        rate = (min(received, ordered) / ordered * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {"ordered": str(ordered), "received": str(received), "variance": str(received - ordered), "fill_percentage": str(rate)}

    @staticmethod
    def _latest_revision(inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        records = inputs.get("records")
        if not isinstance(records, list):
            raise ExecutionError("records must be a list")
        authorized = [record for record in records if isinstance(record, dict) and record.get("authorized") is True]
        if not authorized:
            raise BlockedExecution("no authorized revision is available")
        try:
            latest_number = max(int(record["revision"]) for record in authorized)
        except (KeyError, TypeError, ValueError) as exc:
            raise ExecutionError("authorized records require numeric revision values") from exc
        latest = [record for record in authorized if int(record["revision"]) == latest_number]
        if len(latest) != 1:
            raise ExecutionError("latest authorized revision is ambiguous")
        return {"revision": latest_number, "record": latest[0]}

    @staticmethod
    def _structured_equal(inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        if "left" not in inputs or "right" not in inputs:
            raise ExecutionError("structured_equal requires left and right")
        return {"equal": inputs["left"] == inputs["right"]}

    @staticmethod
    def _extract_fields(inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        content = inputs.get("content")
        fields = inputs.get("fields")
        format_name = inputs.get("format")
        if not isinstance(content, str) or not isinstance(fields, list):
            raise ExecutionError("extract_fields requires string content and field list")
        if len(content) > 1_000_000:
            raise ExecutionError("structured input exceeds 1,000,000 characters")
        if format_name == "json":
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                raise ExecutionError("JSON extraction requires an object")
            return {"values": {field: parsed.get(field) for field in fields}}
        if format_name == "csv":
            rows = list(csv.DictReader(StringIO(content)))
            return {"rows": [{field: row.get(field) for field in fields} for row in rows]}
        raise ExecutionError("format must be json or csv")

    @staticmethod
    def _join_records(inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        left = inputs.get("left")
        right = inputs.get("right")
        left_key = inputs.get("left_key")
        right_key = inputs.get("right_key", left_key)
        if not isinstance(left, list) or not isinstance(right, list) or not isinstance(left_key, str) or not isinstance(right_key, str):
            raise ExecutionError("join_records requires record lists and key names")
        index: dict[Any, list[dict[str, Any]]] = {}
        for record in right:
            if not isinstance(record, dict) or right_key not in record:
                raise ExecutionError(f"right record missing key {right_key}")
            index.setdefault(record[right_key], []).append(record)
        joined: list[dict[str, Any]] = []
        unmatched: list[dict[str, Any]] = []
        for record in left:
            if not isinstance(record, dict) or left_key not in record:
                raise ExecutionError(f"left record missing key {left_key}")
            matches = index.get(record[left_key], [])
            if not matches:
                unmatched.append(record)
            for match in matches:
                joined.append({"left": record, "right": match})
        return {"joined": joined, "unmatched_left": unmatched}

    @staticmethod
    def _validate_json_schema(inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            import jsonschema
        except ImportError as exc:
            raise BlockedExecution("jsonschema dependency is unavailable") from exc
        if "instance" not in inputs or "schema" not in inputs:
            raise ExecutionError("validate_json_schema requires instance and schema")
        try:
            jsonschema.validate(instance=inputs["instance"], schema=inputs["schema"])
        except jsonschema.ValidationError as exc:
            raise ExecutionError(f"JSON Schema validation failed: {exc.message}") from exc
        except jsonschema.SchemaError as exc:
            raise ExecutionError(f"invalid JSON Schema: {exc.message}") from exc
        return {"valid": True}

