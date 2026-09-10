# Transportation

## 1. Purpose and scope

This section governs inbound transportation to Northstar distribution centers and, where applicable, Direct-Store-Delivery (DSD) locations. It applies to vendors, shippers, brokers, carriers, and transportation providers acting for a vendor or Northstar.

It covers Vendor-Prepaid freight, Northstar-Managed Pickup, DSD, and the domestic leg of Northstar Direct Import (NDI) after lawful U.S. release. Import admissibility remains governed by `05_IMPORT_REQUIREMENTS.md`.

Northstar Logistics owns routing, carrier assignment, and transportation operating standards. Distribution Center Operations owns physical receiving evidence under `07_DISTRIBUTION_CENTER_RECEIVING.md`. Quality & Regulatory (Q&R) controls food-safety, temperature, sanitation, and product-safety disposition. Vendor Compliance coordinates recurring transportation non-compliance and corrective action.

This section does not change the freight-responsibility or OTIF formulas in `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md`.

## 2. Definitions

| Term | Northstar meaning |
|---|---|
| **Vendor-Prepaid** | Vendor controls and pays for transportation to the Northstar destination unless commercial terms state otherwise. |
| **Northstar-Managed Pickup** | Northstar or its designated provider selects and controls the carrier after the vendor makes conforming freight available by the PO Ready By requirement. |
| **Shipment Routing Record (SRR)** | VendorLink record containing routing request data, freight term, origin, equipment needs, carrier assignment, pickup details, temperature/security instructions, and linked transportation evidence. |
| **Ready By Time** | PO-controlled time by which Northstar-managed freight must be completely staged, conforming, documented, and available for pickup. |
| **Transportation Incident** | In-transit event that may materially affect timing, safety, security, temperature control, shipment identity, or cargo condition. |
| **Seal Event** | Application, removal, breakage, replacement, or unexplained change of a trailer/container seal. |

The SRR does not replace a PO, ASN, DockSchedule appointment, APLR, AFP, ICR, QVP, or private-label technical release.

## 3. Vendor and carrier responsibilities

Vendors remain responsible for transportation agents they select for Vendor-Prepaid or DSD freight.

Vendors and carriers must:

1. use transportation providers legally authorized for the service being performed;
2. comply with applicable vehicle, driver, hours-of-service, weight, cargo-securement, hazardous-materials, food-transportation, and safety laws;
3. never request or permit a driver to violate law in order to meet a Northstar schedule;
4. provide accurate shipment weight, pallet/carton count, equipment, temperature, hazardous-material, and pickup-location data;
5. follow Northstar routing instructions for Northstar-Managed Pickup freight;
6. protect freight from contamination, theft, weather, shifting, crushing, and other reasonably preventable damage;
7. preserve temperature, seal, status, and incident evidence when required; and
8. immediately stop movement when a legal authority orders the vehicle or shipment out of service.

A Northstar-contracted motor carrier must maintain the existing **$1,000,000 combined single-limit auto liability** and **$150,000 cargo liability per occurrence**, unless contract terms require more. High-value loads may require declared-value coverage.

A carrier or broker subject to a government order prohibiting operation may not transport Northstar-controlled freight.

## 4. Northstar transportation process

### 4.1 Freight-term determination

The active PO and authorized revision control whether a shipment is Vendor-Prepaid, Northstar-Managed Pickup, or another specifically approved term. A vendor may not change freight term because a preferred carrier is unavailable.

If freight term is wrong or ambiguous, the vendor must request a PO correction before tendering freight. Shipment movement does not itself modify the PO.

### 4.2 Northstar-Managed Pickup routing request

For Northstar-Managed Pickup, the vendor must submit a complete SRR routing request:

| Shipment type | Minimum complete-request lead time before Ready By Time |
|---|---:|
| Standard dry LTL | 2 Northstar business days |
| Dry truckload | 3 Northstar business days |
| Refrigerated/frozen truckload | 3 Northstar business days |
| Regulated hazardous-material load | 3 Northstar business days |
| NDI domestic handoff requiring Northstar routing | 3 Northstar business days after expected lawful release is reasonably known |

A late request does not change Ready By. Logistics may route when capacity exists, or the vendor may request a PER under file `01`. Northstar-Managed freight may not be tendered to a substitute carrier without written Logistics approval.

### 4.3 Required routing data

A complete SRR must contain, as applicable:

- NVID and ship-from facility;
- PO number and active revision;
- destination;
- Ready By date/time and origin operating hours;
- pallet, carton, weight, and cube estimates;
- floor-load or palletized status;
- required equipment type;
- temperature specification and pre-cooling requirement;
- hazardous-material status and legally required transport description;
- pickup contact and after-hours contact;
- special handling or security requirement;
- import-release dependency when applicable.

A change in equipment type, hazardous-material status, temperature requirement, pickup address, or ship date must be reported before carrier dispatch when known. A change of more than **10%** in expected gross shipment weight or pallet/carton count must also be updated before pickup when known.

### 4.4 Pickup readiness

For Northstar-Managed Pickup, compliant readiness means the ordered freight is at the correct origin and, by Ready By Time:

- produced/released for shipment;
- packed and labeled to the active APLR;
- segregated from non-Northstar freight sufficiently for accurate pickup;
- supported by required shipping and quality documents;
- staged so normal loading can begin without production or repacking work;
- available during the confirmed pickup window; and
- supported by credible readiness evidence.

Credible readiness evidence includes warehouse timestamps, staged-freight records/photos, loader records, or contemporaneous carrier communication. Q&R release requirements remain controlling.

A late Northstar-designated carrier does not make the vendor late when timely readiness is credibly shown. Carrier arrival does not cure freight that was not actually ready.

### 4.5 Bill of lading

Every Northstar DC shipment must have a bill of lading or legally equivalent shipping document containing, as applicable:

- shipper and origin;
- consignee and destination;
- carrier and trailer/container number;
- freight term;
- PO number;
- SRR identifier for Northstar-Managed Pickup;
- pallet/carton count and gross weight;
- item/SKU detail sufficient to identify the load;
- seal number when a seal is required;
- temperature operating instruction for controlled loads; and
- hazardous-material description and emergency information when legally required.

Detailed ASN transmission belongs to `09_VENDOR_PORTAL_AND_INVOICING.md`.

## 5. Vehicle sanitation, loading, and cargo security

Food transportation equipment must be suitable and maintained so it does not create an unsafe condition. Food trailers must be clean, dry when appropriate, free of objectionable odor/pest evidence, structurally sound, and free from contaminating residue or prior cargo.

Where prior cargo, cleaning, or sanitation history is necessary to determine suitability—particularly for bulk or higher-risk food transportation—the vendor/carrier must provide that information when requested by Q&R or Logistics.

Food must not be co-loaded with incompatible chemicals, waste, live animals, or other material that could reasonably contaminate or taint it unless an approved physical segregation method makes the combination acceptable and lawful.

The loading party must use blocking, bracing, dunnage, load bars, straps, or other appropriate means to prevent cargo movement and damage. Applicable FMCSA cargo-securement requirements always control.

### 5.1 Seal control

All closed **truckload** shipments to a Northstar DC must be sealed at origin unless the transportation mode requires intermediate access. LTL and authorized multi-stop loads may use documented chain-of-custody controls instead.

For R3 food, private-label safety-sensitive product, or other Q&R-designated secure loads, every Seal Event must be traceable. If a seal is removed in transit, records must identify:

- prior seal number;
- reason for removal;
- date/time and location;
- person or authority removing it; and
- replacement seal number, if any.

An unexplained seal break, mismatch, or undocumented replacement on an R3/safety-sensitive load is a Transportation Incident and will normally cause a receiving hold under file `07`.

## 6. Temperature-controlled transportation

The AFP, QVP, product specification, or written Q&R instruction controls the required transportation temperature. Northstar receiving fallback thresholds in file `07` are not substitute transit setpoints.

Before loading R3 refrigerated or frozen food, the mechanically refrigerated compartment must be pre-cooled to the specified operating condition unless the applicable product instruction expressly states otherwise.

Unless Q&R or the applicable shipping specification authorizes another operating method, R3 refrigerated/frozen truckload transportation uses **continuous refrigeration operation** while product is in transit.

For R3 temperature-controlled truckloads, electronic temperature evidence must record at intervals no greater than **15 minutes** when equipment is capable. A shipper-provided recorder may not be removed, disabled, reset, or intentionally shielded.

When Logistics or Q&R requests a reefer download or equivalent temperature record, the carrier/vendor must provide it within **4 business hours** unless an emergency or technical limitation is documented.

A known temperature excursion, refrigeration-unit failure, accidental shutdown, or suspected logger tampering must be reported to Logistics and Q&R within **1 hour of discovery**. Final product disposition remains with Q&R and file `07` receiving evidence.

## 7. In-transit events and escalation

The carrier or responsible vendor must notify Logistics:

- within **1 hour** of a collision, theft, hijacking attempt, unexplained seal breach, temperature-control failure, contamination concern, government impoundment, or cargo-spill event affecting Northstar freight; and
- within **2 hours** after learning of another event reasonably expected to delay pickup or delivery by more than **2 hours**.

Initial notice should identify the load, location, event, known cargo condition, expected delay, and containment/recovery action. Supporting evidence belongs in the SRR within 1 business day when available.

For Vendor-Prepaid freight, credible evidence of a carrier-controlled delay may support a PER request but does not automatically exclude the event from vendor performance. For Northstar-Managed Pickup, Northstar-carrier delay after documented vendor readiness is handled under the responsibility split in file `01`.

Emergency routing instructions may be given verbally by Logistics when delay would materially worsen a safety or service event, but they must be documented in VendorLink within 1 business day.

## 8. Transportation performance and non-compliance

Northstar may maintain a separate scorecard for carriers it directly tenders freight to. The carrier scorecard does not alter vendor OTIF.

| Measure | Northstar standard |
|---|---:|
| Tender acceptance against committed capacity | >=94% |
| On-time pickup against confirmed pickup window | >=95% |
| Required milestone/status reporting | >=97% |
| Required temperature-record availability for controlled loads | 100% |

Two consecutive measured months below a standard, or any Critical Transportation Event, triggers Logistics review. With fewer than 10 eligible loads, percentages are informational unless an event is Critical.

**Critical Transportation Events** include intentional temperature-record tampering, knowingly using an unsafe/prohibited vehicle, falsified custody/status, serious undeclared hazardous-material transport, or re-brokering that materially defeats safety/security controls.

**Major Transportation Events** include unauthorized equipment substitution, missing required seal, repeated routing-data error, unapproved routing departure, or vendor-caused loading delay greater than 90 minutes after a conforming carrier arrives.

Three Major Transportation Events attributable to the same vendor/carrier within a rolling 60 days trigger corrective-action review. If Q&R classifies the event as a quality finding, file `06_QUALITY_AND_COMPLIANCE.md` CAP timing controls. Otherwise, a requested transportation CAP is due within 10 Northstar business days.

Dollar chargebacks, freight-cost recovery, detention/demurrage recovery, cargo claims, and appeals are governed by `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md`.

## 9. Exceptions and approval

| Exception | Minimum Northstar approval |
|---|---|
| Alternate routing, mode, pickup window, or equipment with no safety effect | Logistics Manager |
| Recurring vendor routing-process exception | Logistics Manager + Vendor Compliance Manager |
| Temperature, sanitation, food-safety, or safety-sensitive seal exception | Director, Quality & Regulatory |
| NDI port/intermodal/domestic handoff change | Logistics Manager + Import Compliance Lead |
| Emergency same-day operational deviation | Logistics Manager; written record within 1 business day |

No Northstar employee may authorize an exception that waives law, directs a driver to exceed legal hours/weight limits, permits knowingly unsafe food transportation, bypasses a government hold, falsifies shipping papers, conceals a hazardous material, or overrides a Q&R safety hold.

## 10. Records and evidence

Completed-shipment evidence should allow Northstar to reconstruct:

- controlling PO/freight term;
- SRR and routing request;
- carrier assignment/tender;
- Ready By evidence when Northstar-Managed;
- BOL;
- pickup and delivery milestones;
- DockSchedule appointment and Gate Arrival Time;
- seal history where required;
- temperature records where required;
- sanitation/previous-cargo evidence when requested;
- Transportation Incident notices;
- linked PER/RER/Q&R records; and
- final claim or corrective-action record if applicable.

Transportation records are retained **7 years after final delivery or later claim/incident closure**, unless a longer rule applies.

## 11. Examples / scenarios

**Scenario 1 — Collect freight ready, Northstar carrier late.**  
A frozen-food vendor completes the SRR three business days before Ready By and produces warehouse timestamps showing the load staged and released at 08:00. Northstar's assigned carrier does not arrive until 13:30. The vendor is not considered late merely because of the carrier delay, provided readiness evidence is credible; file `01` responsibility logic controls.

**Scenario 2 — Reefer excursion.**  
A carrier discovers its refrigeration unit stopped for 35 minutes. It restarts the unit but does not notify Northstar because the displayed air temperature returns to setpoint. This violates Northstar policy. Recovery of the setpoint does not erase the excursion; Logistics/Q&R must receive notice and the temperature evidence must be preserved for disposition.

**Scenario 3 — Seal changed at inspection.**  
A law-enforcement inspection requires a sealed R3 load to be opened. The carrier records the old seal, time/location, inspecting authority, and replacement seal. The receiving team may still inspect the event, but there is a documented chain of custody rather than an unexplained seal mismatch.

**Scenario 4 — Vendor uses its own carrier on Northstar-Managed Pickup.**  
A vendor cannot obtain a Northstar routing confirmation in time and sends the load on its preferred LTL carrier without approval. Even if the load arrives on time, the unauthorized routing is a transportation process failure; the PO freight term did not change.

## 12. Related Northstar policies

- `01_PURCHASE_ORDERS_AND_DELIVERY_PERFORMANCE.md` — freight responsibility, Ready By performance, OTIF, PER.
- `02_PRODUCT_FRESHNESS.md` — shelf-life and remaining-life calculations.
- `04_PACKAGING_AND_LABELING.md` — pallet/case identification, SSCC, pack configuration.
- `05_IMPORT_REQUIREMENTS.md` — NDI/VLI and import-release controls.
- `06_QUALITY_AND_COMPLIANCE.md` — Q&R findings, testing, CAP, safety authority.
- `07_DISTRIBUTION_CENTER_RECEIVING.md` — DockSchedule, Gate Arrival, physical inspection, temperature holds.
- `09_VENDOR_PORTAL_AND_INVOICING.md` — ASN and electronic transaction mechanics.
- `10_RETURNS_RECALLS_CHARGEBACKS_AND_APPEALS.md` — claims, freight cost recovery, deductions, appeals.

## Reference basis

- **Family Dollar / Dollar Tree — Vendor Resources; Part 9 Transportation Guidelines.**  
  https://corporate.familydollar.com/vendor-resources  
  https://corporate.dollartree.com/_assets/_39d1c3acf241280d452921a9e95f7d6b/dollartreeinfo/db/1137/9043/file/FD_Vendor_Guide_Part_9_Transportation_Requirements.pdf  
  Influenced the separation of prepaid/collect freight, routing release, appointments, BOL data, blocking/bracing, seal control, and DSD transportation structure.

- **Dollar Tree — Logistics / Custom Vendor Portal and C3 Reservations.**  
  https://corporate.dollartree.com/vendor-real-estate-partners/logistics  
  Influenced the use of structured shipment-release data followed by separate appointment coordination.

- **U.S. Food and Drug Administration — FSMA Final Rule on Sanitary Transportation of Human and Animal Food; FSMA FAQs.**  
  https://www.fda.gov/food/food-safety-modernization-act-fsma/fsma-final-rule-sanitary-transportation-human-and-animal-food  
  https://www.fda.gov/food/food-safety-modernization-act-fsma/frequently-asked-questions-fsma  
  Influenced sanitation, shipper/carrier responsibility, written temperature specifications, cleaning/previous-cargo evidence, carrier training concepts, and temperature-control records.

- **Sysco — Quality Assurance / Carrier Operational Guidelines.**  
  https://sysco.com/en-us/products/products/quality-assurance  
  Influenced food-transport sanitation, reefer monitoring, seal chain-of-custody, carrier status reporting, and carrier-performance concepts.

- **Federal Motor Carrier Safety Administration — Cargo Securement Rules; Hazardous Materials Compliance.**  
  https://www.fmcsa.dot.gov/regulations/cargo-securement/cargo-securement-rules  
  https://www.fmcsa.dot.gov/regulations/hazardous-materials/how-comply-federal-hazardous-materials-regulations  
  Influenced the legal boundary for cargo securement, shipping papers, placarding, vehicle suitability, and hazardous-material carrier responsibilities.

Northstar Regional Markets is fictional and is not affiliated with any referenced organization. All Northstar-specific system names, thresholds, score standards, approval matrices, forms, deadlines, and examples above are original fictional policy.
