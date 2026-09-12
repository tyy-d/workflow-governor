from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class OperatorSchemaValidationError(ValueError):
    pass


class OperatorSchemaValidator:
    def __init__(self, repository_root: Path) -> None:
        root = repository_root.resolve()
        self._profile_schema = self._load(root / "operator_model" / "profile.schema.json")
        self._event_schema = self._load(root / "operator_model" / "evidence_event.schema.json")
        capability_schema = self._load(root / "company" / "northstar" / "schemas" / "northstar_operator_capability_schema.json")
        self.dimension_order = tuple(capability_schema["dimension_order"])
        if len(self.dimension_order) != 19:
            raise OperatorSchemaValidationError("northstar-operator-v1 must contain exactly 19 dimensions")
        self._profile = Draft202012Validator(self._profile_schema, format_checker=FormatChecker())
        self._event = Draft202012Validator(self._event_schema, format_checker=FormatChecker())

    def validate_profile(self, profile: dict[str, Any]) -> None:
        self._validate(self._profile, profile, "profile")
        if len(profile.get("capabilities", ())) != len(self.dimension_order):
            raise OperatorSchemaValidationError("profile capability vector does not match canonical dimension order")

    def validate_event(self, event: dict[str, Any]) -> None:
        self._validate(self._event, event, "evidence event")

    @staticmethod
    def _validate(validator: Draft202012Validator, value: dict[str, Any], label: str) -> None:
        errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
        if errors:
            rendered = "; ".join(f"{'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors)
            raise OperatorSchemaValidationError(f"invalid {label}: {rendered}")

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))
