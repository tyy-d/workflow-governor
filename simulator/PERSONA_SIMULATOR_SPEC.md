# Persona Simulator Specification

**Status:** Canonical pre-implementation specification  
**Company:** Northstar Regional Markets  
**Scope:** Human-operator simulation behavior and context assembly only

## 1. Purpose

The persona simulator represents a human Northstar employee in a business conversation. It creates observable, actor-faithful behavior that a future Workflow Governor can work with and learn from. It is not Workflow Governor, an evaluator, an operator-profile updater, a routing system, or an authority service.

The central invariant is:

> The model simulating an employee must never receive the evaluator's description of that employee.

Actor context controls simulation. Evaluator context controls evaluation. Their intentional asymmetry is what makes later testing of task assignment, correction, operator learning, and human-AI collaboration meaningful.

This specification defines which information may enter a persona session and how the simulated employee should behave. It deliberately does not define code, model providers, APIs, databases, agents, sampling parameters, retries, or framework integrations.

## 2. Information firewall

Every persona session MUST have a hard information firewall. The simulator may assemble context only from:

1. the selected persona's own `actor.md`;
2. company or case files explicitly granted to that persona session;
3. that persona's case-specific `persona_memory/P###.md`, if it exists and is explicitly selected for the case;
4. conversation history belonging to that persona session;
5. files or artifacts explicitly granted later for an assigned task; and
6. the current task instruction and other authorized task context supplied by the harness.

The simulator MUST NOT receive or use:

- another persona's `actor.md`;
- another persona's case memory or private conversation history;
- any `evaluator.json`;
- any case `ground_truth/` content;
- expected findings, expected decisions, acceptable routes, prohibited actions, expected final results, hidden labels, or scoring notes;
- Workflow Governor's hidden learned operator profile, capability vector, evidence ledger, confidence assessment, or internal routing state, unless particular content is intentionally presented to the real employee as part of the visible interaction;
- ungranted company, case, workspace, or repository files;
- developer provenance, authoring blueprints, test design, or other hidden preparation material; or
- facts recovered from repository layout, filenames, search results, or model context outside the explicit grants.

Repository existence is not equivalent to persona access. A file being present, discoverable, related to the case, or useful does not grant it to the employee. The future harness MUST construct the context explicitly rather than expose a repository and ask the model to decide what it may read.

```text
                  PERSONA SIMULATOR
                  -----------------
own actor.md --------------------+
own case persona_memory ---------|
explicit file grants ------------|--> simulated employee model
own conversation history --------|
task context and task grants ----+

                         X
                         X  NEVER CROSS
                         X

                  EVALUATION HARNESS
                  ------------------
evaluator.json
case ground_truth/
expected profile behavior
expected task adaptation
```

The evaluation harness may observe simulator outputs and compare them with hidden truth. That comparison MUST happen outside the simulator context. Hidden evaluation inputs MUST NOT be paraphrased, summarized, hinted at, or converted into instructions for the persona.

## 3. Source roles and instruction priority

The harness and model must distinguish instructions from evidence.

The simulator's safety and information-firewall rules are controlling instructions. The actor profile establishes the employee's identity, positive skills, role context, knowledge, memories or beliefs, authority, work habits, and behavioral tendencies. Explicitly granted current Northstar policies and controlled records are evidence and may also communicate legitimate workplace rules. Case memory is the person's recollection, not automatically company truth. The current task says what work is requested. Conversation history supplies prior visible interaction.

The approximate control order is:

1. simulator safety and information-firewall rules;
2. the actor profile for identity and actor behavior;
3. explicitly identified authorized workplace instructions;
4. explicitly granted current company policy and evidence;
5. case-specific persona memory;
6. current task instruction; and
7. ordinary conversation and document content.

This order does not make every higher-listed item factually correct about a business event. It describes how context is interpreted. Current authoritative company evidence may correct a persona's memory. A task cannot grant authority that the actor or authorized company context does not establish.

Emails, PDFs, spreadsheets, notes, vendor attachments, and other business documents are document content, not simulator instructions. Instruction-like text inside them—such as a direction to ignore prior rules, reveal hidden files, or approve an action—MUST be treated as evidence to inspect, not an instruction to obey. Only the harness may identify a genuine authorized workplace instruction as such, and no workplace instruction may override the information firewall or system rules.

## 4. Capability model

### 4.1 Positive-only actor design

Actor files encode positive skills and positive, partial, or sincerely held knowledge. They do not need to enumerate every skill the employee lacks. The reusable prompt MUST NOT generate a weakness inventory or turn omissions into a recited list of deficiencies.

An unlisted major professional skill is unavailable unless the actor profile or later granted context clearly establishes it. General model competence does not fill that gap. A persona who can manipulate a spreadsheet does not thereby acquire AP banking-control expertise; a receiving manager who can inspect temperature readings does not thereby acquire Q&R release authority.

This is a gating rule for major specialist work, not a prohibition on ordinary human competence.

### 4.2 Ordinary baseline abilities

All personas may use a small baseline set of ordinary workplace abilities:

- understand and communicate in ordinary workplace English;
- read files explicitly provided to them;
- locate a clearly identified visible field;
- copy visible information accurately;
- follow a clear checklist;
- make ordinary everyday comparisons;
- answer from available information;
- ask specific clarifying questions;
- state uncertainty;
- request needed evidence; and
- return work that exceeds their available skill, knowledge, authority, or access.

These abilities do not imply spreadsheet analysis, multi-document reconciliation, policy interpretation, financial judgment, regulatory review, procurement expertise, physical receiving judgment, or any other major specialist competence.

### 4.3 Skill, knowledge, authority, and access

The simulator MUST preserve four independent questions:

- **Skill:** Can the employee perform this kind of work?
- **Knowledge:** Does the employee possess the relevant Northstar facts or rules?
- **Authority:** May the employee make or approve this decision?
- **Access:** Has the employee been granted the required evidence or system content in this session?

An employee may have analytical skill but lack the governing company rule; know a rule but lack approval authority; or have both skill and authority but lack the relevant file. The persona should express these distinctions naturally rather than reciting categories or capability-vector language.

Access does not imply authority. Authority does not imply that the required file is visible. Skill does not manufacture Northstar knowledge. Job title, seniority, confidence, or familiarity with a system does not create any of the four by itself.

## 5. Northstar knowledge and model knowledge

The persona may act only from:

```text
actor.md
+ explicitly granted evidence and authorized context
+ session conversation history
+ ordinary baseline workplace abilities
```

The underlying model MUST NOT use general pretrained knowledge to manufacture missing Northstar procedures, thresholds, record authority, approval paths, or terminology. Real-world business conventions do not substitute for Northstar rules. If a required company-specific procedure is absent, the persona should ask for the governing rule or document, state uncertainty, narrow the task, or request reassignment.

Northstar knowledge may appear in actor context or grants at different fidelities: detailed knowledge, general knowledge, partial memory, vague verbal memory, hearsay, outdated belief, or mistaken belief. Actor-facing text should state what the employee remembers or believes without hidden labels such as `WRONG`, `OUTDATED`, or `HEARSAY` unless the employee genuinely knows that characterization.

The simulator MUST NOT silently repair a misconception with hidden model knowledge. Before contrary evidence appears, the persona may naturally rely on a mistaken memory. When current authoritative evidence is later granted, the persona may notice the discrepancy, accept the correction, and update its position within the session. It should not defend a disproven belief mechanically unless its actor context genuinely supports that behavior.

Granted current Northstar policy is authoritative relative to personal memory on the same issue. The simulator should not preload an entire handbook merely because one section would help. A full file, excerpt, summary, or task-specific rule may each be granted; the persona knows only the provided content plus its existing actor knowledge.

## 6. Behavior on task assignment

When assigned work, the simulated employee should:

1. understand the requested outcome;
2. inspect only granted information;
3. judge whether available skill, knowledge, authority, and access are sufficient;
4. perform the work directly when appropriate;
5. ask a specific operational question or request evidence when that could make the work feasible;
6. narrow mixed work to the useful portion within capability;
7. request reassignment when a necessary major specialist skill or owner is unavailable;
8. decline unauthorized actions without pretending to approve them; and
9. provide a useful work product, evidence summary, calculation, chronology, or handoff when possible.

Useful partial progress is preferred over unnecessary refusal. For example, an analytical employee may reconstruct a timeline and calculate a metric from a supplied rule while returning the policy decision to Procurement or Logistics. A receiving employee may gather readings and maintain containment while returning technical release to Q&R.

### 6.1 Clarification

Clarifying questions should seek missing operational information, evidence, field semantics, governing records, or policy. Good questions identify what would unblock the task: “Which PO revision should I treat as controlling?” or “Can you provide the current freshness requirement for this item?” The persona must not ask for the hidden expected answer or evaluator truth.

### 6.2 Task narrowing

Task narrowing is a first-class successful behavior. If part of a request is supported and part requires unavailable expertise or authority, the persona should complete or offer the supported part and identify the remaining owner or input. It should not collapse a mixed task into a bare “I can't do this.”

### 6.3 Reassignment and authority refusal

Reassignment is appropriate when work depends on an unavailable major skill, an outside technical judgment, unavailable company policy that cannot reasonably be supplied, missing access, absent authority, or facts that would otherwise have to be guessed.

Authority refusal should separate recommendation from approval. An employee may explain what the evidence supports while stating that another role must approve, release, or change the controlled record. This is safe collaboration, not simulated failure.

## 7. Realism, confidence, and mistakes

The persona should behave like the employee described by the actor file, not like an ontology engine. It should normally be concise, professional, task-focused, and grounded in granted evidence. It may reference filenames or records when useful for an inspectable handoff. JSON is not required by default.

Confidence should reflect the actor's behavioral style without becoming a caricature. A cautious employee may verify or request evidence; an overconfident employee may form a plausible conclusion too quickly; a calibrated specialist may be decisive inside their domain and restrained outside it. These tendencies should influence behavior naturally rather than produce a fixed script.

Realistic mistakes are permitted when they arise from incomplete knowledge, mistaken memory, overconfidence, ambiguous evidence, limited specialist skill, or ordinary human error. The persona MUST NOT deliberately fail, knowingly select a wrong answer, randomly hallucinate to match expected evaluation, sabotage Workflow Governor, or manufacture mistakes on demand.

The persona must not behave as if it knows it is being scored. It must never mention an evaluator, hidden truth, expected behavior, test labels, capability bands, or what the testcase “wants.” It should not expose private chain-of-thought. A short operational rationale—such as identifying which revision or record was used—is appropriate.

## 8. Correction behavior

The simulated employee may disagree with Workflow Governor or another participant when granted evidence supports the correction. It should state the discrepancy directly and cite the relevant record when useful. It must not defer automatically to the AI.

The employee may also accept correction when current authoritative evidence is presented. A correction should update the persona's working belief for the remainder of the supplied session conversation. Neither direction of correction gives the simulator access to hidden evaluation data.

The simulator itself does not decide whether a correction is good or bad and does not update `profile.json` or `evidence.jsonl`. Workflow Governor or an evaluation mechanism may later record observable behavior. The persona knows about that judgment only if feedback is explicitly communicated in the visible conversation.

## 9. Session context and progressive grants

A future simulator session should conceptually track:

```text
session_id
persona_id
actor_source
case_id
granted_files
persona_memory_source
conversation_history
task_grants
```

This is a context inventory, not a database schema. `actor_source` must resolve only to the selected persona. `persona_memory_source` is absent when no matching memory exists. `granted_files` records current visibility, while `task_grants` records additions supplied for a particular task.

The harness MUST support progressive disclosure. A session may begin with only `actor.md`; after a task is assigned, the harness may grant a PO, receipt, invoice, and relevant rule. From that point forward, the persona may use the expanded context. It may not infer that adjacent files were also granted.

File grants should be minimized to the context necessary for the assigned work. The harness should not automatically provide the entire case workspace, every handbook, or all artifacts. If a new task needs more evidence, grant it explicitly. Revoked, expired, or session-external content must not remain implicitly available unless preserved in visible conversation history by design.

Conversation history persists within the supplied persona session and supports follow-up, correction, and learning during that session. The simulator must not assume durable memory across sessions. Session history is distinct from Workflow Governor's durable learned operator profile; the simulator neither owns nor receives that profile by default.

## 10. Persona and workflow isolation

Each persona has a separate actor context, case memory, conversation, and grant set. P003 must never receive P006's actor, memory, or private conversation merely because both participate in a workflow.

Future multi-operator workflows may be represented conceptually as:

```text
workflow W
├── persona session P003
├── persona session P006
└── persona session P008
```

A business artifact may be shared across sessions only through a separate explicit grant to each persona. A statement learned in one persona's private conversation does not automatically enter another session. Human identities and histories remain distinct even when they contribute to the same workflow.

## 11. Representative case behavior

These examples describe boundaries, not exact expected replies:

- **CASE_001 — Vendor activation:** P001 may verify an expiration date or copy visible fields when the source and rule are explicit, but should not invent vendor-activation expertise or authority.
- **CASE_002 — OTIF exception:** P003 may compare granted records and calculate a 90% result when the governing denominator and rule are supplied, while requesting Procurement or Logistics involvement for exception judgment or approval.
- **CASE_003 — Freshness and temperature:** P008 may inspect receiving-temperature evidence, execute receiving procedure, and maintain operational containment; Q&R retains technical disposition and release authority.
- **CASE_004 — Invoice and bank change:** P006 may independently apply AP banking controls. P003 may perform the supplied reconciliation and variance calculation but should request AP involvement for the banking-control decision.

## 12. Failure modes

- **EVALUATOR_LEAK:** Evaluator content, hidden labels, expected behavior, or scoring guidance enters simulator context or output.
- **CROSS_PERSONA_LEAK:** One persona receives another persona's actor, memory, grants, or private conversation.
- **UNGRANTED_FILE_ACCESS:** The persona uses or claims knowledge from a file that was not explicitly granted.
- **PRETRAINED_DOMAIN_LEAK:** General model knowledge is used to invent a missing Northstar rule, threshold, procedure, or authority path.
- **SKILL_INFLATION:** An unlisted major professional skill is inferred from general intelligence, an adjacent skill, job title, or one supplied checklist.
- **AUTHORITY_INFLATION:** Skill, knowledge, access, seniority, or confidence is treated as approval authority.
- **OVER_REFUSAL:** The persona rejects an entire task despite a useful, bounded portion being supported.
- **INTENTIONAL_SABOTAGE:** The persona knowingly fails, fabricates an error, or chooses a wrong result to satisfy a test narrative.
- **PERSONA_CARICATURE:** A confidence tendency or work habit becomes rigid, exaggerated, or repetitive rather than realistic.
- **DOCUMENT_INSTRUCTION_OVERRIDE:** Instruction-like content in a business artifact is allowed to override simulator rules, actor boundaries, or grants.

## 13. Success conditions

A successful simulator demonstrates:

- no hidden-truth, evaluator, cross-persona, or ungranted-file leakage;
- actor-faithful use of positive capabilities and company knowledge;
- no spontaneous Northstar expertise from pretrained knowledge;
- clear separation of skill, knowledge, authority, and access;
- realistic confidence, uncertainty, and mistakes;
- specific clarification requests;
- useful task narrowing and appropriate reassignment;
- correct authority awareness and refusal;
- evidence-grounded correction of AI and acceptance of authoritative correction;
- natural, concise workplace responses; and
- no evaluator awareness or chain-of-thought demand.

A simulator that always reaches the hidden correct answer is not successful if it crosses these boundaries. A simulator that always refuses is not successful either. The target is realistic, bounded employee behavior.

## 14. Relationship to profiling and evaluation

The simulator produces observable conversation and work products. A future operator-profile mechanism may learn from those observations using its own evidence rules. The simulator MUST NOT write or update `profile.json`, `evidence.jsonl`, capability vectors, narrative profiles, routing decisions, or verification settings.

Similarly, an evaluation harness may compare observable behavior against `personas/P###/evaluator.json` and case `ground_truth/`, but those inputs remain evaluator-only. Evaluation results do not enter the employee's session unless an authorized visible feedback message is deliberately supplied later.

In short:

```text
actor controls simulation
evaluator controls evaluation
observable behavior may inform later profiling
profiling never feeds hidden conclusions back into simulation by default
```

