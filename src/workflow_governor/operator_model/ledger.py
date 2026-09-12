from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any, Iterable

from workflow_governor.operator_model.schema import OperatorSchemaValidator


_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")
_DEDUPE_PREFIXES = ("response_id:", "verification_id:")


class OperatorEvidenceLedger:
    def __init__(self, runtime_root: Path, validator: OperatorSchemaValidator) -> None:
        self._root = runtime_root.resolve()
        self._validator = validator

    def append(self, event: dict[str, Any]) -> bool:
        self._validator.validate_event(event)
        path = self.path_for(event["operator_id"])
        existing = list(self.read(event["operator_id"]))
        event_key = _dedupe_key(event)
        for recorded in existing:
            if recorded["event_id"] == event["event_id"] or (event_key and _dedupe_key(recorded) == event_key):
                if recorded != event:
                    raise ValueError("duplicate evidence identity has conflicting content")
                return False
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(event, separators=(",", ":"), sort_keys=True) + "\n"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        return True

    def read(self, operator_id: str) -> Iterable[dict[str, Any]]:
        path = self.path_for(operator_id)
        if not path.exists():
            return ()
        events = tuple(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        for event in events:
            self._validator.validate_event(event)
            if event["operator_id"] != operator_id:
                raise ValueError("operator ledger contains a cross-operator event")
        return events

    def path_for(self, operator_id: str) -> Path:
        if not _SAFE_ID.fullmatch(operator_id):
            raise ValueError(f"unsafe operator_id: {operator_id!r}")
        return self._root / "operators" / operator_id / "evidence.jsonl"


def _dedupe_key(event: dict[str, Any]) -> tuple[str, ...]:
    refs = event.get("source_refs", ())
    return tuple(sorted(ref for ref in refs if ref.startswith(_DEDUPE_PREFIXES)))
