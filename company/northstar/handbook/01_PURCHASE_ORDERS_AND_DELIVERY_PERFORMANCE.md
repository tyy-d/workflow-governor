# Purchase Orders and Delivery Performance

## 1. Purpose and scope

This policy governs issuance, revision, acceptance, fulfillment, and performance measurement of merchandise POs issued to **Active** vendors for approved items, including domestic DC and authorized DSD deliveries. International POs follow this section for PO authority, quantity control, and communication; import-specific requirements belong in `05_IMPORT_REQUIREMENTS.md`.

**Procurement** owns commercial PO content; **Vendor Compliance** owns performance governance; **Logistics**, **Distribution Center Operations**, and **Store Operations** provide delivery evidence; **Quality & Regulatory** retains independent safety-hold authority. These delivery standards are **Northstar contractual policy**, not statutory timing or fill-rate requirements.

## 2. Definitions

- **PO** — a Northstar purchase order transmitted through Northstar VendorLink or an approved electronic connection and identified by PO number and revision number.
- **PO revision** — a Northstar-issued change to quantity, item, cost, destination, dates, freight term, or another controlled PO field.
- **Delivery window** — the earliest and latest date/time during which the PO requires delivery or another defined performance event.
- **Vendor-prepaid** — the vendor controls transportation to the Northstar destination.
- **Northstar-managed pickup** — Northstar or its designated carrier controls transportation after the vendor makes product available at the approved origin.
- **Compliant unit** — an ordered unit received as the correct approved item, pack, and condition and not rejected for damage, quality, safety, labeling, or other receiving nonconformity.
- **Net Ordered Units** — units on the latest valid PO revision after eligible Northstar-initiated cancellations are removed.
- **Performance Exception Record (PER)** — a VendorLink record authorizing an exclusion or adjustment to a delivery-performance result.
- **Critical PO** — a PO specifically flagged by Northstar for a promotion, seasonal event, constrained supply, launch, or other business-critical requirement.

## 3. Vendor responsibilities

Vendors must monitor the approved PO channel each Northstar business day; acknowledge new POs and material revisions on time; verify NVID, origin, destination, SKU, pack/UOM, quantity, cost, freight term, and dates; fulfill only the latest authorized revision; promptly report threatened shortages or delays; preserve fulfillment evidence; and ensure third-party warehouses/carriers follow applicable instructions.

No item, pack, manufacturing site, destination, or quantity may be substituted unilaterally. A vendor-requested change is effective only after Northstar issues a revision or explicit written authorization. Product safety and law take priority over delivery performance.

## 4. Northstar PO process

### 4.1 Issue and acknowledgment

A commercial PO is valid only when it is transmitted by Northstar through VendorLink or an approved electronic connection. A forecast, spreadsheet, email estimate, verbal statement, sample request, or merchandising discussion is not a PO.

The vendor must send an acknowledgment no later than:

| Situation | Required acknowledgment |
|---|---:|
| Standard new PO or material revision | Within **1 Northstar business day** after transmission |
| Earliest required performance date is fewer than 3 business days away | Within **4 business hours** after transmission |

The acknowledgment must identify each affected line as **Accepted**, **Change Requested**, or **Rejected**, with a reason for any non-acceptance. If a vendor ships against a PO without acknowledging it, shipment is treated as acceptance of the PO terms; the missing acknowledgment remains a process violation.

### 4.2 PO discrepancies

A vendor that identifies an incorrect cost, pack, quantity, destination, freight term, facility, or date must stop the affected fulfillment activity and request correction. The original PO remains controlling until Northstar transmits a revision.

Northstar revisions are version-controlled. After a newer revision is transmitted, the superseded version must not be used for subsequent fulfillment. If a revision is transmitted after product has already shipped or has been formally made ready for Northstar-managed pickup, Procurement determines commercial disposition and the performance treatment must be documented.

### 4.3 Shortage and delay notice

When a vendor becomes aware that it is unlikely to meet the PO, it must notify Northstar **within 1 business day of discovery** and, when reasonably foreseeable, at least **2 business days before** the affected delivery or ready window begins.

The notice must identify the PO and line, affected quantity, expected availability, cause, proposed recovery action, and whether other Northstar POs are affected. Notice does not by itself excuse the performance failure.

### 4.4 Shipment and receipt

Unauthorized substitutions and unauthorized over-shipments are not permitted. Northstar may reject excess or incorrect product, accept it without increasing the performance numerator above ordered quantity, or direct another disposition.

Split shipments require prior approval unless the PO expressly permits them. A partial shipment does not create a new due date for the unfilled balance.

Physical appointment, receiving, pallet, temperature, carrier, and routing procedures are governed by `07_DISTRIBUTION_CENTER_RECEIVING.md` and `08_TRANSPORTATION.md` once those policies are issued.

## 5. Required records and data

| Record | Minimum purpose |
|---|---|
| Original PO and every revision | Establish authoritative item, quantity, cost, destination, freight term, and dates |
| Electronic transmission log | Establish when the PO/revision became available to the vendor |
| Vendor acknowledgment | Establish acceptance or requested changes |
| Vendor shortage/delay notice, if applicable | Establish awareness, cause, quantities, and proposed recovery |
| Shipment/ready notice | Establish shipment or Northstar-managed pickup readiness |
| ASN, BOL, packing list, or equivalent shipment record | Connect physical shipment to PO and quantity |
| Appointment/gate/pickup evidence, when applicable | Establish transportation timing |
| Receiving or store-delivery record | Establish actual units and receipt time |
| Rejection/shortage/damage codes | Establish why units were not compliant |
| Northstar cancellation or PO revision record | Establish authorized denominator changes |
| PER, if applicable | Establish approved score exclusion or adjustment |

Electronic timestamps control when available. Manual corrections must preserve the user, date, reason, original value, replacement value, and supporting evidence.

## 6. Delivery-performance standards and calculations

### 6.1 Timeliness responsibility

Northstar measures the event controlled by the vendor.

| Fulfillment method | Vendor-controlled on-time event |
|---|---|
| Vendor-prepaid DC delivery | Compliant product arrives at the Northstar destination within the controlling delivery/appointment window |
| Northstar-managed pickup | Product is fully staged, conforming, documented, and available at the approved origin by the PO **Ready By** deadline |
| DSD | Compliant product is delivered to the authorized store within the controlling PO/store delivery window |

For Northstar-managed pickup, a Northstar-selected carrier arriving late does not make the vendor late if credible evidence shows the full required quantity was ready at the required time. For vendor-prepaid freight, the vendor normally remains responsible for its carrier's performance unless an approved PER applies.

### 6.2 Quantity calculations

For each PO:

**Net Ordered Units** = latest authorized ordered units − eligible Northstar-initiated cancellations.

A Northstar cancellation reduces Net Ordered Units only if the cancellation/revision was transmitted **before the earlier of** (a) actual vendor shipment or formal pickup readiness, or (b) the start of the controlling delivery/ready window. Vendor-caused cancellations, stockouts, production downtime, or unilateral quantity reductions remain in Net Ordered Units.

**On-Time Unit Rate** = compliant units meeting the on-time event ÷ Net Ordered Units × 100.

**Fill Rate** = compliant units received by PO final close ÷ Net Ordered Units × 100.

Numerators are capped at Net Ordered Units; over-shipment cannot improve a score.

A PO reaches **final close 5 calendar days after** the end of its controlling delivery window unless all lines are fully received, rejected, or formally closed earlier. Product received after the delivery window but before final close can improve Fill Rate but cannot improve On-Time Unit Rate.

### 6.3 PO and monthly targets

A PO is **On Time** when its On-Time Unit Rate is at least **98.0%**. It is **In Full** when its Fill Rate is at least **98.0%**. It is an **OTIF Pass** only when both conditions are met.

Monthly scorecards use eligible POs reaching final close during the calendar month.

| Metric | Northstar target |
|---|---:|
| OTIF Pass Rate | **≥95.0%** of eligible POs |
| Weighted Fill Rate | **≥98.5%** of Net Ordered Units |

If fewer than **5 eligible POs** close in a month, the scorecard is informational and does not by itself trigger a status restriction, although individual Critical PO or severe failures may still require review.

### 6.4 Score bands

| Result | Condition | Default action |
|---|---|---|
| **Meets Standard** | OTIF ≥95.0% and weighted fill ≥98.5% | No performance action |
| **Watch** | OTIF 90.0–94.99% or fill 96.0–98.49% | Vendor warning and root-cause review |
| **Corrective** | OTIF <90.0% or fill <96.0%, or two consecutive Watch months | Corrective Action Plan (CAP) required within **10 business days** |

Two consecutive Corrective months, or three Corrective months in any rolling six-month period, triggers a formal performance review. Vendor Compliance Manager and the responsible Procurement manager may place the affected vendor, item group, or lane in **Restricted** status when continued ordering presents material service risk.

A single Critical PO with more than **20% of Net Ordered Units** not delivered on time, or a zero-delivery/no-ready event without timely notice, triggers immediate performance review even if the monthly score remains above target.

Dollar amounts and formal chargeback appeal procedures are defined in `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md`. Vendor-caused premium freight or other documented recovery cost may be assessed under that policy.

## 7. Exceptions and escalation

A PER may remove or adjust a scored event only when the evidence shows the event was not reasonably attributable to the vendor or when Northstar knowingly approved a business deviation.

Reviewable circumstances include Northstar system/PO errors; Northstar changes after shipment or confirmed readiness; Northstar-managed carrier failures when readiness is proven; DC closure or unavailable receiving capacity despite timely vendor action; documented government closure, severe weather, natural disaster, or comparable external disruption; and a Q&R hold caused solely by Northstar review delay on otherwise conforming product.

The following are normally vendor-controlled and are not excused merely by explanation: production shortfall, labor shortage, raw-material shortage, equipment failure, inaccurate inventory, failure of a vendor-selected carrier, failure to monitor the PO channel, or late discovery of a foreseeable capacity problem.

A vendor requesting a PER must submit evidence within **3 business days after the affected event** unless the event itself prevents timely submission. Retroactive requests submitted later require written justification for the delay.

| Exception type | Minimum approval |
|---|---|
| PO/data error caused by Northstar | Vendor Compliance Manager + Procurement manager |
| Northstar-managed transportation or appointment failure | Logistics Manager |
| Material commercial exception to quantity/date | Procurement manager + Vendor Compliance Manager |
| Any exception involving product-safety or regulatory hold | Director, Quality & Regulatory |
| Post-scorecard correction changing a final monthly result | Vendor Compliance Manager + manager of the function owning the evidence |

No PER may waive law, authorize shipment of known unsafe product, or override a Quality & Regulatory safety hold.

## 8. Non-compliance

Depending on severity and repetition, non-compliance may cause a warning, refusal/return of unauthorized product, cancellation of affected quantities, CAP, recovery of vendor-caused costs under the chargeback policy, temporary PO restriction for affected items/lanes, broader Vendor Compliance review, or Suspension for material misrepresentation, deliberate shipment contrary to a safety hold, or repeated failure with integrity concerns.

Performance restriction is a service/commercial control and does not imply a food-safety violation unless Quality & Regulatory separately determines one exists.

## 9. Records and evidence retention

POs, revisions, acknowledgments, shipment/ready records, receipt records, scorecard calculations, PERs, CAPs, and material performance correspondence must be retained for **7 years after PO final close**, unless a longer period applies because of recall, litigation hold, tax requirement, contract requirement, or another Northstar policy.

The final monthly scorecard must preserve its source PO population, calculation version, exclusions, PER identifiers, and manual corrections.

## 10. Examples / scenarios

### Scenario A — vendor requests a quantity reduction
Northstar orders 1,000 units. The vendor can supply only 850 and requests a reduction, but Northstar does not issue a revision. The vendor ships 850. Net Ordered Units remain 1,000 because the shortage was vendor-caused; the request alone did not change the PO.

### Scenario B — buyer cancellation before shipment
Northstar orders 2,000 units, then transmits a revision cancelling 400 units before the vendor ships and before the delivery window starts. Net Ordered Units become 1,600. Performance is calculated against 1,600 units.

### Scenario C — collect carrier arrives late
A Northstar-managed carrier arrives six hours after the Ready By deadline. VendorLink records the vendor's timely ready notice, and dock evidence shows all required product was staged and available. The delay is not vendor late; Logistics may approve the transportation exception.

### Scenario D — late units improve fill but not timeliness
A PO for 1,000 units receives 950 within the delivery window and 50 two days later. The final Fill Rate can reach 100%, but the On-Time Unit Rate remains 95%; the PO therefore fails OTIF.

### Scenario E — safety hold
A refrigerated product is not released because the vendor submitted evidence indicating a product-safety concern. The vendor may not ship merely to preserve OTIF. Quality & Regulatory determines whether the failure is vendor-caused and whether any performance exclusion is appropriate.

## 11. Related Northstar policies

- `00_COMPANY_AND_VENDOR_OVERVIEW.md` — vendor status, risk tiers, VendorLink, NVID, onboarding, and safety-hold authority.
- `02_PRODUCT_FRESHNESS.md` — minimum remaining shelf life and date-code performance.
- `04_PACKAGING_AND_LABELING.md` — item, case, barcode, labeling, and shipment-data requirements.
- `05_IMPORT_REQUIREMENTS.md` — import PO, customs, origin, and international transit requirements.
- `06_QUALITY_AND_COMPLIANCE.md` — facility approval, audit/certification, testing, quality holds, and CAP detail.
- `07_DISTRIBUTION_CENTER_RECEIVING.md` — appointments, receiving evidence, physical acceptance/rejection, and receiving tolerances.
- `08_TRANSPORTATION.md` — carrier, routing, pickup, freight-term, and transportation execution requirements.
- `09_VENDOR_PORTAL_AND_INVOICING.md` — PO/invoice electronic transactions and financial matching.
- `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md` — chargeback amounts, appeals, returns, recalls, and deductions.

## Reference basis

The following public materials were consulted for process concepts only. Northstar is fictional and is not affiliated with these organizations. Northstar thresholds, systems, formulas, names, approvals, and examples above are original.

- **Dollar Tree, Inc. — Merchandise Vendors**  
  https://corporate.dollartree.com/vendor-real-estate-partners/merchandise-vendors  
  Influenced the use of electronic purchase-order connectivity and structured vendor transaction channels.

- **Dollar Tree, Inc. — Inbound Shipping Requirements and Regulations (January 22, 2026)**  
  https://corporate.dollartree.com/_assets/_18ad4f2a9b9567efd9c98c4f5673d6ab/dollartreeinfo/db/1137/8592/file/Dollar%2BTree%2BVendor%2BIB%2BShipping%2BRequirements%2Band%2BRegulations.pdf  
  Influenced the separation of order-release accuracy, routing execution, carrier coordination, and vendor responsibility for avoidable logistics costs.

- **Family Dollar — Vendor Guide Part 1: Purchase Order On-Time and In-Full Program**  
  https://corporate.dollartree.com/_assets/_05f5c7276183866d7a2635f240201cc7/dollartreeinfo/db/1137/9040/file/FD_Vendor_Guide_Part_1_Purchase_Order_On_Time_In-Full_Program.pdf  
  Influenced the concepts of combining timeliness with fullness, assigning different responsibility points for prepaid versus collect freight, and treating vendor- and buyer-driven cancellations differently in performance calculations.

- **United Natural Foods, Inc. (UNFI) — Supplier Terms & Conditions, updated July 30, 2026**  
  https://www.unfi.com/supplier-terms.html  
  Influenced PO-centered control of delivery time/place/quantity, acceptance through order confirmation or shipment, and prompt response to delivery requirements.

- **US Foods — Purchase Order Terms and Conditions**  
  https://www.usfoods.com/content/dam/usf/pdf/Policies/usf_purchase_order_terms_and_conditions.pdf  
  Influenced the concepts of fulfilling ordered quantities unless otherwise agreed, tying shipment records to the PO, and promptly notifying the buyer of expected delay.
