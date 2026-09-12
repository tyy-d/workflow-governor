# PARALLEL_WORKSTREAM_PLAN.md

## Purpose

This document converts the sequential capability dependencies in `HACKATHON_BUILD_PLAN.md` into a three-person parallel implementation strategy for the hackathon.

It does **not** replace `HACKATHON_BUILD_PLAN.md`.

Use the two documents together:

- `HACKATHON_BUILD_PLAN.md` defines **what must exist and what depends on what**.
- `PARALLEL_WORKSTREAM_PLAN.md` defines **who owns each subsystem, what can be built concurrently, and when integration happens**.
- `AGENTS.md` remains the repository-wide operating contract.

The goal is to prevent the team from serializing work unnecessarily while also avoiding merge conflicts, duplicated implementations, and interface drift.

---

# 1. Team Ownership

The three primary coders are:

| Coder | Track | Primary Ownership |
|---|---|---|
| **Daniel** | Track A — Workspace & Workflow State | workspace discovery, targeted retrieval, workflow/artifact persistence, filesystem state |
| **Thomas** | Track B — Planning & Execution | task discovery, planning, deterministic execution, bounded local-model execution |
| **Frank** | Track C — Human & Operator Intelligence | human task interface, persona simulator adapter, evidence ledger, operator profile |

These ownership boundaries are deliberate.

Each coder should be able to make substantial progress without waiting for neighboring tracks.

No coder should casually modify another coder's owned subsystem merely because that subsystem is incomplete.

---

# 2. Parallelization Principle

The team should distinguish:

```text
implementation dependency
```

from:

```text
interface dependency
```

Most components do not need the neighboring implementation to exist if the shared interface has already been defined.

For example:

```text
Daniel builds WorkspaceMap production
Thomas builds planner against a mock WorkspaceMap
Frank builds human-task handling against a mock TaskSpec
```

All three can work simultaneously.

The repository should therefore use:

```text
shared contracts
+
track-local implementations
+
test-local mocks
```

instead of:

```text
wait for upstream code
→ start downstream code
```

---

# 3. Execution Shape

The recommended competition-day structure is:

```text
                         SHARED START
                 P00 — Contracts + Bootstrap
                           |
                  interfaces temporarily frozen
                           |
          +----------------+----------------+
          |                |                |
          v                v                v

      DANIEL           THOMAS           FRANK
      TRACK A          TRACK B          TRACK C

   A01 Workspace    B01 Planning     C01 Human Task
   Discovery        & Task Discovery Interface
        |                |                |
   A02 Artifact     B02 Deterministic C02 Persona
   Store            Execution         Adapter
        |                |                |
   A03 Workflow     B03 Local Model   C03 Evidence
   State            Execution         + Profile
          |                |                |
          +----------------+----------------+
                           |
                  P01 — CASE_001 INTEGRATION
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
         Thomas        Daniel/Frank    remaining owner
         Routing       Evaluation      NVIDIA adapter
             |             |             |
             +-------------+-------------+
                           |
                     DEMO INTEGRATION
                           |
                       HARDENING
```

The exact owner of post-P01 work may be adjusted based on who finishes their first-wave track earliest, but ownership changes must be explicit.

---

# 4. Shared Phase — P00

Before branching into parallel work, the team performs one short synchronization phase:

```text
PROMPT_00_SHARED_CONTRACTS_AND_BOOTSTRAP.md
```

P00 should create only:

- importable project skeleton;
- common path/config utilities;
- shared enums;
- common data contracts;
- minimal errors;
- smoke tests;
- empty subsystem packages/directories.

P00 should **not** implement real:

- workspace discovery;
- planning;
- deterministic execution;
- model execution;
- human interface;
- profile learning;
- adaptive routing;
- evaluator;
- NVIDIA integration;
- UI.

The purpose of P00 is to make parallel development safe.

---

# 5. Contracts to Freeze After P00

The team should agree on the smallest useful shared vocabulary.

Exact implementation language may vary, but the conceptual contracts should cover at least:

## Workspace contracts

```text
FileRecord
WorkspaceMap
EvidenceRef
```

## Planning/task contracts

```text
WorkflowPlan
TaskSpec
TaskDependency
TaskContext
TaskResult
Finding
```

## Execution contracts

```text
ExecutorType
TaskStatus
ExecutionStatus
```

Recommended executor values:

```text
DETERMINISTIC
LOCAL_MODEL
HUMAN
```

## Human contracts

```text
HumanTaskResponse
HumanResponseType
```

Useful response types:

```text
COMPLETE
CLARIFICATION_REQUESTED
TASK_NARROWED
REASSIGNMENT_REQUESTED
AUTHORITY_DECLINED
```

## Workflow identity/state contracts

```text
WorkflowID
TaskID
OperatorID
```

The shared contracts should remain intentionally small.

Do not freeze unnecessary future architecture.

---

# 6. Shared Contract Freeze Rule

After P00 is merged, the shared contract package is temporarily frozen.

A track may not casually modify a shared contract.

If a coder discovers that a contract prevents correct implementation, they should create an:

```text
INTERFACE_CHANGE_REQUEST
```

containing:

```text
affected interface:
current problem:
proposed change:
why track-local adaptation is insufficient:
other tracks likely affected:
```

The team should review and merge the smallest compatible change.

This prevents:

```text
Thomas changes TaskSpec
→ Frank's branch breaks
→ Daniel adapts differently
→ integration conflict
```

---

# 7. Git Branch Strategy

After P00 is merged into `main`, create:

```text
feature/workspace-state
feature/planning-execution
feature/human-operator
```

Ownership:

```text
Daniel -> feature/workspace-state
Thomas -> feature/planning-execution
Frank  -> feature/human-operator
```

Each branch should modify mostly disjoint directories.

Recommended rule:

> Merge coherent subsystem increments early rather than keeping one enormous branch open until the end.

Example:

```text
A01 complete -> merge
B01 complete -> merge
C01 complete -> merge
```

Then the next wave continues from updated `main`.

---

# 8. Track A — Daniel — Workspace & Workflow State

## Mission

Daniel owns the durable information substrate of Workflow Governor.

His work answers:

```text
What files exist?
What evidence is available?
How can the system retrieve only what it needs?
Where does workflow state live?
Can work be resumed and inspected from disk?
```

## Primary ownership

Daniel should primarily own:

```text
src/workspace/**
src/artifacts/**
src/workflow_state/**   # if this module exists after P00
tests/workspace/**
tests/artifacts/**
tests/workflow_state/**
```

Exact paths may follow the P00 repository layout.

He should not own:

```text
src/planning/**
src/execution/**
src/human/**
src/operator_model/**
src/routing/**
```

unless explicitly reassigned.

### A01 — Workspace Discovery

Build:

```text
authorized workspace path
→ compact WorkspaceMap
```

Priorities:

- deterministic file enumeration;
- relative paths;
- file type;
- size;
- basic metadata;
- extractability;
- lightweight previews where appropriate;
- targeted retrieval;
- bounded context;
- unreadable-file handling.

Avoid:

- reading all files fully;
- sending everything to a model;
- case-specific relevance rules;
- hidden ground truth.

Use CASE_001 workspace only for independent testing. The planner does not need to exist.

### A02 — Workflow Artifact Store

Implement the persistent artifact model around the canonical workflow directory structure. Functions should accept shared contracts, and tests may construct fake `WorkflowPlan`, `TaskSpec`, `TaskResult`, and `Finding` objects.

### A03 — Workflow State / Resume

If time permits before P01, make workflow state resumable: reopen manifest, enumerate tasks, preserve statuses, load findings/corrections, and determine unresolved tasks. Prefer filesystem-backed state over a database for MVP.

---

# 9. Track B — Thomas — Planning & Execution

## Mission

Thomas owns the reasoning/execution core that turns a sparse goal into bounded work.

His track answers:

```text
What work needs to happen?
What evidence does each task need?
Which tasks are deterministic?
Which tasks require semantic reasoning?
What result did each executor produce?
```

## Primary ownership

Thomas should primarily own:

```text
src/planning/**
src/execution/**
src/model/**
tests/planning/**
tests/execution/**
tests/model/**
```

He should not implement workspace persistence, operator profiles, persona simulation, or evaluation framework.

### B01 — Task Discovery & Planning

Build:

```text
goal
+
WorkspaceMap
+
targeted evidence
+
relevant policy
→ WorkflowPlan
```

The planner should produce objective, assumptions, unresolved questions, tasks, dependencies, evidence needs, candidate executor class, and consequential decision points.

If Daniel's real Workspace Discovery is unavailable, create a test-local `MockWorkspaceMap`. Do **not** implement WorkspaceScout inside Track B.

### B02 — Deterministic Execution

Implement a small deterministic executor for date/threshold comparison, percentages, quantity reconciliation, version ordering, structured equality, simple table/CSV/JSON extraction, and schema validation where relevant.

Consume shared `TaskSpec` and `TaskContext`; return shared `TaskResult`.

### B03 — Bounded Local-Model Execution

Implement semantic/model execution behind a small adapter. Give the model only the task instruction, relevant evidence, relevant policy, and required workflow state. Start with one local model. Do not build multi-model routing.

---

# 10. Track C — Frank — Human & Operator Intelligence

## Mission

Frank owns the human collaboration layer.

His track answers:

```text
How does a human receive bounded work?
How can the human clarify, narrow, reassign, or refuse?
How do we simulate operators safely?
How is evidence about operator capability recorded?
How is an operator profile persisted and updated conservatively?
```

## Primary ownership

Frank should primarily own:

```text
src/human/**
src/persona/**
src/operator_model/**
tests/human/**
tests/persona/**
tests/operator_model/**
```

He should not implement planner internals, deterministic tools, or workspace discovery.

### C01 — Human Task Interface

Build a minimal interface capable of presenting a shared `TaskSpec` and supporting:

```text
COMPLETE
CLARIFICATION_REQUESTED
TASK_NARROWED
REASSIGNMENT_REQUESTED
AUTHORITY_DECLINED
```

The first implementation may be CLI/minimal local interaction. If Thomas's planner is unavailable, construct mock `TaskSpec` fixtures rather than implementing planning.

### C02 — Persona Simulator Adapter

Implement behavior consistent with `PERSONA_SIMULATOR_SPEC.md` and `persona_system_prompt.md`. Strict context: own actor, own case memory, explicit grants, session history, current task. Never expose evaluator, ground truth, another persona's files, hidden operator profile, or provenance.

### C03 — Evidence Ledger & Operator Profile

Implement schema-backed `profile.json` and append-only `evidence.jsonl` under operator runtime state. Start conservatively: attribution, localized implications, capability/evidence separation, knowledge separate, authority categorical, access separate. Do not use evaluator truth or ML-based profiling.

---

# 11. Mock-First Rule

All three tracks must follow:

> Do not wait for an unavailable neighboring subsystem. Use the P00 shared interface and a test-local mock.

Examples:

```text
Daniel does not need planner:
construct fake TaskResult to test persistence.

Thomas does not need WorkspaceScout:
construct MockWorkspaceMap.

Frank does not need planner:
construct TaskSpec fixture.
```

Mocks belong in tests/fixtures for that track. Do not create fake production implementations that later compete with the real subsystem.

---

# 12. No Cross-Track Rescue Coding

If another subsystem is incomplete, Codex must not decide to implement that subsystem too just so local tests pass.

Use:

```text
neighbor missing
→ mock contract
→ continue local subsystem
```

If the shared interface is inadequate, raise an `INTERFACE_CHANGE_REQUEST`.

---

# 13. First Integration Checkpoint — P01

P01 occurs after enough of A01/A02, B01/B02/B03, and C01 exists to compose a CASE_001 path. C02/C03 may already exist but should not block the first base integration if delayed.

P01 integrates:

```text
sparse request
→ workspace discovery
→ planning
→ deterministic/local-model execution
→ human handoff where appropriate
→ workflow artifact persistence
→ final safe state
```

Primary benchmark:

```text
CASE_001_VENDOR_ACTIVATION
```

---

# 14. P01 Integration Ownership

Thomas coordinates runtime flow because Track B owns orchestration-facing planning/execution. Daniel owns fixes inside workspace/artifact modules. Frank owns fixes inside human/operator modules.

Do not fix another owner's module without coordination.

---

# 15. P01 CASE_001 Success Gate

The integrated system should be able to:

- accept the sparse CASE_001 request;
- inspect only authorized workspace material;
- identify relevant onboarding evidence;
- distinguish vendor status from informal claims;
- identify the COI blocker;
- preserve authority boundaries;
- avoid treating draft PO as transmitted;
- produce actionable next steps;
- persist plan, tasks, findings, and final state;
- avoid evaluator/ground-truth access;
- avoid case-specific hardcoding.

If this does not work, advanced routing should wait.

---

# 16. Second Parallel Wave

Once P01 works, parallelize again.

Recommended initial assignment:

```text
Thomas -> Adaptive Routing
Daniel -> Evaluation / runtime reliability
Frank  -> Profile/scaffolding refinement
First free owner -> NVIDIA/OpenClaw/NemoClaw/OpenShell adapter
```

Reassignment must be explicit.

Evaluator code may read hidden evaluator/ground-truth files; runtime code may not. Keep evaluator tooling physically/logically separate.

---

# 17. CASE Progression

Use:

```text
CASE_001
→ CASE_002
→ CASE_003
→ CASE_004
```

Do not parallelize by having each coder independently solve a different case in production code. Parallelize by subsystem, not benchmark answer.

Before P01, each track can use CASE_001 independently for subsystem validation without hidden truth.

---

# 18. Merge Discipline

A branch should be mergeable when:

- owned tests pass;
- shared contracts are respected;
- no other track directory was casually modified;
- no fixture was changed to make tests pass;
- no absolute local paths are introduced;
- no hidden truth enters runtime;
- Codex report clearly states limitations.

Prefer small coherent merges.

---

# 19. Interface Compatibility Tests

Maintain lightweight compatibility tests such as:

```text
WorkspaceMap serializes/deserializes.
WorkflowPlan contains valid TaskSpec objects.
TaskResult can be persisted by artifact store.
HumanTaskResponse carries enough information for later evidence events.
```

These verify composition, not business correctness.

---

# 20. Context Discipline Per Track

Every Codex track prompt should read only:

```text
AGENTS.md
relevant HACKATHON_BUILD_PLAN section
PARALLEL_WORKSTREAM_PLAN.md
relevant component spec
shared contracts
owned source files
one current benchmark fixture when needed
```

Do not load all handbooks, personas, cases, evaluators, or specs.

---

# 21. Codex Prompt Naming

Use:

```text
PROMPT_00_SHARED_CONTRACTS_AND_BOOTSTRAP.md

PROMPT_A01_WORKSPACE_DISCOVERY.md
PROMPT_A02_WORKFLOW_ARTIFACT_STORE.md
PROMPT_A03_WORKFLOW_STATE.md

PROMPT_B01_TASK_DISCOVERY_AND_PLANNING.md
PROMPT_B02_DETERMINISTIC_EXECUTION.md
PROMPT_B03_LOCAL_MODEL_EXECUTION.md

PROMPT_C01_HUMAN_TASK_INTERFACE.md
PROMPT_C02_PERSONA_SIMULATOR_ADAPTER.md
PROMPT_C03_OPERATOR_PROFILE.md

PROMPT_P01_CASE_001_INTEGRATION.md
```

Second-wave prompts may be:

```text
PROMPT_P02A_ADAPTIVE_ROUTING.md
PROMPT_P02B_EVALUATION.md
PROMPT_P02C_NVIDIA_INTEGRATION.md
```

followed by demo/hardening prompts.

---

# 22. Track Prompt Requirements

Every track prompt must specify:

```text
owner
branch
files to read
directories allowed to modify
directories forbidden to modify
shared contracts consumed
mocks allowed
benchmark fixture
required tests
completion gate
what not to build
Codex final report format
```

Every shared/integration prompt must additionally specify contract-change rules, subsystem owners, regression checks, fixture immutability, and rollback/fallback expectations.

---

# 23. Communication Protocol

Use blocker categories:

```text
TRACK_LOCAL_BUG
INTERFACE_CHANGE_REQUEST
UPSTREAM_SPEC_CONFLICT
INTEGRATION_BLOCKER
FIXTURE_DEFECT_SUSPECTED
EXTERNAL_INTEGRATION_BLOCKER
```

Each report should include:

```text
symptom
smallest failing component
evidence/error
owner
proposed next action
```

---

# 24. What a Coder Should Do After Finishing Early

Do not invade another track automatically.

Preferred work:

1. merge and help test integration;
2. create interface compatibility tests;
3. inspect CASE_001 behavior;
4. improve owned subsystem reliability;
5. take a formally reassigned second-wave task;
6. assist with demo integration.

---

# 25. Parallelization Anti-Patterns

Do not:

- have all three people edit the same orchestrator file;
- let every track define its own `TaskSpec`;
- let every track create its own file-loading utilities;
- duplicate profile structures;
- let each coder build a separate mini-Governor;
- assign each coder a case and merge case-specific solutions;
- let Codex modify shared contracts opportunistically;
- wait for upstream implementations when mocks suffice;
- keep all branches unmerged until the end.

---

# 26. Target Parallel Waves

## Wave 0 — Shared

All:

```text
P00
```

## Wave 1 — Fully Parallel

Daniel:

```text
A01
A02
A03 if time
```

Thomas:

```text
B01
B02
B03
```

Frank:

```text
C01
C02
C03
```

## Integration 1

All:

```text
P01 CASE_001
```

## Wave 2 — Parallel Again

Possible assignment:

```text
Thomas -> Adaptive Routing
Daniel -> Evaluation / runtime reliability
Frank  -> Profile/scaffolding refinement
First free owner -> NVIDIA integration
```

## Integration 2

```text
Cases 002–004
demo UI
metrics
security/integration verification
```

## Freeze

```text
demo hardening
pitch support
no major architecture changes
```

---

# 27. Success Criteria

The parallel plan is successful if:

- Daniel, Thomas, and Frank can all code after P00 without waiting;
- most branch modifications occur in disjoint directories;
- shared contracts change rarely;
- mocks replace missing neighbors during local development;
- CASE_001 integration requires wiring rather than rewrites;
- no hidden fixture knowledge leaks into production code;
- no coder duplicates another track's subsystem;
- later CASE_002–004 failures reveal generalization problems rather than merge-architecture problems.

---

# 28. Final Principle

Optimize for:

```text
stable contracts
+
parallel subsystem ownership
+
early integration
```

not maximum isolated coding.

The goal is for Daniel, Thomas, and Frank to build independently for meaningful periods, converge quickly at CASE_001, then split again for the stronger-demo layer.
