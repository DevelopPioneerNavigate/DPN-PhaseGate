# PG-01 Rev B — Mechanical Interfaces & Assembly Review (v1.5)

[Physical test rig](../README.md) · [Legacy Rev A CAD](../cad/pg01_bench.scad) · [Current Rev B CAD](../cad/pg01_assembly_v1_5.scad) · [Revisioned 3D coordinates](../../data/engineering/pg01-assembly-v1.5.json) · [Windows Assembly Studio](../../desktop/assembly_page.py)

**Status: provisional geometry and printable fit-check details only. No components are built, purchased, load-rated, powered, or physically tested.** The machine is a real proposed low-voltage instrumented test rig, not a claim that a matter-transfer field exists.

## 01 / Critical mechanical correction

A review of the Rev A CAD found that the originally proposed **680 mm travel was shorter than the 800 mm Gate A-to-B center spacing**. That would not position a carriage at both instrument station centers. The old rail height also placed the guide envelope uncomfortably close to the gate’s circular clear opening. Rev B changes the design targets and adds executable clearance calculations:

| Design feature | Rev A | Rev B | Engineering interpretation |
|---|---:|---:|---|
| Station A/B center spacing | 800 mm | 800 mm | Constant ring datum separation |
| Nominal rail length | 1,200 mm | 1,200 mm | Trial mechanical envelope |
| Requested centered carriage travel | 680 mm | **900 mm** | Reaches both A/B centers with 100 mm theoretical extra travel |
| Nominal two-guide vertical center | old design 27 mm | **191 mm** | Raises manual guides through intended clear annular opening |
| Tray top / bottom of nominal payload | approximate 56 mm | **205 mm** | Places payload within gate clear opening |
| Gate opening | 260 mm ID | 260 mm ID | Still a passive annular frame |

The candidate 100 mm-wide, 80 mm-high payload bounding box has roughly **48 mm radial clearance** to the 260 mm opening; the proposed rail-edge envelope has approximately **25 mm**. The requested margin is **20 mm**. The symmetric carriage end reserve for a 900 mm stroke with a 130 mm-long tray on 1,200 mm rails is **85 mm per end**.

These checks are **numerical envelope comparisons**, not a true swept-solid intersection, FEA, assembly tolerance stack, shock/impact analysis or independent review. Real hardware may change these values. The default simulator must refuse inconsistent CAD dimensions.

## 02 / Physical component and joint studies

| Interface | Trial CAD part | Proposed hole detail | Approval needed before manufacture |
|---|---|---|---|
| J-01 segment joint between six ring segments | `PG01-RevB-Joint-Splice.stl` | 3.4 mm candidate through holes, 22 mm spacing | Actual approved fastener, insert geometry, loads and material |
| J-02 rail/body attachment | `PG01-RevB-Rail-Clamp.stl` | 4.5 mm candidate holes, 25 mm spacing | Actual purchased rail profile, bolt engagement and mechanical forces |
| J-03 strain-relieved low-voltage cable | `PG01-RevB-Cable-Clip.stl` | 3.4 mm attachment clearance | USB bend radius, snag/abrasion protection and insulation |

Older ring, camera-bracket and tray STL models remain bundled for continuity; the Rev B CAD adds **three additional trial parts**. All six STLs are compiled with **free OpenSCAD** on GitHub Actions and automatically checked for finite triangle coordinates and coarse mesh envelopes.

## 03 / Camera & instrument routing

Station A and B optical devices have explicit positions in the data model: camera bracket envelopes approximately `x=-182 mm, y=±425 mm, z=395 mm`. Low-voltage sensor/camera routing is modeled outside the ring at `x=-205 mm`, away from the centrally moving tray. The exact cable clips, connector IP ratings, USB cable length, shielding, grounding, communication integrity and strain relief remain **engineering decisions, not facts inferred from the CAD**.

No energized emitter coils, high voltage, cryogenic hardware, lasers, motorized carriage or field drivers are part of this revision.

## 04 / Native Assembly Studio workflow

Open PhaseGate v1.5 and use **Assembly Studio** from the left mission dock or Ctrl+K. You can:

- Rotate the presentation between **isometric, front and top projections** (native Qt 3D-coordinate projections; not precision CAD rendering).
- Reveal individual physical subsystems: **structure, motion, optics, cable routing, sensors, and guarding**.
- Use **Explode** to separate the conceptual machine into inspectable groups, with no motor or physical control commands.
- Select one of **15 assembly elements** or click a visible part to see its material envelope, coordinates, risk and unreviewed interfaces.
- Review the four computed check outputs for proposed payload clearance, rail clearance, station reach and carriage end reserve.

This display is connected to the `data/engineering/pg01-assembly-v1.5.json` design and the `data/engineering/pg01-rig-manifest.json` build source. Deliberate source disagreements cause startup/CI validation failure instead of a plausible but incorrect render.

The pre-existing **Gate Engineering** screen remains the official operator-entered receiving, dimensional-inspection, BOM and work-package ledger. Assembly Studio does not report tasks as complete or authorize fabrication.

## 05 / Physical WP-01 acceptance tasks

1. Measure actual proposed rail and carriage CAD from a selected supplier; revise bolt patterns and carriage height to preserve envelope clearances.
2. Establish true frame strength and stability under loads with qualified mechanical design review.
3. Print **one ring segment, one joint splice and one rail clamp** as inexpensive trial fit parts; measure key dimensions on a calibrated measuring tool.
4. Resolve physical cable path, hard-stop forces, ring/base attachment, protective covers, moving load paths and camera field of view.
5. Revise tolerances from observed print and as-received dimensions; independently sign off the fabrication drawing revision.
6. Only after WP-01/WP-02 approvals, consider purchasing/assembling mechanical, sensor and optical components.

## 06 / Check the code and artifacts

```bash
python tools/export_pg01_build_pack.py --check
python -m unittest discover -s tests -p test_assembly_model.py -v
python -m unittest discover -s tests -p test_fabrication.py -v
python tools/export_pg01_build_pack.py --out build/PG01-RevB-Workpack
```

[Download the newest successful CAD/BOM artifacts](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/pg01-cad.yml) or [the standalone v1.5 Windows application](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml).

**Engineering note:** Numerical PASS never equals physical clearance or safety approval. Actual two-way physical-object transport has not been measured or demonstrated, and no physically supported field-generating subsystem has been specified.
