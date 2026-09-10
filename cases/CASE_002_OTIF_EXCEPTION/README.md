# CASE_002_OTIF_EXCEPTION

## Business event

Bright Meadow Foods ships shelf-stable soup against PO 78214 to HVDC. An authorized revision increases the order from 800 to 1,000 units and moves the Ready By and delivery dates. The vendor acknowledges the revision, later tenders only 900 compliant units, and Northstar's designated carrier suffers a tractor failure that causes pickup and receipt delays. The vendor seeks removal of the entire OTIF miss.

## Test purpose

This foundational/intermediate case tests latest-authorized-revision recognition, acknowledgment interpretation, deterministic Net Ordered Units and performance calculations, event-timeline reconstruction, managed-pickup responsibility, exception evidence, and separation of excusable timing from a vendor-controlled shortage. It resists both “the vendor caused everything” and “the carrier excuses everything.”

## Recommended personas

- `P002` — strong fit for PO/revision authority, OTIF policy, vendor responsibility, and the Procurement recommendation; must preserve Logistics approval authority for a managed-transportation PER.
- `P003` — strong fit for version comparison, joins, timeline construction, and reproducible arithmetic once the governing rules are supplied; not an independent policy interpreter or approver.
- `P008` — strong fit for SRR, Ready By, carrier, gate, and receiving evidence; not the owner of Procurement's final commercial interpretation or Logistics Manager approval.

## Relevant Northstar policy

- `company/northstar/handbook/01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`, especially sections 4.1–4.4, 6.1–6.3, and 7.
- `company/northstar/handbook/08_TRANSPORTATION.md`, especially sections 4.1–4.5, 7, 9, and 10.
- `company/northstar/handbook/07_DISTRIBUTION_CENTER_RECEIVING.md`, especially sections 2, 4, 5.3, and 9.

Handbook 10 was not needed because this case ends at performance-exception disposition and does not assert a chargeback.

## Design notes

- Workspace artifacts: 25.
- Latest authorized order: Rev 2, 1,000 units; there are no eligible Northstar cancellations.
- Vendor performance: 900 compliant units ready by the controlling Ready By deadline and 900 accepted by final close. Correct On-Time Unit Rate is 90.0%; Fill Rate is 90.0%; both fail the 98.0% PO thresholds, so the PO fails OTIF.
- Quantitative trap: using superseded Rev 1's 800-unit denominator caps both numerators at 800 and falsely produces 100.0% On-Time and 100.0% Fill, an OTIF Pass.
- Mixed responsibility: the Northstar-selected carrier's tractor failure explains the late physical receipt and supports a managed-transportation correction/exclusion, but it does not excuse the vendor's 100-unit shortage.
- The preliminary score export intentionally uses destination arrival as the timeliness event and shows 0.0% On-Time. Correct managed-pickup treatment replaces that with the 900 units credibly ready on time; it does not turn the shortage into an exception.
- The vendor's request is timely and plausible but overbroad. No PER approval is present; the Logistics Manager remains the policy-named minimum approver for the transportation portion.
- No required human-only facts exist, and no persona-memory files are created. The core result is fully discoverable from workspace evidence plus policy.
- Intentional contradictions include Rev 1 versus Rev 2 terms, a copied-forward Rev 1 planning row, scheduled versus actual carrier milestones, and the vendor's total-waiver claim versus the quantity records.
- Noise is limited to one prior shipment record and one unrelated carrier status message.
- Difficulty: `INTERMEDIATE` (also suitable as a foundational mixed-responsibility test).

## Policy adaptation

Northstar measures a managed-pickup vendor at Ready By, not at DC arrival. Accordingly, the raw correct On-Time Unit Rate is 900/1,000 rather than treating all units as late at destination. The carrier delay is still material because it caused the preliminary arrival-based misclassification and is the valid scope of the PER review.

## Upstream audit

The requested source set was internally compatible. No upstream file was changed.
