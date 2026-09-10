# Packaging and Labeling

## 1. Purpose and scope

This policy governs consumer-unit packaging, inner packs, master shipping cases, barcodes, lot/date-code presentation, pallet/logistics labels, and label artwork/data for merchandise supplied to Northstar Regional Markets. It applies to branded, private-label, food, personal-care, household, and general-merchandise items unless a category-specific Northstar specification is more stringent.

Vendor Compliance owns administrative packaging compliance. Merchandising owns consumer presentation and assortment intent. Quality & Regulatory (Q&R) owns regulated label content, allergen and safety information, product-contact packaging concerns, and safety-related holds. Logistics owns case/pallet identification standards. The Private Brand Manager coordinates Northstar-owned artwork under `03_PRIVATE_LABEL_PRODUCTS.md`.

This file defines what packaging and labels must contain and how approved configurations are controlled. `07_DISTRIBUTION_CENTER_RECEIVING.md` will define physical receiving inspection and disposition; `08_TRANSPORTATION.md` will define carrier/loading execution; `05_IMPORT_REQUIREMENTS.md` will define import documentation and country-of-origin processes beyond the label itself.

## 2. Definitions

**Approved Packaging & Label Record (APLR)** — the version-controlled VendorLink record governing the approved consumer package, case configuration, identifiers, label content, code placement, and logistics-label requirements for an item.

**Consumer Unit** — the lowest Northstar-authorized unit offered for retail sale.

**Inner Pack** — an intermediate grouping inside a shipping case that is not normally the Northstar sellable unit unless separately approved.

**Master Case** — the normal shipping case used to move one approved case configuration through Northstar's distribution network.

**Consumer GTIN** — the GS1 Global Trade Item Number assigned to the sellable unit and represented in the approved retail barcode.

**Case GTIN** — the GTIN assigned to an approved non-consumer shipping configuration when such identification is required.

**SSCC** — Serial Shipping Container Code, an 18-digit GS1 identifier used as a unique logistics-unit identifier, normally encoded in GS1-128.

**Controlled Label Data** — regulated or Northstar-controlled identity, quantity, ingredients/allergens, nutrition, warnings, claims, lot/date codes, GTINs, and responsible-business information.

**Packaging Configuration** — the approved Consumer Unit, Inner Pack, Master Case quantity, physical attributes, materials, and logistics presentation.

## 3. Vendor responsibilities

Vendors must:

1. ship only the current approved Packaging Configuration for the ordered Northstar item;
2. ensure Consumer GTIN, Case GTIN, Northstar SKU, pack quantity, dimensions, and weights agree with the active APLR and item master;
3. ensure barcodes are correctly encoded, legible, durable, and positioned for the intended scanning environment;
4. maintain package integrity suitable for the product and expected distribution conditions;
5. make all legally required consumer statements applicable to the product and jurisdiction;
6. ensure ingredient, allergen, warning, nutrition, claim, and date-code information agrees with the current approved product/specification data;
7. prevent obsolete or superseded artwork from being used after the authorized transition period;
8. preserve lot/batch identification required by this policy; and
9. obtain written approval before any controlled packaging or label change is placed into Northstar commerce.

A vendor using a contract manufacturer, printer, co-packer, packaging converter, or label supplier remains responsible for the final product presented to Northstar.

## 4. Northstar process

### 4.1 Initial packaging and label setup

Before an item becomes orderable, VendorLink must contain an APLR for each authorized sellable and shipping configuration. For private-label items, the APLR links to the PLTF; APLR approval does not replace file 03 `Production Authorized` or `Shipping Authorized` gates.

### 4.2 Review ownership

- **Merchandising** — consumer presentation, item identity, and retail configuration.
- **Q&R** — regulated/safety content, ingredients/allergens, warnings, product-contact concerns, and traceability.
- **Logistics** — case/pallet handling data and logistics labels.
- **Vendor Compliance** — completeness, version control, and exceptions.

A PO does not authorize an unapproved pack or label. PO quantity controls ordered units, not Packaging Configuration.

### 4.3 Legal baseline

Applicable law controls mandatory labeling; Northstar approval is not regulatory approval. FDA-regulated food, FSIS-regulated meat/poultry, cosmetics, household consumer commodities, and CPSC-regulated products must carry their applicable required identity, quantity, ingredient/allergen, nutrition, inspection/handling, warning, tracking, or business information. Northstar stickers or security devices may not obscure required information.

### 4.4 Northstar retail-unit controls

Every Consumer Unit must carry the approved Consumer GTIN unless VendorLink documents a category exception; the scanned value must resolve to the same item, size/count, and selling configuration in the APLR. Northstar also requires readable English identity/safety information; human-readable lot/batch codes on all R2/R3 foods and private-label personal-care/household-chemical items; AFP-compliant date coding for freshness-controlled items; and durable, legible variable data. Barcodes, lot/date codes, allergen statements, and mandatory warnings may not be placed where ordinary package opening or seams routinely destroy or obscure them. The APLR records the format and normal location.

### 4.5 Shipping-case controls

Each Master Case must match the approved case pack; alternate counts, mixed assortments, Inner Packs, display shippers, or unit configurations require Section 7 approval. Case identification must include, as applicable:

| Field | Requirement |
|---|---|
| Northstar SKU | Required on Master Cases |
| Product description | Required; must reasonably match Northstar item description |
| Case quantity | Required |
| Consumer GTIN | Required for homogeneous cases |
| Case GTIN | Required where assigned in APLR |
| Lot/batch code | Required for R2/R3 food and other lot-controlled items |
| Freshness date | Required where AFP requires case-level visibility |
| Handling/orientation mark | Required when safe handling depends on orientation, fragility, or other condition |

Authorized mixed cases must have an APLR-defined assortment and case identifier. Liquids requiring upright handling need visible orientation marks on two opposing sides; fragile goods need adequate protection and special-handling identification. Legally required hazardous-material markings cannot be replaced by Northstar symbols.

### 4.6 Pallet and logistics labels

Each non-exempt palletized DC shipment must have a unique SSCC and a scannable GS1-128 logistics label. The label must identify or electronically associate:

- SSCC;
- NVID;
- applicable PO number;
- pallet sequence when multiple pallets are shipped (`1 of N`, `2 of N`, etc.);
- case quantity; and
- SKU/lot/date information sufficient to distinguish pallet contents when the pallet is single-SKU or lot controlled.

Multiple lot/date groups must be distinguishable physically and in label/data; otherwise file 02's least-fresh-date rule controls. ASN/SSCC electronic association is reserved for file 09.

### 4.7 Barcode verification

Before first shipment of a new barcode, and after any change reasonably capable of affecting scanning, vendors must verify production-representative packaging. Northstar private-label barcode evidence must show **ISO/ANSI grade 2.0 (C) or better** when verifier grading is available. A new/changed barcode sample of 10 units/cases must produce **10 correct decodes out of 10**; any wrong decode requires correction and re-verification before shipment.

## 5. Required documents and data

The APLR must contain or link the following where applicable:

| Record/data | Minimum content |
|---|---|
| Final consumer artwork | Current controlled artwork or branded-supplier label image |
| Consumer identifier | Consumer GTIN and barcode symbology |
| Shipping hierarchy | Inner Pack and Master Case quantities/configurations |
| Case identifier | Case GTIN/symbology if assigned |
| Physical master data | Unit/case dimensions, net content/count, gross weight, materials as relevant |
| Lot/date-code specification | Format, meaning, location, example, decode method |
| Regulatory/claim label data | Ingredients, allergens, nutrition, warnings, claims, responsible-business statement as applicable |
| Logistics label configuration | SSCC requirement and required pallet data |
| Packaging-change history | Prior version, effective lot/date, approval record |
| Barcode evidence | New/change verification evidence when required |

Q&R may require package-material or food-contact evidence when the material, product, or use creates a safety or regulatory concern; detailed testing rules belong in `06_QUALITY_AND_COMPLIANCE.md`.

## 6. Standards and thresholds

### 6.1 Configuration accuracy

- **Zero tolerance** for an unauthorized Consumer GTIN, case pack, substituted sellable size/count, mandatory allergen statement, mandatory safety warning, or lot/date-code meaning.
- If actual case gross weight or any outer dimension differs from the active APLR by **more than 5%**, corrected data or an approved packaging change is required before the next shipment. Safety/handling risk may trigger hold regardless of percentage.
- Variable lot/date codes must remain human-readable without destructive opening of the Master Case when case-level visibility is required by the APLR.
- Labels used to correct or supplement packaging must be securely affixed and may not detach under normal distribution conditions.

### 6.2 Controlled label changes

For branded items, planned changes to Controlled Label Data, Consumer GTIN, case pack, protective materials, lot/date-code format, barcode placement, or case/logistics configuration require submission **at least 30 calendar days before first affected shipment**. Private-label Material Changes remain subject to file 03's **60-day PLCR**; freshness changes remain subject to file 02. VendorLink approval is required before shipment, and Northstar cannot authorize GTIN reuse contrary to applicable GS1 rules.

### 6.3 Issue severity

| Severity | Examples | Default action |
|---|---|---|
| Critical Packaging/Label Event | undeclared/wrong allergen; missing mandatory safety warning; GTIN resolves to different product; falsified lot/date code; unauthorized private-label identity; packaging defect creating credible safety risk | Q&R hold and immediate escalation |
| Major | wrong case pack; non-scannable barcode; missing required lot code; incorrect case/pallet label; required SSCC missing; >5% unreported case master-data variance | hold/correction or receiving disposition; compliance event |
| Minor | cosmetic/placement defect that does not impair legality, traceability, scan, identity, or safe handling | correction at next production unless pattern escalates |

Three Major events for the same NVID/product family within a rolling **60 days** trigger a packaging corrective-action review even if each individual shipment was ultimately accepted.

## 7. Exceptions and escalation

Packaging/label exceptions must be documented in VendorLink with affected SKU/lot/quantity, deviation, evidence, correction, approver, and expiry. A **Temporary Overlabel Authorization (TOA)** may correct an eligible non-safety defect when the new label is accurate, durable, preserves traceability, and does not conceal required information.

Approval authority:

| Exception | Required approval |
|---|---|
| Case/logistics marking only, no consumer/safety effect | Logistics Manager + Vendor Compliance Manager |
| Consumer presentation/marketing text with no regulated or technical effect | Merchandising Manager; Private Brand Manager for Northstar private label |
| Regulated label, allergen, mandatory warning, lot/date-code meaning, product-contact packaging, or safety-related condition | Director, Quality & Regulatory |
| Commercial packaging substitution affecting case pack/PO fulfillment | Procurement Manager + Vendor Compliance Manager; plus Q&R where product/safety may be affected |
| Private-label Material Change | PLCR process in file 03; applicable Q&R/Private Brand approvals remain required |

No exception may waive law, knowingly permit unsafe or misbranded product, hide an expired/falsified date, conceal an allergen or mandatory warning, retroactively legitimize an unauthorized private-label change, or deliberately map one item to another item's GTIN.

## 8. Non-compliance

Packaging or labeling non-compliance may result in hold, rejection, relabeling/overlabeling, repacking, rework, item restriction, corrective action, vendor-status review, or later chargeback under `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md`.

A vendor must not ship known mislabeled or incorrectly packaged product merely to preserve OTIF. `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md` governs performance measurement, but safety, legal labeling, approved item identity, and traceability take precedence.

Critical Packaging/Label Events are reported immediately to Q&R and Vendor Compliance. Intentional concealment, falsified label/traceability records, or repeated shipment after explicit stop direction may trigger Suspension under file 00.

## 9. Records and evidence

Records must permit Northstar to reconstruct which packaging/label version governed an item and shipment. Evidence includes:

- current and historical APLRs;
- artwork/label versions and approval dates;
- GTIN and case-identifier assignments;
- case-pack, dimension, and weight history;
- lot/date-code specifications and examples;
- barcode-verification results;
- SSCC/logistics-label records where applicable;
- TOAs and packaging exceptions;
- photographs or production samples used for approval;
- packaging/label deviations and corrective actions; and
- links to PLTF, AFP, quality, import, PO, and receiving evidence where relevant.

Northstar retains packaging/label approval and change records for **7 years after the later of item retirement or last Northstar receipt**, unless law, recall, litigation hold, contract, or another policy requires longer retention.

## 10. Examples / scenarios

### Scenario A — wrong case count

A 12-unit case is approved, but the vendor proposes 10-unit cases while keeping total units unchanged. The PO does not override the APLR; the alternate case pack needs approval before shipment.

### Scenario B — barcode artwork change

A shampoo redesign moves and reduces the barcode while keeping the GTIN. Production-representative verification is required; all 10 sampled units must decode to the approved Consumer GTIN.

### Scenario C — allergen overlabel request

A private-label cookie's allergen statement does not match the approved formula. Q&R must determine whether lawful correction/release is possible; a TOA cannot bypass an undeclared-allergen condition.

### Scenario D — mixed-date pallet

Two date groups are separately identified and physically segregated, so file 02 may evaluate them independently. If intermixed and not reliably separable, the least-fresh date controls.

### Scenario E — unreported case-size increase

A new case is 8% wider than the APLR. Master data must be updated before the next shipment; a handling/storage risk may justify hold even though the consumer label is correct.

## 11. Related Northstar policies

- `00_COMPANY_AND_VENDOR_OVERVIEW.md` — vendor status, risk tiers, exception principles, and Q&R authority.
- `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md` — PO authority and prohibition on unapproved substitutions.
- `02_PRODUCT_FRESHNESS.md` — date-code meaning, Approved Freshness Profiles, remaining life, and least-fresh-date rule.
- `03_PRIVATE_LABEL_PRODUCTS.md` — PLTF, PLCR, Production/Shipping Authorization, and private-label change control.
- `05_IMPORT_REQUIREMENTS.md` — import records and detailed country-of-origin requirements.
- `06_QUALITY_AND_COMPLIANCE.md` — product/package testing, regulatory evidence, and corrective-action mechanics.
- `07_DISTRIBUTION_CENTER_RECEIVING.md` — physical inspection, scan, hold, and receiving disposition.
- `08_TRANSPORTATION.md` — loading, carrier, routing, and hazardous transportation requirements.
- `09_VENDOR_PORTAL_AND_INVOICING.md` — ASN/electronic transaction and SSCC association.
- `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md` — cost recovery, returns, recall disposition, and appeals.

## Reference basis

Northstar is fictional and unaffiliated with the organizations below; these public sources were used only for structural concepts.

- **Family Dollar / Dollar Tree — Product & Packaging: Carton Marking Requirements.** https://corporate.dollartree.com/_assets/_881425332f996a34ebbd53344944a2c5/dollartreeinfo/db/1137/9048/file/FD_Vendor_Guide_Part_4_Product_and_Packaging_Carton_Marking_Requirements.pdf — informed structured Master Case fields, case-pack/inner-pack distinctions, handling marks, mixed-case treatment, and exception approval concepts.
- **Dollar Tree — UPC Basics Guide.** https://corporate.dollartree.com/_assets/_e8138176ce928b3deb1bd6fce547bf84/dollartreeinfo/db/1137/8577/file/Dollar_Tree_UPC_Basics_Guide.pdf — informed scan-quality, quiet-zone, placement, and production barcode-verification concepts.
- **GS1 US — Create a Shipping Case; Packaging Levels; Serialized Shipping Container Codes; Barcode Placement & Printing Guidelines.** https://www.help.gs1us.org/create-a-case-and-generate-a-barcode ; https://www.help.gs1us.org/packaging-level ; https://www.gs1us.org/upcs-barcodes-prefixes/serialized-shipping-container-codes ; https://www.gs1us.org/upcs-barcodes-prefixes/how-to-use-your-upc-barcodes/place-barcodes-on-products — informed GTIN hierarchy, case identifiers, SSCC/logistics-unit identification, and barcode usability concepts.
- **FDA — Guidance for Industry: Food Labeling Guide; Food Allergies.** https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-industry-food-labeling-guide ; https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies — informed the separation between legal food-label requirements and retailer approval, including current allergen-labeling concepts.
- **USDA Food Safety and Inspection Service — What is required on a food label?** https://ask.fsis.usda.gov/article/What-is-required-on-a-food-label — informed the distinct labeling baseline for meat and poultry products under FSIS jurisdiction.
- **FDA — Cosmetics Labeling Guide / Summary of Cosmetics Labeling Requirements.** https://www.fda.gov/cosmetics/cosmetics-labeling-regulations/cosmetics-labeling-guide ; https://www.fda.gov/cosmetics/cosmetics-labeling-regulations/summary-cosmetics-labeling-requirements — informed cosmetic identity, ingredient, net-content, business-information, warning, and prominence concepts.
- **Federal Trade Commission — Fair Packaging and Labeling Act regulations/policy.** https://www.ftc.gov/legal-library/browse/rules/fair-packaging-labeling-act-regulations-under-section-4-fair-packaging-labeling-act — informed identity, business-name/place, and net-quantity concepts for household consumer commodities.
- **U.S. Consumer Product Safety Commission — Labeling Requirements Overview.** https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/CPSC-Labeling-Requirements-Overview — informed product-specific consumer warning/tracking-label boundaries for CPSC-regulated goods.
