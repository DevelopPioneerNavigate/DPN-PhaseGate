# PG-01 // Illustrated engineering blueprints

**[← Visual Atlas](../VISUAL-ATLAS.md)** · [Full architecture](PG-01-architecture.md) · [Engineering requirements](requirements.md) · [Implementation plan](PG01-IMPLEMENTATION-PLAN.md)

> **Blueprint status — concept only.** The drawings describe low-voltage scientific instrumentation. They are **not** fabrication-ready: physical dimensions, tolerances, camera mounting, controller/power choice and qualified safety review remain unresolved. **No physical teleportation mechanism has been proposed or demonstrated.**

## 01 · Front elevation — what each part does

<img src="../../assets/pg01-blueprint-front.svg" width="100%" alt="Concept front elevation showing independent sample platform, camera view and local logger"/>

| Callout | Component | Purpose | Needed before building |
|---|---|---|---|
| A1 | Inspectable enclosure | Prevent hidden normal transit or unnoticed substitutions | Approved size, material, inspection access |
| A2 | Camera + independent witness view | Continuous optical record of sample area | Field-of-view, timestamp uncertainty |
| A3 | Load-cell platform | Track measured mass with uncertainty | Load range, safe mount, calibrated references |
| A4 | Sensor ADC | Digitize the low-level sensor signal | Logic level, noise, settling and rate |
| A5 | Local logger | Capture original UTC/monotonic timestamps | Hardware decision, data schema |
| A6 | Rated low-voltage supply | Power electronics safely | Voltage/current budget and protection |

## 02 · Top view — how the two stations relate

<img src="../../assets/pg01-blueprint-top.svg" width="100%" alt="Two separate inspection enclosures connected only by logging data"/>

**A and B must remain independently inspectable.** Dashed connections indicate digital logging/network links, **not a physical object-transfer pathway**. Actual physical separation, doors, cameras, and wiring positions are design decisions to record before physical work.

## 03 · Measurement architecture

<img src="../../assets/pg01-system.svg" width="100%" alt="Proposed twin station measurement architecture"/>

The audit console correlates observations and checks record integrity. It does not trigger a matter-transfer process.

## 04 · Data from sensor to research record

<img src="../../assets/pg01-dataflow-diagram.svg" width="100%" alt="Five-step evidence lifecycle: sensors, raw records, integrity hashes, controls and actual run manifest"/>

Every real run requires preregistered methods, calibrated sensors, original data, controls, independent oversight, and safety approval. The [actual-run manifest](../../data/experiments/manifest.json) starts empty; **mock data is never a real result**.

## 05 · Real component reference photography and manufacturer drawings

For **actual equipment photographs**, photographs of variants, schematics and mechanical details, use the verified manufacturer reference pages rather than mislabeling generic stock images:

| Candidate part | Manufacturer photo / engineering files | Selection status |
|---|---|---|
| Raspberry Pi Camera Module 3 | [Official product photographs](https://www.raspberrypi.com/products/camera-module-3/) · [Official drawings and design files](https://pip.raspberrypi.com/categories/1207-design-files) | Candidate, not purchased |
| Camera Module 3 variants / compatibility | [Official Raspberry Pi camera documentation](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/accessories/camera/cm3.adoc) | Compatibility unconfirmed |
| HX711-class scale amplifier | [Datasheet reference](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/73/HX711.pdf) | ADC candidate only |
| Load cell + reference masses | [Hardware selection register](PG-01-bom.csv) · [NIST measurement uncertainty guidance](https://www.nist.gov/publications/overview-recommended-guide-determining-and-reporting-uncertainties-balances-and-scales) | Capacity/calibration TBD |

*Manufacturer photographs and CAD belong to their owners. Link to original hosted resources rather than copying copyrighted images or claiming them as DPN-built hardware.*

## 06 · Drawing legend

- **Cyan** — measurement geometry, information and instrument connections.
- **Violet** — independent record/camera instrumentation and engineering review.
- **Amber** — warnings, missing approvals, unverified physics.
- **TBD / not to scale** — values must be measured or selected, never invented.

### Next gate

Finalize the [PG-01 Implementation Plan](PG01-IMPLEMENTATION-PLAN.md) scope and draft a signed independent instrument/safety design review **before** hardware construction.
