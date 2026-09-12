from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Any

from workflow_governor.core.models import EvidenceRef
from workflow_governor.core.serialization import to_primitive
from workflow_governor.execution.runner import HumanHandoff
from workflow_governor.human.contracts import HumanTaskResponse, ResponseValidationResult


_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


class FileHumanInteractionStore:
    """Small replaceable P01 inbox/outbox for bounded human artifacts."""

    def __init__(self, runtime_root: Path) -> None:
        self._root = runtime_root.resolve()

    def write_handoff(self, handoff: HumanHandoff) -> Path:
        directory = self._interaction_dir(handoff.workflow_id, handoff.handoff_id)
        return self._write_idempotent(directory / "handoff.json", to_primitive(handoff))

    def write_submission(self, response: HumanTaskResponse) -> Path:
        directory = self._interaction_dir(response.workflow_id, response.handoff_id) / "responses"
        return self._write_idempotent(directory / f"{self._safe(response.response_id)}.json", to_primitive(response))

    def read_submission(self, workflow_id: str, handoff_id: str, response_id: str) -> dict[str, Any]:
        path = self._interaction_dir(workflow_id, handoff_id) / "responses" / f"{self._safe(response_id)}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def write_validation(self, response: HumanTaskResponse, result: ResponseValidationResult) -> Path:
        directory = self._interaction_dir(response.workflow_id, response.handoff_id) / "validation"
        return self._write_idempotent(directory / f"{self._safe(response.response_id)}.json", to_primitive(result))

    def register_artifact(self, response: HumanTaskResponse, filename: str, content: bytes) -> EvidenceRef:
        safe_name = Path(filename).name
        if safe_name != filename or safe_name in {"", ".", ".."}:
            raise ValueError("artifact filename must be a simple basename")
        digest = sha256(response.response_id.encode() + b"\0" + safe_name.encode() + b"\0" + content).hexdigest()
        artifact_id = f"HA-{digest[:20]}"
        directory = self._interaction_dir(response.workflow_id, response.handoff_id) / "responses" / self._safe(response.response_id) / "artifacts"
        path = directory / f"{artifact_id}-{safe_name}"
        directory.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != content:
            raise ValueError("artifact identifier collision")
        if not path.exists():
            path.write_bytes(content)
        relative = path.relative_to(self._root).as_posix()
        return EvidenceRef(source=relative, artifact_id=artifact_id, label=safe_name)

    def is_registered(self, handoff_id: str, response_id: str, evidence_ref: EvidenceRef) -> bool:
        if not evidence_ref.artifact_id:
            return False
        try:
            handoff = self._safe(handoff_id)
            response = self._safe(response_id)
        except ValueError:
            return False
        expected_parent = self._root / "workflows"
        candidate = (self._root / evidence_ref.source).resolve()
        if not candidate.is_relative_to(expected_parent) or not candidate.is_file():
            return False
        parts = candidate.parts
        return handoff in parts and response in parts and candidate.name.startswith(f"{evidence_ref.artifact_id}-")

    def _interaction_dir(self, workflow_id: str, handoff_id: str) -> Path:
        return self._root / "workflows" / self._safe(workflow_id) / "artifacts" / "human" / self._safe(handoff_id)

    @staticmethod
    def _safe(value: str) -> str:
        if not _SAFE_ID.fullmatch(value):
            raise ValueError(f"unsafe identifier: {value!r}")
        return value

    @staticmethod
    def _write_idempotent(path: Path, value: Any) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
        if path.exists():
            if path.read_text(encoding="utf-8") != encoded:
                raise ValueError(f"identifier already exists with different content: {path.name}")
            return path
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(encoded, encoding="utf-8")
        with temporary.open("r+b") as stream:
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        return path
