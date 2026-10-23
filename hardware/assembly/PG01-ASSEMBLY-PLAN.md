# PG-01 Rev A — Build, Fit-Check & Acceptance Plan

[Hardware overview](../README.md) · [CAD source](../cad/pg01_bench.scad) · [Power review](../electrical/PG01-ELECTRICAL-REVIEW.md) · [Native engineering app](../../desktop/build_page.py)

**Status:** work instructions prepared only. **No fabrication/physical tests completed or verified.**

## Before materials procurement

A project owner must select actual manufacturers and revisions, drawings, material grades, fastener sizes, actual load cells and bearing ratings. The current parametric CAD is a bounding/fit-check model; it contains no engineer-approved tolerances, welding specifications, compliance certificates or load-bearing calculations.

Mechanical risks include tipping, pinch points, rotating/ sliding carriage contact, sharp printed edges, cable snagging and overload or deflection of sensor beams. An assembled prototype must be evaluated by a qualified person.

### WP-01 — Geometry design review
- [ ] Inspect exact clearance envelope, floor/bench space, three-dimensional collision limits and camera views.
- [ ] Validate outside ring diameter 360 mm / clear opening 260 mm, two rings at 800 mm spacing.
- [ ] Confirm 1200 mm guide fit and actual 900 mm usable travel with hard stops and guards.
- [ ] Determine and record material/process choice and realistic dimensional tolerance.
- [ ] Resolve actual fastener hole patterns by qualified mechanical analysis; original OpenSCAD holes are provisional.
- [ ] Assign CAD revision and sign physical integration dimensions.

**Acceptance:** reviewed/dimensioned drawing and traceable mechanical assumptions.

### WP-02 — Electrical safety and low-voltage signoff
- [ ] Verify Pico 2, HX711 breakout and strain gauge documentation by part/revision.
- [ ] Verify digital 3.3 V compatibility, bridge excitation and power distribution.
- [ ] Validate USB cable security, power budget, camera permissions and unplug behavior.
- [ ] Identify hazards; label test article and workstation.
- [ ] Independent reviewer records approval or blocks construction/power-on.

**Acceptance:** signed electrical design review; no current connection without approval.

### WP-03 — Unpowered annular frame fit-check
- [ ] Print a **single** `PG01-Gate-Ring-Segment.stl` fit-check; inspect slot, hole clearances and layer direction.
- [ ] Verify material suitability and deburr all sharp edges.
- [ ] Only after fit check, fabricate required ring modules and support structure.
- [ ] Confirm actual base rigidity and stable supports at A/B; two frame segments cannot be treated as rated for load.
- [ ] Record as-built OD/ID, spacing, leveling and fastener torques from selected material datasheets.

**Acceptance:** two mechanically inspected unpowered frames with station markers A and B.

### WP-04 — Manual linear shuttle
- [ ] Install commercially rated straight linear guide with a manually guided carriage, no motor.
- [ ] Check end stops, pinch guards, stroke, parallel rails and cable clearance.
- [ ] Use a payload tray that cannot contact or interfere with an independent scale at either station.
- [ ] Record simple conventional passes and no-motion null controls.
- [ ] Verify carriage can't collide with gate frames under anticipated handling.

**Acceptance:** repeatable operator-controlled *conventional physical movement*, not teleportation.

### WP-05 — Independent USB sensor bring-up
- [ ] Connect **only** reviewed low-voltage hardware.
- [ ] Load separate A and B identifiers into the proposed Pico 2 MicroPython firmware.
- [ ] Validate frame station IDs, monotonic sequences, raw signed count range, missing/silent link detection.
- [ ] Swap cables deliberately as a control: incorrect mapping must flag an error.
- [ ] Make unverified `BENCH_*.jsonl` logs and inspect checksum sidecars.

**Acceptance:** genuine local instrument data with honest faults and no false measurement units.

### WP-06 — Metrology
- [ ] Use traceable mass standards (minimum three masses; two or more readings per mass).
- [ ] Document zero, repeatability, calibration residuals, range, ambient temperature, drift, hysteresis and out-of-range responses.
- [ ] Use station-specific `BENCH_CAL_*.json` profiles with appropriate expiry and review.
- [ ] Preserve original raw samples and source worksheets.

**Acceptance:** independently reviewed and bounded measurement claims; fit RMSE alone is NOT total uncertainty.

### WP-07 — Optical witness control
- [ ] Install two cameras with physically documented positions and safe lighting.
- [ ] Obtain filming permission and establish retention policy.
- [ ] Record authorized bench stills and verify hash manifests.
- [ ] Characterize host arrival jitter without claiming camera exposure synchronization.
- [ ] Consider external visible reference flash only after appropriate viewing safety review.

**Acceptance:** independent footage files and documented recording limitations, not established simultaneity.

### WP-08 — Controlled experiments
- [ ] Pre-register observable outcomes and failure thresholds.
- [ ] Run no-object, static-object, manual-shuttle and camera/serial disconnection controls.
- [ ] Preserve unmodified original readings, media and environmental setup.
- [ ] Invite independent review; report negative outcomes too.
- [ ] Write an approved experiment only under formal review and with actual evidence.

**Acceptance:** reviewed null/reference baseline that demonstrates equipment reliability and limitations.

### WP-09 — New-physics feasibility research
- [ ] Define an independently falsifiable hypothesis that makes a nontrivial measurable prediction.
- [ ] Model energy, momentum, mass continuity, radiation hazards, thermal/mechanical limits and alternatives.
- [ ] Specify instrumentation sufficient to distinguish claimed effects from ordinary transport, signal spoofing, timing artifacts or measurement error.
- [ ] Have independent scientific/safety reviewers assess whether a powered field subsystem is warranted.

**Acceptance:** testable proposal; not a claim that macroscopic transport is physically feasible or demonstrated.

## Machine upgrade principle

The visual concept shows a large engineered ring, central alignment deck, active emitter systems and major industrial support infrastructure. In Rev A, the **real machine** comprises passive frame shells, manual carriage, sensors, controllers and cameras. Future optical alignment, vibration logging or lighting accessories can be specified based on bench findings. **Field generation, high-power systems and energized apertures have no verified operational definition or approved part list** and are deliberately excluded from procurement.

## Evidence recording in the Windows app

Open **Gate Engineering**: review the drawn envelope, select a work package and choose **Log Selected Work Package**. Record your operator name and a specific photo/test/drawing reference. The program enforces dependency sequence and stores an auditable local checksum file separate from the scientific experiment manifest. Task status is labelled **operator-reported**, never independent approval. Use **Parts & BOM** to export the proposed inventory and **Acceptance Gates** to review outstanding signoffs.

These instructions support a real, incremental physical construction program, not a pre-claim of successful portal physics.
