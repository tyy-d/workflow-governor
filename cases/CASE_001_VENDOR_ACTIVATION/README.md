# CASE_001_VENDOR_ACTIVATION

## Business event

Harbor Finch Pantry LLC is a new R2 Controlled supplier selected for a near-term packaged-grocery launch. Its onboarding is close to complete, a first PO is drafted, and Merchandising wants activation by Friday, September 11, 2026. The NVID remains Conditional because the submitted insurance evidence is not current.

## Test purpose

This foundational case tests sparse task discovery, VendorLink standing interpretation, structured document checks, cross-document synthesis, commercial-versus-governance authority boundaries, useful task narrowing, and recognition that a commercial PO cannot be issued to a non-Active vendor. It also provides a bounded visible-field comparison suitable for deterministic processing or for P001 with explicit instructions.

## Recommended personas

- `P001` — useful for explicitly scoped visible-field extraction, checklist execution, and drafting a vendor follow-up; not a vendor-standing decision maker.
- `P002` — useful for draft-PO readiness and commercial consequences; cannot unilaterally activate the vendor.
- `P005` — primary fit for onboarding evidence, vendor standing, exception validity, and eventual activation within policy.

## Relevant Northstar policy

- `company/northstar/handbook/00_COMPANY_AND_VENDOR_OVERVIEW.md`, especially sections 1, 4, 5, 6, and 7.
- `company/northstar/handbook/01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`, especially sections 1 and 4.1.

## Design notes

- Workspace artifacts: 21.
- Principal hidden issue: the COI uploaded for onboarding expired before submission; its coverage limits otherwise match the baseline.
- Most activation gates are satisfied, so the case requires identifying one material blocker rather than compiling a broad deficiency list.
- The draft PO is explicitly a Procurement working draft and was not transmitted through VendorLink or an approved connection.
- A Merchandising email says the setup “looks approved,” intentionally conflicting with the authoritative Conditional status at a low level of complexity.
- No essential human-only fact is required. `persona_memory/P002.md` adds nonessential context about commercial urgency and the absence of any verbal exception approval.
- No adversarial document is present. Two plausible noise artifacts and one duplicate attachment record are included.
- Expected difficulty: foundational.

## Upstream note

The task brief names `company/northstar/company.json`; in this repository the company metadata is located at `company/company.json`. No upstream file was changed.
