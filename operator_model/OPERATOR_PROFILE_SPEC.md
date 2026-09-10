# Workflow Governor Operator Profile Specification

**Status:** Canonical pre-implementation design specification  
**Company:** Northstar Regional Markets  
**Capability schema:** `northstar-operator-v1`  
**Canonical dimension source:** `company/northstar/schemas/northstar_operator_capability_schema.json`

## 1. Purpose and scope

An operator profile is a compact, evidence-backed model of how Workflow Governor should collaborate with one human operator. It should help the system answer:

- What work is this operator currently well suited to perform?
- What evidence supports that belief?
- What company or domain knowledge do they appear to possess?
- How much scaffolding and verification should the current task receive?
- What remains uncertain?
- What is the operator authorized and able to access?

The profile is an operational collaboration aid. It is **not** a psychological model, an HR evaluation, an intelligence or potential score, a permanent judgment, or a substitute for authorization and access controls. It MUST describe demonstrated workplace-relevant behavior narrowly enough to support task presentation, verification, and candidate selection.

This document specifies future behavior and data semantics only. It does not define executable profile updates, routing, storage models, APIs, user interfaces, persona simulation, Workflow Governor behavior, or integration with OpenClaw, NemoClaw, or OpenShell.

## 2. Normative invariants

Future implementations MUST preserve these invariants:

1. The short narrative is the primary representation for LLM reasoning. The capability vector is a secondary, standardized routing aid.
2. Capability, evidence confidence, knowledge, authority, access, confidence/communication style, and personality are distinct concepts. None may be silently substituted for another.
3. The capability vector has exactly the 19 dimensions, in exactly the order, defined by `northstar-operator-v1`. This specification does not add or redefine dimensions.
4. Capability and capability-evidence confidence use `[0,1]`, but they update independently.
5. `(capability = 0.5, evidence_confidence = 0.0)` means **unknown**, not average or weak performance.
6. Learned claims MUST be traceable to evidence-ledger references. Model-generated updates without evidence references are prohibited.
7. Authority and access are hard constraints. A high capability estimate MUST NOT authorize an action or create a grant.
8. Profile state belongs to a stable `operator_id`, not to a workflow. Temporary case observations may remain in case context rather than becoming durable profile state.
9. Negative durable updates require outcome verification and error attribution. A wrong final output is not automatically an operator error.
10. Appropriate clarification, task narrowing, refusal, or reassignment may be evidence of safe and capable collaboration rather than failure.

If another artifact uses a capability-like label not present in the canonical schema, an implementation MUST map it to a canonical dimension only when the semantics are unambiguous; otherwise it remains evaluator or narrative terminology and MUST NOT expand the vector. In particular, some initial persona evaluators use `structured_data_entry` and `food_safety_review`, while the canonical schema uses `structured_data_handling` and represents relevant food-safety work within `quality_compliance`. The schema controls runtime vector identity.

## 3. Hybrid operator representation

A future profile conceptually contains:

```text
Operator Profile
├── identity and schema metadata
├── capability vector C
├── capability evidence-confidence vector E
├── stable_summary
├── recent_notes
├── knowledge model
├── authority model
├── access/grant state
├── evidence statistics
└── evidence ledger references
```

The durable snapshot may conceptually live at:

```text
runtime/operators/<operator_id>/profile.json
```

and resemble:

```json
{
  "operator_id": "NRM-E0417",
  "company_id": "northstar-regional-markets",
  "capability_schema_version": "northstar-operator-v1",
  "capabilities": [],
  "capability_evidence": [],
  "stable_summary": "",
  "recent_notes": "",
  "knowledge": [],
  "authority": {},
  "access": {},
  "evidence_stats": {},
  "evidence_refs": [],
  "last_updated": ""
}
```

This is illustrative, not a finalized serialization schema. A snapshot is derived state; the evidence ledger is its durable factual basis.

## 4. Capability and evidence-confidence vectors

The future system should maintain two fixed-length vectors:

```text
C = current capability estimates
E = confidence that relevant evidence supports those estimates
```

Both vectors MUST follow `dimension_order` from the canonical capability schema. Values MUST remain in `[0,1]`. `C[i]` estimates task-execution capability on dimension `i`; `E[i]` estimates the strength and coverage of evidence behind that estimate. The pair must be interpreted together.

```text
Person A: spreadsheet_analysis = 0.50, evidence = 0.00
Meaning: the system does not yet know.

Person B: spreadsheet_analysis = 0.30, evidence = 0.85
Meaning: meaningful evidence supports a weak-performance estimate.
```

Those states MUST NOT be treated as equivalent. Rankings and task-fit comparisons SHOULD retain an explicit unknown state rather than converting uncertainty into a penalty.

No final update equation, learning rate, decay rate, routing formula, or dimension weights are defined here. Future update logic MUST follow these principles:

- Verified success may increase relevant capability and evidence confidence.
- Verified relevant failure may decrease relevant capability while increasing evidence confidence.
- Unverified outcomes and self-reports carry less evidentiary weight than independently or deterministically verified results.
- One event may affect multiple dimensions, but only dimensions materially exercised or implicated may move. Unrelated dimensions MUST NOT move.
- Task difficulty matters. Meaningful, difficult work generally supports stronger inference than trivial work.
- Scaffolding matters. Success after a detailed checklist is weaker evidence of independent capability than comparable unassisted success, although it remains valid evidence of checklist-driven execution.
- Repeated consistent outcomes matter more than one isolated outcome.
- Recent evidence may affect recent notes and temporary verification more quickly than the stable estimate.
- Evidence confidence should grow more from repeated, verified, independently checked, meaningfully difficult outcomes and less from indirect inference, one unverified result, self-report, or heavily scaffolded trivial work.
- Future systems may model staleness or decay, but this specification sets no constants.

The vector MAY support candidate-human ranking, task/person suitability comparison, scaffolding priors, verification priors, and multi-operator queue ranking. It MUST NOT independently authorize work.

## 5. Skill and company knowledge are separate

Capability describes ability to execute a class of work. Knowledge describes possession and reliability of topic-specific facts, rules, terminology, and company practices. Neither proves the other.

An operator who says, “Give me the applicable requirement and I can compare it against the certificate,” may have high `document_comparison` capability while lacking or being uncertain about Northstar quality knowledge. That response should primarily update knowledge state and collaboration guidance, not lower document-comparison capability. Conversely, recalling a Northstar policy does not prove the ability to perform complex spreadsheet analysis.

Company knowledge MUST NOT be encoded by adding vector dimensions. A compact topic-level record may resemble:

```json
{
  "topic": "invoice_processing",
  "level": "DETAILED",
  "confidence": "HIGH",
  "status": "CURRENT_AS_OBSERVED",
  "basis": ["EVT-0018", "EVT-0031"]
}
```

Recommended ordered knowledge levels are:

```text
UNKNOWN < VAGUE < GENERAL < DETAILED < SPECIALIST
```

Knowledge confidence is distinct from knowledge level. The model MUST be able to represent correct knowledge, partial knowledge, uncertainty, potentially stale knowledge, contradicted knowledge, and a belief that conflicts with an authoritative document. Verbal confidence and job title do not make a belief authoritative.

When an operator confidently recalls an outdated OTIF threshold, the system SHOULD preserve evidence that the belief was held, mark the topic as stale or contradicted, reduce confidence as appropriate, and use current authoritative policy as company truth. It MUST NOT broadly reduce unrelated numerical or analytical capability. Later correction evidence may revise the topic record.

## 6. Evidence ledger

The future append-only evidence ledger is conceptually stored at:

```text
runtime/operators/<operator_id>/evidence.jsonl
```

An event should be an attributable observation rather than a free-floating score change. A conceptual event shape is:

```json
{
  "event_id": "EVT-000123",
  "operator_id": "NRM-E0417",
  "timestamp": "...",
  "event_type": "TASK_VERIFIED_CORRECT",
  "task_id": "...",
  "task_family": "...",
  "capabilities_exercised": [],
  "difficulty": "...",
  "scaffolding_level": "STRUCTURED",
  "outcome": "...",
  "verification": "DETERMINISTIC",
  "error_attribution": null,
  "knowledge_topics": [],
  "profile_implications": [],
  "source_refs": []
}
```

Useful event families include:

- `TASK_COMPLETED`
- `TASK_VERIFIED_CORRECT`
- `TASK_VERIFIED_INCORRECT`
- `TASK_RETURNED`
- `CLARIFICATION_REQUESTED`
- `TASK_NARROWED`
- `REASSIGNMENT_REQUESTED`
- `OPERATOR_CORRECTED_AI`
- `AI_CORRECTED_OPERATOR`
- `KNOWLEDGE_DEMONSTRATED`
- `KNOWLEDGE_CORRECTED`
- `AUTHORITY_DECLINED`
- `AUTHORITY_VERIFIED`
- `ACCESS_DENIED_OR_UNAVAILABLE`

Event names are conceptual, but implementations SHOULD distinguish observation, verification, attribution, and profile implication. A completion event alone does not prove correctness. Evidence references should identify the task, verification result, relevant records, policy basis, and correcting party where available.

### 6.1 Mandatory error attribution

Before a durable negative capability update, the system MUST attribute the material cause among at least:

```text
OPERATOR_ERROR
AI_ERROR
SOURCE_CONTRADICTION
AMBIGUOUS_INSTRUCTION
MISSING_INFORMATION
TOOL_ERROR
POLICY_AMBIGUITY
UNRESOLVED
```

Mixed attribution SHOULD be possible. If an AI extracted the wrong invoice quantity and the operator reasonably relied on it, the system must not automatically lower invoice skill. If instructions omitted which PO revision governed, the result may reflect ambiguous instruction or missing information. `UNRESOLVED` MUST delay or weaken a negative update rather than defaulting to operator blame.

An operator correcting the AI is positive evidence for the capabilities and knowledge actually demonstrated. The system MUST retain the correction provenance rather than merely recording that the final team output was correct.

### 6.2 Task return, narrowing, and refusal

A returned task is not inherently a failed task. The event must distinguish:

- failure to perform work within a relevant demonstrated skill;
- request for a missing governing rule or source;
- safe narrowing to a bounded subtask;
- reassignment because specialist knowledge is absent;
- refusal because authority is absent;
- inability to proceed because access or information is missing.

“I can compare the fields, but Q&R must make the regulatory determination” may be positive evidence of uncertainty calibration, role awareness, authority awareness, and safe collaboration. It should not broadly lower capability.

## 7. Narrative profile

The LLM should normally consume a concise narrative rather than the raw numerical vector. The profile has two text layers.

### 7.1 `stable_summary`

- Target: 1,000–1,500 characters.
- Hard maximum: 1,600 characters.
- Purpose: durable operational strengths, demonstrated task boundaries, useful knowledge, recurring verified patterns, recommended scaffolding, and verification considerations.
- Update behavior: conservative; consolidate periodically or after material evidence.

### 7.2 `recent_notes`

- Target: no more than 400 characters.
- Hard maximum: 500 characters.
- Purpose: recent deviations, emerging patterns, temporary verification needs, or meaningful corrections not yet appropriate for the stable summary.
- Example: “Last two PO comparisons required correction because revision numbers were overlooked.”

The combined LLM-facing narrative therefore targets roughly 1,000–1,600 characters and MUST remain below 2,000 characters. It SHOULD include demonstrated strengths, representative successful tasks, clarification needs, recurring verified errors, useful company knowledge, current scaffolding, verification concerns, and appropriate task-return patterns. It MUST omit irrelevant biography and vague labels such as “smart,” “bad,” “weak employee,” or “high potential.”

Preferred language is evidence-oriented: “Repeatedly completes structured document comparisons correctly and works independently on ordinary spreadsheet reconciliation. Has required explicit governing policy before handling Q&R judgments.” Every factual claim MUST be supported by ledger events or trusted authority/access records. The narrative MUST distinguish repeated evidence from one-off observations and known facts from uncertainty. It SHOULD NOT repeat the full vector numerically.

## 8. Scaffolding and verification

Scaffolding describes how work is presented:

```text
NONE         outcome or task goal only
LIGHT        short reminder, relevant context, and evidence links
STRUCTURED   subtasks, criteria, governing rule, and expected output
STEP_BY_STEP detailed checklist or microtask instructions
```

The profile may recommend a level, but scaffolding MUST NOT be a function of capability score alone. Evidence confidence, topic knowledge, task consequence, novelty, recent errors, access conditions, and the availability of deterministic checks all matter. A highly capable analyst may need `STRUCTURED` instructions when a Northstar-specific policy is unfamiliar. A specialist with repeated verified success may need `NONE` or `LIGHT` support in a familiar domain.

Verification intensity may use:

```text
NORMAL
ENHANCED
MANDATORY
```

An unknown operator on consequential work may justify stronger verification. Repeated relevant errors may justify temporary enhanced verification; repeated verified success may permit lighter review where policy allows. Cheap deterministic verification SHOULD be preferred when appropriate. Safety, security, financial, access, separation-of-duties, and authority-required checks remain hard controls and MUST NOT be removed because capability is high.

## 9. Authority and access

Authority is categorical and sourced from trusted company or explicitly validated role data. It MUST NOT be represented as a fuzzy capability such as `release_quality_hold = 0.82`. A conceptual model may record:

```json
{
  "release_quality_hold": {
    "state": "VERIFIED_DENIED",
    "source_refs": ["ROLE-0041"]
  },
  "approve_procurement_exception": {
    "state": "VERIFIED_GRANTED",
    "scope": "assigned_category",
    "source_refs": ["ROLE-0041", "POLICY-01"]
  }
}
```

The model SHOULD distinguish `VERIFIED_GRANTED`, `VERIFIED_DENIED`, `CLAIMED`, and `UNKNOWN`. Claims may prompt validation but cannot authorize action. Authority MUST NOT be inferred solely from skill, job performance, confidence, knowledge, seniority, or job title.

Access and grants are separate from authority and capability. An operator may be capable and authorized but lack current file access, or have file access without decision authority. Access state may record allowed scopes, denied scopes, temporary grants, expiration, and source references. A temporary missing file or denied path MUST NOT become a capability failure. Job title alone does not imply access.

## 10. Identity and multiple operators

Every profile MUST be keyed by a stable `operator_id`, such as `NRM-E0417`, and scoped to `company_id`. A runtime `active_operator_id` selects the learned profile for the current human interaction. Several people may use the same workflow at different times; their evidence and profiles MUST remain separate.

The workflow definition is not the operator profile. Task or case context may temporarily note that one operator has seen a particular record, but workflow state MUST NOT be used as a substitute for durable person identity or be copied automatically into another operator's profile.

## 11. Task requirements and routing compatibility

Future tasks may declare sparse requirements over the same canonical 19 dimensions. For example, an invoice-reconciliation task may mark `numerical_reconciliation` as highly relevant, `cross_document_reasoning` as highly relevant, and `invoice_matching` as very highly relevant. Tasks need not contain dense, manually authored 19-element vectors, and this specification does not freeze task-vector generation or routing weights.

Task fit should combine narrative context, relevant capability/evidence pairs, knowledge, task difficulty, consequence, scaffolding, and verification options. Authority and access then act as independent constraints. A strong fit means “potentially suitable to perform,” not “authorized to approve.”

## 12. Cold start, conflicting evidence, and cadence

At cold start, every capability value is `0.5`, every evidence-confidence value is `0.0`, and the narrative states that evidence is insufficient while retaining any minimal trusted operational context. Knowledge contains only explicitly available trusted information. Authority contains only trusted company/role records; everything else is unknown. Access contains only explicit grants and restrictions. A new operator MUST NOT be labeled low-skill.

Initial assignments may favor low-risk, bounded, easily verified work that can generate useful evidence. This is guidance, not a fixed assignment algorithm.

Conflicting evidence must be preserved rather than averaged away without explanation. Five verified spreadsheet successes plus one recent verified failure should normally produce a recorded deviation, a modest localized estimate change if warranted, temporary verification, and a recent note—not immediate collapse of a stable estimate. More evidence should resolve whether the event is noise, drift, a difficulty boundary, or an emerging pattern. An operator's statement “I'm bad at spreadsheets” should remain low-weight self-report when repeated verified performance is strong.

Update cadence should follow layered materiality:

```text
event recorded immediately
→ vector and knowledge evidence may update
→ recent_notes may update
→ stable_summary consolidates periodically or after material events
```

Material events include verified success on a meaningful new capability, repeated relevant errors, an operator correction of the AI, discovery of a major skill boundary through reassignment, verified authority/access clarification, and meaningful domain-knowledge correction. Narrative regeneration after every trivial event is neither required nor desirable.

## 13. Northstar case examples

- **CASE_001 — Vendor activation:** A general employee may accurately perform a bounded visible-field or certificate check when the source and rule are supplied. That supports document/structured execution evidence, not Vendor Compliance expertise or authority to activate the vendor.
- **CASE_002 — OTIF exception:** A technical analyst may compare PO revisions and correctly calculate OTIF using supplied policy. That supports analytical capabilities, not independent Procurement interpretation, Logistics approval, or commercial authority.
- **CASE_003 — Freshness and temperature:** A receiving specialist may accurately gather readings, apply the receiving procedure, and maintain containment. Q&R retains technical disposition and release authority. Appropriate return of the release decision is positive boundary behavior.
- **CASE_004 — Invoice and bank change:** A technical analyst may correctly calculate price variance while an AP specialist owns bank-change controls and payment-release procedure. Neither arithmetic success nor invoice access authorizes a bank change.

These examples also show why a workflow should split mixed tasks rather than force one person to own every branch.

## 14. Profile reconstruction and explainability

Durable learned state must be explainable from evidence. A statement such as “Strong at invoice reconciliation” should cite or resolve to repeated relevant ledger events. The system MUST avoid unexplained drift and SHOULD be able to reconstruct a reasonable `C`, `E`, knowledge state, evidence statistics, and narrative basis after snapshot loss or corruption.

Perfect deterministic reproduction of natural-language wording is unnecessary. Factual claims, uncertainty, and material recommendations must remain ledger-backed. Derived state SHOULD retain schema version, source-event coverage, update time, and enough provenance to audit why a value or narrative changed.

## 15. Relationship to hidden persona evaluators

Production persona evaluator files are hidden test truth. Runtime Workflow Governor, the active operator, and persona simulators MUST NOT see them. Evaluation should compare:

```text
hidden evaluator truth
vs evidence available to Workflow Governor
vs learned runtime profile
vs actual task adaptation
```

The system is not expected to infer unobserved truths before relevant evidence exists. Evaluator concepts such as `initial_observability`, reasonable initial uncertainty, and profile convergence therefore matter more than immediate numerical agreement. Hidden evaluator bands must never be copied into runtime state as if learned.

## 16. Prohibited profile-learning patterns

Implementations MUST NOT use or infer:

- one scalar “employee score”;
- personality-vector profiling;
- unknown equals weak;
- job title equals capability;
- confidence equals correctness;
- skill equals authority;
- knowledge equals authority;
- access equals authority or capability;
- one mistake equals permanent downgrade;
- task return equals failure;
- self-report equals verified capability;
- successful checklist completion equals full independent expertise;
- model-generated capability changes without evidence references.

They also MUST NOT reward a confident wrong answer over a cautious correct clarification, treat operational acceptance as formal approval, or allow a successful final team output to hide which party introduced or corrected an error.

## 17. Privacy, fairness, and governance

Profiles MUST remain limited to demonstrated workplace-relevant behavior needed for collaboration. They MUST NOT infer or store unnecessary race, ethnicity, religion, political beliefs, medical conditions, disability, sexual orientation, family status, or other irrelevant protected or sensitive characteristics. Demographic proxies MUST NOT be used to estimate work capability.

Narratives MUST avoid unsupported psychological inference and HR-style judgments. The operator profile MUST NOT be repurposed as an employment-performance rating without separate, explicit governance, validation, notice, access controls, review, and appeal processes. Data retention and visibility should be proportionate to operational need.

## 18. Success criteria

The future mechanism succeeds when it can remain uncertain appropriately; learn demonstrated strengths; avoid overgeneralizing errors; distinguish skill from company knowledge; preserve authority and access as hard constraints; adapt instructions and verification; improve task/person matching; explain profile changes; and support multiple operators sharing one workflow.

Operationally correct adaptation is more important than perfect agreement with hidden numerical evaluator bands. A good profile knows both what the evidence supports and what it does not yet establish.
