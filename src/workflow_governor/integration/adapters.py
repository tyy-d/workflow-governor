from __future__ import annotations

from collections.abc import Mapping, Sequence

from workflow_governor.artifacts.store import ArtifactStore
from workflow_governor.core.config import RuntimeConfig
from workflow_governor.core.errors import ContractValidationError, WorkspaceAccessError
from workflow_governor.core.persistence_json import logical_path
from workflow_governor.core.substrate import (
    DiscoveryLimits,
    RetrievalLimits,
    RetrievedEvidence,
    WorkspaceGrant,
)
from workflow_governor.core.models import TaskContext, TaskSpec
from workflow_governor.execution.runner import (
    ExecutionEvent,
    RunState,
    TaskContextProvider,
)
from workflow_governor.integration.p01 import WorkspaceBundle
from workflow_governor.workspace.scout import WorkspaceScout, allowed


_PRIVATE_COMPONENTS = {"personas", "persona_memory"}
_USABLE_STATUS = "unchanged"


def _validate_runtime_path(path: str) -> None:
    """Apply Track A path checks plus repository-wide private-material rules."""
    logical_path(path)
    allowed(path)
    if _PRIVATE_COMPONENTS.intersection(path.casefold().split("/")):
        raise WorkspaceAccessError("Persona-private source is excluded from runtime access")


class AuthorizedWorkspaceProvider:
    """Prepare a workspace only from trusted grants and explicit selections.

    The objective is intentionally absent from all access decisions. Selection
    values are relative to their associated grant, while EvidenceRef.source is
    the logical grant-root-relative source produced by Track A.
    """

    def __init__(
        self,
        config: RuntimeConfig,
        grants: Sequence[WorkspaceGrant],
        *,
        primary_grant_id: str,
        evidence_selections: Mapping[str, Sequence[str]],
        policy_selections: Mapping[str, Sequence[str]],
        discovery_limits: DiscoveryLimits | None = None,
        retrieval_limits: RetrievalLimits | None = None,
    ) -> None:
        self._config = config
        self._grants = tuple(grants)
        self._primary_grant_id = primary_grant_id
        self._evidence_selections = self._normalize_selections(evidence_selections)
        self._policy_selections = self._normalize_selections(policy_selections)
        self._discovery_limits = discovery_limits or DiscoveryLimits()
        self._retrieval_limits = retrieval_limits or RetrievalLimits()
        grant_ids = [grant.grant_id for grant in self._grants]
        if len(grant_ids) != len(set(grant_ids)):
            raise ContractValidationError("Workspace grant IDs must be unique")
        if primary_grant_id not in grant_ids:
            raise ContractValidationError("Primary workspace grant is not configured")
        configured = set(grant_ids)
        selected = set(self._evidence_selections) | set(self._policy_selections)
        if not selected <= configured:
            raise ContractValidationError("A selection references an unconfigured grant")
        for grant in self._grants:
            _validate_runtime_path(grant.root)
        overlaps = {
            (grant_id, path)
            for grant_id, paths in self._evidence_selections.items()
            for path in paths
            if path in self._policy_selections.get(grant_id, ())
        }
        if overlaps:
            raise ContractValidationError("Evidence and policy selections must be distinct")

    @property
    def grants(self) -> tuple[WorkspaceGrant, ...]:
        return self._grants

    @staticmethod
    def _normalize_selections(
        selections: Mapping[str, Sequence[str]],
    ) -> dict[str, tuple[str, ...]]:
        if not isinstance(selections, Mapping):
            raise ContractValidationError("Selections must map grant IDs to paths")
        normalized: dict[str, tuple[str, ...]] = {}
        for grant_id, paths in selections.items():
            if isinstance(paths, (str, bytes)) or not isinstance(paths, Sequence):
                raise ContractValidationError("Selections require an explicit path sequence")
            unique = tuple(dict.fromkeys(paths))
            for path in unique:
                _validate_runtime_path(path)
            normalized[grant_id] = unique
        return normalized

    def prepare(self, objective: str) -> WorkspaceBundle:
        # The objective is planner input only; construction-time values govern IO.
        del objective
        scout = WorkspaceScout(self._config, self._grants)
        maps = {
            grant.grant_id: scout.discover(grant, self._discovery_limits)
            for grant in self._grants
        }
        for workspace_map in maps.values():
            for record in workspace_map.files:
                _validate_runtime_path(record.relative_path)
        evidence_records = self._retrieve_role(scout, maps, self._evidence_selections)
        policy_records = self._retrieve_role(scout, maps, self._policy_selections)
        all_records = evidence_records + policy_records
        return WorkspaceBundle(
            maps[self._primary_grant_id],
            tuple(record.as_content() for record in evidence_records),
            tuple(record.as_content() for record in policy_records),
            all_records,
        )

    def _retrieve_role(
        self,
        scout: WorkspaceScout,
        maps: Mapping[str, object],
        selections: Mapping[str, tuple[str, ...]],
    ) -> tuple[RetrievedEvidence, ...]:
        records: list[RetrievedEvidence] = []
        for grant in self._grants:
            paths = selections.get(grant.grant_id, ())
            if not paths:
                continue
            retrieved = scout.retrieve(maps[grant.grant_id], paths, self._retrieval_limits)
            for record in retrieved:
                if (
                    record.status != _USABLE_STATUS
                    or record.truncated
                    or record.sha256 is None
                    or record.sha256 != record.discovered_sha256
                    or record.reference.artifact_id != f"sha256:{record.sha256}"
                    or record.reference.label != grant.grant_id
                ):
                    raise WorkspaceAccessError(
                        f"Required evidence is not usable: {record.reference.source} ({record.status})"
                    )
            records.extend(retrieved)
        return tuple(records)


class ArtifactExecutionEventSink:
    """Persist producer-supplied execution facts without deriving new state."""

    def __init__(self, store: ArtifactStore) -> None:
        self._store = store

    def record(self, event: ExecutionEvent) -> None:
        self._store.save_task_status(event.workflow_id, event.task_id, event.status)
        if event.result is not None:
            self._store.save_result(event.workflow_id, event.result)


class PersistingTaskContextProvider:
    """Persist the exact bounded context returned by another provider."""

    def __init__(
        self,
        provider: TaskContextProvider,
        store: ArtifactStore,
        workflow_id: str,
    ) -> None:
        self._provider = provider
        self._store = store
        self._workflow_id = workflow_id

    def get_context(self, task: TaskSpec, run_state: RunState) -> TaskContext:
        context = self._provider.get_context(task, run_state)
        self._store.save_context(self._workflow_id, context)
        return context
