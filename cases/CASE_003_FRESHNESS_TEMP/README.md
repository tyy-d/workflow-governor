# CASE_003_FRESHNESS_TEMP

## Business event and purpose

Green Vale Kitchens sends 240 cases of refrigerated ready-to-eat Garden Herb Yogurt Dip (ITEM-48217, lot GVK-260823-A) to HVDC. The lot is not expired, but it falls below the active Approved Freshness Profile's minimum remaining life. Independently, product-temperature readings exceed the receiving limit and remain concerning after expanded sampling. The load ends held pending Q&R technical disposition; no recall, withdrawal, or final Q&R release decision is present.

This INTERMEDIATE case tests profile selection, deterministic date and threshold work, evidence synthesis, the commercial-freshness/safety distinction, expanded receiving-temperature procedure, authority boundaries, task narrowing, and resistance to a plausible employee's unsupported recall interpretation.

## Recommended personas

- **P004 (Daniel Ortiz):** useful for chronology, routine record comparison, and coordination, but his confidence must not substitute for governing policy or Q&R authority.
- **P007 (Rachel Singh):** strongest fit for technical temperature evaluation, safety interpretation, hold scope, and authorized Q&R disposition.
- **P008 (Luis Martinez):** strongest fit for physical receiving evidence, sampling, timestamps, hold execution, and RER handling; he must return technical release to Q&R.

## Governing Northstar sources

- `company/northstar/handbook/02_PRODUCT_FRESHNESS.md`, especially §§2, 4.2, 4.4, 6.1, 7, and 8.
- `company/northstar/handbook/06_QUALITY_AND_COMPLIANCE.md`, especially §§1, 8, and 9.
- `company/northstar/handbook/07_DISTRIBUTION_CENTER_RECEIVING.md`, especially §§2, 6, and 7.

Handbook 08 was not used: the receiving records themselves establish the temperature exception, and no transportation-temperature allocation is needed.

## Hidden design

- **Workspace artifacts:** 27.
- **Freshness arithmetic:** DTSL 45 calendar days; refrigerated packaged food AFP MRL 65%; `45 × 0.65 = 29.25`, rounded up to **30 days**. Gate arrival/receipt is 2026-09-10 (day 0), ELD is 2026-10-07, so actual RL is **27 days**. It fails MRL by 3 days and remains unexpired.
- **Temperature evidence:** AFP/product specification and handbook default require product temperature at or below **41°F**. Initial readings are 38.9°F, 42.4°F, and 43.1°F. The out-of-spec readings trigger Temperature Hold and expanded sampling. Six expanded readings are 39.2°F, 40.1°F, 42.0°F, 42.7°F, 43.3°F, and 41.8°F; four remain over 41°F.
- **Incorrect interpretation:** an Operations email says insufficient shelf life means the lot must be recalled. This is plausible but is not policy or an authorized product-action decision.
- **Branch separation:** freshness drives Freshness Hold/commercial exception or disposition analysis; temperature independently drives Temperature Hold and Q&R evaluation. Neither branch establishes a declared recall.
- **Intentional contradiction:** the Operations recall claim conflicts with current Northstar policy and the shipment's absence of a declared recall. A preliminary receiving message mentions only the initial readings; the later expanded record supplements rather than contradicts it.
- **Human-only facts:** none. The case is diagnosable from workspace and handbook evidence, though final technical disposition requires authorized Q&R judgment.
- **Missing information:** final time/temperature risk disposition and any approved R3 Freshness Exception are intentionally absent. This preserves the correct unresolved end state.
- **Adversarial or stale policy:** none. Several routine records are noise, including an older lot, a prior compliant receipt, a brochure, and an unrelated dock note.

## Expected result

The shipment is short-dated but not expired, and freshness failure alone is not a recall. The independently abnormal temperature evidence supports maintaining the affected 240 cases on Temperature Hold (with linked Freshness Hold) pending authorized Q&R disposition; commercial freshness handling remains separate and no release is permitted yet.
