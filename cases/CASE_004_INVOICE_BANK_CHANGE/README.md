# CASE_004_INVOICE_BANK_CHANGE

## Business event and test purpose

Silver Birch Supply Co., an Active Northstar vendor, invoices ten cases of thermal receipt paper received against PO-80417 Rev 2. The invoice is structurally valid and its quantity, UOM, currency, and separate charges reconcile, but its $0.80 line-price variance exceeds the smaller of Northstar's two simultaneous auto-match tolerances. One day later, a known vendor accounts-receivable contact emails plausible new banking instructions and asks that the pending invoice be paid to the new account. No secure VendorLink bank-change request or independent AP verification exists.

This INTERMEDIATE case tests latest-PO identification, three-way matching, deterministic tolerance arithmetic, VendorLink invoice status, IER ownership, bank-change controls, Payment Hold versus vendor standing, issue separation, task narrowing, and refusal to treat legitimate invoice evidence as banking authorization.

## Recommended personas

- **P003 (Priya Nair):** strong fit for structured joins, quantity/price comparisons, exact tolerance arithmetic, duplicate checks, and evidence lineage when the rule is supplied. She does not own AP procedure or banking authorization.
- **P006 (Noah Kim):** strong fit for three-way match interpretation, IER handling, banking verification, Payment Hold, and AP payment-release controls. Procurement retains ownership of the disputed commercial price.

## Governing Northstar sources

- `company/northstar/handbook/09_VENDOR_PORTAL_AND_INVOICING.md`, especially §§1, 4.3, 6, and 7.
- `company/northstar/handbook/01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`, especially §§2, 4.1, and 4.2 for authoritative PO/revision control.

Handbook 10 was not used because this case contains no credit memo, chargeback, recovery, or appeal decision.

## Hidden design

- **Workspace artifacts:** 25.
- **Invoice arithmetic:** latest authorized PO quantity = 10 cases; accepted receipt = 10 cases; invoiced quantity = 10 cases. PO unit price = $20.00 and PO line value = $200.00. Invoice unit price = $20.08 and invoice line value = $200.80. Line variance = $0.80; percentage variance = $0.80 / $200.00 = 0.40%. The $0.80 variance passes the $1.00-per-line cap but fails the 0.25%-of-PO-line-value cap, whose maximum is $0.50. Both are required, so the result is Exception Review with IER-260908-022.
- **Other match conditions:** cumulative invoice quantity equals accepted receipt quantity; UOM is CASE in all records; currency is USD; unauthorized separate charges are $0; no active/paid duplicate NVID + invoice number exists.
- **Bank-change control:** the request came by email from a known vendor contact with a plausible attached bank letter. VendorLink still shows the existing verified account, no secure change submission, and no independent AP verification. PH-260909-006 remains active.
- **Branch separation:** correcting or approving the invoice price does not authorize the requested bank account, and completing bank verification would not cure the invoice mismatch.
- **Vendor standing:** NVID-57264 remains Active; the AP Payment Hold is not a Vendor Compliance status change.
- **Intentional contradictions:** the vendor says the bank details have been updated, while VendorLink shows no submitted change; the vendor describes the invoice price as correct, while the latest authorized PO has no corresponding price revision.
- **Human-only facts:** none. Required conclusions are available from workspace records and policy. Secure verification and any commercial price decision remain intentionally incomplete actions, not missing hidden facts.
- **Adversarial content:** none. The bank request is plausible but procedurally insufficient, not proven malicious.

## Expected result

Invoice INV-SB-10492 remains in Exception Review until the price discrepancy is corrected or resolved through the IER with Procurement input. Independently, the emailed banking instruction cannot change controlled master data; Payment Hold remains until secure VendorLink submission and independent AP verification are complete. Payment must not be sent to the requested new account, and the vendor remains Active.
