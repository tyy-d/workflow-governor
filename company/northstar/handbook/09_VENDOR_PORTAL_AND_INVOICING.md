# Vendor Portal and Invoicing

## 1. Purpose and scope

This policy defines how Northstar vendors exchange controlled commercial records and how Accounts Payable validates, approves, holds, pays, or rejects invoices. It applies to merchandise vendors, private-label manufacturers, import vendors, distributors/brokers, Direct-Store-Delivery (DSD) suppliers, and other suppliers when Northstar requires use of the same transaction controls.

Northstar VendorLink is the system of record for vendor identity, transaction status, supporting documents, exceptions, and payment visibility. Vendors may transact through VendorLink or an approved electronic connection such as EDI or API. A connected channel changes transmission method, not the underlying Northstar record or policy.

Accounts Payable (AP) owns invoice validation, payment setup, payment holds, remittance, and invoice status. Procurement owns commercial terms and PO pricing. Vendor Compliance owns vendor standing and administrative exceptions. Logistics, Distribution Center Operations, Quality & Regulatory (Q&R), and other teams remain authoritative for the operational records they create.

This file does not redefine PO acceptance or OTIF under `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`, packaging identifiers under `04_PACKAGING_AND_LABELING.md`, receiving facts under `07_DISTRIBUTION_CENTER_RECEIVING.md`, or transportation requirements under `08_TRANSPORTATION.md`.

## 2. Definitions

**Electronic transaction channel** — VendorLink web entry, approved EDI, approved API, or another channel expressly authorized by IT and Vendor Compliance.

**ASN (Advance Ship Notice)** — Shipment-level electronic notice describing what is being shipped, where it is going, and the shipment identifiers needed for receiving.

**Invoice Eligible Date (IED)** — the date from which Northstar's contractual payment term begins, defined in Section 6.

**Invoice Exception Record (IER)** — VendorLink record documenting an invoice validation or matching issue, the evidence reviewed, ownership, status, and resolution.

**Three-way match** — comparison of the authorized PO/revision, Northstar receiving record, and vendor invoice.

**Remittance Advice** — Northstar payment record identifying invoices, credits, deductions, and amounts included in a payment.

## 3. Vendor responsibilities

Vendors must:

1. maintain access to VendorLink or an approved electronic connection;
2. protect credentials and promptly remove access for personnel who no longer require it;
3. use the NVID and Northstar identifiers assigned to the legal entity actually transacting with Northstar;
4. transmit records using the latest authorized PO/revision and approved item data;
5. submit accurate ASNs, invoices, credit memos, and supporting evidence within the applicable deadlines;
6. monitor VendorLink for rejections, invoice holds, payment status, and correction requests;
7. correct transmission or invoice defects rather than repeatedly resubmitting unchanged rejected records; and
8. notify Northstar immediately if credentials, bank instructions, or electronic-connection security may have been compromised.

Email, spreadsheets, PDFs, or verbal communications are not authoritative substitutes for required electronic transactions unless an approved outage exception applies.

## 4. Northstar electronic transaction process

### 4.1 Transaction channels and control

VendorLink maintains the authoritative transaction status even when a vendor uses EDI or API. Northstar may require connectivity testing before production use. Test transactions must use designated test credentials or environments and cannot create live commercial obligations.

A vendor may not switch production channels without Vendor Compliance and IT approval. Northstar may temporarily require portal entry if an electronic connection is failing and continued business is necessary.

The core transaction set is:

| Record | Direction | Controlling policy purpose |
|---|---|---|
| Purchase Order / PO Revision | Northstar to vendor | Commercial authorization; file 01 controls |
| PO Acknowledgment | Vendor to Northstar | Acceptance/change request/rejection; file 01 timing controls |
| ASN | Vendor to Northstar | Shipment contents and receiving identifiers |
| Invoice | Vendor to Northstar | Request for payment |
| Credit Memo | Vendor to Northstar | Vendor-issued reduction of amount owed |
| Remittance Advice | Northstar to vendor | Payment, credits, and deductions applied |

### 4.2 ASN requirements

An ASN is required for DC-bound merchandise unless VendorLink marks the lane or vendor class ASN Exempt. DSD suppliers use the transaction type assigned in their VendorLink profile.

The ASN must be accepted by Northstar **before shipment arrival** and normally:

- no later than physical departure from the ship point; and
- at least **4 hours before the confirmed DC appointment** when transit time allows.

For transit under 4 hours, transmission before departure satisfies the timing requirement.

At minimum, the ASN includes:

- NVID;
- PO number and applicable revision;
- ship-from location and destination;
- ship date and expected arrival date/time;
- carrier and transportation identifier when known;
- BOL or equivalent shipment reference;
- trailer/container identifier when applicable;
- pallet/carton count;
- item and shipped quantity by PO line;
- SSCC for each pallet when required by file 04; and
- lot/date/temperature-control data when VendorLink requires those fields for the item.

An ASN does not authorize an over-shipment, substitution, changed destination, or changed PO quantity. If the shipment changes after ASN acceptance, the vendor must transmit a replacement ASN before arrival when the channel supports replacement. The latest accepted ASN controls receiving expectations.

### 4.3 Invoice creation

Merchandise invoices must reference the applicable NVID and PO. One invoice may cover multiple receipts against one PO when permitted, but may not combine different NVIDs or currencies.

Required invoice fields are:

- NVID and legal vendor name;
- unique vendor invoice number;
- invoice date;
- PO number;
- shipment/receipt reference when available;
- item/PO-line identifier;
- quantity invoiced;
- unit price;
- line extension;
- separately identified freight, tax, deposit, allowance, or other charge where authorized;
- invoice currency; and
- total invoice amount.

Invoices may be transmitted after shipment departure but must not represent product that has not shipped. Northstar recommends transmission within **2 business days** and requires submission no later than **10 calendar days after Northstar Receipt Date**, unless the written commercial agreement specifies another deadline.

## 5. Required data and system evidence

The following records should exist after a normal cycle:

| Evidence | Owner / origin | Minimum linkage |
|---|---|---|
| PO and revision history | Procurement / VendorLink | PO number + revision |
| PO acknowledgment | Vendor | PO + lines + status + timestamp |
| ASN acceptance/rejection | VendorLink | PO + shipment + ASN version |
| Receiving record | DC Operations | PO + receipt + item/quantity |
| Invoice record | Vendor / AP | NVID + invoice number + PO |
| IER, if any | AP / owning team | Invoice + exception reason |
| Approval/payment status | AP | Invoice + status + timestamp |
| Remittance Advice | AP | Payment + invoices/credits/deductions |

Where the shipment uses SSCCs, VendorLink must preserve association among ASN, SSCC, PO, shipment, and receipt. File 04 remains authoritative for SSCC requirements.

Q&R documents such as COAs, quality releases, or holds may be linked to the transaction, but AP does not independently determine their technical adequacy.

## 6. Invoice validation, matching, and payment

### 6.1 Automated validation

An invoice is rejected before matching when any of the following applies:

- NVID is invalid or does not match the PO vendor;
- invoice number is missing;
- the same NVID + invoice number already exists as an active or paid invoice;
- PO does not exist or is not payable to that NVID;
- invoice currency conflicts with the PO without written authorization;
- required line-item identifiers are absent;
- mathematical totals do not reconcile; or
- invoice is structurally unreadable by the approved electronic channel.

A rejected invoice does not establish an IED.

### 6.2 Three-way match

For merchandise received through a Northstar DC, AP compares invoice data with the latest authorized PO and the receipt record.

Unless a contract provides a stricter rule, an invoice line automatically matches only when all of the following are true:

1. invoiced cumulative quantity is **not greater than Northstar accepted receipt quantity** for that PO line;
2. invoiced unit price equals the authorized PO unit price, or differs by no more than **$1.00 per invoice line and 0.25% of the PO line value**, whichever permits the smaller variance;
3. unauthorized freight, handling, tax, deposit, or miscellaneous charges equal **$0**; and
4. invoice currency and unit of measure agree with the PO.

Any variance outside these tolerances creates an IER. Tolerance permits automation; it does not authorize a vendor to change negotiated pricing.

If receipt quantity is lower than invoiced quantity, Northstar pays only the validated payable quantity unless DC Operations corrects the receipt or Procurement authorizes another commercial resolution.

### 6.3 Invoice status

VendorLink uses these statuses:

- **Received** — structurally accepted by VendorLink;
- **Validation Failed** — required fields/structure failed;
- **Match Pending** — awaiting receipt or matching data;
- **Exception Review** — IER open;
- **Approved for Payment** — validation and required approvals complete;
- **Scheduled** — approved and assigned to a payment run;
- **Paid** — Northstar issued payment;
- **Rejected** — invoice cannot be processed as submitted;
- **Void** — Northstar administratively canceled an unpaid invoice record with audit history preserved.

### 6.4 Invoice Eligible Date and payment term

Unless a signed agreement or PO states a different term, Northstar's default merchandise payment term is **Net 30**.

For DC merchandise, the Invoice Eligible Date is the **later of**:

- the date Northstar receives a structurally valid invoice; or
- the Northstar Receipt Date for the merchandise covered by the invoice.

For Northstar-Managed Pickup, pickup alone does not start the AP payment clock unless the commercial agreement expressly says otherwise. For DSD or non-DC transactions, VendorLink uses the applicable accepted delivery/service-completion record.

An IER caused by vendor data can pause payment approval until corrected, but Northstar must preserve the original valid-invoice receipt timestamp. AP may reset the IED only when the original submission was not a valid invoice or the vendor materially changes the amount, vendor identity, currency, or commercial basis.

## 7. Exceptions and escalation

### 7.1 Invoice Exception Record

An IER identifies:

- invoice and PO;
- exception category;
- disputed fields/values;
- evidence reviewed;
- responsible Northstar owner;
- vendor response if required;
- disposition; and
- timestamps.

Vendor responses requested through an IER are normally due within **5 business days**. If no response is received after 10 business days, AP may reject the invoice or pay the undisputed validated amount, depending on the exception.

Price/term disputes are owned by Procurement. Receipt quantity disputes are owned by DC Operations. Freight/routing disputes are owned by Logistics. Tax/banking/payment-control issues are owned by AP/Finance. Safety/quality holds are owned by Q&R.

### 7.2 System outage exception

When VendorLink or an approved Northstar connection is unavailable for more than **2 consecutive hours** during a time-sensitive transaction window, Vendor Compliance or IT may authorize a temporary alternate method. The vendor must later backfill the authoritative electronic record within **1 business day after service restoration**.

A vendor-side outage does not automatically waive transaction deadlines. Vendor Compliance and the owning function determine whether evidence supports an exception.

### 7.3 Bank-account changes

Banking instructions are controlled vendor-master data. A bank change must be submitted through the secure VendorLink workflow before the requested effective date and requires independent AP verification using a previously established contact method or other approved fraud-control procedure.

No bank change is effective solely because of an email, invoice note, phone call from an unverified number, or altered remittance instruction attached to an invoice. AP may place the NVID on **Payment Hold** while verification is incomplete. Payment Hold does not by itself change the vendor's Active/Restricted/Suspended status.

## 8. Non-compliance

Examples include late/missing ASN, duplicate invoices, repeated invalid fields, invoicing unreceived quantities, unauthorized charges, repeated channel failures, false receipt references, or attempts to redirect payment through unverified bank-change instructions.

Three vendor-controlled electronic transaction failures of the same material type within a rolling **60-day** period trigger a Vendor Compliance review. A deliberate duplicate-billing scheme, knowingly false invoice, falsified receipt reference, or fraudulent payment-redirection attempt may trigger immediate payment hold, vendor-status review, and investigation.

Dollar deductions, chargebacks, recovery amounts, and formal appeals are governed by `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md`.

## 9. Records and evidence

POs, acknowledgments, ASNs, invoices, credit memos, IERs, remittance advice, payment-status history, bank-change verification evidence, and transaction audit logs are retained for **7 years after final payment or final resolution**, unless another Northstar policy or applicable legal requirement requires longer.

VendorLink must preserve the submitted value, corrected value, identity of the actor or system, timestamp, channel, and disposition for controlled transaction changes. A corrected record must not silently overwrite the audit history of the prior record.

## 10. Examples / scenarios

### Scenario A — duplicate invoice

Vendor A transmits invoice `INV-7841`, which Northstar accepts. The vendor resends the same NVID and invoice number the next day because payment status is not yet visible. VendorLink rejects the second submission as a duplicate. The original invoice remains the only payable record.

### Scenario B — invoice quantity exceeds receipt

A PO line authorizes 1,000 cases. Northstar receives and accepts 960. The vendor invoices 1,000. The line enters Exception Review; AP cannot automatically pay 1,000. DC Operations must correct the receipt evidence or the invoice must be corrected to the validated quantity.

### Scenario C — late ASN but timely delivery

A prepaid shipment arrives inside its valid DockSchedule window but its ASN was transmitted only 30 minutes before arrival when transit exceeded four hours. Receiving timeliness under file 01 may still pass because Gate Arrival Time was compliant, but the shipment has a separate electronic-transaction non-compliance event under this file.

### Scenario D — attempted bank change by email

An accounts-receivable employee emails new ACH instructions and asks AP to redirect a scheduled payment. AP does not change banking data from the email. The NVID is placed on Payment Hold until the secure VendorLink request and independent verification are complete.

## 11. Related Northstar policies

- `00_COMPANY_AND_VENDOR_OVERVIEW.md` — NVID, vendor status, master-data controls, banking setup.
- `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md` — PO authority, revisions, acknowledgments, OTIF calculations.
- `04_PACKAGING_AND_LABELING.md` — GTIN, SSCC, packaging hierarchy.
- `05_IMPORT_REQUIREMENTS.md` — ICR/SIP import records.
- `06_QUALITY_AND_COMPLIANCE.md` — technical acceptance of Q&R records and holds.
- `07_DISTRIBUTION_CENTER_RECEIVING.md` — receipt quantity, Gate Arrival, Receiving Dispositions.
- `08_TRANSPORTATION.md` — SRR, BOL, routing and carrier records.
- `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md` — deductions, chargebacks, credits, recovery, formal appeals.

## Reference basis

Northstar Regional Markets is fictional and is not affiliated with the organizations below. These sources were consulted for process concepts only.

- **Dollar Tree, Inc. — Merchandise Vendors**  
  https://corporate.dollartree.com/vendor-real-estate-partners/merchandise-vendors  
  Influenced the requirement that merchandise suppliers exchange purchase orders and invoices electronically through either a portal or an approved EDI connection, with connectivity testing before production use.

- **Dollar Tree, Inc. — Supplies & Services / Ariba Training Center**  
  https://corporate.dollartree.com/vendor-real-estate-partners/supplies-services  
  https://corporate.dollartree.com/vendor-real-estate-partners/supplies-services/ariba-training-center  
  Influenced electronic PO/invoice validation, supplier visibility, standardized transaction workflows, and portal-versus-integrated-channel concepts.

- **US Foods — Supplier Information**  
  https://www.usfoods.com/for-investors-media-and-suppliers/supplier-info  
  Influenced supplier self-service for invoice submission, documentation, claims, and invoice/payment management.

- **Sysco — Supplier Resources**  
  https://sysco.com/en-us/suppliers/supplier-partnerships/supplier-resources  
  Influenced supplier-portal visibility into purchase orders, invoice status, payments, supporting evidence, and inquiries.

- **UNFI — Supplier Terms & Conditions (last updated July 30, 2026)**  
  https://www.unfi.com/supplier-terms.html  
  Influenced the structure of invoice timing relative to receipt, PO-controlled commercial terms, deductions/setoff concepts, and the distinction between an invoice and an authorized change to the purchase order.
