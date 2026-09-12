# GB10 integration handoff

## Ownership and synchronization

Started from clean `e7acd3d` with Thomas's frontend but no backend. While local integration was running, fetched and fast-forwarded `797ccaf` (Track B implementation `5f622f6`). Existing frontend edits were preserved; no teammate backend files were overwritten. Local branch: `integration/gb10-case001`. No push/merge to remote performed.

Track ownership remains Daniel: workspace/artifact state; Thomas: planning/execution/model; Frank: human/operator. User explicitly requested the complete deployment slice on this GB10. Missing UI-facing adapters live in `src/governor/`, independently of teammate-owned `src/workflow_governor/`. They are integration implementations to hand back to their owners, not replacements for shared modules. No policy, case, persona, evaluator or original specifications are modified.

## Real interfaces consumed

- `core.models`: WorkspaceMap, EvidenceContent/Ref, WorkflowPlan, TaskSpec/Context/Result and executor/status enums.
- `Planner` + `PlanValidator`: actual local model draft becomes shared WorkflowPlan; authorized references, operations and DAG are checked.
- `PlanLifecycle.approve`: browser approval creates a serialized shared approval history.
- `MinimalTaskRunner`: executes the selected task with actual completed predecessor states; the HTTP UI deliberately schedules one task at a time. No automatic approval in P01Coordinator is used.
- `LocalModelExecutor` + `ModelContextBuilder`: validate granted/required sources and bound the context before the adapter invokes Qwen.
- `DeterministicExecutor`: `extract_fields` and `compare_dates` operate on actual source values. `governor.deterministic` only assembles the batch and line citations.
- Core execution events and results persist as `tasks/<id>/attempts/<attempt>/core-execution.json`; `mock_assisted` is false.

No shared contract changes were needed. Two semantic gaps are handled only in the UI adapter: pre-approval revision requests (shared lifecycle currently revises approved plans only), and human response/resume persistence (not yet supplied in the synced Track B code). Approved-plan edits after execution are not supported by this demo and fail rather than silently replacing results. Profile/persona functionality is not implemented.

## HTTP interface (same origin as frontend)

- GET `/api/health`, `/api/workspaces`, `/api/workflows`, `/api/workflows/<id>`
- POST `/api/workflows`: `{objective, workspace: "vendor-activation", name?}` → persisted workflow + background planning.
- POST `/api/workflows/<id>/approve`, `/plan` (retry), `/revise` `{note}`.
- POST `/api/workflows/<id>/tasks/<task>/execute` → real deterministic/model execution.
- POST `.../human`: `{action, operator, judgment, reason}`. All fields required. Complete records bounded review, not external authority. Other actions block with an explicit reason.
- POST `.../resume`: `{note}` → ready/needs-human after dependency checks.
- POST `/api/workflows/<id>/evidence/<evidence>`: `{action}` → local review/conflict annotation. Evidence request delivery is deliberately rejected as not connected.

Workflow snapshots match `frontend/src/types.ts`; sources, operation/error, actual results, approval and source grants are durable. API errors never mark tasks complete. Only configured workspace roots and scoped handbook sections are readable. Runtime never reads case README, hidden truth, persona memory, evaluators or provenance. New evidence upload is not implemented; future grants require an explicit server configuration change.

## Evidence and authority

Discovery exposes filenames/metadata first, then up to 8 model-selected workspace files, at most 2 explicitly referenced pending-record originals, and 2 scoped policy extracts. Each source is snapshotted with SHA-256 and original line numbers. Findings require source ID and a valid nonempty line; the server resolves the exact source text. Invented source IDs or absent lines cause a visible failed/blocked task. Human responses are separate cited artifacts. Full model requests, output, usage and elapsed time are recorded; thinking is disabled for bounded demo execution and no private reasoning is stored.

Review completion and business activation are distinct. Final status Completed means the review plan finished. Any external blocker, missing evidence, unverified authority or required handoff remains in the final result. No connector writes to VendorLink, procurement, email or any real business system. OpenClaw remains an independently verified demo and is not an executor in this application.

## Observed integration failure and repair

The first real run completed planning, deterministic work, local synthesis and the browser human clarification/resume cycle, then correctly blocked final synthesis because the final task cited a predecessor's source that was omitted from its task context. The source and quote were real, but not in that invocation's bounded context. The context builder now inherits only source IDs actually cited by dependency results (within the already granted workflow snapshots). Strict citation validation was retained. Original failed model output/error remains on disk; a new full run verifies the repaired adapter.

Further runtime validation found model-generated quote text could omit Markdown or become empty under constrained decoding. The final model citation contract now requests **source ID and line number only**; the server resolves the exact nonempty original line from the granted snapshot. It never generates evidence quotations from model text. Missing sources, missing/blank lines, and incompatible legacy quotations remain errors. Source references alone do not mechanically prove semantic entailment; the visible human review remains necessary. Legacy formatting-only corrections retain explicit audit metadata.

A completeness check also found that metadata selection picked a pending checklist without its referenced original document. Discovery now follows at most two exact authorized filenames named on REVIEW/FAIL/BLOCKED/PENDING/MISSING/EXPIRED source lines. This is a generic one-hop retrieval rule, not a case-specific filename/result rule. The latest CASE_001 run includes the original certificate through the recorded checklist reference. Approved historical plans/snapshots are not silently rewritten; a new workflow validates the expanded discovery.
