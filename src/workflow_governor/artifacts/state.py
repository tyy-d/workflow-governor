"""Reconstruct persisted facts without scheduling or executing tasks."""

from dataclasses import dataclass, field
import os
import re

from workflow_governor.core.errors import ContractValidationError, PersistenceError, WorkspaceAccessError
from workflow_governor.core.persistence_json import logical_path, safe_id
from workflow_governor.core.substrate import Diagnostic, WorkflowManifest


@dataclass
class WorkflowSnapshot:
    manifest: WorkflowManifest
    workspace_map: object = None
    evidence: tuple = ()
    current_plan: object = None
    plans: dict = field(default_factory=dict)
    tasks: dict = field(default_factory=dict)
    statuses: dict = field(default_factory=dict)
    contexts: dict = field(default_factory=dict)
    results: dict = field(default_factory=dict)
    findings: dict = field(default_factory=dict)
    corrections: tuple = ()
    final_state: object = None
    final_artifacts: dict = field(default_factory=dict)
    diagnostics: tuple = ()


class WorkflowStateLoader:
    def __init__(self, store):
        self.store = store

    def load(self, workflow_id, *, strict=False):
        store = self.store
        snapshot = WorkflowSnapshot(store.load_manifest(workflow_id))
        diagnostics = []

        def attempt(path, callback):
            try:
                return callback()
            except (PersistenceError, ContractValidationError, WorkspaceAccessError, OSError, ValueError, TypeError):
                try:
                    logical_path(path)
                    diagnostic_path = path
                except ContractValidationError:
                    diagnostic_path = None
                diagnostics.append(Diagnostic("damaged_artifact", "Persisted artifact could not be restored", diagnostic_path, "error"))
                return None

        def optional(path, callback):
            return attempt(path, lambda: callback() if store.path(workflow_id, path).exists() else None)

        # Invalid structural roots are fatal, not a brand-new empty workflow.
        for folder in ("plans", "tasks", "artifacts", "findings", "final", "final/artifacts"):
            try:
                if not store.path(workflow_id, folder).is_dir():
                    raise PersistenceError("Invalid root structure")
            except (PersistenceError, OSError) as exc:
                raise PersistenceError("Invalid workflow root structure", (Diagnostic("invalid_structure", "Workflow directory is missing or unsafe", folder, "fatal"),)) from exc

        snapshot.workspace_map = optional("workspace_map.json", lambda: store.load_workspace_map(workflow_id))
        snapshot.evidence = optional("input/retrieved_evidence.json", lambda: store.load_evidence(workflow_id)) or ()
        revisions = []
        for path in attempt("plans", lambda: sorted(store.path(workflow_id, "plans").iterdir())) or []:
            match = re.fullmatch(r"plan_([0-9]+)\.json", path.name)
            if match and int(match[1]) > 0 and path.name == f"plan_{int(match[1]):04d}.json":
                revisions.append(int(match[1]))
            elif not path.name.endswith(".tmp"):
                diagnostics.append(Diagnostic("invalid_plan_filename", "Unknown plan artifact was skipped", "plans", "error"))
        revisions.sort()
        for revision in revisions:
            record = attempt(f"plans/plan_{revision:04d}.json", lambda: store.load_plan(workflow_id, revision))
            if record is not None:
                snapshot.plans[revision] = record
        current = snapshot.manifest.current_plan_revision
        if current is not None:
            snapshot.current_plan = snapshot.plans.get(current)
            if snapshot.current_plan is None:
                diagnostics.append(Diagnostic("missing_current_plan", "Manifest points to an unavailable plan revision", "manifest.json", "error"))
            else:
                projection = attempt("plan.md", lambda: store.path(workflow_id, "plan.md").read_text(encoding="utf-8"))
                if projection is not None and projection != snapshot.current_plan.display_text:
                    diagnostics.append(Diagnostic("stale_plan_projection", "plan.md differs from the committed plan", "plan.md", "error"))
        for revision in revisions:
            if current is None or revision > current:
                diagnostics.append(Diagnostic("uncommitted_plan", "Revision is beyond the manifest commit pointer", f"plans/plan_{revision:04d}.json"))

        entries = attempt("tasks", lambda: sorted(store.path(workflow_id, "tasks").iterdir())) or []
        for entry in entries:
            task_id = entry.name
            try:
                safe_id(task_id)
            except ContractValidationError:
                diagnostics.append(Diagnostic("invalid_task_directory", "An invalid task directory was skipped", "tasks", "error"))
                continue
            for kind, bucket, loader in (("task", snapshot.tasks, store.load_task),
                                         ("status", snapshot.statuses, store.load_task_status),
                                         ("context", snapshot.contexts, store.load_context),
                                         ("result", snapshot.results, store.load_result)):
                path = f"tasks/{task_id}/{kind}.json"
                value = optional(path, lambda: loader(workflow_id, task_id))
                if value is not None:
                    bucket[task_id] = value
            if task_id not in snapshot.tasks:
                diagnostics.append(Diagnostic("missing_task", "Task directory has no usable task definition", f"tasks/{task_id}/task.json", "error"))
            if task_id in snapshot.results and task_id in snapshot.statuses:
                if str(snapshot.results[task_id].status) != snapshot.statuses[task_id]:
                    diagnostics.append(Diagnostic("status_conflict", "Persisted status differs from the result; neither was rewritten", f"tasks/{task_id}/status.json", "error"))
            if snapshot.statuses.get(task_id, "").upper() == "COMPLETED" and task_id not in snapshot.results:
                diagnostics.append(Diagnostic("missing_completed_result", "Completion was recorded but its result is unavailable", f"tasks/{task_id}/result.json", "error"))

        if snapshot.current_plan:
            for task in snapshot.current_plan.plan.tasks:
                if task.task_id not in snapshot.tasks:
                    diagnostics.append(Diagnostic("missing_planned_task", "A planned task has no saved definition", f"tasks/{task.task_id}/task.json", "error"))
        finding_paths = attempt("findings", lambda: sorted(store.path(workflow_id, "findings").glob("*.json"))) or []
        for path in finding_paths:
            value = attempt("findings", lambda: store.load_finding(workflow_id, path.stem))
            if value is not None:
                snapshot.findings[path.stem] = value
        corrections = attempt("corrections.jsonl", lambda: store.load_corrections(workflow_id))
        if corrections:
            snapshot.corrections, errors = corrections
            diagnostics.extend(errors)
        snapshot.final_state = optional("final/state.json", lambda: store.load_final_state(workflow_id))
        index = optional("final/artifact_index.json", lambda: store.load_final_artifact_index(workflow_id)) or {}
        for relative in index:
            value = attempt(f"final/artifacts/{relative}", lambda: store.load_final_artifact(workflow_id, relative))
            if value is not None:
                snapshot.final_artifacts[relative] = value
        final_root = store.path(workflow_id, "final/artifacts")
        for directory, folders, files in os.walk(final_root, followlinks=False):
            for name in folders + files:
                relative = (type(final_root)(directory) / name).relative_to(final_root).as_posix()
                safe = attempt(f"final/artifacts/{relative}", lambda: store.path(workflow_id, f"final/artifacts/{relative}"))
                if safe is not None and name in files and relative not in index and not name.endswith(".tmp"):
                    diagnostics.append(Diagnostic("unindexed_final_artifact", "Final artifact has no committed index entry", f"final/artifacts/{relative}", "error"))
        snapshot.diagnostics = tuple(diagnostics)
        if strict and diagnostics:
            raise PersistenceError("Workflow contains persistence diagnostics", diagnostics)
        return snapshot
