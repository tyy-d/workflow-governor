# Distribution Center Receiving

## 1. Purpose and scope

This policy governs inbound merchandise received at Northstar Regional Markets distribution centers. It applies to vendor-prepaid, Northstar-managed pickup, and approved third-party shipments that physically arrive at a Northstar DC. It does not replace purchase-order terms, freshness rules, quality release requirements, import controls, or transportation responsibility established elsewhere in this handbook.

Northstar operates two regional distribution centers for handbook purposes:

| Code | Facility | Region served |
|---|---|---|
| HVDC | Hudson Valley Distribution Center, Newburgh, New York | Primarily New York and northern New Jersey |
| LVDC | Lehigh Valley Distribution Center, Allentown, Pennsylvania | Primarily Pennsylvania and southern New Jersey |

Distribution Center Operations owns physical receiving, count evidence, dock disposition, and proof of receipt. Logistics owns appointment-network rules. Quality & Regulatory (Q&R) owns food/product-safety holds and technical disposition. Vendor Compliance coordinates recurring receiving non-compliance and corrective action.

Direct-Store-Delivery shipments are outside this DC procedure unless the PO specifically routes them through a DC.

## 2. Definitions

**DockSchedule** — Northstar's appointment system for DC inbound deliveries. It may exchange shipment information with VendorLink.

**Gate Arrival Time** — timestamp recorded when the tractor/trailer or delivery vehicle first presents at the correct Northstar DC gate with sufficient information to identify its scheduled shipment.

**Northstar Receipt Date** — for a delivery that is ultimately unloaded, the local calendar date of Gate Arrival Time. For an accepted drop trailer, it is the local date Northstar accepts custody of the trailer. A shipment turned away before Northstar accepts custody or begins unloading has no Northstar Receipt Date.

**Receiving Exception Record (RER)** — VendorLink record documenting a receiving discrepancy, evidence, affected quantities, preliminary responsibility, disposition, and approvals.

**Receiving Hold** — physical or system segregation that prevents affected product from entering saleable inventory until disposition is authorized.

**Receiving Disposition** — Accepted, Accepted with Exception, Held, Partially Rejected, or Rejected.

## 3. Vendor and carrier responsibilities

Before arrival, the vendor/carrier must:

- obtain a confirmed DockSchedule appointment when an appointment is required;
- use the correct Northstar destination and PO;
- ensure shipment quantities, item identities, lot/date coding, pallet configuration, and required labels match authorized records;
- provide required shipping documents;
- protect the load against shifting, contamination, infestation, water intrusion, and damage;
- preserve required temperature conditions and seal integrity;
- notify Logistics promptly when a confirmed appointment will be missed.

## 4. Appointment, arrival, and receiving process

### 4.1 Appointment requirements

Live-unload inbound shipments require a confirmed DockSchedule appointment unless the lane is configured as an approved standing shuttle, parcel/express exception, or documented emergency delivery.

Vendor-prepaid appointment requests should be submitted at least **2 Northstar business days before planned arrival**. Same-day appointments require available capacity and approval by the applicable DC Receiving Manager; approval of a same-day appointment does not erase a late PO-performance event already created under `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`.

A carrier is considered within the normal appointment arrival window when Gate Arrival Time is from **45 minutes before** through **30 minutes after** the confirmed appointment time.

- Arrival more than 45 minutes early: the DC may require the vehicle to wait offsite or in an assigned staging area.
- Arrival more than 30 minutes late: record **Late Arrival**; the DC may work the load in, hold it for later unloading, or require rescheduling.
- No Gate Arrival by **60 minutes after** the appointment without a DC-approved reschedule: record **No Show**.

For vendor-prepaid deliveries, Gate Arrival Time is the receiving timestamp used to evaluate the controlling arrival window under file `01`. Delay between compliant gate arrival and door assignment is not vendor lateness unless vendor/carrier action caused the delay.

### 4.2 Gate and dock check-in

DC Operations records or verifies:

- appointment/reservation number;
- PO number and revision where available;
- NVID/vendor name;
- carrier and trailer/container number;
- seal number when applicable;
- Gate Arrival Time;
- shipment type (prepaid, Northstar-managed, drop, other approved type);
- visible trailer condition before unloading when material.

After entering the site, the driver must present required paperwork or complete electronic check-in within **15 minutes**, unless directed otherwise by Northstar personnel.

### 4.3 Required receiving documents/data

| Evidence | Standard requirement |
|---|---|
| Confirmed DockSchedule appointment | Required when appointment-controlled |
| Valid Northstar PO/revision | Required for commercial receipt |
| Bill of lading | Required for truckload/LTL freight unless approved alternate record applies |
| Packing list | Required unless shipment data approved by Northstar fully substitutes for it |
| Shipment/ASN reference | Required when the vendor is ASN-enabled; detailed message rules are in file `09` |
| Seal number | Required when the load is tendered under seal |
| Lot/date information | Required where APLR/AFP/QVP requires it |
| Temperature/set-point evidence | Required when requested or when applicable product controls require it |
| Import release/readiness evidence | Required when file `05` identifies a release condition; physical arrival alone is not government release |

## 5. Physical inspection and count controls

### 5.1 Trailer and load condition

DC Operations checks for:

- broken or unexplained seal;
- pest evidence;
- chemical or fuel odor;
- standing water, active leakage, mold, blood, fecal material, or other contamination;
- unsafe shifted load or collapsed pallets;
- visible temperature-abuse indicators;
- product damage or tampering.

Credible contamination, infestation, unexplained safety-sensitive seal failure, or evidence that food may have become unsafe requires a Receiving Hold and prompt Q&R escalation. DC Operations may stop unloading when continued unloading would create a safety risk.

### 5.2 Pallets and load configuration

Unless the active APLR, PO, or lane instruction authorizes another configuration, Northstar's default pallet standard is:

| Requirement | Northstar default |
|---|---:|
| Footprint | 48 x 40 inch, four-way entry |
| Maximum gross pallet weight | 2,200 lb |
| Maximum loaded height, pallet included | 66 inches |
| Product overhang | None permitted |
| Condition | Structurally sound; no protruding fasteners, broken load-bearing members, visible contamination, or unstable load |

Floor-loaded merchandise requires PO/lane authorization or prior Logistics/DC approval. An unauthorized floor load may be received when operationally feasible but must be documented in an RER.

Pallet/case identification, GTIN, SSCC, lot-code, and date-code requirements remain controlled by `04_PACKAGING_AND_LABELING.md`. Where an SSCC is required, DC Operations scans or captures it and compares it with available shipment/ASN information.

### 5.3 Quantity and identity

- Unauthorized substitutions are not receivable as the ordered item.
- Unordered product must not enter saleable inventory without an authorized PO/revision or documented commercial exception.
- Overages above ordered quantity are rejected or held unless the PO/revision authorizes them.
- Shortages are recorded against actual received quantity and flow to file `01` performance calculations.
- Wrong-item or wrong-destination merchandise is segregated pending disposition.

If visible damaged cases equal **5 or more cases or 1.0% of presented cases, whichever threshold is reached first**, DC Operations must open an RER before closing the receipt. Any safety-sensitive leakage, contamination, tampering, allergen concern, or product-integrity risk requires an RER and hold regardless of quantity.

## 6. Food, freshness, and temperature receiving controls

### 6.1 Freshness inspection

For freshness-controlled product, DC Operations uses the active Approved Freshness Profile (AFP) from file `02` as ground truth. Receiving personnel do not redefine shelf life.

Unless Q&R establishes another sampling plan, receiving checks at least **3 cases per item/lot** distributed across the accessible load for readable lot/date information and applies the AFP calculation. If multiple dates are present, the least-remaining-life logic in file `02` controls unless groups can be reliably segregated.

Short-dated or undecodable product is placed on the applicable Freshness Hold rather than being silently accepted.

### 6.2 Temperature inspection

For temperature-controlled R3 food loads, receiving personnel record:

1. trailer/container ambient reading or refrigeration setting when available; and
2. at least **3 product-temperature readings** from spatially separated locations, normally front, middle, and rear of the load.

For temperature-controlled R2 product, at least **2 product readings** are required unless the QVP/AFP requires more. Q&R may establish item-specific sampling.

When no stricter item specification applies, Northstar uses these company receiving defaults:

| Category | Northstar receiving default |
|---|---|
| Refrigerated TCS food | 41°F (5°C) or below |
| Raw shell eggs | Refrigerated equipment ambient 45°F (7°C) or below |
| Other refrigerated quality-controlled food | 45°F or below unless AFP/QVP is stricter |
| Frozen food | Hard frozen, no material evidence of thaw/refreeze, and product reading 10°F or below unless AFP/QVP specifies another limit |

Any out-of-specification temperature, thaw/refreeze evidence, off-odor, or credible cold-chain concern triggers **Temperature Hold** for the affected scope. Receiving expands sampling to at least **6 product readings where safely practicable** and provides the evidence to Q&R. Product may not be released merely because most readings are acceptable. Q&R determines whether time/temperature evidence supports release, restricted disposition, or rejection.

## 7. Exceptions, holds, and escalation

### 7.1 Receiving authority

The DC Receiving Manager may approve temporary operational handling exceptions involving dock sequencing, staging, unloading method, or non-safety pallet handling when capacity and worker safety permit.

The Logistics Manager must approve recurring appointment/lane exceptions or alternate scheduled-arrival arrangements.

The Director, Quality & Regulatory or delegated Q&R authority controls release from food/product-safety, contamination, temperature, integrity, regulatory, or technical-quality holds.

Procurement/Merchandising may decide whether commercially unwanted but otherwise compliant product should be accepted, but cannot override a Q&R safety hold.

### 7.2 Conditions that normally require hold or rejection

| Condition | Default action |
|---|---|
| No valid PO and no approved emergency authorization | Reject/hold outside saleable inventory |
| Wrong DC | Reject or redirect under Logistics instruction |
| Unapproved item/substitution | Hold or reject |
| Import product lacking required release/readiness evidence | Import/Receiving Hold |
| Broken/mismatched seal on R3 or safety-sensitive load | Hold pending inspection/Q&R review |
| Visible infestation or material contamination | Stop unload if needed; Q&R Hold |
| Temperature-controlled food out of specification | Temperature Hold |
| Expired product | Q&R/Freshness Hold under file `02` |
| Product under active Q&R/vendor suspension | Do not release to saleable inventory |
| Minor pallet/label defect without safety or identity impact | Receive with RER when operationally feasible |

An exception may not waive law, a government detention, active product recall, Q&R safety hold, known undeclared allergen, falsified lot/date data, or unresolved evidence that food may be unsafe.

## 8. Non-compliance and recurring performance

Receiving exceptions may produce rework, rejection, corrective action, vendor review, or later cost recovery under file `10`; this file sets no dollar chargebacks.

Vendor Compliance initiates a receiving corrective-action review when any of the following occurs for the same NVID/product family or inbound lane:

- **3 Major receiving events within 60 calendar days**;
- **2 Late Arrival/No Show events within 30 days** on a lane with at least 4 scheduled deliveries;
- any Critical receiving event involving contamination, infestation, deliberate identity/date falsification, or credible safety risk; or
- a pattern that materially disrupts DC operations even if individual events are below a numeric trigger.

Where file `06` classifies the issue as a quality finding, its CAP severity and deadlines control.

## 9. Records and evidence

At receipt close, Northstar should retain enough evidence to reconstruct what physically occurred. The receiving record should include, as applicable:

- PO/revision, NVID, carrier, trailer/container;
- appointment number and confirmed time;
- Gate Arrival Time, dock/door assignment time, unload start/end time;
- Northstar Receipt Date;
- BOL/packing-list/ASN references;
- seal number and seal exception;
- item/lot/date quantities presented, accepted, held, and rejected;
- SSCC/pallet scan evidence when required;
- temperature readings and measurement locations;
- freshness checks;
- damage/contamination observations and photographs;
- RER number and approvals;
- final Receiving Disposition;
- proof of delivery or signed/electronic receipt evidence.

Receiving records and linked RERs are retained for **7 years after receipt close**, unless another policy or legal requirement requires longer retention.

## 10. Examples / scenarios

**Scenario 1 — compliant gate arrival, delayed dock.** A prepaid carrier has a 10:00 appointment and checks in at the HVDC gate at 10:22. Northstar does not assign a door until 11:05. The vendor is on time because Gate Arrival Time is within the +30-minute window; Northstar's dock delay does not create vendor lateness.

**Scenario 2 — refrigerated load over limit.** Three product readings are 39°F, 42°F, and 43°F for an item whose AFP requires 41°F maximum. The receiver opens a Temperature Hold, expands sampling, and routes the evidence to Q&R. The receiver may not average the readings and release the load.

**Scenario 3 — import shipment physically arrives without release evidence.** An NDI container is at LVDC with correct PO and packaging, but the required import-release status cannot be verified. Physical arrival does not prove government release. DC Operations places it on Import/Receiving Hold and contacts the Import Compliance Lead.

**Scenario 4 — minor operational defect.** A pallet is structurally safe but has a missing required SSCC label. The item identity and case labels are otherwise verifiable. The DC may receive with an RER if operationally feasible, but the event remains a packaging/receiving non-compliance and may contribute to corrective-action review.

## 11. Related Northstar policies

- See `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md` for PO quantity, On-Time, Fill, and OTIF calculations.
- See `02_PRODUCT_FRESHNESS.md` for remaining-life calculations and Freshness Exceptions.
- See `04_PACKAGING_AND_LABELING.md` for APLR, GTIN, SSCC, lot/date placement, and packaging standards.
- See `05_IMPORT_REQUIREMENTS.md` for Import Ready, Import Hold, ICR/SIP, and government-release controls.
- See `06_QUALITY_AND_COMPLIANCE.md` for FQR/QVP, quality finding severity, testing, and CAP requirements.
- See `08_TRANSPORTATION.md` for carrier, sanitation, routing, seal, and cold-chain execution requirements.
- See `09_VENDOR_PORTAL_AND_INVOICING.md` for detailed ASN and electronic transaction mechanics.
- See `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md` for returns, disposition cost recovery, deductions, and appeals.

## Reference basis

Northstar Regional Markets is fictional and is not affiliated with the organizations below. The sources were used only for public process concepts.

- **Family Dollar — Vendor Resources / Part 8: Distribution Requirements**  
  https://corporate.familydollar.com/vendor-resources  
  https://www.dollartree.com/file/general/FD_Vendor_Guide_Part_8_Distribution_Requirements.pdf  
  Influenced the use of explicit pallet condition/configuration rules, product grouping, receiving identification, packing-list evidence, and documented handling of non-compliant loads.

- **Dollar Tree — Logistics and Inbound Shipping Requirements and Regulations**  
  https://corporate.dollartree.com/vendor-real-estate-partners/logistics  
  https://www.dollartree.com/file/general/Dollar_Tree_Vendor_Inbound_Shipping_Requirements_and_Regulations.pdf  
  Influenced appointment-system structure, shipment-number/appointment confirmation concepts, required inbound documents, and arrival-window controls.

- **U.S. Food and Drug Administration — FSMA Final Rule on Sanitary Transportation of Human and Animal Food**  
  https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-final-rule-sanitary-transportation-human-and-animal-food  
  Influenced receiver inspection for sanitation and temperature abuse, temperature-control evidence, and the principle that potentially unsafe food should not be distributed before qualified evaluation.

- **U.S. Food and Drug Administration — 2022 Food Code / receiving-temperature provisions**  
  https://www.fda.gov/media/184685/download  
  Influenced the regulatory distinction for refrigerated TCS foods and raw shell eggs. Northstar's broader frozen/refrigerated sampling rules and thresholds are company policy, not representations that every Food Code provision directly governs a Northstar DC.
