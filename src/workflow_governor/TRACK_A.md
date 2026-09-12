# Track A integration and GB10 Ubuntu handoff

Track A is a standard-library implementation for Python 3.11+. It does not need
a GPU, model server, cloud API, or dependency installation. The existing Track B
`jsonschema` dependency and development dependencies are unchanged.

## Run on Ubuntu / GB10

From the repository root:

```bash
export PYTHONPATH="$PWD/src"
python3 -u -m unittest discover -s tests -v
python3 -u -m workflow_governor.track_a discover \
  --workflow-id track-a-demo \
  --objective 'Inspect authorized workspace evidence' \
  --grant-id case-workspace \
  --grant-root cases/CASE_001_VENDOR_ACTIVATION/workspace \
  --path documents/VENDORLINK_STATUS_NVID-10482.json
python3 -u -m workflow_governor.track_a inspect track-a-demo --strict
```

The second command creates a workflow; use a new ID for a new run. Inspection is
read-only and can run from another process. Files live in
`runtime/workflows/<workflow_id>/`. No business completion is asserted by this demo.
No runtime output belongs in Git.

For the entire repository regression suite using the existing dev dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -u -m pytest -v --durations=0 -o log_cli=true -o addopts=''
```

`RuntimeConfig(repository_root, runtime_root=None)` takes machine-local paths.
Relative runtime roots resolve against the repository, never the caller's later
working directory. `WORKFLOW_GOVERNOR_RUNTIME` overrides the default `runtime`.
`RuntimeConfig.from_environment()` also accepts `WORKFLOW_GOVERNOR_REPOSITORY`.
Persisted workspace grants contain repository-relative paths, so a checkout can
move from Windows to Ubuntu while retaining the same logical evidence locations.

## Interface change record: additive durable serialization

Baseline: Thomas's shared types in main at `797ccaf`. Track A reuses these exact
`WorkflowPlan`, `TaskSpec`, `TaskContext`, `TaskResult`, `FileRecord`, `WorkspaceMap`,
`EvidenceRef`, `ExecutorType`, `ExecutionStatus`, and `PlanStatus` classes.

Requested integration change: add `DurableModel` as a serialization mixin to the
existing dataclasses. No constructor fields, enum members, task statuses,
dependency rules, planning rules, or human-routing behavior are changed.
The existing `to_json()` remains unchanged for Track B prompts. The new
`to_dict()` / `from_dict()` methods validate a separate version-1 durable format,
including nested records, enums, safe IDs and paths, UTC dates, and finite JSON.
Unknown schema versions/fields are rejected. Existing unversioned persisted data
needs an explicit migration; it is not silently guessed into the new format.

`TaskSpec` still has no status. Status is saved separately by the producer.
`ExecutionStatus` is reused as-is; Track A does not create a competing TaskStatus.
`WorkflowPlan` still has no plan status; `save_plan(..., status=PlanStatus.APPROVED)`
stores the existing status in a `StoredPlan` envelope. Omitting it preserves `None`.
For a Track B `PlanRecord`, pass `record.plan` and `status=record.status`.

There is no shared standalone `Finding` class on this baseline. `save_finding`
accepts a JSON object (or dataclass) in a versioned `StoredRecord` envelope, with
optional human-readable `text`. It preserves producer fields without assigning
confidence, taxonomy, or business semantics. A future Finding contract can use
this transport without a second competing schema. Frank's human/persona/operator
modules and `HumanTaskResponse` remain outside this change.

## Connect the components

```python
from pathlib import Path
from workflow_governor.core.config import RuntimeConfig
from workflow_governor.workspace import (
    WorkspaceScout, WorkspaceGrant, DiscoveryLimits, RetrievalLimits,
)
from workflow_governor.artifacts import ArtifactStore, WorkflowStateLoader

config = RuntimeConfig(Path.cwd())
grant = WorkspaceGrant('selected', 'authorized/workspace')
scout = WorkspaceScout(config, grants=(grant,))
workspace_map = scout.discover(grant, DiscoveryLimits())
retrieved = scout.retrieve(workspace_map, ['notes.md'], RetrievalLimits())
planner_evidence = tuple(item.as_content() for item in retrieved)

store = ArtifactStore(config)
store.create_workflow('run-1', 'Inspect the selected evidence', (grant,))
store.save_workspace_map('run-1', workspace_map)
store.save_evidence('run-1', retrieved)
# Use the shared objects actually produced by the other tracks:
# store.save_plan('run-1', plan_record.plan, status=plan_record.status)
# store.save_task('run-1', task)
# store.save_context('run-1', context)
# store.save_result('run-1', result)
# store.save_task_status('run-1', task.task_id, result.status)
snapshot = WorkflowStateLoader(ArtifactStore(config)).load('run-1')
```

Select usable evidence based on its reported status before supplying it to a
planner. A changed file returns new content and both hashes, not a silent claim
that the discovery hash still matches. `EvidenceRef.source` is the logical
repository-relative source used by Thomas's granted-source checks;
`artifact_id='sha256:<digest>'` records the current hash and `label` the grant ID.
The file record path and every retrieve request are relative to the grant root.
Map metadata records the grant, timestamp, byte count, and diagnostics. File
metadata records extension, mtime, SHA-256, extraction status, preview, and errors.
Text/Markdown/JSON/CSV extraction returns bounded UTF-8 text, not business parsing.

Loading a workspace map never grants filesystem access. After a restart the
trusted application must explicitly construct the scout with the accepted grants.
Do not let ordinary workspace documents or untrusted callers select grants.

## Persistence and recovery behavior

- All replacement writes use a sibling temp file, flush/fsync, and `os.replace()`.
  Ubuntu also fsyncs the parent directory. Plan revisions never overwrite older
  revisions. The manifest is the commit pointer; `plan.md` is a derived display.
- A crash can leave an uncommitted revision or stale display. Reload reports it;
  it never promotes an orphan revision or silently rewrites approval state.
- Corrections are append-only JSON Lines. A torn last entry is preserved and
  separated before the next append; valid later entries remain recoverable.
- Final files live in `final/artifacts/`; a versioned index stores hashes/sizes.
  Missing, changed, or unindexed final files are diagnosed on reload.
- `WorkflowSnapshot` restores plans, definitions, explicit statuses, contexts,
  results, findings, corrections, final metadata/files, and diagnostics. It is
  an inspection object, not an executable run queue or Governor.
- Missing/corrupt manifests or required root directories are fatal. Localized
  corruption preserves usable artifacts and identifies damage. Strict loading
  raises on any diagnostic. Conflicting status/result records are left intact
  with a diagnostic; completion is never inferred from missing data.
- The store assumes one trusted writer per workflow. Filesystem path checks are
  not an OS sandbox against a hostile process concurrently replacing directories.
  Symlinks and Windows reparse/junction paths are rejected, even for in-root links.
- Hashing consumes the byte budget. Files larger than the remaining/per-file
  budget have `sha256=None` and a limit diagnostic; no prefix hash masquerades
  as a complete file hash. Character budgets apply after bounded byte reads.
- Task/context/result/finding saves replace their current artifacts. Plan
  revisions and correction entries preserve history; this is not a general
  event-sourcing system or automatic executor-resume implementation.

CASE_001 coverage is a **structural discovery/persistence smoke test**. It only
reads the explicitly granted `workspace/`. Tests never load hidden evaluator or
ground-truth content. Full business evaluation and actual GB10 hardware/model
integration remain separate work.
