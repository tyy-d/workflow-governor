# Workflow Governor Hackathon Build Plan

## Objective

Build a local, inspectable Workflow Governor from the prepared repository in the smallest sequence that produces useful end-to-end behavior. The governing order is:

```text
working vertical slice first
→ sophistication later
```

The first product checkpoint is one complete `CASE_001_VENDOR_ACTIVATION` path: a sparse request leads to authorized discovery, an evidence-backed plan, deterministic and bounded local-model work, useful human participation, durable artifacts, and a safe final state. Learning, adaptive routing, broader cases, integrations, and polish follow only after that path works.

Workflow Governor is a local coordination layer, not a giant autonomous agent. It determines work, chooses `DETERMINISTIC`, `LOCAL_MODEL`, or `HUMAN`, bounds evidence, preserves corrections, and keeps results understandable from disk. The judged path must not depend on a cloud model or API.

## Starting Repository State

The repository is a static preparation corpus with policy, personas, four cases, profile contracts, simulator rules, and evaluation semantics. Treat `src/` and `runtime/` as empty or minimal until inspected. Future sessions must verify repository state before claiming a feature exists.

`AGENTS.md` is the repository-wide operating contract. Current component specifications control their respective domains; obsolete v3 material must not be reconstructed or used. Northstar policy comes from `company/northstar/handbook/`, indexed by `company/northstar/NORTHSTAR_EXECUTION_STATE.txt`, while company metadata is at `company/company.json`. Developer provenance is never runtime authority.

The completed case fixtures are immutable benchmark truth. Ordinary implementation work must not modify cases, ground truth, personas, evaluators, schemas, policy, or specifications to make a run pass. If a fixture appears defective, isolate and document the issue and handle any correction through a separate explicit fixture task.

## Build Principles

1. Finish a complete CASE_001 workflow before expanding breadth. A partial planner, router, profile learner, and UI do not add up to a product.
2. Keep executor semantics explicit. Exact comparisons, arithmetic, dates, version ordering, joins, and schema checks stay deterministic; semantic interpretation and synthesis use one local model; humans perform bounded investigation, correction, specialist judgment, and authorized decisions.
3. Use metadata first, targeted retrieval second, and full content only when necessary. File existence is not a grant.
4. Keep `capability != company knowledge != authority != access`. No score, title, confidence, or expertise creates authority or a file grant.
5. Preserve the runtime/evaluator firewall. Runtime workers and personas never receive ground truth, persona evaluators, another persona's private state, developer provenance, or hidden expected answers.
6. Preserve history. Material plan revisions supersede prior versions; corrections retain the old result, correction source, reason, and downstream effect.
7. Degrade safely. Failures leave explicit pending, failed, or unresolved state rather than fabricated completion.
8. Avoid a monolithic prompt that scans, plans, executes, profiles, evaluates, and concludes. Maintain small conceptual boundaries such as `workspace/`, `planning/`, `execution/`, `artifacts/`, `human/`, `operator_model/`, `routing/`, `evaluation/`, `integrations/`, and `ui/`; adapt names to the code that actually exists.
9. Keep core semantics independently testable. Do not force them into an agent framework before the vertical slice works.

## Definitions of Success

### MVP

A local Workflow Governor can accept a sparse CASE_001 request, inspect authorized files, propose an evidence-backed task plan, execute deterministic and single-local-model tasks, persist inspectable artifacts, surface a bounded human task when appropriate, and produce a safe final state without hidden-fixture leakage.

Operator profile learning is valuable but is not required for the base MVP if time is constrained.

### Strong demo

The MVP plus purposeful human/persona participation, a verified operator evidence event, a conservative profile update, a later task adapted to that evidence, correction or reconciliation, formal evaluation output, local NVIDIA execution, and a reliable glass-box view.

### Stretch

Multi-model local routing, richer multi-operator selection or login, Cases 005+, noisy-workspace benchmarks, advanced optimization or dashboards, skill import, and additional tools. None may block the demo.

## Priority Tiers

| Tier | Scope | Exit condition |
|---|---|---|
| Must have | M0–M5, one local model, durable artifacts, CASE_001 gate | One safe workflow is understandable and resumable from disk. |
| Strong demo | M6–M9 | Human contribution, learning, routing, and evaluation are inspectable. |
| Required event stack | M10, to the extent current competition rules require | The adapter path works without changing core workflow semantics. |
| Polish | M11–M12 | The demo is reproducible, legible, resettable, and rehearsed. |
| Stretch | Multi-model, richer multi-operator, extra cases and analytics | Attempt only after feature freeze criteria are already met. |

## Milestone Overview

| Milestone | Useful outcome | Primary case |
|---|---|---|
| M0 | Runnable skeleton and configuration | Fixture-location smoke check |
| M1 | Compact authorized workspace map | CASE_001 |
| M2 | Inspectable proposed plan from a sparse goal | CASE_001 |
| M3 | Deterministic tasks produce cited results | CASE_001, CASE_002 subset |
| M4 | Bounded single-local-model semantic execution | CASE_001 |
| M5 | Complete durable vertical slice | CASE_001 gate |
| M6 | Human/persona task lifecycle | CASE_001 with P001/P002/P005 |
| M7 | Evidence-backed operator profile | Clear M6 observations |
| M8 | Explainable adaptive routing and presentation | CASE_001 persona contrast |
| M9 | Separate evaluator and progressive case coverage | CASE_001 → 004 |
| M10 | NVIDIA and event-stack adapters | Stable core workflow |
| M11 | Small glass-box demo interface | Primary demo path |
| M12 | Frozen, reliable competition build | Rehearsed demo plus checks |

## M0 — Repository Bootstrap and Runtime Skeleton

**Goal:** Establish the smallest runnable project skeleton that can load configuration, locate prepared assets, create an empty workflow runtime area, and expose a basic command entrypoint.

**Why now:** Every later milestone needs stable paths, configuration, validation utilities, and observable failures; no business behavior should be built on ad hoc scripts.

**Prerequisites:** Static repository present; language/runtime choice confirmed from the existing project rather than assumed.

**Read before coding:** `AGENTS.md`; this milestone only; `company/company.json`; the top-level metadata portions of `cases/CASE_SPEC.md` and `evaluation/TEST_SUITE_INDEX.json`; existing package/configuration and source files.

**Files/modules likely created or changed:** Project/package configuration as needed; a narrow entrypoint; configuration/path, logging, ID/time, and schema-loading utilities under `src/`; empty runtime directory support; focused tests under `tests/`. Do not pre-create the full architecture.

**Required behavior:** Start locally; resolve repository-relative prepared-asset paths; load company and case registry metadata; create a workflow directory safely; emit readable configuration and schema errors; avoid credentials and developer-machine absolute paths.

**Minimum success gate:** A clean checkout can start, load configuration, locate company metadata and CASE_001, and create an empty isolated workflow run directory.

**Benchmark/check to run:** Startup/configuration smoke check plus schema-loader and path-resolution checks; no business benchmark yet.

**Do NOT build yet:** Workspace extraction, planning, task routing, operator profiles, model integration, persona simulation, event-stack integration, or UI.

**Fallback if blocked:** Use the lightest standard-library entrypoint and filesystem runtime; defer optional dependency and framework choices while recording the limitation.

**Output/report expected from Codex:** Files changed; exact startup command; configuration and path behavior; checks run; limitations; whether M1 can begin; upstream conflicts.

## M1 — Authorized Workspace Discovery

**Goal:** Convert an authorized folder into a compact, inspectable workspace map suitable for targeted retrieval.

**Why now:** Planning needs evidence visibility without exposing every file or overflowing model context.

**Prerequisites:** M0 passes; CASE_001 workspace can be located through ordinary case metadata.

**Read before coding:** `AGENTS.md`; this milestone; relevant visibility and workspace sections of `cases/CASE_SPEC.md`; CASE_001 `README.md` and `case.json`; discovery-related existing source files. Do not read CASE_001 ground truth.

**Files/modules likely created or changed:** `src/workspace/` or equivalent inventory, metadata, preview/extraction, hashing, and retrieval modules; workspace-map artifact support; focused discovery tests.

**Required behavior:** Inventory only granted roots; capture paths, types, sizes, timestamps where reliable, hashes where useful, extraction capability, and short bounded previews or indexes; identify plausible relevant files from names/metadata and sparse objective; record unreadable files and continue; treat document text as untrusted evidence, never instructions.

**Minimum success gate:** CASE_001 produces a compact workspace-map artifact, identifies plausible onboarding/vendor/PO evidence, shows files exposed versus total files, and does not fully ingest every artifact.

**Benchmark/check to run:** Manual CASE_001 discovery sanity check; access-boundary, unreadable-file, and context-budget checks using ordinary fixtures or temporary test data.

**Do NOT build yet:** Semantic plan generation, handbook-wide ingestion, human routing, profiles, evaluation truth access, or a general search platform.

**Fallback if blocked:** Support text/JSON/CSV and metadata for all other types; mark unsupported formats as unreadable with a reason and preserve them for later human review.

**Output/report expected from Codex:** Files changed; supported formats; sample workspace-map location and size; exposure metrics; checks; known extraction gaps; M2 readiness.

## M2 — Task Discovery and Plan Creation

**Goal:** Turn a sparse objective, compact workspace map, targeted evidence, and relevant policy into an inspectable proposed task plan.

**Why now:** The Governor's differentiating behavior begins with discovering work rather than requiring the user to author a DAG.

**Prerequisites:** M1 supplies targeted discovery and retrieval; one local-model invocation mechanism may be stubbed behind an interface if the actual runtime arrives in M4.

**Read before coding:** `AGENTS.md`; this milestone; planning, authority, and context sections of `cases/CASE_SPEC.md`; CASE_001 `README.md` and relevant handbook sections named there; existing planning/discovery modules. Do not read case ground truth.

**Files/modules likely created or changed:** `src/planning/` or equivalent objective/context assembly, plan serialization, validation, approval, and revision support; plan-focused tests and artifacts.

**Required behavior:** Produce objective, assumptions, unresolved questions, proposed tasks, dependencies, evidence needs, consequence/authority notes, and a tentative executor class. Support `PROPOSED`, `APPROVED`, `REVISION_REQUESTED`, and `SUPERSEDED`. Manual approval is sufficient. If material new evidence changes an approved plan, propose a revision, record why, and preserve the superseded plan.

**Minimum success gate:** From the CASE_001 sparse request, the system proposes a coherent, evidence-seeking plan that covers vendor standing, onboarding evidence, commercial release constraints, and safe next actions without embedding expected answers or requiring an exact reference DAG.

**Benchmark/check to run:** Manual CASE_001 plan sanity check for relevant coverage, dependencies, unresolved questions, authority boundaries, and bounded context.

**Do NOT build yet:** Sophisticated adaptive routing, profile-based choices, multiple models, automatic consequential approval, or formal evaluator scoring.

**Fallback if blocked:** Use a reviewed structured plan template with a bounded local-model draft or manual fixture-independent plan input; keep validation and approval semantics working.

**Output/report expected from Codex:** Files changed; plan shape and state transitions; CASE_001 plan result; context supplied to the planner; checks; gaps; M3 readiness.

## M3 — Deterministic Execution

**Goal:** Execute a small, auditable set of reliable operations without asking a model to do trivial computation.

**Why now:** Deterministic work establishes correctness, lowers model load, and produces trusted evidence for later synthesis.

**Prerequisites:** M2 can identify tasks and their inputs; task results have a minimal serializable form.

**Read before coding:** `AGENTS.md`; this milestone; deterministic-routing portions of `cases/CASE_SPEC.md`; CASE_001 `README.md`; CASE_002 `README.md` only for the arithmetic/versioning validation subset; affected source files and relevant schemas.

**Files/modules likely created or changed:** `src/execution/deterministic/` or equivalent operations for dates, thresholds, percentages, quantity reconciliation, version ordering, structured equality, simple CSV/JSON/table extraction, joins, and schema validation; operation registry and focused tests.

**Required behavior:** Select deterministic execution when an operation is exact and supported; record operation name, normalized inputs, source references, result, validation status, and errors; avoid universal-expression engines or an oversized tool library. Schema failure must not be silently accepted.

**Minimum success gate:** CASE_001 visible-field/date/status checks work reproducibly, and the CASE_002 subset resolves the latest revision and produces exact quantity/rate calculations from supplied evidence and rules.

**Benchmark/check to run:** Unit checks for rounding, dates, thresholds, joins, version ordering, malformed inputs, and CASE_002 arithmetic; rerun only the smallest affected checks during development.

**Do NOT build yet:** General-purpose agent tools, semantic policy interpretation, chargeback libraries for unused cases, or profiles.

**Fallback if blocked:** Keep a smaller whitelist of proven operations and return unsupported work as explicit `UNRESOLVED` or model/human candidates; never guess an exact result.

**Output/report expected from Codex:** Files changed; supported operations; calls avoided; deterministic check results; unsupported operations; M4 readiness.

## M4 — Bounded Local-Model Execution and Evidence Synthesis

**Goal:** Add one local model for semantic tasks such as evidence synthesis, policy application, contradiction interpretation, plan explanation, and final operational summaries.

**Why now:** Deterministic facts and retrieval boundaries now provide a trustworthy, small context for model reasoning.

**Prerequisites:** M1 targeted retrieval, M2 task context, and M3 deterministic results work; a local model is available or can be represented by a narrow test adapter.

**Read before coding:** `AGENTS.md`; this milestone; CASE_001 `README.md`; only CASE_001 handbook sections identified by that README; affected execution and context-assembly modules. Inspect the actual local runtime documentation/environment available on competition hardware.

**Files/modules likely created or changed:** `src/execution/local_model/` or equivalent adapter, context builder, structured-output validation, bounded retry, and synthesis modules; focused integration tests.

**Required behavior:** Supply only the task instruction, relevant evidence, relevant policy, deterministic results, and necessary workflow state; cite evidence; distinguish facts, conclusions, assumptions, and unresolved issues; validate structured outputs; retry only boundedly; record model/runtime configuration. One model only.

**Minimum success gate:** The local model safely synthesizes CASE_001 evidence, identifies that urgency does not create authority, preserves uncertainty, and produces a usable task result without receiving the full case, handbook, evaluator, or ground truth.

**Benchmark/check to run:** Repeat the bounded CASE_001 synthesis several times for structural validity and material consistency; inspect context manifest and failure behavior.

**Do NOT build yet:** Multi-model selection, cloud dependency, persona simulation, profile learning, framework-first orchestration, or UI.

**Fallback if blocked:** Preserve the adapter boundary; run deterministic tasks and create a pending human synthesis task. A mock may test plumbing, but it cannot be presented as a working local-model benchmark.

**Output/report expected from Codex:** Files changed; actual local runtime used; context size/sources; validation and retry behavior; CASE_001 synthesis result; failures; M5 readiness.

## M5 — Durable Workflow Artifacts and CASE_001 Vertical Slice

**Goal:** Make the workflow resumable and understandable from disk, then pass the first full product gate.

**Why now:** Discovery, planning, deterministic work, and semantic work become a product only when their state and evidence form one inspectable run.

**Prerequisites:** M0–M4 minimum gates pass.

**Read before coding:** `AGENTS.md`; this milestone; workflow-artifact guidance in `AGENTS.md`; CASE_001 `README.md`, `case.json`, and only its named policy sections; affected modules. No ground truth during runtime execution.

**Files/modules likely created or changed:** `src/artifacts/`, workflow state/recovery orchestration, and focused tests; runtime output shaped approximately as `manifest.json`, versioned `plan.md`, `input/`, `tasks/<task_id>/{task,context,result}.json`, `artifacts/{screenshots,extracts,calculations,human}/`, `findings.md`, `corrections.jsonl`, and `final/`.

**Required behavior:** Atomically or safely persist lifecycle state, inputs, grants, evidence references, executor, results, failures, and final state; resume or at least inspect an interrupted workflow; retain corrections and superseded plans. No database is required. The CASE_001 run must identify Conditional status, the expired COI blocker, and the unreleased draft PO; distinguish urgency from authorization; avoid releasing the PO; and state safe next actions.

**Minimum success gate:** A fresh sparse CASE_001 run completes without case-ID branching, evaluator/ground-truth access, or hardcoded answers, and another person can reconstruct what happened solely from the runtime directory.

**Benchmark/check to run:** CASE_001 end-to-end artifact audit, runtime-context manifest review, restart/interruption check, schema validation, and explicit prohibited-action review.

**Do NOT build yet:** Operator learning, adaptive routing, formal evaluator, event-stack integration, dashboard, or extra-case generalization beyond small deterministic checks.

**Fallback if blocked:** Preserve every completed artifact and mark the failed task and final state unresolved. Fix the smallest failing layer; do not weaken safety checks or mutate CASE_001.

**Output/report expected from Codex:** Files changed; workflow ID/path; what completed; CASE_001 gate outcome; checks; exact unresolved state; limitations; M6 readiness.

## M6 — Human and Persona Task Interface

**Goal:** Present and receive bounded work through one interface usable by a real human and, in tests, the persona simulator.

**Why now:** Human work should attach to an already functioning workflow rather than compensate for missing core semantics.

**Prerequisites:** M5 CASE_001 gate passes; task and artifact lifecycles are durable.

**Read before coding:** `AGENTS.md`; this milestone; `simulator/PERSONA_SIMULATOR_SPEC.md`; `simulator/prompts/persona_system_prompt.md`; only relevant P001/P002/P005 `actor.md` files and permitted CASE_001 memory/grants for the selected run; affected human-task modules. `PERSONA_BLUEPRINT.md`, persona evaluators, and case ground truth remain authoring/evaluator-only.

**Files/modules likely created or changed:** `src/human/`, isolated simulator adapter, grant/context assembler, task response handling, and tests; human artifacts under the workflow runtime.

**Required behavior:** Package a bounded goal, explicitly granted files, necessary policy/context, expected output, consequence and authority boundary. Support completion, clarification, narrowing, partial completion, reassignment, authority refusal, and pending human state. A human unavailable on one branch must not block independent branches. Persona context is limited to own `actor.md`, own selected case memory, explicit grants, own history, and current task; never evaluators, ground truth, another persona, or hidden runtime profile.

**Minimum success gate:** CASE_001 can assign an appropriately scoped visible-field task to P001, commercial interpretation to P002, or onboarding/standing work to P005; useful partial work is preserved and unauthorized decisions are returned safely.

**Benchmark/check to run:** CASE_001 persona interaction sanity checks for P001/P002/P005, grant manifest inspection, clarification/narrowing/refusal flows, and simulator failure-mode review.

**Do NOT build yet:** Learned profile updates, adaptive ranking, full multi-operator login, elaborate UI, or evaluator-driven prompting.

**Fallback if blocked:** Use a terminal or file-based inbox/outbox with explicit task status and grants. If no human responds, leave the task pending and complete independent work.

**Output/report expected from Codex:** Files changed; task package and lifecycle; grants used; persona/human outcomes; firewall checks; limitations; M7 readiness.

## M7 — Operator Evidence Ledger and Profile

**Goal:** Record attributable human-work evidence and maintain a conservative, explainable operator profile.

**Why now:** Profiles should learn from actual task behavior, not precomputed persona truth or speculation.

**Prerequisites:** M6 produces durable human task outcomes, verification, corrections, and source references.

**Read before coding:** `AGENTS.md`; this milestone; `operator_model/OPERATOR_PROFILE_SPEC.md`; `operator_model/profile.schema.json`; `operator_model/evidence_event.schema.json`; canonical capability schema; affected operator-model modules. Read one relevant persona actor only for an interaction test; do not read its evaluator in runtime work.

**Files/modules likely created or changed:** `src/operator_model/`; `runtime/operators/<operator_id>/profile.json` and append-only `evidence.jsonl`; schema validation and focused tests.

**Required behavior:** Initialize all 19 dimensions in canonical order with capability `0.5` and evidence confidence `0.0`; keep knowledge, authority, access, capability, and confidence separate; key state by stable `operator_id`; record event, task context, source refs, verification, attribution, significance, and localized implications. Use the MVP sequence `classified evidence event → deterministic bounded update → narrative refresh only after meaningful events`. Do not freeze a formula here; implementation increments should remain small and conservative. Negative durable updates require verified outcome and supported attribution, not mere team failure. Preserve contradictory evidence.

**Minimum success gate:** A clear verified M6 event changes only materially exercised capabilities/knowledge, raises evidence confidence proportionately, leaves unrelated dimensions unknown, and produces a concise evidence-backed narrative that validates against schemas.

**Benchmark/check to run:** Cold-start, verified success, verified correction, clarification/authority refusal, unresolved attribution, contradictory evidence, and ledger-reconstruction checks.

**Do NOT build yet:** Machine-learned scoring, one-dimensional competence scores, aggressive decay, adaptive candidate optimization, or evaluator-derived initialization.

**Fallback if blocked:** Persist schema-valid evidence events without changing the snapshot; reconstruct or update profiles later. Evidence integrity is more important than visible score movement.

**Output/report expected from Codex:** Files changed; event/profile paths; before/after evidence; dimensions affected and why; validation; limitations; M8 readiness.

## M8 — Adaptive Human Routing, Presentation, and Verification

**Goal:** Rank eligible humans transparently and adapt task instructions and verification to observed evidence without weakening hard controls.

**Why now:** Routing can only be evidence-backed after profiles and real task outcomes exist.

**Prerequisites:** M7 profile and evidence semantics pass; M6 task interface accepts scaffolding and verification policy.

**Read before coding:** `AGENTS.md`; this milestone; routing/scaffolding sections of `OPERATOR_PROFILE_SPEC.md`; canonical capability schema; relevant selected actor files and CASE_001 README; current routing/human modules. Hidden evaluators are not routing inputs.

**Files/modules likely created or changed:** `src/routing/`; task-requirement representation; candidate filter/ranker; scaffolding and verification policy; rationale artifacts and tests.

**Required behavior:** Combine task requirements, capability estimate plus evidence confidence, knowledge, verified authority, access, risk, scaffolding, and verification. Filter authority/access before preference ranking. Emit candidate, fit rationale, required scaffolding, and verification. Support `NONE`, `LIGHT`, `STRUCTURED`, `STEP_BY_STEP` and `NORMAL`, `ENHANCED`, `MANDATORY`. Adapt presentation, not the underlying business requirement, unless safe narrowing is explicit. High capability never bypasses bank controls, Q&R authority, approvals, security, or separation of duties. Maintain `active_operator_id`; a simple selector is enough.

**Minimum success gate:** CASE_001 produces explainable differences among P001/P002/P005: a new/unknown operator gets evidence links and structure, demonstrated specialists get concise instructions, and no persona receives unauthorized approval work.

**Benchmark/check to run:** Candidate-order and ineligibility checks; cold-start unknown handling; before/after task-presentation comparison; mandatory-control invariance; CASE_001 persona contrast.

**Do NOT build yet:** Complex optimization, title-only routing, full authentication, multi-model routing, or hidden-evaluator-informed selection.

**Fallback if blocked:** Use a small rule-based eligibility filter and transparent weighted heuristic; if confidence is insufficient, choose a low-risk verifiable assignment or request human selection.

**Output/report expected from Codex:** Files changed; ranking inputs/rationale; presentation and verification examples; CASE_001 behavior; checks; limitations; M9 readiness.

## M9 — Separate Evaluation and Progressive Case Generalization

**Goal:** Build a physically and logically separate evaluator that reports pass/partial/fail evidence across runtime behavior, then progress through Cases 001–004.

**Why now:** Runtime semantics must exist before an evaluator can assess them, and separation prevents hidden truth from shaping implementation behavior.

**Prerequisites:** M5 core run works; M6–M8 exist for persona/profile modes being evaluated.

**Read before coding:** `AGENTS.md`; this milestone; `evaluation/EVALUATION_SPEC.md`; `evaluation/TEST_SUITE_INDEX.json`; `cases/CASE_SPEC.md`; only the current case README and its evaluator-side ground truth; selected persona evaluator only for persona/profile modes; affected evaluation code. Never pass these hidden inputs to runtime.

**Files/modules likely created or changed:** A separate `src/evaluation/` or evaluator-only package, reports, fixtures/configuration, and evaluator tests. Context assembly must make the one-way runtime-output-to-evaluator flow inspectable.

**Required behavior:** Support `CASE_ONLY`, `PERSONA_INTERACTION`, `PROFILE_LEARNING`, and `FULL_WORKFLOW` as time permits; compare semantically rather than exact DAG/task names; report required findings, decisions, prohibited actions, final state, task-family coverage, routing, persona interaction, profile convergence, evidence attribution, and context efficiency. Surface each hard failure; do not hide it in an aggregate score. Label contamination explicitly.

**Minimum success gate:** A valid CASE_001 run receives a reproducible developer-facing report with clear evidence and no reverse flow of hidden truth. Only then add CASE_002, CASE_003, and CASE_004 in order.

**Benchmark/check to run:** Formal CASE_001 evaluation; then CASE_002 revision/OTIF mixed responsibility; CASE_003 freshness/temperature and unresolved Q&R disposition; CASE_004 invoice/bank-control parallel branches. Do not run all cases after every small edit.

**Do NOT build yet:** A huge scoring framework, benchmark-specific runtime branches, case-ID answer selection, fixture edits, dashboards, or self-evaluation by the runtime model.

**Fallback if blocked:** Emit a small layer-by-layer pass/partial/fail report with explicit hard failures and source references. Keep unsupported evaluation layers marked unavailable.

**Output/report expected from Codex:** Files changed; modes supported; firewall evidence; per-case report paths and outcomes; hard failures; limitations; M10 readiness.

## M10 — NVIDIA, OpenClaw, NemoClaw, and OpenShell Adapters

**Goal:** Run the proven local-model workload on available Dell/NVIDIA hardware and connect the required competition event stack through narrow adapters while preserving OpenShell security boundaries.

**Why now:** Integration should demonstrate and transport already-working semantics, not define them or consume the time needed to build the core.

**Prerequisites:** Stable M5 core, preferably M9 CASE_001 evaluation; current competition requirements and on-site environment are available.

**Read before coding:** `AGENTS.md`; this milestone; current event documentation, installed versions, hardware/runtime environment, and existing integration interfaces at implementation time. Do not assume APIs, CLI commands, or versions from this static plan, and do not browse unless the future task authorizes it.

**Files/modules likely created or changed:** `src/integrations/` adapters and configuration; deployment/startup scripts if appropriate; integration checks. Core planning, task, artifact, and profile semantics should need little or no change.

**Required behavior:** Expose local inference and required event-stack capabilities through replaceable interfaces; record which path executed; retain bounded contexts, local data handling, sandboxing, access controls, and safe failure. Do not claim privacy or hardware properties not demonstrated.

**Minimum success gate:** The primary CASE_001 path uses the required local NVIDIA/event-stack integration without semantic regressions, hidden cloud dependence, or loss of artifact evidence.

**Benchmark/check to run:** Adapter contract checks, core regression, sandbox/access failure test, startup/reconnect behavior, and one integrated CASE_001 run.

**Do NOT build yet:** Framework-driven redesign, scattered vendor-specific logic, multi-model orchestration, or UI polish.

**Fallback if blocked:** Preferred: core + local NVIDIA model + OpenClaw + NemoClaw + OpenShell. Fallback A: working core + local NVIDIA model + minimum integration required by current event rules. Fallback B: preserve local model, end-to-end workflow, and artifacts while isolating the incomplete framework adapter. Never damage the working core to force integration.

**Output/report expected from Codex:** Files changed; exact current integration path; environment/version evidence; checks; fallback level used; limitations; M11 readiness.

## M11 — Glass-Box Demo Interface

**Goal:** Provide a small reliable view of the incoming objective, discovery, plan, executors, evidence, human work, profile adaptation, corrections, unresolved items, and final result.

**Why now:** The UI should expose stable artifacts and behavior rather than becoming an alternate workflow engine.

**Prerequisites:** M5 stable core; whichever M6–M10 features will appear in the demo are working from their native interfaces.

**Read before coding:** `AGENTS.md`; this milestone; actual runtime artifact contracts and startup commands; current UI/source files; primary demo case README. Do not load all case content or evaluator truth into the UI.

**Files/modules likely created or changed:** `src/ui/` or a lightweight dashboard/terminal renderer; read-only artifact views plus narrowly controlled actions such as plan approval and human response; UI checks.

**Required behavior:** Make evidence lineage, task executor, state transitions, authority stops, corrections, and unresolved work visible. Likely human control points are plan approval, consequential authorization, specialist disposition, correction confirmation, and final review; do not add approval to every harmless step. Prefer a lightweight web view, local dashboard, or terminal plus generated visuals based on what is most stable.

**Minimum success gate:** A judge can follow the primary workflow without reading raw JSON, while the underlying files remain the source of durable state and no hidden evaluator data appears.

**Benchmark/check to run:** Walk the primary demo from clean start; verify artifact links, refresh/restart, pending and failure states, accessibility/readability, and absence of hidden content.

**Do NOT build yet:** Elaborate frontend architecture, authentication, broad multi-user features, advanced dashboards, or new business behavior.

**Fallback if blocked:** Use a stable terminal timeline and generated Markdown/HTML summary directly from artifacts; reliability and inspectability outrank visual ambition.

**Output/report expected from Codex:** Files changed; interface/start command; visible workflow stages; demo walkthrough outcome; checks; limitations; M12 readiness.

## M12 — Demo Hardening and Pitch Readiness

**Goal:** Freeze features and make the selected competition path reproducible, safe, fast to reset, and easy to explain.

**Why now:** Late architecture work threatens a functioning demo; remaining effort should remove execution and presentation risk.

**Prerequisites:** One end-to-end demo works; the required local/integration path works or has an explicitly acceptable fallback; major CASE_001 checks pass.

**Read before coding:** `AGENTS.md`; this milestone; actual startup/reset documentation; latest benchmark and demo reports; only source files implicated by observed failures.

**Files/modules likely created or changed:** Startup/reset helpers, configuration examples, targeted reliability fixes, demo fixtures/scripts where allowed, concise README updates, and captured evidence. Finalize README only now that commands and dependencies are known; earlier README changes should remain minimal and factual.

**Required behavior:** Reproducible startup, clean recoverable reset, stable case loading, bounded model behavior, helpful errors, visible artifacts, explicit unresolved state, no leakage, and consistent demo narration. Fix correctness, safety, reliability, and judging-story issues only. Capture actual metrics rather than invented targets.

**Minimum success gate:** Two clean rehearsals complete the primary demo through the same safe final state; a forced model/tool/human failure degrades visibly; required integration and major evaluation checks remain green.

**Benchmark/check to run:** Clean-machine or clean-environment startup where practical; CASE_001 formal run; selected CASE_002–004 generalization evidence; integration smoke check; leakage audit; reset and rehearsal checklist.

**Do NOT build yet:** New architecture, multi-model routing, complex multi-user support, new cases, speculative tools, or cosmetic work that risks stability.

**Fallback if blocked:** Remove nonessential demo branches, use the strongest previously verified adapter level, and preserve the core narrative. Report exact partial state rather than masking failures.

**Output/report expected from Codex:** Files changed; frozen feature set; commands; rehearsal and benchmark outcomes; metrics; known limitations; fallback status; final conflicts/blockers.

## Case and Evaluation Progression

Cases advance deliberately:

1. `CASE_001_VENDOR_ACTIVATION` proves sparse discovery, Conditional vendor standing, expired evidence, authority boundaries, safe PO handling, and simple human adaptation. It is the first major gate.
2. `CASE_002_OTIF_EXCEPTION` adds latest-revision resolution, deterministic OTIF/fill arithmetic, event chronology, and mixed vendor/carrier responsibility.
3. `CASE_003_FRESHNESS_TEMP` adds remaining-life arithmetic, freshness-versus-safety separation, abnormal temperature evidence, Q&R authority, and a correctly unresolved technical disposition.
4. `CASE_004_INVOICE_BANK_CHANGE` adds three-way matching, simultaneous tolerance tests, independent financial/control branches, and secure bank-change handling.

Recommended checkpoints are: manual CASE_001 plan sanity after M2; deterministic checks after M3; full CASE_001 artifact gate after M5; persona interaction sanity after M6; profile/routing behavior after M8; formal CASE_001 evaluation after M9; then Cases 002–004. Cases 005–010 are not MVP requirements. The first four already span all eight personas, 17 of 19 capability dimensions, and the major authority, safety, and business patterns.

The likely primary demo is CASE_001 because the stakes and boundary are easy to explain. Use P001, P002, and P005 to show differing task presentation and authority, and optionally add one narrow CASE_002 deterministic calculation. Cases 002–004 primarily demonstrate generalization; the live demo need not execute all four.

## Context Discipline and Future Prompt Architecture

Each future Codex task implements exactly one milestone. It should name exact files to read, directories it may modify, validations, stop conditions, and later work it must not begin. At minimum it reads:

```text
AGENTS.md
the relevant HACKATHON_BUILD_PLAN.md milestone
the relevant component specification
one relevant case README/metadata
affected existing source files
```

It must not automatically load all specs, cases, handbooks, personas, ground truth, or existing runtime runs. Ground truth and persona evaluators are read only by an evaluator task after runtime output exists. Handbook retrieval is limited to sections needed by the current case and task. After compaction or continuation, inspect actual files and tests rather than relying solely on a prior chat claim.

| Future prompt | Scope |
|---|---|
| `PROMPT_00_BOOTSTRAP.md` | M0 only: project skeleton, paths, configuration, runtime creation. |
| `PROMPT_01_WORKSPACE_DISCOVERY.md` | M1 only: authorized compact inventory and retrieval. |
| `PROMPT_02_TASK_DISCOVERY.md` | M2 only: sparse-goal plan and revision states. |
| `PROMPT_03_DETERMINISTIC_EXECUTION.md` | M3 only: small exact operation set and checks. |
| `PROMPT_04_LOCAL_MODEL_EXECUTION.md` | M4 only: one bounded local model and validation. |
| `PROMPT_05_WORKFLOW_ARTIFACTS.md` | M5 only: durable orchestration and CASE_001 gate. |
| `PROMPT_06_HUMAN_PERSONA_INTERFACE.md` | M6 only: bounded human lifecycle and simulator firewall. |
| `PROMPT_07_OPERATOR_PROFILE.md` | M7 only: evidence ledger and conservative profile. |
| `PROMPT_08_ADAPTIVE_ROUTING.md` | M8 only: eligible ranking, scaffolding, verification. |
| `PROMPT_09_EVALUATION.md` | M9 only: separate evaluation and progressive cases. |
| `PROMPT_10_NVIDIA_INTEGRATION.md` | M10 only: current hardware/event-stack adapters. |
| `PROMPT_11_DEMO_INTERFACE.md` | M11 only: stable glass-box view. |
| `PROMPT_12_DEMO_HARDENING.md` | M12 only: freeze, reliability, metrics, rehearsal. |

These files are names and scopes only; do not create them until separately requested.

Each milestone handoff reports: files changed, what works, checks/tests run, benchmark result, known limitations, next-milestone readiness, and upstream conflicts. The next task verifies repository state. Optional manual plan status uses `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `PASS`, and `DEFERRED`; this document should remain mostly stable and need not be edited after every milestone.

## Integration, Security, and Failure Strategy

The local-first story is evidence-based: company-sensitive documents stay on the demonstrated local execution path; each worker receives bounded context; artifacts expose what was used; and the judged core has no cloud-LLM dependency. Security must be visible in context manifests, grants, evaluator/runtime separation, access failures, document-as-evidence handling, and OpenShell sandbox behavior where integrated—not merely claimed in a slide.

Expected graceful failures include:

| Failure | Required behavior |
|---|---|
| Workspace extraction | Record unreadable file and reason, continue other discovery, surface unresolved evidence. |
| Local model | Preserve task state and inputs; retry boundedly or route to human; never fabricate completion. |
| Human unavailable | Leave task pending and continue independent branches. |
| Schema validation | Reject malformed durable state visibly; repair or retry locally. |
| Policy/evidence missing | Preserve uncertainty and identify the owner or evidence needed. |
| Integration adapter | Isolate failure, retain core run, and select the documented fallback level. |
| Correction | Retain old result, append correction provenance, update affected downstream state. |

Plan changes follow `current plan → revision proposed → reason recorded → prior plan superseded`. Consequential execution never silently rewrites an approved plan.

## Risk Register

| Risk | Mitigation |
|---|---|
| NVIDIA/OpenClaw/NemoClaw/OpenShell consumes too much time | Integrate after core semantics, keep narrow adapters, preserve fallback levels and the working core. |
| Local model output is inconsistent | Deterministic preprocessing, small contexts, structured outputs, schema validation, and bounded retry. |
| Codex context explodes | One milestone per prompt, narrow read lists, targeted retrieval, and no routine whole-repository rereads. |
| Operator profile becomes unstable | Conservative deterministic updates, verified attribution, localized effects, and demo only clear evidence-backed changes. |
| Demo becomes too complex | Keep CASE_001 primary; use other cases as benchmark evidence and cut nonessential branches. |
| Fixture or evaluator truth leaks | Physical/logical evaluator separation, explicit context manifests, grant checks, and contamination reporting. |
| Late feature work breaks reliability | Enforce feature freeze and accept a documented fallback instead of redesigning the core. |

## Metrics to Capture

Capture a small number of real, judge-friendly measures from runtime artifacts:

- model calls avoided by deterministic execution;
- files or bytes exposed to each worker versus the authorized workspace total;
- human task scope before and after decomposition;
- operator evidence/profile state before and after a verified event;
- workflow and task completion time;
- required findings and decisions captured;
- prohibited actions avoided or controls that prevented an attempted action;
- failures, retries, and unresolved tasks.

Do not invent target numbers. Explain why-local with observed execution location, bounded document exposure, inspectable artifacts, and absence of a required cloud model.

## Demo Strategy

The strongest sequence is:

1. A user gives a vague CASE_001 objective.
2. The Governor inventories the authorized workspace and retrieves targeted evidence.
3. It proposes an evidence-backed plan for approval.
4. A deterministic executor handles a visible-field, date, status, or calculation check.
5. The local model synthesizes relevant evidence and policy.
6. A human receives a bounded task and contributes or corrects something meaningful.
7. The evidence ledger records the verified contribution and updates the operator profile conservatively.
8. A later task is presented differently based on demonstrated capability or knowledge.
9. The run ends with a safe result, explicit unresolved actions, evidence lineage, and preserved corrections.

This demonstrates coordination rather than “an agent read documents.” The interface should show why each executor was selected and where authority stopped execution.

## Feature Freeze Rule

Once one end-to-end demo works, the required local/integration path works at an acceptable fallback level, and major benchmark checks pass, stop adding major functionality. Spend remaining time on correctness, safety, reproducibility, screenshots, artifacts, observed metrics, presentation, and pitch rehearsal. Do not begin multi-model orchestration, complex multi-user support, new fixture generation, or a frontend rewrite late in the event.

## Completion Checklist

- [ ] M0–M5 pass and CASE_001 is understandable from disk.
- [ ] Runtime never reads case ground truth, persona evaluators, another persona's private state, or developer provenance.
- [ ] Deterministic work is not repeatedly delegated to a model.
- [ ] One local model works with bounded context and no judged cloud dependency.
- [ ] Conditional status, expired COI, draft PO, authority boundary, and safe next actions are correct in CASE_001.
- [ ] Human tasks support clarification, narrowing, partial completion, reassignment, and authority refusal.
- [ ] Profile changes are schema-valid, attributable, localized, conservative, and keep unknown distinct from weak.
- [ ] Routing filters authority/access independently and preserves mandatory controls.
- [ ] Evaluator is one-way and reports hard failures without averaging them away.
- [ ] Cases progress 001 → 002 → 003 → 004 without fixture mutation or ID-based answers.
- [ ] Integration is isolated, current documentation was inspected on-site, and fallback level is explicit.
- [ ] Demo interface exposes objective, discovery, plan, executors, evidence, human work, corrections, profile change, and final state.
- [ ] Startup, reset, failure behavior, leakage audit, and two clean rehearsals pass.
- [ ] README reflects actual commands and dependencies rather than speculative setup.
- [ ] Feature freeze is active; stretch work cannot endanger the working core.
