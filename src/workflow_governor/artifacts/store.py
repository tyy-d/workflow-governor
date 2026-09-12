"""Single-writer filesystem persistence. Manifest is the plan commit pointer."""

import hashlib
import os
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

from workflow_governor.core.codec import from_dict, primitive
from workflow_governor.core.config import confined
from workflow_governor.core.errors import ContractValidationError, PersistenceError, WorkspaceAccessError
from workflow_governor.core.models import PlanStatus, TaskContext, TaskResult, TaskSpec, WorkflowPlan, WorkspaceMap
from workflow_governor.core.persistence_json import json_text, logical_path, parse_json, safe_id, utc_now
from workflow_governor.core.substrate import Diagnostic, RetrievedEvidence, StoredRecord, ValidatedModel, WorkflowManifest


@dataclass(frozen=True)
class StoredPlan(ValidatedModel):
    revision: int
    plan: WorkflowPlan
    status: PlanStatus | None
    display_text: str

    def _validate(self):
        if self.revision < 1:
            raise ContractValidationError("Plan revisions start at one")


def atomic_write(path: Path, data: bytes):
    """Flush a temporary sibling, then atomically replace the destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temp = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        if os.name == "posix":
            fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


class ArtifactStore:
    def __init__(self, config):
        self.config = config

    def workflow_root(self, workflow_id):
        safe_id(workflow_id)
        try:
            return confined(self.config.workflows_root, workflow_id)
        except (OSError, WorkspaceAccessError) as exc:
            raise PersistenceError("Invalid workflow root", (Diagnostic("invalid_root", "Workflow root is unsafe", severity="fatal"),)) from exc

    def path(self, workflow_id, relative):
        logical_path(relative)
        try:
            return confined(self.workflow_root(workflow_id), relative)
        except (OSError, WorkspaceAccessError) as exc:
            raise PersistenceError("Unsafe artifact path", (Diagnostic("unsafe_path", "Artifact path is unsafe", relative, "error"),)) from exc

    def _write(self, workflow_id, relative, data):
        try:
            root = self.workflow_root(workflow_id)
            if not root.is_dir():
                raise PersistenceError("Workflow does not exist")
            atomic_write(self.path(workflow_id, relative), data)
        except OSError as exc:
            raise PersistenceError("Artifact write failed", (Diagnostic("write_failed", "Artifact write failed", relative, "error"),)) from exc

    def _save(self, workflow_id, relative, record):
        self._write(workflow_id, relative, json_text(record.to_dict()).encode("utf-8"))

    def _load(self, workflow_id, relative, cls):
        try:
            data = parse_json(self.path(workflow_id, relative).read_text(encoding="utf-8"))
            return from_dict(cls, data)
        except PersistenceError:
            raise
        except (OSError, ValueError, TypeError, ContractValidationError) as exc:
            raise PersistenceError("Artifact could not be decoded", (Diagnostic("invalid_artifact", "Artifact is missing, unreadable, or malformed", relative, "error"),)) from exc

    def create_workflow(self, workflow_id, objective, grants):
        now = utc_now()
        manifest = WorkflowManifest(workflow_id, objective, tuple(grants), now, now)
        root = self.workflow_root(workflow_id)
        try:
            root.mkdir(parents=True, exist_ok=False)
            for folder in ("input", "plans", "tasks", "artifacts", "findings", "final/artifacts"):
                self.path(workflow_id, folder).mkdir(parents=True)
            self._save(workflow_id, "manifest.json", manifest)
        except OSError as exc:
            raise PersistenceError("Workflow creation failed; existing workflows are never overwritten") from exc
        return manifest

    def save_manifest(self, manifest):
        manifest.to_dict()
        self.load_manifest(manifest.workflow_id)
        if manifest.current_plan_revision is not None:
            self.load_plan(manifest.workflow_id, manifest.current_plan_revision)
        self._save(manifest.workflow_id, "manifest.json", manifest)

    def load_manifest(self, workflow_id):
        try:
            manifest = self._load(workflow_id, "manifest.json", WorkflowManifest)
            if manifest.workflow_id != workflow_id:
                raise ContractValidationError("Manifest identity does not match directory")
            return manifest
        except (PersistenceError, ContractValidationError) as exc:
            raise PersistenceError("Fatal workflow manifest error", (Diagnostic("invalid_manifest", "Workflow manifest cannot be trusted", "manifest.json", "fatal"),)) from exc

    def save_workspace_map(self, workflow_id, workspace_map):
        manifest = self.load_manifest(workflow_id)
        grant = workspace_map.metadata.get("grant")
        if grant not in [g.to_dict() for g in manifest.grants] or workspace_map.root != grant.get("root"):
            raise WorkspaceAccessError("Workspace map does not match a workflow grant")
        self._save(workflow_id, "workspace_map.json", workspace_map)

    def load_workspace_map(self, workflow_id):
        result = self._load(workflow_id, "workspace_map.json", WorkspaceMap)
        manifest = self.load_manifest(workflow_id)
        grant = result.metadata.get("grant")
        if grant not in [g.to_dict() for g in manifest.grants] or result.root != grant.get("root"):
            raise PersistenceError("Persisted workspace map has an invalid grant")
        return result

    def save_evidence(self, workflow_id, evidence):
        items = tuple(evidence)
        if not all(isinstance(item, RetrievedEvidence) for item in items):
            raise ContractValidationError("Expected retrieved evidence records")
        self._save(workflow_id, "input/retrieved_evidence.json", StoredRecord("retrieved_evidence", {"items": [item.to_dict() for item in items]}))

    def load_evidence(self, workflow_id):
        record = self._load_envelope(workflow_id, "input/retrieved_evidence.json", "retrieved_evidence")
        try:
            return tuple(RetrievedEvidence.from_dict(item) for item in record.payload["items"])
        except (KeyError, TypeError, ContractValidationError) as exc:
            raise PersistenceError("Invalid retrieved evidence artifact") from exc

    def plan_revisions(self, workflow_id):
        directory = self.path(workflow_id, "plans")
        if not directory.is_dir():
            raise PersistenceError("Missing or invalid plan directory")
        revisions = []
        for path in directory.iterdir():
            if path.name.startswith("plan_") and path.suffix == ".json":
                value = path.stem[5:]
                if not value.isdigit() or int(value) < 1 or path.name != f"plan_{int(value):04d}.json":
                    raise PersistenceError("Invalid plan revision filename")
                revisions.append(int(value))
        return sorted(revisions)

    def save_plan(self, workflow_id, plan, *, status=None, text=None):
        """Accept Thomas's WorkflowPlan and optional existing PlanStatus, unchanged."""
        manifest = self.load_manifest(workflow_id)
        if not isinstance(plan, WorkflowPlan):
            raise ContractValidationError("Expected the shared WorkflowPlan contract")
        revision = max(self.plan_revisions(workflow_id), default=0) + 1
        if text is None:
            text = f"# {plan.objective}\n\n" + "\n".join(f"- {t.task_id}: {t.objective}" for t in plan.tasks) + "\n"
        record = StoredPlan(revision, plan, status, text)
        self._save(workflow_id, f"plans/plan_{revision:04d}.json", record)
        # The revision is immutable. On interruption, an unreferenced revision is diagnosed.
        manifest = replace(manifest, current_plan_revision=revision, updated_at=utc_now())
        self._save(workflow_id, "manifest.json", manifest)
        # A derived projection. Reload can detect an interrupted projection write.
        self._write(workflow_id, "plan.md", text.encode("utf-8"))
        return revision

    def load_plan(self, workflow_id, revision=None):
        if revision is None:
            revision = self.load_manifest(workflow_id).current_plan_revision
        if type(revision) is not int or revision < 1:
            raise ContractValidationError("Expected a positive plan revision")
        record = self._load(workflow_id, f"plans/plan_{revision:04d}.json", StoredPlan)
        if record.revision != revision:
            raise PersistenceError("Plan revision identity mismatch")
        return record

    def _save_task_record(self, workflow_id, record, kind):
        safe_id(record.task_id)
        self.load_manifest(workflow_id)
        self._save(workflow_id, f"tasks/{record.task_id}/{kind}.json", record)

    def _load_task_record(self, workflow_id, task_id, kind, cls):
        safe_id(task_id)
        record = self._load(workflow_id, f"tasks/{task_id}/{kind}.json", cls)
        if record.task_id != task_id:
            raise PersistenceError("Task identity does not match artifact directory")
        return record

    def save_task(self, workflow_id, task):
        if not isinstance(task, TaskSpec):
            raise ContractValidationError("Expected shared TaskSpec")
        self._save_task_record(workflow_id, task, "task")

    def load_task(self, workflow_id, task_id):
        return self._load_task_record(workflow_id, task_id, "task", TaskSpec)

    def save_context(self, workflow_id, context):
        if not isinstance(context, TaskContext):
            raise ContractValidationError("Expected shared TaskContext")
        self._save_task_record(workflow_id, context, "context")

    def load_context(self, workflow_id, task_id):
        return self._load_task_record(workflow_id, task_id, "context", TaskContext)

    def save_result(self, workflow_id, result):
        if not isinstance(result, TaskResult):
            raise ContractValidationError("Expected shared TaskResult")
        self._save_task_record(workflow_id, result, "result")

    def load_result(self, workflow_id, task_id):
        return self._load_task_record(workflow_id, task_id, "result", TaskResult)

    def save_task_status(self, workflow_id, task_id, status):
        """Persist producer-supplied mechanical status, without deriving readiness."""
        safe_id(task_id)
        if not isinstance(status, str) or not status.strip():
            raise ContractValidationError("A persisted status must be a nonempty string")
        self._save(workflow_id, f"tasks/{task_id}/status.json", StoredRecord("task_status", {"task_id": task_id, "status": str(status)}))

    def load_task_status(self, workflow_id, task_id):
        safe_id(task_id)
        record = self._load(workflow_id, f"tasks/{task_id}/status.json", StoredRecord)
        if (record.kind != "task_status" or record.payload.get("task_id") != task_id
                or not isinstance(record.payload.get("status"), str) or not record.payload["status"].strip()):
            raise PersistenceError("Invalid task status record")
        return record.payload["status"]

    def _envelope(self, kind, payload, text=""):
        return StoredRecord(kind, primitive(payload), text)

    def save_finding(self, workflow_id, finding_id, finding, *, text=""):
        safe_id(finding_id)
        self._save(workflow_id, f"findings/{finding_id}.json", self._envelope("finding", finding, text))
        paths = sorted(self.path(workflow_id, "findings").glob("*.json"))
        projection = "\n".join(self.load_finding(workflow_id, p.stem).display_text for p in paths)
        self._write(workflow_id, "findings.md", (projection + "\n").encode("utf-8"))

    def load_finding(self, workflow_id, finding_id):
        safe_id(finding_id)
        return self._load_envelope(workflow_id, f"findings/{finding_id}.json", "finding")

    def _load_envelope(self, workflow_id, relative, kind):
        result = self._load(workflow_id, relative, StoredRecord)
        if result.kind != kind:
            raise PersistenceError("Stored record kind mismatch")
        return result

    def append_correction(self, workflow_id, correction):
        record = self._envelope("correction", correction)
        path = self.path(workflow_id, "corrections.jsonl")
        self.load_manifest(workflow_id)
        import json
        line = json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8") + b"\n"
        try:
            # A torn final entry is preserved; separate it before appending valid history.
            needs_separator = False
            if path.exists() and path.stat().st_size:
                with path.open("rb") as handle:
                    handle.seek(-1, os.SEEK_END)
                    needs_separator = handle.read(1) != b"\n"
            with path.open("ab") as handle:
                if needs_separator:
                    handle.write(b"\n")
                handle.write(line)
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise PersistenceError("Correction append failed") from exc

    def load_corrections(self, workflow_id, *, strict=False):
        path = self.path(workflow_id, "corrections.jsonl")
        records, diagnostics = [], []
        if not path.exists():
            return (), ()
        try:
            with path.open("rb") as handle:
                for number, line in enumerate(handle, 1):
                    try:
                        record = StoredRecord.from_dict(parse_json(line.decode("utf-8")))
                        if record.kind != "correction":
                            raise ContractValidationError("Wrong correction kind")
                        records.append(record)
                    except (ValueError, TypeError, ContractValidationError):
                        diagnostics.append(Diagnostic("invalid_correction", f"Malformed correction at line {number}", "corrections.jsonl", "error"))
        except OSError as exc:
            raise PersistenceError("Correction log cannot be read") from exc
        if strict and diagnostics:
            raise PersistenceError("Correction log is partially corrupt", diagnostics)
        return tuple(records), tuple(diagnostics)

    def save_final_state(self, workflow_id, state):
        self._save(workflow_id, "final/state.json", self._envelope("final_state", state))

    def load_final_state(self, workflow_id):
        return self._load_envelope(workflow_id, "final/state.json", "final_state")

    def save_final_artifact(self, workflow_id, relative, content):
        logical_path(relative)
        if not isinstance(content, (bytes, str)):
            raise ContractValidationError("Final artifact must be bytes or UTF-8 text")
        data = content.encode("utf-8") if isinstance(content, str) else content
        index_path = self.path(workflow_id, "final/artifact_index.json")
        index = self.load_final_artifact_index(workflow_id) if index_path.exists() else {}
        self._write(workflow_id, f"final/artifacts/{relative}", data)
        index[relative] = {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        self._save(workflow_id, "final/artifact_index.json", StoredRecord("final_artifact_index", index))

    def load_final_artifact_index(self, workflow_id):
        record = self._load_envelope(workflow_id, "final/artifact_index.json", "final_artifact_index")
        for relative, metadata in record.payload.items():
            logical_path(relative)
            if (type(metadata) is not dict or set(metadata) != {"sha256", "size"}
                    or type(metadata["size"]) is not int or metadata["size"] < 0
                    or not isinstance(metadata["sha256"], str) or len(metadata["sha256"]) != 64):
                raise PersistenceError("Invalid final artifact index")
        return record.payload

    def load_final_artifact(self, workflow_id, relative):
        logical_path(relative)
        index = self.load_final_artifact_index(workflow_id)
        if relative not in index:
            raise PersistenceError("Final artifact is not indexed")
        try:
            data = self.path(workflow_id, f"final/artifacts/{relative}").read_bytes()
        except OSError as exc:
            raise PersistenceError("Final artifact cannot be read") from exc
        if hashlib.sha256(data).hexdigest() != index[relative]["sha256"] or len(data) != index[relative]["size"]:
            raise PersistenceError("Final artifact hash or size mismatch")
        return data
