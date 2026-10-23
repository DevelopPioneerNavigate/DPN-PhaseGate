## New v1.6 — Trial manufacturing cards and dimensional evidence

**Gate Engineering / 05 FIRST ARTICLE** adds real operator-measured specimen records, paired actual dimensional readings, HOLD status for missing/out-of-range features, and a local CSV evidence export. [Inspection manual](assembly/PG01-FIRST-ARTICLE-v1.6.md) · [SVG/CSV export tool](../tools/export_pg01_inspection_drawings.py).

The trial rail-clamp bore locations were corrected to avoid the earlier bore/slot overlap. All parts remain candidates for engineering dry-fit review, not manufacturing approval or certified safety.

---

## PG-01 Rev B / v1.5 — Mechanical Assembly & Digital Twin

[**Rev B engineering / correction report**](assembly/PG01-REV-B-INTERFACES-v1.5.md) · [**Interactive source-model geometry**](../data/engineering/pg01-assembly-v1.5.json) · [**New interface STL source**](cad/pg01_assembly_v1_5.scad)

The initial draft's 680 mm requested manual carriage travel was shorter than the 800 mm station spacing; the Rev B proposal now uses **900 mm** travel with a **191 mm** passive rail vertical center and **205 mm** tray top. The Windows app adds the **Assembly Studio** to select 15 part envelopes, show/hide mechanical subsystems, explode the design and view validated mathematical clearance results. The CAD pipeline now creates **six printable trial STLs**, including additional splice, rail clamp and cable clip samples.

**Mechanical hold point:** preliminary envelope calculations are not finite-element, pinch, shock, fastening, cable-bend or real assembly qualification. Physical items remain unpurchased and unbuilt.

---

# DPN PhaseGate — PG-01 Physical Test Rig

**Revision:** v0.1 / bench hardware work breakdown  
**Owner:** DPN Technology / develop · pioneer · navigate  
**State:** CAD and software development. **No components have been purchased, manufactured, assembled, electrically qualified or tested through this work.**

![Physical PG-01 dimensioned engineering blueprint](../assets/pg01-build-physical-rig-v0.1.svg)

## Mission: make the first two-gate laboratory apparatus we can actually inspect and measure

The full-size twin-gate design reference describes the desired industrial design: massive modular ring frames, Gate A and Gate B, instrument racks, an inter-gate payload corridor, optical witness points and a serious research command center. This repo translates it into a **realistic phased construction program** with an initial low-voltage, mechanically stable bench platform.

The first version tests **instrument reliability, carriage transfer controls, mass calibration, imaging and synchrony**. It has no powered 'portal field' and makes no claim that there is a physically established matter-transfer mechanism. A real field-emitter architecture would need its own falsifiable physics proposal, energy/momentum model, safety approval and independently supported observation before it could be engineered.

## The first object to build (PG-01 Rev A)

| Dimension / module | Design target (not approved tolerance) |
|---|---|
| Two separate annular station frames | 360 mm outside diameter × 260 mm clear opening each |
| Annular segmented test ring | 6 segments per gate × two gates, nominal 18 mm axial depth |
| Gate spacing | 800 mm nominal center-to-center |
| Reference center elevation | 270 mm above assembly datum |
| Manual linear guide | 1200 mm design envelope, **unpowered** |
| Target carriage travel | 900 mm, subject to actual end-stop and bearing selection |
| Shuttle platform | 100 × 130 mm |
| Initial test object | 20–250 grams by controlled standard, conditioned on load-cell capabilities |
| Independent scales | 2 × reviewed 5 kg bridge load cell + separate HX711 + Pico 2 |
| Optical stations | 2 × separately identified consented USB cameras |
| Safety | Guarding and manual hard stops, verified low-voltage supplies and cable strain relief |

**Scale strategy:** the 1.6 m aperture, 4 m spacing and 25 kg payload printed in the design render are aspirational *industrial-design placeholders*, not approved construction requirements. The bench version intentionally starts smaller, lighter and manually actuated. The manuscript proposes eventual upgrades only after repeatable, useful physical measurements and professional review.

## Actual files you can work with today

| Deliverable | Direct source |
|---|---|
| Parametric 3D model with separate printable fit-check outputs | [OpenSCAD CAD](cad/pg01_bench.scad) |
| Two-camera / two-station layout | [Physical rig dimension diagram](../assets/pg01-build-physical-rig-v0.1.svg) |
| Machines-readable engineering BOM, stages and gate conditions | [Rig manifest](../data/engineering/pg01-rig-manifest.json) |
| Real Windows app construction workspace | [Build and Engineering Lab code](../desktop/build_page.py) |
| Electrical verification | [Pico 2/HX711 review](electrical/PG01-ELECTRICAL-REVIEW.md) |
| Construction sequence and acceptance checklists | [Assembly procedure](assembly/PG01-ASSEMBLY-PLAN.md) |
| Download STL/CAD/BOM file pack | [PG-01 Parametric CAD & Build Packet runs](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/pg01-cad.yml) |

## Produce physical prototypes without paying for CAD software

Install [OpenSCAD](https://openscad.org/) on Windows and open `hardware/cad/pg01_bench.scad`. The default `part="assembly"` shows the combined shape; switch `part` to `ring_segment`, `camera_bracket` or `payload_tray` to export an STL for preliminary print sizing. Exact dimensions, fit, cable routing, structural stiffness and FDM material compatibility must be reviewed before printing or ordering.

From OpenSCAD CLI (or use the workflow's generated artifact instead):

```bash
openscad -o build/PG01-Gate-Ring-Segment.stl -D 'part="ring_segment"' hardware/cad/pg01_bench.scad
openscad -o build/PG01-Camera-Bracket.stl -D 'part="camera_bracket"' hardware/cad/pg01_bench.scad
openscad -o build/PG01-Payload-Tray.stl -D 'part="payload_tray"' hardware/cad/pg01_bench.scad
python tools/export_pg01_build_pack.py --out build/PG01-Proposed-Engineering-Pack
```

**Manufacturing caution:** these are CAD fit-check meshes. Not tested for thread engagement, dynamic loading, dimensional accuracy, pinch-point safety, magnetic fields or electrical clearances. In a commissioned version, replace with reviewed drawings and tolerance stack-up plus printable/rated material specifications.

## Phase-driven assembly

G0 — CAD review and qualified electronics/safety review.  
G1 — Fabricated unloaded frames and guarded manual shuttle.  
G2 — Independent instrument data + reference mass + optical recording validation.  
G3 — Blinded sham/control baseline and evidence-independent verification.  
G4 — Review of a specific, testable field interaction (if future science warrants it).

The native **Gate Engineering** workspace starts **every work package PLANNED**. Completion can only be *operator-reported* after entering an evidence note and responsible operator. The app's gate status never substitutes for independent safety approval.

## Controls and honest baselines

Before attempting unexplained effects, explicitly demonstrate three conventional conditions: (1) no object moved between A/B, (2) an object moved via the manual rail/shuttle, and (3) sensor/USB/camera input disrupted to test fault flags. Record the controls with original raw measurements and witness files. A successful mechanical shuttle move is **conventional transport**, not evidence of teleportation.

DPN PhaseGate seeks to research whether fundamentally different physical transport is possible, but the desired effect is not established by the appearance of the machine. No energy emitter, cryogenic system, superconducting coil or high-current field system has been designed or approved in this initial apparatus.

## Engineering and provenance

- [Official Raspberry Pi Pico 2 datasheet](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf)
- [SparkFun HX711 board and current product spec](https://www.sparkfun.com/sparkfun-load-cell-amplifier-hx711.html)
- [SparkFun HX711 hookup guide](https://learn.sparkfun.com/tutorials/load-cell-amplifier-hx711-breakout-hookup-guide/all?print=1)
- [OpenSCAD language/reference manual](https://files.openscad.org/documentation/manual/The_OpenSCAD_Language.html)

No automatic purchases, browser dashboard or external paid API are involved. Outputs are engineering work-in-progress with full status visibility rather than fabricated experimental claims.
