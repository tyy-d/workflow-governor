# PROMPT_00_SHARED_CONTRACTS_AND_BOOTSTRAP.md

You are working inside:

```text
workflow-governor/
```

You are performing the **shared pre-branch implementation bootstrap** for a three-person hackathon team.

The coders are:

```text
Daniel — Track A: Workspace & Workflow State
Thomas — Track B: Planning & Execution
Frank  — Track C: Human & Operator Intelligence
```

Your task is to create only the small shared implementation skeleton and interfaces required for Daniel, Thomas, and Frank to work in parallel afterward.

Do not implement any real subsystem behavior yet.

---

# 1. Read First

Read:

```text
workflow-governor/AGENTS.md
workflow-governor/HACKATHON_BUILD_PLAN.md
workflow-governor/PARALLEL_WORKSTREAM_PLAN.md
```

Then read only the specific static contracts needed to define shared types:

```text
workflow-governor/operator_model/profile.schema.json
workflow-governor/operator_model/evidence_event.schema.json
workflow-governor/company/northstar/schemas/northstar_operator_capability_schema.json
workflow-governor/evaluation/TEST_SUITE_INDEX.json
```

Inspect the current repository tree.

Do not load every handbook, persona, case workspace, evaluator, or ground-truth file.

Do not browse the web.

---

# 2. Objective

Create a minimal, importable project skeleton with shared contracts that allow the following three branches to be developed independently:

```text
feature/workspace-state
feature/planning-execution
feature/human-operator
```

After this prompt is complete:

- Daniel must be able to build workspace discovery and artifact persistence without the planner.
- Thomas must be able to build planning/execution against mocked workspace contracts.
- Frank must be able to build human/operator components against mocked task contracts.

The primary deliverable is **stable shared interfaces**, not functionality.

---

# 3. Do Not Build Later Milestones

Do NOT implement:

- real workspace scanning;
- file relevance ranking;
- task planning;
- deterministic execution tools;
- LLM execution;
- human interaction flow;
- persona simulation;
- evidence update logic;
- profile update logic;
- adaptive routing;
- evaluator;
- NVIDIA/OpenClaw/NemoClaw/OpenShell integration;
- UI;
- CASE_001 business logic.

If tempted to implement one of these because a test needs it, use a stub or test-local fixture instead.

---

# 4. Language and Existing Project Conventions

First inspect the repository for an existing implementation language/package structure.

If an implementation language/framework has already been intentionally selected, preserve it.

If implementation directories are effectively empty and no language has been selected, choose the smallest practical local-first stack consistent with the repository and hackathon goals.

Prefer simplicity.

Do not introduce a heavy agent framework.

Do not add cloud dependencies.

If choosing Python because no prior implementation exists, prefer a conventional lightweight package/test structure.

Do not silently replace an existing language choice.

Report the language/environment decision at the end.

---

# 5. Shared Package Goal

Create or establish a small shared core package.

Conceptually it should contain only things such as:

```text
core/
├── models / types
├── enums
├── paths
├── errors
└── config
```

Exact filenames should follow the implementation language.

Avoid a giant `utils` file.

Do not create dozens of files if a smaller layout is clearer.

---

# 6. Shared Contract: FileRecord

Define a compact `FileRecord` representation.

It should be able to represent at least:

```text
relative path
name
file type / extension or media type
size when known
basic metadata
extractability/availability state when useful
```

Do not include full file content by default.

The contract must support workspace mapping without encouraging context dumping.

Do not include case-specific fields.

---

# 7. Shared Contract: WorkspaceMap

Define `WorkspaceMap`.

It should represent:

```text
workspace root identity/path
collection of FileRecord
optional compact metadata
discovery warnings/errors
```

It should be serializable.

Do not include hidden evaluator or ground-truth concepts.

Do not encode relevance answers specific to CASE_001.

Thomas's planner must later be able to consume this contract even if Daniel's real WorkspaceScout is not yet implemented.

---

# 8. Shared Contract: EvidenceRef

Define a compact `EvidenceRef`.

It should be able to identify evidence without embedding arbitrary full content.

Useful conceptual fields:

```text
source/path identifier
optional location/range
optional artifact id
optional short label
```

Keep it generic enough for source files, extracts, calculations, and human-produced artifacts.

Do not define citation-formatting logic.

---

# 9. Shared Contract: ExecutorType

Define the primary executor enum as:

```text
DETERMINISTIC
LOCAL_MODEL
HUMAN
```

Do not add cloud execution to the judged-core executor enum.

Do not add persona IDs as executor types.

A persona/human identity is separate from executor class.

---

# 10. Shared Contract: TaskStatus

Define a small task-status enum sufficient for hackathon runtime.

Reasonable conceptual values include:

```text
PENDING
READY
IN_PROGRESS
BLOCKED
COMPLETED
FAILED
CANCELLED
```

Use fewer if current specs indicate a smaller set.

Do not design an elaborate workflow engine.

---

# 11. Shared Contract: TaskSpec

Define `TaskSpec`.

It should contain enough for Daniel, Thomas, and Frank to compose around it.

At minimum conceptually:

```text
task_id
title or short objective
description/instruction
executor_type or candidate executor class
dependencies
required evidence references
relevant policy/context references where appropriate
consequence/risk metadata if needed
status
```

Avoid freezing fields that belong specifically to future adaptive routing.

Do not put operator capability scores directly inside `TaskSpec`.

Do not put evaluator truth inside it.

The structure must be serializable.

---

# 12. Shared Contract: TaskContext

Define a bounded `TaskContext`.

It should contain the actual context granted for one execution, such as:

```text
task identity
evidence refs
selected extracts/content
policy context
relevant workflow state
```

Its design should reinforce bounded context.

Do not include the entire workspace automatically.

---

# 13. Shared Contract: TaskResult

Define `TaskResult`.

At minimum conceptually:

```text
task_id
status/outcome
executor_type
findings or result summary
evidence_refs
artifacts produced
uncertainty/unresolved issues
short operational rationale if useful
error information when failed
```

Do not store chain-of-thought.

The artifact subsystem must later be able to persist it.

The planning/execution subsystem must later be able to produce it.

The human subsystem must later be able to create compatible results.

---

# 14. Shared Contract: Finding

Define a compact `Finding`.

It should support:

```text
finding id
statement/summary
supporting evidence refs
confidence/uncertainty where useful
status if useful
```

Do not reproduce the hidden benchmark finding taxonomy here.

Runtime findings are observations/conclusions, not evaluator labels.

---

# 15. Shared Contract: WorkflowPlan

Define `WorkflowPlan`.

It should include conceptually:

```text
workflow/plan id
objective
assumptions
unresolved questions
tasks
plan status
version or revision metadata
```

Plan status should remain compatible with:

```text
PROPOSED
APPROVED
REVISION_REQUESTED
SUPERSEDED
```

Do not build planning logic.

Only define the contract.

---

# 16. Shared Contract: HumanResponseType

Define values compatible with the simulator/human-interaction design:

```text
COMPLETE
CLARIFICATION_REQUESTED
TASK_NARROWED
REASSIGNMENT_REQUESTED
AUTHORITY_DECLINED
```

You may include a small additional value only if clearly required by upstream specs.

Do not encode these as success/failure scores.

---

# 17. Shared Contract: HumanTaskResponse

Define a serializable response that can represent:

```text
operator_id
task_id
response_type
work/result supplied
clarifying question
narrowed scope
reassignment note
authority note
evidence/artifacts
timestamp if appropriate
```

Fields not relevant to a specific response type may be optional.

Do not implement persona behavior.

---

# 18. Shared Identity Types

Create simple conventions for:

```text
workflow_id
task_id
operator_id
```

Do not overengineer custom identifier classes unless the language benefits from them.

Keep IDs serializable.

Do not hardcode persona IDs into shared contracts.

---

# 19. Error Contracts

Define a few meaningful shared error categories/exceptions for integration.

Examples conceptually:

```text
ConfigurationError
ContractValidationError
WorkspaceAccessError
ExecutionError
PersistenceError
```

Do not build an exhaustive error taxonomy.

Track-specific errors should remain track-specific.

---

# 20. Path Utilities

Create minimal repository/runtime path utilities.

They should:

- use repository-relative/configurable paths;
- avoid `/Volumes/THOMAS/...`;
- identify static roots;
- identify runtime root;
- allow runtime directories to be created safely later.

Do not enumerate hidden evaluator paths as part of runtime-access helpers.

Evaluator-only code can handle those later.

---

# 21. Configuration

Create only minimal configuration needed for future tracks.

Potential concerns:

```text
repository root
runtime root
local model configuration placeholder
logging level
```

Do not require local-model availability yet.

Do not require API keys.

Do not add cloud configuration.

---

# 22. Serialization

Shared contracts should be easy to serialize to durable JSON or equivalent.

Use the implementation language's straightforward mechanism.

Do not create a database or migration infrastructure.

Where possible, include small deterministic round-trip tests.

---

# 23. Validation

Use deterministic validation where practical.

Do not ask an LLM to validate contracts.

If the project uses Python and adding a small existing validation library would materially simplify contracts, first inspect existing dependencies.

Avoid adding unnecessary dependencies merely for P00.

Simple dataclasses/types plus explicit validation are acceptable.

---

# 24. Empty Track Modules

Create minimal package/module placeholders so the first-wave ownership areas can begin without restructuring the project:

```text
workspace
artifacts
planning
execution
human
persona
operator_model
```

Add later-wave packages only if doing so is truly helpful.

Do not populate them with real behavior.

---

# 25. Test Layout

Create a minimal test structure matching track ownership.

Conceptually:

```text
tests/
├── core/
├── workspace/
├── artifacts/
├── planning/
├── execution/
├── human/
├── persona/
└── operator_model/
```

Do not create benchmark business tests yet.

P00 tests should verify only imports, serialization, enums, contract construction, path portability, and basic compatibility.

---

# 26. Required Compatibility Smoke Tests

Include a few smoke tests that prove tracks can compose through contracts.

At least test conceptually:

### Workspace -> Planning

Construct a `WorkspaceMap` and ensure it is usable as planner input type without workspace implementation.

### Planning -> Execution

Construct `TaskSpec` and `TaskContext`; ensure the result contract is compatible with `TaskResult`.

No actual executor is required.

### Execution -> Artifact

Ensure `TaskResult` is serializable in a form Daniel's artifact store can later persist.

### Human -> Operator Evidence Boundary

Construct `HumanTaskResponse` and verify it carries enough identifiers/result information for Frank's later evidence subsystem.

Do NOT create evidence-event generation yet.

---

# 27. No Production Mocks

Do not create fake production services such as:

```text
FakeWorkspaceScout
FakePlanner
FakeHuman
```

inside runtime packages.

Mocks/fixtures belong in tests.

The production packages should remain explicit stubs/interfaces until their track implements them.

---

# 28. Interface Freeze Marker

Create a concise developer note in code/module documentation indicating:

> Shared P00 contracts are cross-track interfaces. Change them only through an explicit interface change request during parallel development.

Do not create a large new specification file.

---

# 29. Branch Ownership Compatibility

Do not modify `PARALLEL_WORKSTREAM_PLAN.md`.

Ensure the source layout naturally supports:

```text
Daniel:
workspace + artifacts/workflow state

Thomas:
planning + execution + local model

Frank:
human + persona + operator model
```

No single central file should require all three to edit it continuously.

---

# 30. Avoid Central Orchestrator Implementation

You may define a tiny interface/protocol placeholder for future orchestration if truly necessary.

Do NOT implement a giant central `Governor` class now.

That would become a merge-conflict hotspot.

Integration/orchestration belongs to P01.

---

# 31. CASE Fixtures

Do not read CASE_001 workspace in this task unless needed to verify path portability.

Do not encode case facts.

Do not create case-specific shared contracts.

Business fixture work begins inside track prompts.

---

# 32. Evaluator Firewall

P00 runtime modules must not import:

```text
personas/*/evaluator.json
cases/*/ground_truth/
```

Do not create convenience loaders that expose them.

Evaluator-only infrastructure comes later.

---

# 33. Provenance Firewall

Runtime modules must not treat:

```text
company/northstar/provenance/
```

as policy.

Do not include provenance paths in runtime policy helpers.

---

# 34. Dependency Discipline

Before adding a package/dependency:

1. inspect current project dependencies;
2. determine whether the standard library/current dependency is sufficient;
3. add only what materially reduces implementation risk.

Do not install agent frameworks, vector databases, orchestration frameworks, cloud SDKs, or UI frameworks during P00 unless already intentional repository dependencies.

---

# 35. Logging

Provide minimal logging capability only if useful for all tracks.

Do not implement a telemetry system.

Logs must not expose hidden evaluator information.

Runtime debug logging should remain local.

---

# 36. README

Do not finalize README.

README finalization happens after real implementation exists.

---

# 37. Allowed Modifications

You may create/modify only implementation-bootstrap files needed for:

```text
shared core contracts
package/module skeleton
tests for shared contracts
minimal dependency/project configuration if required
```

Do NOT modify:

```text
AGENTS.md
HACKATHON_BUILD_PLAN.md
PARALLEL_WORKSTREAM_PLAN.md
company/**
personas/**
cases/**
operator_model/*.schema.json
operator_model/OPERATOR_PROFILE_SPEC.md
simulator/**
evaluation/EVALUATION_SPEC.md
evaluation/TEST_SUITE_INDEX.json
```

If an upstream spec appears inconsistent, report it rather than changing it.

---

# 38. Completion Gate

P00 is complete only if:

1. project/package imports cleanly;
2. shared contracts are defined;
3. contracts serialize/round-trip where appropriate;
4. paths are portable;
5. no subsystem functionality was prematurely implemented;
6. smoke tests pass;
7. Daniel can begin A01 using `WorkspaceMap`;
8. Thomas can begin B01 using a mocked `WorkspaceMap` and shared task/plan contracts;
9. Frank can begin C01 using mocked `TaskSpec` and `HumanTaskResponse`;
10. no hidden benchmark/evaluator data is exposed through runtime helpers.

---

# 39. Git Recommendation

Do not execute remote Git operations unless explicitly requested.

At the end, recommend that the team merge this shared bootstrap into `main`, then create:

```text
feature/workspace-state
feature/planning-execution
feature/human-operator
```

Do not create or push remote branches unless instructed by the user.

---

# 40. Final Report

After completion, report only:

1. implementation language/runtime selected or preserved;
2. files/directories created or changed;
3. shared contracts created;
4. tests run and result;
5. dependency changes, if any;
6. confirmation that no real subsystem behavior was implemented;
7. confirmation that no hidden evaluator/ground-truth loaders were created;
8. whether any interface uncertainty remains;
9. whether Daniel, Thomas, and Frank can branch independently now;
10. any upstream conflicts found.

Do not paste all source files into chat.

The repository is the deliverable.

Begin now.
