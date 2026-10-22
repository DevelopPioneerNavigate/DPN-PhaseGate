# PG-01 Implementation Plan | Design review package

**[Blueprints](PG-01-BLUEPRINTS.md) · [Architecture](PG-01-architecture.md) · [Safety](../safety/SAFETY-COMMAND.md)**

<img src="../../assets/pg01-blueprint-top.svg" width="100%" alt="Layout decisions precede prototype assembly"/>

> **Visual guide:** Hardware dimensions, sample range, controller and power supply remain open design decisions; no real apparatus has been constructed.

---

[← Project overview](../PROJECT-OVERVIEW.md) · [System architecture](PG-01-architecture.md) · [Inventory](PG-01-bom.csv)

**Purpose:** take a paired **measurement platform** from paper architecture to safe, independently verifiable data capture. **Not a two-way matter portal.**

| Step | Product | Acceptance evidence | Status |
|---|---|---|---|
| **E0 Scope** | Use case, sample mass range, station dimensions, stationary environment, budget | Written reviewed requirements | Open |
| **E1 Electrical** | Rated PSU, controller interface, camera and sensor compatibility, disconnect schematic | Documented no-HV power/thermal safety review | Not started |
| **E2 Mechanical** | Two inspectable/transparent enclosures and load-cell mounts | Drawings, no hidden passage, stability assessment | Not started |
| **E3 Software** | Two independent loggers + local evidence console (real/synthetic mode distinct) | Clock diagnostics, file hashes, failure handling, tests | Not started |
| **E4 Calibration** | Reference mass checks, environmental drift, timestamp uncertainty | Repeatability/linearity/clock-error evaluation | Not started |
| **E5 Protocol approval** | Blinded sham/control experiment preregistration | Actual named reviewer, safety approval, criteria | Not started |
| **E6 Experiment** | Run audited approved tests | Original evidence, analysis, negative results recorded | **Not authorized** |

## Architecture requirements
- Two physically separated and independently observable stations; low voltage by default.
- Mass, camera, timestamp and environmental data saved independently; UTC offset diagnostics recorded.
- Frame drops, clock skew, sensor saturation and missing records create explicit **invalid/inconclusive** statuses, never a portal-success flag.
- Raw evidence not silently edited; register cryptographic hashes and signed custody when possible.
- Demo mode cannot write to actual experiment manifest and is watermarked **SYNTHETIC**.

## Hardware decisions still required

| Decision | Options to evaluate | Decision rule |
|---|---|---|
| Controller | SBC vs microcontroller | camera and data-log performance, cost and voltage fit |
| Scale | Load cell + ADC | sample range, accuracy after calibration, mechanical mount |
| Cameras | Camera Module 3 vs supported USB | coverage, timestamps and sustained recording |
| Time reference | NTP with measured offsets vs wired reference | observed timing error vs test timescale |
| Housing | Transparent enclosure with accessible seals | no concealed transit path and stable weighing |
| Local console | Python stdlib prototype vs future application stack | auditable records, portable build, no paid dependencies |

**Nothing in this plan requires speculative high-energy equipment.** Before buying parts, finalize cost/voltage compatibility and qualified safety review. No guaranteed schedule for physical-object teleportation exists.

## Immediate software milestones

1. Define CSV and JSON event formats, include station ID, calibration ID, UTC+monotonic timestamps.
2. Write mock generator that is obviously synthetic and cannot pollute real evidence.
3. Build a local read-only dashboard listing synchronized station health, source count and **zero genuine transfer events**.
4. Unit test missing files, untrusted input, clock regressions and invalid measurement units.
5. Validate live readings against calibration and witness recordings only after E1–E5.

Related work: [Issue #4](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/issues/4), [Issue #5](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/issues/5), [Safety review #6](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/issues/6).
