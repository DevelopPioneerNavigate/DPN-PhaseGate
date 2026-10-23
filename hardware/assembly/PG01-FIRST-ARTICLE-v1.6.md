# PG-01 v1.6 — Trial Fabrication Drawings & First-Article Inspection

[Hardware plan](../README.md) · [Rev B mechanical model](PG01-REV-B-INTERFACES-v1.5.md) · [Current trial inspection plan](../../data/engineering/pg01-first-article-v1.6.json) · [Offline sheet generator](../../tools/export_pg01_inspection_drawings.py)

**Development state:** software, trial geometry and proposed first-article review sheets. **No physical specimens have been produced, measured, purchased, accepted for load, or independently approved through this release.** The documents are deliberately marked **NOT APPROVED FOR FABRICATION**.

## What can be manufactured for safe preliminary fit studies, after a suitable design review

The CAD package contains models for four trial types:

| Card | Trial part | Critical check groups |
|---|---|---|
| FA-01 | Joint splice plate | Length 48 mm, width 22 mm, plate 6 mm, hole pitch 22 mm, bore 3.4 mm |
| FA-02 | Rail mounting clamp | Length 55 mm, width 42 mm, body 13 mm, hole pitch **34 mm**, bore 4.5 mm |
| FA-03 | Low-voltage cable clip | Base 44×24 mm, attachment pitch 32 mm, bore 3.4 mm, saddle 12 mm |
| FA-04 | Annular frame sector | Parent outer diameter 360 mm, inner diameter 260 mm, radial wall 50 mm, axial 18 mm |

All nominal values and candidate screening limits are machine-readable in the [trial inspection plan](../../data/engineering/pg01-first-article-v1.6.json). **None is a certified or approved manufacturing tolerance**. These are fit-screen proposals only; CAD geometry may need further refinement before purchasing fasteners, printing the assembly, or cutting stock.

### Correction discovered while preparing inspection cards

Rev B's earlier rail clamp used 25 mm hole pitch. Given its 21 mm central slot and 4.5 mm clearance holes, the attachment holes risked intersecting the slot's edges. Rev v1.6 moves the two trial hole centers to ±17 mm, giving a **34 mm pitch** and additional nominal web. The changes are mirrored in OpenSCAD CAD, the Rev B engineering source manifest and the inspection cards. **That does not prove the clamp is adequately strong or that it fits a real rail.**

## Produce real, printable vector sheets

The GitHub CAD workflow renders candidate STL parts and publishes a bundle with four **SVG inspection drawings**, a blank CSV measurement register, source JSON, OpenSCAD code, proposed BOM and integrity checks. The drawings include schematic geometry, source-derived nominal dimensions and specimen/operator/equipment fields. They are review drawings, not fully dimensioned fabrication drawings with a validated tolerance stack.

```bash
python tools/export_pg01_inspection_drawings.py --check
python tools/export_pg01_inspection_drawings.py --out build/PG01-v1.6-Inspection-Cards
python -m unittest discover -s tests -p test_first_article.py -v
```

Every inspection card requires **two separately entered physical observations** for each characteristic; a sample should use a unique specimen ID. The app does not fabricate measurement data, use simulation in the physical measurement ledger or infer approval from CAD.

## New native Windows workflow

1. Launch PhaseGate v1.6 → **Gate Engineering** → **05 FIRST ARTICLE**.
2. Select a trial part (FA-01 through FA-04) and enter a physical specimen ID, e.g. `TRIAL-001`.
3. Select the characteristic to inspect. Choose **RECORD SELECTED FEATURE** and supply two actual readings in millimeters, the person taking them, the calibrated measuring tool ID and a source photo/notebook reference.
4. A local append-only *per-feature revision history* records observations. Out-of-range or missing data automatically produce **HOLD**. All candidate ranges met produce **TRIAL DIMENSIONS RECORDED / PHYSICAL REVIEW REQUIRED**, **not** a green manufacturing release.
5. Export the **CSV** and preserve original files. The existing operator build log is used with SHA-256 checks and atomic saving. It remains separate from scientific experiment evidence.
6. An independent qualified reviewer still must inspect actual part fit, print process, function, fastener design, loads, cable routing, guarding and hardware safety before any hardware use.

The app shows the actual most recent pair and trial status; it never silently promotes entries into the experiment registry or certifies a part.

## Physical inspection sequence

- Verify the source drawing revision and actual printed part ID; document process, machine, material, orientation, batch and environment.
- Check measuring tool identification and traceability. Maintain original instrument records and photos.
- Measure each listed characteristic **twice** and record both readings; disagreement itself is a signal to investigate even when both fall in the proposed range.
- Mark damaged/deformed surfaces or visibly unfit joints as a HOLD even if caliper dimensions appear to pass.
- Conduct a **dry fit only** after the mechanical review: no power, no actuation, no field emitter.
- If actual part is out of candidate range, record results honestly, investigate root cause and revise drawing/CAD through a new revision. Never silently widen tolerances or edit evidence to pass.
- Independent safety and fabrication approvals are **outside** the current automatic gate and must be recorded in separate signed engineering paperwork.

## Remaining readiness gates

**G0**: complete a credible structural assessment, choose specific materials and suppliers, verify nominal mating profiles and fasteners, assess pinch zones; mechanical reviewer signs drawings.

**G1**: conduct limited trial prints and dimensional studies; no assumed printable strength or approved load rating.

**G2**: verify reviewed low-voltage sensor wiring, USB safety, authorized camera use and independent calibration.

**G3**: conduct null and manual-shuttle control trials; all alleged unusual physical effects require separately falsifiable hypotheses and controls.

The research target remains a physical two-gate apparatus, but this revision's working result is its **fabrication-quality infrastructure**, not a demonstrated transfer field.

[Download successful CAD and first-article sheets](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/pg01-cad.yml) · [Windows application builds](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml)
