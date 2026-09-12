"""Track A owned records. Shared planner/executor types remain in models.py."""

import re
from dataclasses import dataclass, fields
from typing import Any, Literal

from .codec import DurableModel, _validate_fields
from .errors import ContractValidationError
from .models import EvidenceContent, EvidenceRef
from .persistence_json import logical_path, safe_id, validate_timestamp


class ValidatedModel(DurableModel):
    def __post_init__(self):
        _validate_fields(self)


@dataclass(frozen=True)
class Diagnostic(ValidatedModel):
    code: str
    message: str
    path: str | None = None
    severity: Literal["warning", "error", "fatal"] = "warning"

    def _validate(self):
        safe_id(self.code)
        if self.path is not None:
            logical_path(self.path)


@dataclass(frozen=True)
class WorkspaceGrant(ValidatedModel):
    grant_id: str
    root: str


@dataclass(frozen=True)
class RetrievedEvidence(ValidatedModel):
    reference: EvidenceRef
    discovered_sha256: str | None
    sha256: str | None
    status: Literal["unchanged", "changed", "missing", "unreadable", "unsupported", "limited", "invalid_utf8", "unverified"]
    content: str
    truncated: bool
    retrieved_at: str
    diagnostics: tuple[Diagnostic, ...] = ()

    def _validate(self):
        for value in (self.sha256, self.discovered_sha256):
            if value is not None and not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ContractValidationError("Invalid SHA-256 hash")
        validate_timestamp(self.retrieved_at)

    def as_content(self) -> EvidenceContent:
        return EvidenceContent(self.reference, self.content, untrusted_document=True)


@dataclass(frozen=True)
class WorkflowManifest(ValidatedModel):
    workflow_id: str
    objective: str
    grants: tuple[WorkspaceGrant, ...]
    created_at: str
    updated_at: str
    current_plan_revision: int | None = None

    def _validate(self):
        if not self.objective.strip():
            raise ContractValidationError("Workflow objective is required")
        validate_timestamp(self.created_at)
        validate_timestamp(self.updated_at)
        if self.current_plan_revision is not None and self.current_plan_revision < 1:
            raise ContractValidationError("Plan revisions start at one")
        if len({g.grant_id for g in self.grants}) != len(self.grants):
            raise ContractValidationError("Duplicate grant ID")


@dataclass(frozen=True)
class StoredRecord(ValidatedModel):
    """Generic envelope for findings/corrections/final metadata, not a new Finding schema."""
    kind: str
    payload: dict[str, Any]
    display_text: str = ""

    def _validate(self):
        safe_id(self.kind)


@dataclass(frozen=True)
class DiscoveryLimits(ValidatedModel):
    max_files: int = 1000
    max_bytes_per_file: int = 1_000_000
    max_total_bytes: int = 10_000_000
    max_preview_chars: int = 300

    def _validate(self):
        if any(getattr(self, f.name) < 0 for f in fields(self)):
            raise ContractValidationError("Limits cannot be negative")


@dataclass(frozen=True)
class RetrievalLimits(ValidatedModel):
    max_chars_per_file: int = 20_000
    max_total_chars: int = 40_000
    max_bytes_per_file: int = 1_000_000
    max_total_bytes: int = 10_000_000

    def _validate(self):
        if any(getattr(self, f.name) < 0 for f in fields(self)):
            raise ContractValidationError("Limits cannot be negative")
