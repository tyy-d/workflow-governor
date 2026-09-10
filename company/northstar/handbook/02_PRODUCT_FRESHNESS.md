# Product Freshness

## 1. Purpose and scope

This policy establishes Northstar Regional Markets requirements for product shelf life, date coding, freshness evidence, and short-dated product decisions. It applies to food and any non-food item with an expiration, best-quality, stability, or usable-life requirement. It does not replace physical receiving, transportation temperature, quality-audit, or label-format rules addressed elsewhere in this handbook.

**Quality & Regulatory (Q&R)** owns food-safety interpretation, date-code integrity, and safety-related holds. **Merchandising** owns intended consumer selling-life requirements. **Procurement** owns commercial supplier commitments. **Vendor Compliance** monitors adherence and coordinates corrective action. **Distribution Center Operations** records physical receiving evidence but may not waive an item freshness requirement.

Northstar distinguishes among:

- **legal/regulatory requirements**, which cannot be waived by Northstar;
- **Northstar freshness requirements**, which are contractual/company controls; and
- **recommended inventory practices**, such as FEFO rotation, that support compliance but are not themselves laws.

## 2. Definitions

**Approved Freshness Profile (AFP)** — the item-level freshness record approved in Northstar VendorLink. An AFP contains the product's declared total shelf life, date-code meaning, storage condition, and Minimum Remaining Life requirement.

**Declared Total Shelf Life (DTSL)** — the vendor-supported number of calendar days from the defined shelf-life start event to the defined end-of-life date under the approved storage condition.

**Shelf-Life Start Event** — the AFP-defined event from which DTSL is measured, such as manufacture date, pack date, bake date, harvest/pack date, or another approved event.

**End-of-Life Date (ELD)** — the AFP-defined date used to calculate remaining life. Depending on the item, it may correspond to an expiration, use-by, best-if-used-by, sell-by, or derived date. The date phrase itself does not automatically determine whether the date is a safety deadline.

**Remaining Life (RL)** — calendar days from the Northstar receipt date to the ELD. The receipt date is day 0. For example, product received April 1 with an ELD of April 21 has 20 days RL.

**Minimum Remaining Life (MRL)** — the minimum RL required when product is received by Northstar, expressed as both an absolute number of days and/or a percentage of DTSL.

**Freshness Eligible Case** — a received case for which an AFP applies and enough date information exists to determine compliance.

**Short-Dated Product** — product that is not expired but has RL below the applicable MRL.

**Expired Product** — product received after its controlling ELD or otherwise beyond a legally controlling use date.

**FEFO** — first-expire, first-out inventory rotation.

## 3. Vendor responsibilities

A vendor must:

1. maintain an approved AFP before an item is released for routine ordering;
2. ship only product whose date code can be interpreted using the AFP or linked code-decoding instructions;
3. ensure every freshness-eligible case meets the MRL at Northstar receipt unless a valid pre-shipment freshness exception exists;
4. preserve lot/batch identity and date-code traceability through shipment;
5. avoid altering, obscuring, relabeling, or replacing a manufacturer date code except through a lawful, documented process approved by Q&R where required;
6. notify Northstar promptly if actual product life, code meaning, storage condition, or stability evidence changes; and
7. use inventory rotation controls reasonably designed to prevent older compliant product from being stranded while newer product is shipped.

FEFO is Northstar's recommended rotation practice; another controlled method is acceptable if it consistently meets MRL and traceability requirements.

## 4. Northstar process

### 4.1 Freshness profile creation

Before item activation, the vendor submits freshness data through VendorLink. Merchandising proposes the commercial MRL; Q&R reviews date-code basis, storage condition, and safety implications; Procurement confirms the supplier commitment.

An AFP becomes authoritative only after approval. Buyer emails, forecasts, verbal statements, and vendor specification sheets do not independently modify it.

No routine PO may be issued for a freshness-controlled item with a missing AFP. A one-time test or sample order may be approved separately and must be marked non-commercial or controlled-test as applicable.

### 4.2 Receipt calculation

For each received freshness-eligible case:

1. identify the controlling date code;
2. convert coded dating to a calendar ELD when necessary using the approved decode method;
3. calculate RL;
4. compare RL with the AFP MRL; and
5. preserve the case/lot result in the receiving evidence.

When a case, pallet, or lot contains multiple valid date codes, the **least remaining life controls** the freshness decision for any grouping that cannot be separately identified and handled. If cases can be reliably segregated by date, each segregated date group may be evaluated separately.

### 4.3 Derived end-of-life dates

If an item does not display a consumer-facing ELD but the AFP defines a manufacture/pack date plus DTSL, Northstar derives:

**Derived ELD = Shelf-Life Start Date + DTSL**

The vendor must provide an approved code-decoding method. Undecodable product is not presumed fresh merely because the packaging appears new.

### 4.4 Freshness versus safety

A failed MRL is normally a **commercial freshness failure**, not automatically a food-safety failure. Q&R determines whether a safety concern also exists.

Many U.S. food package dates are manufacturer quality dates rather than federally mandated safety deadlines. Northstar nevertheless enforces its AFP as company policy. Any legally controlling date requirement takes precedence and cannot be waived through a commercial freshness exception.

## 5. Required documents and data

Each AFP must contain at least:

| Field | Requirement |
|---|---|
| NVID | Seller-of-record vendor identifier |
| Northstar item number | Unique approved item |
| Product / brand description | Current approved description |
| Shelf-Life Start Event | Defined event and date-code source |
| DTSL | Calendar days under approved conditions |
| Date-code type | Open date, closed/coded date, or derived date |
| Date-code meaning | Expiration, use-by, best-quality, sell-by, manufacture/pack, or other |
| Decode instructions | Required when date is not directly readable |
| Approved storage condition | Ambient, refrigerated, frozen, or item-specific |
| MRL | Days and/or percentage, with controlling formula |
| Lot/batch identifier format | Traceability field |
| Supporting specification | Current vendor product specification |
| Approval owners | Merchandising and Q&R; Procurement acknowledgment |

For R3 products, Q&R may additionally require stability studies, shelf-life validation, challenge-study information, certificate-of-analysis linkage, temperature history, or other evidence appropriate to the product. Detailed facility/testing requirements belong in `06_QUALITY_AND_COMPLIANCE.md`.

## 6. Standards and thresholds

### 6.1 Default MRL logic

The **AFP is always controlling**. The following Northstar defaults apply when establishing a new AFP unless Merchandising and Q&R approve a different item-specific requirement.

| Product class | Default MRL at Northstar receipt |
|---|---:|
| Shelf-stable food with DTSL >180 days | **70% of DTSL remaining** |
| Shelf-stable food with DTSL 91–180 days | **70% of DTSL remaining** |
| Shelf-stable food with DTSL ≤90 days | **65% of DTSL remaining** |
| Refrigerated packaged food | **65% of DTSL remaining** |
| Frozen food | **70% of DTSL remaining** |
| Fresh produce, fresh meat/seafood, in-store bakery inputs, and other highly perishable items | **Item-specific AFP required; no category default** |
| Non-food dated/stability-controlled merchandise | **60% of DTSL remaining**, unless item-specific requirement applies |

Percentages are calculated from calendar days and rounded **up to the next whole day**. Example: DTSL 45 days × 65% = 29.25, so MRL = 30 days.

If the AFP states both a percentage and an absolute-day minimum, the **greater** requirement controls. An AFP cannot contain an absolute MRL greater than DTSL.

### 6.2 Date-code and lot rules

- Date codes used for freshness must be legible and traceable to the item and lot/batch.
- A case with no readable or decodable controlling date is placed on **Freshness Hold** unless the AFP explicitly permits another traceable freshness method.
- Product may not be made compliant by manually changing a date code after production unless the relabeling is lawful, traceable, supported by the manufacturer, and approved by Q&R when approval is required.
- An expired case is never counted as freshness-compliant.
- If an expired case is discovered in a lot, the affected lot is placed on Q&R hold pending scope determination.

### 6.3 Freshness performance metric

Northstar measures:

**Freshness Compliance Rate = Freshness-compliant cases ÷ Freshness Eligible Cases × 100**

The monthly vendor target is **≥99.5%** across cases received during the calendar month.

A monthly rate below 99.5% places the vendor on **Freshness Watch**. A rate below **98.0%**, two consecutive Freshness Watch months, any deliberate date-code manipulation, or receipt of expired product triggers a freshness corrective-action review regardless of volume.

A vendor with fewer than **100 freshness-eligible cases** in a month receives an informational percentage; however, expired product, falsification, or other Critical Freshness Events still trigger review.

Freshness performance is separate from OTIF under `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`. Product can be on time and in full yet fail freshness.

### 6.4 Change notification

A planned reduction in DTSL, change in Shelf-Life Start Event, change in date-code meaning, or change in required storage condition must be submitted through VendorLink at least **45 calendar days before** affected product is shipped to Northstar.

If a vendor discovers an unplanned condition that may invalidate the approved shelf life, it must notify Q&R and Vendor Compliance within **1 business day of discovery** and before further affected shipments when reasonably possible.

A formulation, packaging, or label change may also trigger separate notice requirements under `03_PRIVATE_LABEL_PRODUCTS.md`, `04_PACKAGING_AND_LABELING.md`, or `06_QUALITY_AND_COMPLIANCE.md`.

## 7. Exceptions and escalation

A vendor that cannot meet MRL must request a **Freshness Exception (FE)** before shipping the affected lot. The request must identify the PO, item, quantity, lot/date codes, actual RL, required MRL, reason, proposed disposition, and evidence that product remains lawful and suitable for the intended sale period.

| Exception | Minimum approval |
|---|---|
| R1/R2 non-safety short-date commercial exception | Merchandising Manager + Vendor Compliance Manager |
| R3 food short-date exception with no identified safety concern | Merchandising Manager + Director, Quality & Regulatory |
| Exception affecting a promotion or material supply commitment | Above approvals + Procurement Manager |
| Retroactive request after shipment | Same functional approvals + written reason why pre-shipment approval was not obtained |

An FE must state the exact approved lot/quantity and expires after that shipment or on the stated date, whichever occurs first. Blanket or no-expiry freshness exceptions are invalid.

Northstar will not approve an FE to waive a legal date requirement, knowingly distribute unsafe product, conceal a loss of shelf-life validation, or legitimize altered/falsified date codes.

Disposition of short-dated but safe product by donation, markdown, alternate channel, or other use is a human commercial decision after Q&R confirms the safety/regulatory position.

## 8. Non-compliance

Freshness non-compliance may result in Freshness Hold, case/lot rejection, segregation, return or disposition, Freshness Watch, corrective action, recovery of documented costs under the later chargeback policy, item restriction, or vendor status review.

Deliberate code alteration, falsified shelf-life data, concealment of a known stability problem, or shipment of product known to be expired may cause immediate Suspension under the integrity rules in `00_COMPANY_AND_VENDOR_OVERVIEW.md`.

DC personnel may execute an established freshness hold or rejection rule using the AFP and receiving evidence. They may not waive MRL because of business urgency. Commercial exceptions require the approvals above, and safety decisions remain with Q&R.

## 9. Records and evidence

Northstar must preserve, as applicable:

- current and historical AFP versions;
- vendor shelf-life specifications and decode instructions;
- approval history;
- lot/batch and date-code evidence;
- receiving-date evidence used in RL calculations;
- Freshness Hold records;
- Freshness Exceptions;
- monthly freshness calculations;
- corrective actions; and
- evidence supporting any manual override or disposition.

Freshness records tied to a PO are retained for **7 years after PO final close** unless a longer retention period applies because of recall, litigation hold, regulatory requirement, contract requirement, or another Northstar policy.

## 10. Examples / scenarios

### Scenario A — percentage calculation
A refrigerated item has DTSL of 45 days and an AFP using the 65% default. MRL is 30 days after rounding up. Product received with 31 days RL passes freshness; product with 29 days RL is short-dated.

### Scenario B — mixed dates on one pallet
A pallet contains 40 cases with 120 days RL and 10 cases with 55 days RL. The cases are visually identical but lot/date codes allow reliable segregation. Northstar may evaluate the two groups separately. If they cannot be reliably segregated, 55 days controls the pallet-level freshness decision.

### Scenario C — quality date versus safety
A shelf-stable item arrives below its AFP MRL but before its manufacturer's best-quality date. It fails Northstar freshness policy even though the date alone does not establish that the food is unsafe. A commercial FE may be considered; Q&R determines whether any safety concern exists.

### Scenario D — undecodable code
A case shows code `6J2217` but the current AFP contains no decode key. The product goes on Freshness Hold. A vendor email claiming that the code is “good for another year” is supporting information, not an authoritative AFP change.

### Scenario E — altered date
Receiving evidence shows a new sticker placed over the manufacturer's original date, and the vendor cannot provide an approved, traceable relabeling record. The lot is held and escalated to Q&R and Vendor Compliance for integrity review; business need cannot override the investigation.

## 11. Related Northstar policies

- `00_COMPANY_AND_VENDOR_OVERVIEW.md` — vendor status, risk tiers, VendorLink, NVID, safety-hold authority, and integrity rules.
- `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md` — PO performance and OTIF; freshness is measured separately.
- `03_PRIVATE_LABEL_PRODUCTS.md` — private-label product-change and specification obligations.
- `04_PACKAGING_AND_LABELING.md` — date-code placement, labeling, case marking, and packaging requirements.
- `05_IMPORT_REQUIREMENTS.md` — import transit planning and origin documentation.
- `06_QUALITY_AND_COMPLIANCE.md` — shelf-life validation evidence, audits, testing, quality holds, and food-safety review.
- `07_DISTRIBUTION_CENTER_RECEIVING.md` — physical inspection, receipt timestamp, temperature evidence, segregation, and rejection execution.
- `08_TRANSPORTATION.md` — cold-chain transportation and carrier controls.
- `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md` — disposition costs, deductions, appeals, returns, and recalls.

## Reference basis

The following public materials were consulted for process concepts only. Northstar is fictional and is not affiliated with these organizations. Northstar percentages, thresholds, systems, forms, approvals, and examples above are original.

- **Family Dollar — Routing, Shipping, and Packaging Instructions: Freshness Policy**  
  https://corporate.dollartree.com/_assets/_26d252d65b21bf1556d097bdb377688a/dollartreeinfo/db/1137/8589/file/Family_Dollar_Routing_Shipping_and_Packaging_Instructions.pdf  
  Influenced use of an item-specific guaranteed/committed remaining-life concept, strict short-date control, and evaluating the least-fresh date when multiple expiration dates occur together.

- **United Natural Foods, Inc. (UNFI) — Supplier Terms & Conditions, updated July 30, 2026**  
  https://www.unfi.com/supplier-terms.html  
  Influenced percentage-of-total-shelf-life thinking and explicit supplier responsibility for meeting shelf-life requirements at distribution-center receipt.

- **UNFI — UpNext Supplier Inquiry**  
  https://www.unfi.com/services/supplier-services/up-next/upnext-supplier-inquiry.html  
  Influenced collection of shelf life at production and product shipping/selling temperature as structured supplier item data.

- **U.S. Food and Drug Administration — FDA Food Code / retail cold-holding guidance**  
  https://www.fda.gov/food/retail-food-protection/fda-food-code  
  Influenced the distinction between retail food-safety temperature controls and Northstar's separate commercial shelf-life requirements; operational receiving temperatures are reserved for later Northstar policies.

- **USDA Food Safety and Inspection Service — Food Product Dating**  
  https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/food-product-dating  
  Influenced the legal/quality distinction for common date labels, the distinction between open and coded dating, and recognition that most federal food date labels are quality rather than safety requirements, with specific exceptions such as infant formula.
