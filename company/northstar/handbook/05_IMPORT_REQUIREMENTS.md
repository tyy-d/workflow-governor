# Import Requirements

## 1. Purpose and scope

This policy governs merchandise manufactured, grown, harvested, packed, or otherwise sourced outside the United States and supplied to Northstar Regional Markets for U.S. sale or distribution. It applies both when Northstar controls the U.S. import entry and when a vendor imports merchandise before domestic delivery to Northstar.

The policy is owned jointly by Vendor Compliance, Procurement, Logistics, and Quality & Regulatory (Q&R). The **Import Compliance Lead**, a role within Vendor Compliance, owns customs-data readiness and coordinates Northstar-authorized customs brokers. Q&R owns food, product-safety, and other regulatory admissibility evidence. Logistics owns international routing and handoff requirements. Procurement owns commercial sourcing decisions.

This section does not replace the commercial PO rules in `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`, the technical release gates for private label in `03_PRIVATE_LABEL_PRODUCTS.md`, or packaging/label approval under `04_PACKAGING_AND_LABELING.md`.

### Legal/regulatory distinction

U.S. import requirements vary by commodity, source country, transaction, and agency jurisdiction. Applicable law controls; Northstar approval is an internal commercial control, not government authorization. Potentially applicable regimes include CBP customs requirements, FDA food-import controls, USDA/FSIS or APHIS requirements, CPSC certification, and Lacey Act declarations.

## 2. Definitions

| Term | Northstar meaning |
|---|---|
| **Northstar Direct Import (NDI)** | Northstar, or a Northstar-designated U.S. entity, is the buyer/import party controlling the customs entry and approved broker relationship. |
| **Vendor-Landed Import (VLI)** | Vendor or another non-Northstar party completes importation before domestic delivery to Northstar. |
| **Importer of Record (IOR)** | Party responsible for the CBP entry. This is not necessarily the same party as the FSVP importer. |
| **FSVP Importer** | The party identified under FDA's FSVP rules for a covered food entry. |
| **Import Compliance Record (ICR)** | VendorLink item/source record containing Northstar's approved import facts for one item, manufacturing/source site, and country-of-origin configuration. |
| **Shipment Import Packet (SIP)** | Shipment-specific documents and data supporting an NDI entry. |
| **Import Ready** | VendorLink status confirming that Northstar import-data prerequisites are satisfied. It does not authorize production, shipment absent a PO, or technical release. |
| **Import Hold** | Northstar administrative control preventing shipment, entry-directed delivery, or distribution until a stated import issue is resolved. |

## 3. Vendor responsibilities

An Import Vendor must:

1. disclose the actual manufacturer or producing facility and all material source countries relevant to the imported item;
2. provide truthful and complete product descriptions, composition/material information, origin data, quantities, weights, values, and supporting records;
3. use only the source site and country configuration approved in the active ICR;
4. notify Northstar before changing manufacturer, source country, substantial transformation location, material composition, or other facts that may affect admissibility, duty treatment, agency jurisdiction, or origin;
5. provide shipment documents early enough for Northstar or its broker to meet legal filing deadlines;
6. never instruct a Northstar broker to alter classification, value, origin, manufacturer identity, regulatory data, or importer identity without written Northstar authorization; and
7. immediately disclose any government detention, refusal, seizure, exam, forced-labor inquiry, regulatory hold, or material customs discrepancy affecting Northstar merchandise.

Intermediaries do not eliminate the obligation to identify the actual manufacturing/source facility when required.

## 4. Northstar process

### 4.1 Determine import model

Procurement records each imported sourcing arrangement as NDI or VLI before the first commercial PO. The Import Compliance Lead confirms the IOR model. For food, Q&R separately determines the applicable FSVP status; the FSVP importer must not be inferred from the CBP IOR field.

### 4.2 Build and approve the ICR

The vendor submits the ICR in VendorLink. At minimum it identifies:

- NVID and Northstar item number;
- seller/exporter;
- actual manufacturer/producer and site address;
- country of origin and, when different, country of export;
- product description and material/composition details sufficient for import review;
- proposed HTSUS classification data or Northstar-requested classification support;
- regulatory-agency applicability;
- labeling/country-of-origin marking configuration linked to the active APLR;
- food FSVP/Prior Notice/facility-registration applicability;
- applicable CPSC, USDA/FSIS, APHIS, Lacey Act, permit, or certificate status; and
- any preferential duty claim and supporting origin basis.

For private-label products, the manufacturing site must match the Approved Manufacturing Site in the PLTF. An approved ICR cannot legitimize an undisclosed private-label site.

### 4.3 Import Ready gate

A new imported item/source combination may not be released for an NDI shipment until VendorLink shows **Import Ready**. Import Ready requires Vendor Compliance and all applicable Q&R review to be complete.

Import Ready does not replace:

- an Active vendor status;
- a commercial PO and revision under file 01;
- Production Authorized or Shipping Authorized under file 03; or
- an active APLR/AFP when those records are required.

### 4.4 Shipment preparation for NDI

For each shipment, the vendor creates an SIP containing the commercial invoice, packing list, transport document data, PO/item references, quantities, manufacturer/source information, country-of-origin data, and any required agency documents or confirmation numbers.

Northstar's approved broker compares SIP data against the active ICR and PO; material mismatch results in Import Hold until corrected or approved.

### 4.5 Border and agency events

Merchandise under CBP or another government agency detention, hold, exam, refusal, or conditional-release restriction remains under Import Hold. Northstar facilities must not treat government release as proven merely because freight physically arrives at a domestic location.

The vendor must notify the Import Compliance Lead and applicable Q&R owner within **4 business hours** after learning of a material government action and provide the official notice or broker evidence within **1 business day** when available.

## 5. Required documents and data

| Situation | Required Northstar evidence |
|---|---|
| All imported items | Active ICR; manufacturer/source site; origin; item description; applicable APLR; regulatory applicability assessment |
| NDI shipment | SIP; commercial invoice; packing list; bill of lading/air waybill or equivalent data; broker-entry references when available |
| Ocean NDI | ISF-support data, including manufacturer, seller, stuffing location, consolidator, origin, HTS, buyer, ship-to, IOR and consignee data as applicable |
| FDA-regulated food | FSVP status/exemption basis; foreign-facility registration information where applicable; prior-notice responsibility and confirmation evidence |
| FSIS-regulated meat/poultry/egg product | Eligible country/establishment evidence and required foreign inspection/import certification |
| CPSC-certified imported product | Applicable CPC/GCC or other required certificate data and evidence of required eFiling |
| Covered plant/wood product | APHIS permit/admissibility evidence when applicable; Lacey Act declaration data when required |
| Preferential tariff claim | Valid origin certification or other supporting evidence required for the specific preference program |
| Forced-labor-sensitive sourcing | Supply-chain traceability evidence requested by Vendor Compliance, including upstream source identity when necessary |

For VLI transactions, Northstar may request entry, origin, FSVP, certificate, permit, or admissibility evidence when needed to verify legality or investigate a concern.

## 6. Standards and thresholds

### 6.1 ICR timing

- New imported item/source configuration: complete ICR submission at least **15 Northstar business days** before the first planned foreign cargo-ready date.
- Planned manufacturer, origin, or material/composition change that may affect import treatment: updated ICR at least **10 business days** before the affected cargo-ready date, unless another Northstar policy requires earlier notice.
- No affected shipment may proceed until required reapproval is complete.

### 6.2 NDI shipment-data timing

For Northstar policy purposes:

- ocean shipment data needed for ISF must reach the approved broker at least **96 hours before planned vessel loading**;
- other complete SIP data must reach the approved broker at least **2 Northstar business days before planned international departure**, unless the broker/routing instruction sets an earlier deadline;
- applicable government filing deadlines always control when earlier or otherwise different.

These are Northstar lead times, not legal filing deadlines.

### 6.3 Zero-tolerance import-data conflicts

Shipment may not be released under an uncorrected conflict involving:

- actual manufacturer/source site;
- country of origin;
- item identity;
- IOR or FSVP importer identity where required;
- declared customs value where known to be false;
- legally required certificate/permit/agency admissibility status; or
- a claim known or reasonably suspected to rely on falsified documentation.

HTS or preference questions that are genuinely uncertain must be routed to the Import Compliance Lead and broker; the vendor must not select a more favorable treatment merely to reduce duty.

### 6.4 Food imports

For covered FDA foods, the ICR must identify whether Northstar, another U.S. party, or a documented exemption addresses FSVP. When Northstar is the FSVP importer, detailed supplier-verification activities are owned by Q&R and will be governed by `06_QUALITY_AND_COMPLIANCE.md`.

Required FDA Prior Notice must be filed and confirmed according to applicable law before the imported food arrives. A missing or invalid confirmation for an NDI shipment prevents Northstar-directed domestic release until corrected.

For FSIS-regulated meat, poultry, or egg products, Northstar accepts only source-country/establishment combinations eligible for U.S. import and required inspection/certification pathways.

### 6.5 Consumer-product certificates

Where a CPSC rule requires a CPC or GCC, the responsible importer must maintain certificate support. For covered imported products subject to CPSC eFiling effective July 8, 2026, Northstar requires successful filing before Northstar distribution.

### 6.6 Plant and wood products

Where APHIS permits, phytosanitary conditions, or Lacey Act declarations apply, required data must be approved before shipment. "Unknown" species or harvest-country data is not acceptable when required for a declaration unless an agency-authorized designation or exception applies.

### 6.7 Import performance trigger

Three **Import Documentation Failures** for the same NVID within a rolling **90 calendar days** trigger a corrective-action review. An Import Documentation Failure is a vendor-controlled late, missing, or materially inaccurate document/data event that causes or credibly risks a missed government filing, cargo hold, booking cancellation, entry delay, or material rework.

A corrective-action plan is due within **10 business days** after written request.

## 7. Exceptions and escalation

Northstar may approve commercial/process exceptions only where lawful.

| Exception | Minimum approval |
|---|---|
| Non-material clerical document correction before departure | Import Compliance Lead |
| Alternate NDI port/routing with no regulatory impact | Logistics Manager + Import Compliance Lead |
| Temporary administrative import-data gap that does not affect legal filing/admissibility | Vendor Compliance Manager + Import Compliance Lead |
| Food regulatory/FSVP ambiguity | Director, Quality & Regulatory |
| Material origin/manufacturer/composition change | Import Compliance Lead + Vendor Compliance Manager; Q&R if product/regulatory scope is affected |
| Post-detention commercial disposition decision | Vendor Compliance Manager + Procurement Manager + owner of the government/regulatory issue |

No Northstar employee may waive a statutory or regulatory import requirement, authorize knowingly false customs data, bypass an active government detention, or approve merchandise known to be prohibited from import.

A shipment potentially connected to forced labor, a Withhold Release Order, Xinjiang-origin production, or an entity subject to the UFLPA rebuttable presumption must be placed on Import Hold and escalated for evidence review. Northstar policy does not allow a vendor to substitute a different exporter name to avoid such review.

## 8. Non-compliance

Northstar may:

- cancel or delay a foreign booking;
- place an item or shipment on Import Hold;
- reject the proposed source country or manufacturing site;
- refuse to release a PO for an unready source;
- require a corrective-action plan;
- place the affected item/vendor lane under Restricted status review; or
- initiate Suspension review for intentional falsification, concealed source sites, false origin/value information, forged government certificates, or deliberate evasion of import prohibitions.

Dollar deductions, recovery of demurrage/detention, re-export, destruction, testing, brokerage, or other non-compliance costs are governed by `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md`.

## 9. Records and evidence

For NDI entries, Northstar retains the ICR, SIP, broker/entry records, government notices, agency confirmations, exceptions, and disposition evidence for **7 years after the later of U.S. entry or final disposition**, unless longer retention applies.

This exceeds CBP's general five-year rule for many entry records; applicable legal requirements still control.

For VLI items, Northstar retains the import-admissibility evidence actually collected in VendorLink for the normal item/vendor retention period.

## 10. Examples / scenarios

### Scenario A — source country changes after approval

A private-label kitchen item has an approved China source site and Import Ready status. The vendor moves production to Vietnam without updating the ICR. Even if the product is physically identical, the shipment must not proceed because manufacturer/origin facts changed. A PLCR may also be required under file 03.

### Scenario B — FSVP importer mismatch

An FDA food entry lists Northstar as CBP IOR but the ICR identifies a different party as FSVP importer. The agent must not assume Northstar is the FSVP importer merely from the IOR field. Q&R verifies the actual FSVP arrangement before release.

### Scenario C — late ocean data

An NDI ocean supplier sends complete ISF-support data 50 hours before vessel loading. The legal filing may still potentially be completed, but the supplier has missed Northstar's 96-hour data lead time. The event is recorded as an Import Documentation Failure if vendor-controlled.

### Scenario D — CPSC certificate missing

An imported regulated household product arrives with no evidence of the required CPSC certificate/eFiling. The item remains on Import Hold even though its consumer label and barcode match the approved APLR.

### Scenario E — government detention

A vendor learns that a food shipment has been detained and waits two days before informing Northstar. This violates the four-business-hour notification rule and may trigger both import and PO-performance review depending on the delivery impact.

## 11. Related Northstar policies

- `00_COMPANY_AND_VENDOR_OVERVIEW.md` — Import Vendor role, vendor status, general regulatory obligations.
- `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md` — PO authority and delivery-performance consequences.
- `02_PRODUCT_FRESHNESS.md` — shelf-life requirements that remain applicable to imported food.
- `03_PRIVATE_LABEL_PRODUCTS.md` — approved manufacturing site and private-label change gates.
- `04_PACKAGING_AND_LABELING.md` — country-of-origin marking/label configuration and APLR controls.
- `06_QUALITY_AND_COMPLIANCE.md` — detailed FSVP verification, food-safety audits, testing, regulatory evidence and CAP mechanics.
- `08_TRANSPORTATION.md` — international routing/carrier execution where applicable.
- `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md` — cost recovery and appeals.

## Reference basis

Northstar Regional Markets is fictional and is not affiliated with the organizations below. These sources were used only as public structural references.

- **Dollar Tree / Family Dollar — Family Dollar Vendor Guide, Part 6: Import Guidelines**  
  https://corporate.dollartree.com/_assets/_31244b2c7981abe613097911c2c234ee/dollartreeinfo/db/1137/9046/file/FD_Vendor_Guide_Part_6_Import_Guidelines.pdf  
  Influenced the structured pre-shipment data model, manufacturer/origin/HTS documentation, FDA-related import data, and advance ocean-shipment information concept.

- **U.S. Customs and Border Protection — Entry Summary / importer guidance and recordkeeping**  
  https://www.help.cbp.gov/s/article/Article-1643  
  https://www.help.cbp.gov/s/article/Article1840  
  Influenced the distinction between retailer internal readiness and formal customs entry/recordkeeping obligations.

- **U.S. Food and Drug Administration — FSVP and Prior Notice**  
  https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-final-rule-foreign-supplier-verification-programs-fsvp-importers-food-humans-and-animals  
  https://www.fda.gov/industry/fda-import-process/prior-notice-imported-foods  
  Influenced the separate FSVP-importer model, supplier-verification linkage, and shipment-level prior-notice controls.

- **USDA Food Safety and Inspection Service — Import Guidance**  
  https://www.fsis.usda.gov/inspection/import-export/import-guidance  
  Influenced country/establishment eligibility and import-certificate/reinspection concepts for meat, poultry, and egg products.

- **U.S. Consumer Product Safety Commission — Certificates and eFiling**  
  https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Certificates  
  Influenced certificate/eFiling controls for covered imported consumer products.

- **USDA APHIS — Lacey Act and plant-product import requirements**  
  https://www.aphis.usda.gov/plant-imports/file-lacey-act-declaration  
  https://www.aphis.usda.gov/plant-imports/how-to-import  
  Influenced plant/wood traceability, declarations, permits, and source-data controls.

- **DHS / CBP — Uyghur Forced Labor Prevention Act resources**  
  https://www.dhs.gov/uflpa  
  Influenced Northstar's Import Hold and supply-chain evidence escalation for forced-labor risk.
