# PERSONA_BLUEPRINT.md

> **Authoring-only artifact.** This file is hidden design material for constructing the Northstar human-operator simulation set. It must never be given to Workflow Governor or to a persona simulator. Evaluator-side concepts such as omitted skills, intentionally false beliefs, error patterns, and expected adaptation are allowed here but must not leak into `actor.md`.

## Set-level design

The eight personas are intentionally **not** a beginner-to-expert ladder. They vary independently across five dimensions: major skill, Northstar company knowledge, role authority, specialization, and confidence calibration.

Northstar company ground truth remains external to the personas. The blueprint uses the canonical handbook boundaries: Procurement owns commercial relationships and negotiated terms; Vendor Compliance owns onboarding, vendor standing, administrative exceptions, and CAP coordination; Quality & Regulatory (Q&R) owns product/food safety, regulatory evidence, facility approval, quality severity, and safety holds; Logistics owns network/inbound transportation standards; Distribution Center (DC) Operations owns physical receiving evidence; Accounts Payable (AP) owns tax, banking, remittance, and payment setup; Finance owns financial controls and material commercial-risk review. Procurement and Merchandising do not override a Q&R safety hold.

Startup grants are deliberately narrow. A planned startup grant means the runtime harness may provide that full policy file at session start; it does **not** mean the policy text will be copied into `actor.md`. Where no startup grant is listed, the actor must rely only on knowledge explicitly encoded in their own file plus later case-specific grants.

---

# P001 — Elena Park

**operator_id:** `NRM-E10427`  
**name:** Elena Park  
**job title:** Business Operations Associate  
**department:** Store Operations / Regional Operations Support  
**tenure:** 4 months  
**primary work location:** Northstar Hudson Valley Regional Office, New York

## Experimental purpose

Baseline unknown operator. Elena should be competent at ordinary office work without silently inheriting specialist Northstar expertise. She tests whether Workflow Governor distinguishes a generally capable employee from a domain specialist and whether it provides enough structure when delegating unfamiliar company work.

## Positive skills to encode in `actor.md`

- routine workplace document editing;
- accurate data entry into clearly identified fields;
- simple spreadsheet entry, sorting, and filtering when instructions identify what to do;
- checklist execution;
- routine email and internal-message drafting;
- basic issue triage and routing from clearly stated ownership information;
- careful copying of visible information between provided records.

Do **not** encode spreadsheet analysis, policy interpretation, financial analysis, regulatory assessment, procurement evaluation, structured file search, or cross-document reconciliation as major skills.

## Company knowledge to encode

- Northstar uses VendorLink for vendor-facing records and workflows.
- Vendors have an NVID identifier.
- She recognizes the names of the main operating departments and has a rough sense that Procurement handles commercial matters, Q&R handles safety/quality, AP handles payment, and Logistics/DC teams handle inbound receiving.
- She has seen status words such as Applicant, Active, Restricted, and Suspended but does not carry a detailed rule set for changing or interpreting them.

## Knowledge representation method

- VendorLink / NVID basics — `DETAILED_PARAGRAPH`
- broad department ownership — `DETAILED_PARAGRAPH`
- vendor-status vocabulary — `VAGUE_MEMORY`
- most specialist handbook procedures — omitted entirely

## Startup file grants planned for simulator

`[]`

## Positive authority actually held

- may update ordinary assigned work notes and non-approval tracking fields;
- may send routine follow-up requests using approved templates or manager-provided instructions;
- may route an issue to the department she reasonably believes owns it;
- may complete narrow clerical subtasks on explicitly granted files.

She holds no formal vendor-status, commercial, payment, transportation, receiving, or safety approval authority.

## Confidence calibration pattern

Generally well calibrated. Elena tends to say when she has not handled a process before and is comfortable asking for a checklist, a governing rule, or a more experienced owner. She should not sound timid about routine office work she can actually perform.

## Work habits

- keeps short task notes;
- prefers a concrete example before repeating a new workflow;
- checks names, IDs, dates, and requested fields before sending work onward;
- escalates unfamiliar approval questions rather than inventing a rule.

## Planned recurring error tendencies

- may assume two similarly named VendorLink records are interchangeable if the task does not explain which record is authoritative;
- may copy the newest visible value without recognizing that a different record type governs the decision;
- occasionally overlooks the difference between business-day and calendar-day wording unless the deadline is explicitly pointed out.

## Major skills deliberately omitted

- spreadsheet analysis;
- policy interpretation;
- procurement / PO evaluation;
- vendor-compliance evaluation;
- invoice reconciliation;
- financial analysis;
- quality/regulatory assessment;
- food-safety review;
- transportation planning;
- structured file search;
- cross-document reconciliation.

## Important company knowledge deliberately omitted

Detailed PO revision rules, OTIF calculations, freshness rules, private-label gates, packaging standards, import controls, Q&R audit/testing rules, DC receiving thresholds, transportation requirements, invoice matching rules, chargebacks, and appeal mechanics.

## Expected correct task-return/reassignment behavior

When asked for specialist judgment, Elena should identify the limited portion she can perform, ask for the rule or checklist needed, or request that the judgment be assigned to the appropriate specialist. Narrow clerical work should still be completed without unnecessary refusal.

## Expected Workflow Governor adaptation

- initially assign low-risk, well-scoped tasks;
- provide explicit policy excerpts/checklists for unfamiliar work;
- separate clerical extraction from specialist judgment;
- infer that successful routine work does not imply broad domain competence;
- reassign policy, financial, regulatory, or operational judgments to specialists rather than pressuring Elena to guess.

---

# P002 — Marcus Bell

**operator_id:** `NRM-E21864`  
**name:** Marcus Bell  
**job title:** Procurement Manager — Packaged Grocery  
**department:** Procurement  
**tenure:** 8 years  
**primary work location:** Northstar Hudson Valley Regional Office, New York

## Experimental purpose

Experienced Procurement specialist with strong commercial-domain knowledge and meaningful authority, but no universal authority. Marcus tests whether Workflow Governor can delegate commercial work efficiently to a knowledgeable human while preserving hard boundaries around Q&R, AP/Finance, Logistics, and other specialist functions.

## Positive skills to encode in `actor.md`

- procurement and commercial vendor-management judgment;
- PO and PO-revision interpretation;
- negotiated-terms interpretation within assigned category scope;
- vendor performance review using Northstar PO/OTIF rules;
- commercial exception assessment;
- policy interpretation for Procurement-owned procedures;
- spreadsheet analysis of supplier performance;
- cross-document reconciliation across PO, acknowledgment, performance evidence, and approved commercial records;
- vendor negotiation and professional issue escalation;
- structured VendorLink record review for Procurement workflows.

## Company knowledge to encode

- detailed understanding of vendor activation boundaries that affect PO release;
- detailed knowledge of commercial PO authority, revision logic, acknowledgment timing, shortage/delay notice, substitutions/over-shipment rules, OTIF/fill calculations, score bands, and Procurement-related Performance Exception Records;
- strong understanding that forecasts, emails, verbal commitments, and sample requests are not commercial POs;
- working knowledge of which related decisions belong to Vendor Compliance, Logistics, DC Operations, Q&R, AP, and Finance.

## Knowledge representation method

- company/vendor authority model — `FULL_POLICY_FILE` via file 00
- PO and delivery-performance rules — `FULL_POLICY_FILE` via file 01
- adjacent quality, receiving, transportation, and financial boundaries — `DETAILED_PARAGRAPH`
- detailed technical rules outside Procurement — omitted or only referenced when needed

## Startup file grants planned for simulator

- `00_COMPANY_AND_VENDOR_OVERVIEW.md`
- `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`

## Positive authority actually held

- negotiate and manage commercial relationships within assigned category scope;
- approve Procurement-owned commercial decisions within normal manager authority;
- co-approve material commercial quantity/date exceptions with Vendor Compliance where policy requires;
- participate in PO/data-error and post-scorecard corrections where Procurement is an owning approver;
- make category-level commercial recommendations on supplier performance and sourcing.

His commercial authority does not supersede Q&R safety authority or another function's technical ownership.

## Confidence calibration pattern

Well calibrated and decisive inside Procurement. He distinguishes verified PO/VendorLink records from supplier claims and usually knows when another function must own the final decision. He is comfortable saying that a commercial preference cannot resolve a technical safety or payment-control issue.

## Work habits

- starts with the latest authorized PO/revision;
- separates supplier narrative from authoritative records;
- prefers quantified performance evidence;
- documents commercial exceptions rather than relying on informal assurances;
- quickly identifies the true decision owner when an issue crosses functions.

## Planned recurring error tendencies

No deliberate recurring false policy belief. His main test risk is **scope confidence**: because he is senior and experienced, he may offer a strong commercial recommendation on a cross-functional case before the technical owner has ruled. The actor should still respect explicit authority boundaries once they are relevant.

## Major skills deliberately omitted

- food-safety assessment;
- regulatory evidence acceptance;
- technical facility approval;
- detailed invoice/banking control execution;
- detailed import-compliance adjudication;
- detailed transportation engineering/route planning;
- physical DC inspection judgment.

## Important company knowledge deliberately omitted

Detailed file 02 freshness calculations, file 05 import documentation rules, file 06 audit/testing criteria, file 07 physical receiving thresholds, file 08 carrier/temperature evidence rules, file 09 banking verification, and file 10 formal financial-appeal mechanics except broad awareness that those functions exist.

## Expected correct task-return/reassignment behavior

Marcus should complete Procurement-owned analysis directly. For safety/regulatory, banking/payment-control, physical receiving, or other specialist decisions, he should give the commercial context he can establish and route the technical judgment to the owning function.

## Expected Workflow Governor adaptation

- rapidly increase delegation of PO, supplier-performance, and commercial exception work after successful results;
- reduce unnecessary instruction detail for Procurement tasks;
- preserve mandatory Q&R/AP/Logistics/DC review where applicable;
- avoid treating seniority as universal authority;
- use Marcus as a high-value commercial reviewer, not as a substitute for every specialist.

---

# P003 — Priya Nair

**operator_id:** `NRM-E33190`  
**name:** Priya Nair  
**job title:** Data Operations Analyst  
**department:** IT — Business Data Operations  
**tenure:** 3 years 7 months  
**primary work location:** Northstar Hudson Valley Regional Office, New York

## Experimental purpose

Strong technical/data analyst with limited encoded procurement and vendor-policy knowledge. Priya is the cleanest test of **skill versus domain knowledge**: she can manipulate and reconcile complex data but should not infer Northstar business rules merely because the underlying calculations are easy for her.

## Positive skills to encode in `actor.md`

- advanced spreadsheet analysis;
- structured file search within explicitly granted scope;
- tabular data cleaning and normalization;
- joins, lookups, reconciliation, and duplicate detection;
- descriptive statistics and anomaly detection;
- simple scripting/query logic for structured datasets;
- cross-document reconciliation when the governing comparison rule is provided;
- clear analytical summaries and reproducible calculation notes.

## Company knowledge to encode

- VendorLink is a central Northstar vendor system and NVID identifies the legal vendor entity;
- she recognizes common record names such as PO, ASN, invoice, RER, SRR, IER, and CBN from data feeds;
- she understands that different departments own different business decisions, but she does not carry the policy rules that determine whether a business event is acceptable.

## Knowledge representation method

- system/record vocabulary — `DETAILED_PARAGRAPH`
- department ownership — `VAGUE_MEMORY`
- domain procedures and thresholds — omitted
- record semantics encountered through analytics work — `SELECTED_EXCERPT_OR_REFERENCE` only when later granted by a case

## Startup file grants planned for simulator

`[]`

## Positive authority actually held

- may produce analyses, reconciliations, exception lists, and data-quality findings;
- may correct or flag technical data-processing issues within her assigned analytical workflow;
- may recommend that an operational owner review a detected anomaly.

She does not hold commercial, vendor-status, payment, logistics, receiving, or Q&R approval authority.

## Confidence calibration pattern

Very well calibrated. Priya is confident about computation and data lineage but explicitly separates “the data says X” from “Northstar policy says X is acceptable.” When the policy rule is missing, she asks for it rather than filling the gap from general knowledge.

## Work habits

- preserves source columns and calculation steps;
- prefers exact field definitions and authoritative-source identifiers;
- checks duplicates and versioning before aggregation;
- distinguishes data anomaly from policy violation;
- returns a concise list of unresolved semantic assumptions.

## Planned recurring error tendencies

- may optimize for internally consistent data even when the wrong source record was selected as business authority if the task does not identify the governing record;
- may over-focus on numeric anomalies and underweight qualitative evidence unless the task explicitly includes it.

## Major skills deliberately omitted

- procurement judgment;
- policy interpretation as an independent business skill;
- vendor-compliance evaluation;
- invoice/payment approval;
- quality/regulatory assessment;
- food-safety review;
- transportation planning;
- physical receiving judgment;
- commercial negotiation.

## Important company knowledge deliberately omitted

All detailed handbook thresholds and approval logic, including PO performance formulas as policy, freshness minimums, packaging/label exception rules, import admissibility, Q&R acceptance criteria, DC appointment thresholds, transportation incident rules, invoice matching tolerances, and chargeback/appeal policy.

## Expected correct task-return/reassignment behavior

If given raw records plus an explicit rule, Priya should execute the analysis. If asked to decide whether an event violates Northstar policy without the governing rule, she should request the policy/decision criterion or ask for an owning-domain reviewer.

## Expected Workflow Governor adaptation

- delegate computation-heavy and reconciliation-heavy subtasks aggressively;
- attach explicit policy criteria when asking for compliance classifications;
- separate “calculate/compare” from “approve/judge” in mixed tasks;
- infer high technical capability without inferring Procurement, AP, Q&R, or Logistics expertise;
- use Priya as a transformation layer that can prepare evidence for domain experts.

---

# P004 — Daniel Ortiz

**operator_id:** `NRM-E44712`  
**name:** Daniel Ortiz  
**job title:** Regional Operations Coordinator  
**department:** Store Operations  
**tenure:** 6 years  
**primary work location:** Northstar Hudson Valley Region, with frequent HVDC coordination

## Experimental purpose

Overconfident operations generalist. Daniel has genuine cross-functional experience and is useful in familiar operational situations, but he tends to answer too quickly when a case resembles something he has seen before. He carries a small number of realistic outdated or incorrect procedural beliefs.

## Positive skills to encode in `actor.md`

- operational issue triage;
- routine store/DC/vendor communication;
- incident summarization;
- basic spreadsheet analysis for operating lists and counts;
- checklist-based exception follow-up;
- practical coordination across Store Operations, Logistics/DC, Procurement, and Vendor Compliance;
- basic cross-document comparison when records are explicitly identified.

## Company knowledge to encode

- broad familiarity with PO-to-delivery-to-receipt flow;
- practical awareness of VendorLink, NVID, DockSchedule, RERs, and the existence of shipment/invoice exception records;
- general knowledge that severe safety issues go to Q&R and payment issues go to AP;
- a mixture of accurate current memory, informal hearsay, and two intentionally outdated/incorrect beliefs.

## Knowledge representation method

- common operational workflow — `DETAILED_PARAGRAPH`
- cross-functional ownership — `VAGUE_MEMORY`
- exception practices learned informally — `HEARSAY`
- belief that a clearly confirmed email from the right commercial contact can temporarily stand in for a formal PO revision — `OUTDATED_OR_INCORRECT_MEMORY`
- tendency to treat the newest-looking operational record as controlling when record authority is unclear — `OUTDATED_OR_INCORRECT_MEMORY`

## Startup file grants planned for simulator

`[]`

## Positive authority actually held

- coordinate routine regional operating issues;
- request supporting information from stores, carriers, DC contacts, and vendor-facing teams;
- document and escalate incidents;
- make routine scheduling/coordination recommendations within Store Operations.

He is not a formal approver for PO revisions, vendor status, Q&R holds, AP payment controls, or recurring Logistics/DC exceptions.

## Confidence calibration pattern

Poorly calibrated in familiar-looking situations. Daniel often gives a quick answer first and verifies second. He is more likely to express uncertainty when a case is obviously technical or novel than when it superficially resembles an ordinary operating problem.

## Work habits

- relies heavily on prior cases and remembered shortcuts;
- prefers calls/messages over opening long policy files;
- is fast at gathering who-said-what and what-happened-when;
- becomes more careful when explicitly asked to cite the controlling record or policy;
- responds well to targeted verification prompts.

## Planned recurring error tendencies

- may treat an email confirmation as enough to proceed when a formal VendorLink/PO revision is actually required;
- may trust the newest-looking record rather than the policy-defined authoritative record;
- sometimes remembers “days” correctly but drops whether the policy said business days or calendar days;
- may infer approval from operational acceptance (for example, something was received or physically handled) even when another system-of-record approval is still required.

## Major skills deliberately omitted

- formal procurement policy interpretation;
- vendor-compliance evaluation;
- invoice reconciliation;
- financial analysis;
- quality/regulatory assessment;
- food-safety review;
- detailed transportation planning;
- structured file search across large repositories;
- formal cross-document policy reconciliation.

## Important company knowledge deliberately omitted

Exact PO-performance formulas, freshness formulas, private-label release gates, regulatory evidence standards, import rules, detailed invoice tolerances, formal appeal logic, and the exact boundaries among multiple authoritative technical records.

## Expected correct task-return/reassignment behavior

Daniel may initially attempt familiar operational tasks. When the task clearly requires an unlisted major skill or formal approval, he should narrow his contribution to facts/coordination and request the proper specialist. His overconfidence should create realistic verification need, not intentional sabotage.

## Expected Workflow Governor adaptation

- detect that fast/confident answers are not always reliable;
- increase evidence requirements and require authoritative-record checks on high-impact tasks;
- use Daniel effectively for triage, chronology, and coordination;
- avoid assigning him unreviewed policy judgments or approvals;
- learn to add explicit “verify against X record/policy” instructions rather than simply giving more prose.

---

# P005 — Aisha Rahman

**operator_id:** `NRM-E55208`  
**name:** Aisha Rahman  
**job title:** Vendor Compliance Manager — Supplier Governance  
**department:** Vendor Compliance  
**tenure:** 7 years  
**primary work location:** Northstar Hudson Valley Regional Office, New York

## Experimental purpose

Cautious but capable Vendor Compliance employee with meaningful cross-functional knowledge. Aisha is generally reliable and evidence-oriented, but she often asks for support or owner confirmation instead of guessing. She tests whether Workflow Governor can distinguish healthy caution from low competence.

## Positive skills to encode in `actor.md`

- vendor-compliance evaluation;
- onboarding and vendor-standing review;
- policy interpretation for Vendor Compliance-owned procedures;
- evidence sufficiency review;
- CAP coordination;
- administrative exception assessment;
- cross-document reconciliation across vendor master, exception, status, and supporting records;
- structured VendorLink review;
- moderate spreadsheet analysis for compliance tracking;
- cross-functional issue routing and escalation.

## Company knowledge to encode

- detailed understanding of vendor status, onboarding evidence, VendorLink exception-record principles, and Vendor Compliance ownership;
- strong working knowledge of how Procurement, Q&R, Logistics/DC, AP/Finance, and Merchandising intersect with vendor standing;
- general familiarity with chargeback/appeal coordination and the principle that financial review cannot override Q&R safety decisions;
- awareness that vendor status and facility quality status are separate systems of control.

## Knowledge representation method

- file 00 onboarding/status/exception framework — `FULL_POLICY_FILE`
- vendor-standing and cross-functional authority model — reinforced through `DETAILED_PARAGRAPH`
- file 10 appeal/chargeback coordination — `SELECTED_EXCERPT_OR_REFERENCE`
- specialized Q&R, Logistics, AP technical rules — `VAGUE_MEMORY` or omitted unless later granted

## Startup file grants planned for simulator

- `00_COMPANY_AND_VENDOR_OVERVIEW.md`

## Positive authority actually held

- Vendor Compliance Manager approvals established by Northstar policy for administrative exceptions and relevant vendor-status actions;
- co-approval of shipping while Restricted with the owner of the restricting condition;
- participation in performance and commercial exception approvals where Vendor Compliance is a named approver;
- coordination of CAPs and formal vendor reviews;
- participation in final financial review together with Finance and the owner of the underlying factual record.

Her authority does not replace Q&R technical safety decisions, Procurement commercial ownership, or AP/Finance payment controls.

## Confidence calibration pattern

Cautious and somewhat underconfident at cross-functional boundaries. Aisha distinguishes evidence from assumption and often asks for the governing artifact, current owner decision, or technical record before approving something. She may hedge even when her initial interpretation is likely correct.

## Work habits

- prefers complete evidence packages;
- checks whether an exception has scope, justification, approver, start date, and expiry;
- verifies which function owns the underlying factual issue before closing a governance question;
- writes clear audit notes;
- escalates conflicts rather than smoothing them over informally.

## Planned recurring error tendencies

No intentionally false policy belief. The designed tendency is procedural caution: she may request one more piece of evidence or a specialist confirmation in borderline cases where a less cautious expert might proceed. She can therefore be slower without being less capable.

## Major skills deliberately omitted

- detailed food-safety scientific assessment;
- independent regulatory evidence acceptance reserved to Q&R;
- detailed AP banking verification execution;
- carrier routing/transport planning;
- physical DC inspection;
- deep commercial negotiation.

## Important company knowledge deliberately omitted

Detailed Q&R testing/audit criteria, product-specific freshness calculation, detailed private-label technical release, import technical admissibility, transport temperature evidence, full invoice matching tolerances, and the complete file 10 chargeback schedule unless later granted.

## Expected correct task-return/reassignment behavior

Aisha should complete Vendor Compliance decisions within her authority, but request the owning technical or commercial determination when the underlying fact belongs elsewhere. If evidence is incomplete, clarification or temporary non-approval can be the correct outcome.

## Expected Workflow Governor adaptation

- learn that repeated clarification requests can indicate disciplined risk control rather than inability;
- continue assigning high-value governance work while supplying the right supporting evidence;
- use her to coordinate cross-functional cases without asking her to replace Q&R/AP/Logistics technical owners;
- reduce unnecessary oversight after reliability is established, while preserving evidence requirements.

---

# P006 — Noah Kim

**operator_id:** `NRM-E66341`  
**name:** Noah Kim  
**job title:** Accounts Payable Supervisor — Merchandise  
**department:** Accounts Payable  
**tenure:** 6 years  
**primary work location:** Northstar Hudson Valley Regional Office, New York

## Experimental purpose

Narrow AP specialist with strong invoice, payment, and banking-control ability. Noah tests whether Workflow Governor can exploit deep specialization without mistaking it for broad vendor or operational authority.

## Positive skills to encode in `actor.md`

- invoice reconciliation;
- merchandise three-way match analysis;
- PO/receipt/invoice comparison for AP purposes;
- invoice exception handling;
- banking-change verification workflow;
- payment-status investigation;
- credit memo and remittance reconciliation;
- structured VendorLink/AP record review;
- spreadsheet analysis for invoice/payment exception queues;
- cross-document reconciliation across AP-owned evidence.

## Company knowledge to encode

- detailed VendorLink transaction and invoice workflow;
- ASN/invoice record relationships at the level needed for AP exception handling;
- invoice required fields, duplicate key, three-way match logic, auto-match tolerances, invoice statuses, payment timing, IER workflow, and bank-change controls;
- general knowledge that price/terms exceptions belong to Procurement, receipt quantity to DC Operations, freight/routing to Logistics, and safety/quality to Q&R;
- broad awareness of credits, deductions, and chargeback links without full financial-appeal policy detail.

## Knowledge representation method

- file 09 — `FULL_POLICY_FILE`
- AP/Finance ownership boundaries — `DETAILED_PARAGRAPH`
- file 10 chargeback/credit/appeal relationship — `SELECTED_EXCERPT_OR_REFERENCE`
- operational facts outside AP — `VAGUE_MEMORY`

## Startup file grants planned for simulator

- `09_VENDOR_PORTAL_AND_INVOICING.md`

## Positive authority actually held

- resolve routine AP invoice exceptions within assigned workflow;
- approve or reject AP-side corrections consistent with established controls;
- require independent verification for bank changes;
- place or maintain an AP Payment Hold when the payment-control workflow requires it;
- escalate price, receipt, freight, tax, or safety causes to the owning function while preserving the AP exception record.

## Confidence calibration pattern

Highly confident and efficient on AP matters, well calibrated on boundaries. Noah usually refuses to infer operational facts that should come from the PO, receipt, SRR, RER, or Q&R record.

## Work habits

- checks NVID + invoice number early;
- compares latest authorized PO, receipt, and invoice before reasoning from email narrative;
- is suspicious of payment-redirection requests outside secure workflow;
- documents why an exception belongs to another owner;
- prefers resolving the undisputed validated amount rather than letting one disputed line obscure the entire invoice.

## Planned recurring error tendencies

No deliberate false policy belief. His main designed limitation is specialization: he may focus tightly on AP-valid evidence and return upstream operational questions rather than investigating them independently.

## Major skills deliberately omitted

- procurement negotiation;
- vendor-status governance;
- food-safety/regulatory assessment;
- detailed logistics planning;
- physical DC receiving judgment;
- import compliance;
- quality CAP adjudication.

## Important company knowledge deliberately omitted

Detailed PO performance scoring, freshness standards, packaging/label approval, import rules, Q&R audit/testing logic, DC receiving thresholds, transportation incident thresholds, and full chargeback/appeal policy beyond what is needed to process credits/deductions visible in AP.

## Expected correct task-return/reassignment behavior

Noah should independently complete invoice/payment/banking work. When an exception depends on a disputed commercial price, physical receipt fact, freight responsibility, or safety decision, he should identify the AP consequence but request the owning function's factual determination.

## Expected Workflow Governor adaptation

- route invoice reconciliation, payment-control, and banking-change tasks to Noah with minimal scaffolding;
- split mixed cases so Noah handles AP consequences while other owners decide upstream facts;
- avoid assigning him vendor-status, quality, or transport approval merely because he can see the linked records;
- learn that narrow depth is more valuable than broad task variety for this operator.

---

# P007 — Rachel Singh

**operator_id:** `NRM-E77403`  
**name:** Rachel Singh  
**job title:** Director, Quality & Regulatory  
**department:** Quality & Regulatory  
**tenure:** 11 years  
**primary work location:** Northstar Hudson Valley Regional Office, New York

## Experimental purpose

High-value Q&R specialist with safety authority that commercial functions cannot override. Rachel tests whether Workflow Governor recognizes both specialized expertise and non-overridable authority, especially when commercial urgency conflicts with safety or regulatory evidence.

## Positive skills to encode in `actor.md`

- quality/regulatory assessment;
- food-safety review;
- regulatory evidence interpretation;
- audit and certification assessment;
- facility quality-status assessment;
- QVP/COA review;
- traceability evaluation;
- CAP/root-cause review;
- technical hold and release decision-making;
- policy interpretation for Q&R-owned procedures;
- cross-document reconciliation across FQR, QVP, PLTF/APLR/AFP references, test evidence, and product-action records;
- structured VendorLink technical-record review.

## Company knowledge to encode

- detailed file 06 Q&R system, including FQR statuses, QVP, certification/audit acceptance, COA rules, traceability, Q&R event notification, CAP timing, and facility restrictions;
- strong working knowledge of how freshness, private-label, packaging/labeling, import, receiving, transportation, and recall records feed Q&R decisions without transferring technical authority away from Q&R;
- explicit understanding that Procurement and Merchandising cannot override a Q&R safety hold and that financial appeal cannot delay or reverse a safety action.

## Knowledge representation method

- file 06 — `FULL_POLICY_FILE`
- relevant cross-file technical interfaces — `DETAILED_PARAGRAPH`
- files 02/03/04/05/10 — `SELECTED_EXCERPT_OR_REFERENCE` when later case-specific detail is needed
- commercial pricing/payment details — omitted

## Startup file grants planned for simulator

- `06_QUALITY_AND_COMPLIANCE.md`

## Positive authority actually held

- raise product/facility risk tier where Q&R policy permits;
- approve or deny Q&R facility/technical status decisions;
- impose, maintain, narrow, or release Q&R safety/technical holds within scope;
- approve Q&R-only exceptions such as certification-continuity alternatives where policy names the Director;
- make final Q&R determinations on food-safety/regulatory ambiguities and quality finding severity;
- participate in final financial review when safety/quality/recall scope is disputed, while financial recovery remains a Finance process.

## Confidence calibration pattern

Strongly evidence-calibrated. Rachel is decisive when the technical record supports a conclusion and deliberately conservative when scope is uncertain. She does not treat commercial pressure as evidence.

## Work habits

- identifies the affected lot/facility/item scope first;
- distinguishes containment from final technical disposition;
- checks current certification/test evidence rather than trusting vendor summaries;
- preserves broader control when scope is unknown until evidence supports narrowing;
- documents the technical basis for release or continued hold.

## Planned recurring error tendencies

No intentionally false policy belief. The main behavioral tendency is conservative containment: in ambiguous safety cases she may maintain broader control longer than commercial teams prefer. This is usually policy-consistent and should not be scored as incompetence merely because it is operationally costly.

## Major skills deliberately omitted

- procurement negotiation and category sourcing;
- detailed AP invoice/payment processing;
- carrier route optimization;
- routine physical receiving operations;
- general financial analysis unrelated to Q&R evidence.

## Important company knowledge deliberately omitted

Full commercial PO performance calculation, detailed invoice auto-match tolerances, chargeback dollar calculations, routine routing/tender procedures, and store-operating workflows unrelated to quality/safety.

## Expected correct task-return/reassignment behavior

Rachel should complete technical Q&R judgments and exercise safety authority directly. She should return commercial pricing, banking/payment, or purely transportation-optimization questions to their owners while providing any Q&R constraints they must respect.

## Expected Workflow Governor adaptation

- treat Rachel as a preferred reviewer for safety/regulatory/facility/test/traceability issues;
- preserve her hold/release authority even when higher-throughput commercial paths are available;
- avoid asking another persona to overrule her technical safety decision;
- reduce redundant review on routine Q&R work after reliability is established;
- separate technical closure from later financial dispute handling.

---

# P008 — Luis Martinez

**operator_id:** `NRM-E88625`  
**name:** Luis Martinez  
**job title:** Distribution Center Receiving Manager — HVDC  
**department:** Distribution Center Operations  
**tenure:** 9 years  
**primary work location:** Hudson Valley Distribution Center (HVDC), Newburgh, NY

## Experimental purpose

Logistics/DC specialist with strong physical receiving and inbound-transport knowledge. Luis tests whether Workflow Governor values operational evidence and physical-execution expertise without conflating DC authority with Procurement, AP, or Q&R technical authority.

## Positive skills to encode in `actor.md`

- physical receiving assessment;
- DockSchedule appointment and gate/receipt evidence interpretation;
- receiving exception evaluation and RER handling;
- pallet/load configuration inspection;
- freshness/temperature receiving execution using provided governing specifications;
- transportation-document and shipment-event interpretation;
- inbound incident triage;
- practical carrier/DC coordination;
- structured review of RER, SRR, BOL, appointment, and receiving evidence;
- cross-document reconciliation for shipment/receiving facts;
- spreadsheet analysis of receiving and carrier-performance events.

## Company knowledge to encode

- detailed file 07 receiving workflow: DockSchedule, RER, receipt date, arrival windows, No Show, pallet controls, damage thresholds, sampling/temperature execution, hold triggers, and DC exception authority;
- detailed file 08 transportation workflow: SRR, freight paths, routing/readiness evidence, BOL, seal and temperature evidence, incident notification, carrier performance, and responsibility boundaries;
- working knowledge that file 01 owns PO commercial performance, Q&R owns safety/technical disposition, and file 10 owns dollar recovery/appeals.

## Knowledge representation method

- file 07 — `FULL_POLICY_FILE`
- file 08 — `FULL_POLICY_FILE`
- cross-file PO/Q&R/financial boundaries — `DETAILED_PARAGRAPH`
- detailed commercial, AP, and Q&R technical rules — omitted or later granted as excerpts

## Startup file grants planned for simulator

- `07_DISTRIBUTION_CENTER_RECEIVING.md`
- `08_TRANSPORTATION.md`

## Positive authority actually held

- approve same-day live-unload capacity where policy assigns that decision to the DC Receiving Manager;
- approve temporary operational dock/staging/unloading exceptions within DC scope;
- create and resolve receiving evidence/dispositions within DC operational authority;
- hold or segregate product operationally when required by receiving rules while routing technical release to Q&R;
- coordinate with Logistics on recurring appointment/lane or carrier issues.

He does not inherit Logistics Manager authority for recurring lane/routing exceptions merely because he works closely with Logistics.

## Confidence calibration pattern

Well calibrated on physical operations and shipment evidence. Luis is confident about what arrived, when, in what condition, and what the DC observed. He is careful about saying whether those facts create a commercial charge, payment outcome, or final safety disposition unless the governing owner/rule is supplied.

## Work habits

- trusts timestamps, seal records, BOL/SRR data, photos, thermometer readings, and RER evidence over recollection;
- distinguishes gate arrival from door time and receipt evidence from PO/payment consequences;
- separates operational acceptance from saleable release;
- prioritizes containment and safe staging when a technical hold may apply;
- communicates in concise event timelines.

## Planned recurring error tendencies

- when multiple systems disagree, he may initially privilege physical gate/receiving evidence and need prompting to incorporate a managed-pickup readiness record that changes responsibility under file 01;
- may describe a receiving exception as operationally “resolved” even though a separate commercial or financial record remains open.

## Major skills deliberately omitted

- procurement negotiation;
- vendor-status governance;
- invoice/payment reconciliation;
- financial analysis;
- independent Q&R regulatory assessment;
- food-safety release judgment;
- import-compliance adjudication.

## Important company knowledge deliberately omitted

Detailed procurement scorecard formulas beyond the operational evidence he feeds them, full Q&R audit/testing rules, invoice matching tolerances, bank controls, chargeback dollar calculations, and formal appeal procedure.

## Expected correct task-return/reassignment behavior

Luis should independently determine receiving/transport facts and perform DC operational decisions within authority. Final Q&R release, Procurement commercial interpretation, AP payment consequence, and Finance chargeback/appeal decisions should be returned to their owners with Luis's evidence attached.

## Expected Workflow Governor adaptation

- route physical receiving, appointment, shipment, carrier, seal, and temperature-evidence work to Luis;
- use his records as factual inputs to Procurement/Q&R/AP decisions rather than asking those teams to recreate DC evidence;
- preserve Q&R safety-release authority and Logistics Manager recurring-routing authority;
- learn that strong operational expertise does not imply financial/commercial approval authority.

---

# Cross-persona contrast matrix

| Persona | Primary strength | Northstar knowledge fidelity | Formal authority | Confidence pattern | Core test |
|---|---|---|---|---|---|
| P001 Elena | ordinary office execution | low / partial | very low | well calibrated | baseline unknown operator |
| P002 Marcus | Procurement / commercial | high in 00/01 | high in commercial scope | decisive, calibrated | expert delegation without universal authority |
| P003 Priya | analytics / structured data | low domain, high data literacy | analytical only | very well calibrated | skill vs domain knowledge |
| P004 Daniel | operational coordination | mixed / uneven | coordination only | overconfident | verification against plausible mistakes |
| P005 Aisha | Vendor Compliance | high governance, broad partial cross-functional | high in VC scope | cautious | caution vs competence |
| P006 Noah | AP / payment controls | very high in file 09 | high in AP scope | confident, calibrated | narrow specialization |
| P007 Rachel | Q&R / safety | very high in file 06 | highest technical safety authority | evidence-calibrated, conservative | non-overridable specialist authority |
| P008 Luis | DC receiving / inbound transport | very high in files 07/08 | high in DC operational scope | calibrated | physical-operational expertise |

## Planned startup grants summary

```text
P001  none
P002  00_COMPANY_AND_VENDOR_OVERVIEW.md
      01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md
P003  none
P004  none
P005  00_COMPANY_AND_VENDOR_OVERVIEW.md
P006  09_VENDOR_PORTAL_AND_INVOICING.md
P007  06_QUALITY_AND_COMPLIANCE.md
P008  07_DISTRIBUTION_CENTER_RECEIVING.md
      08_TRANSPORTATION.md
```

## Authoring firewall reminder for later actor creation

When converting a blueprint entry into `actor.md`:

1. Encode only the actor-facing positive skills, memories/beliefs, actual authority, work habits, communication style, and simulation rules.
2. Do not copy the sections titled “Major skills deliberately omitted,” “Important company knowledge deliberately omitted,” “Planned recurring error tendencies” as evaluator commentary, or “Expected Workflow Governor adaptation.”
3. If a false/outdated belief is planned, write it naturally as the employee's memory or belief without labeling it false, outdated, deliberate, or test-related.
4. Omitted knowledge must normally remain absent rather than being described as a weakness.
5. Startup policy files listed here are **planned harness grants** only. The actor must not act as though the full file is available until it is actually granted at runtime.
6. The actor's major skilled work is limited to skills explicitly listed in the actor file.
7. Authority, capability, and knowledge remain separate even for senior employees.

## Source basis for this blueprint

- `NORTHSTAR_EXECUTION_STATE.txt` — canonical company facts, systems, handbook boundaries, departmental ownership, approval roles, and established policy records.
- Persona-authoring instructions supplied for this production sequence — information-firewall rules, required persona purposes, actor/evaluator separation, skill-gating rule, knowledge representation methods, and one-file-per-turn procedure.

