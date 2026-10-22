<div align="center">

<img src="assets/phasegate-hero.svg" alt="DPN Technology PhaseGate — advanced physical systems research" width="100%">

<br>

**A DPN Technology research program exploring the scientific feasibility of two-way physical-object transfer.**

[![Research Integrity](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/research-integrity.yml/badge.svg?branch=main)](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/research-integrity.yml)
![Stage](https://img.shields.io/badge/PROGRAM-RESEARCH%20%26%20DESIGN-8965E8?style=flat-square)
![Prototype](https://img.shields.io/badge/PG--01-PAPER%20DESIGN-32BCD5?style=flat-square)
![Physical Transfer](https://img.shields.io/badge/MATTER%20TRANSFER-UNVERIFIED-DF9E69?style=flat-square)

**[VISUAL ATLAS](docs/VISUAL-ATLAS.md)** · **[PROJECT OVERVIEW](docs/PROJECT-OVERVIEW.md)** · **[START HERE](docs/START-HERE.md)** · **[ENGINEERING](docs/engineering/PG-01-architecture.md)** · **[RESEARCH DATA](data/README.md)** · **[ISSUES](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/issues)**

</div>

---

### Mission at a glance

**Ultimate scientific question:** Could the *same intact physical object* enter one gateway and emerge from a separate gateway, in either direction, without traveling by conventional means?

**Our work today:** Build an accountable research library and design safe **measurement stations** that could examine claims under controlled conditions. **We have not demonstrated a physical portal, traversable wormhole, or object teleportation.**

<img src="assets/phasegate-status.svg" alt="Research active; PG-01 evidence stations in design; physical-object transfer unverified" width="100%">

> [!IMPORTANT]
> **Evidence boundary:** Quantum teleportation transfers quantum information, not intact macroscopic objects. Our planned PG-01 equipment measures and documents experiments; it does not physically transport matter. A green software check validates data structure, **not** a breakthrough in physics.

### Illustrated research atlas

The complete research library now has visual guides, labelled concept blueprints, an evidence ladder and direct links to manufacturer hardware photographs. **Start with the diagrams, then use the detailed scientific notes.**

| Explore our engineering drawings | Understand evidence and scientific limits |
|:--|:--|
| <img src="assets/pg01-blueprint-front.svg" alt="PG-01 concept front elevation" width="100%"> | <img src="assets/phasegate-evidence-ladder.svg" alt="Six levels of scientific evidence" width="100%"> |
| **[View the complete blueprint set →](docs/engineering/PG-01-BLUEPRINTS.md)** | **[Explore the physics guide →](docs/physics/PHYSICS-COMMAND.md)** |

<img src="assets/phasegate-research-pipeline.svg" alt="From literature and hypotheses to experimental records and independent review" width="100%">

**[Open the complete PhaseGate Visual Research Atlas →](docs/VISUAL-ATLAS.md)**

### Native Windows App — PhaseGate Research Operations v0.6

**Major upgrade:** the primary PhaseGate software is now a **true PySide6/Qt native Windows desktop application**, replacing the basic browser console as our development focus. Animated orbital graphics, seven functional screens, diagnostics, source explorer, custom icon, real window controls, research inventory and offline operation. **All station telemetry remains clearly marked as SYNTHETIC**; no portal or connected instruments exist.

| Download | Preview | Engineering |
|---|---|---|
| **[Native Windows EXE builds](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml)** — open a successful run, download the v0.6 artifact, extract and launch DPN-PhaseGate.exe | **[Native UI screenshot artifact](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml)** — included in successful Windows builds | [Native desktop manual](desktop/README.md) · [Hardware blueprint](docs/engineering/PG01-PROTOTYPE-SPECS-v0.5.md) |

The application is a compiled **standalone .exe**, not a browser wrapper. Existing v0.5 browser code remains under [legacy console/](console/README.md) for historical reference.

For development with Python 3.12+ on Windows:

```powershell
python -m pip install -r desktop/requirements.txt
python -m desktop
```

CI smoke-tests Qt screens and uploads the screenshot plus actual Windows executable after packaging.

### PG-01 Research Console v0.5 — Legacy Browser Prototype

**Now implemented:** a responsive, locally running DPN-themed demonstration console. It shows two **simulated** measurement stations, a moving synthetic chart, project record counts, demo audit events and a clearly marked synthetic-only export. No hardware, cameras, transfer events or actual experiment logging are connected.

<img src="assets/pg01-hardware-v0.5.svg" width="100%" alt="Conceptual paired load-cell station hardware architecture with USB connections to a local PC"/>

| Run on Windows | Engineering specifications | Electrical signal drawing |
|---|---|---|
| **[Double-click START_PHASEGATE_CONSOLE.bat](START_PHASEGATE_CONSOLE.bat)** (after cloning) | [PG-01 prototype parts and sizing](docs/engineering/PG01-PROTOTYPE-SPECS-v0.5.md) | [Proposed HX711 / Pico 2 signal map](assets/pg01-interface-pinout-v0.5.svg) |

For a terminal launch (Python 3.12+, no extra packages):

    python -m console.server --port 8765

Then open **http://127.0.0.1:8765**. This is a local, read-only synthetic demonstration; don't expose it to the internet. **[Full console instructions →](console/README.md)**

### Pick your path

| **01 / EXPLORE** | **02 / ENGINEER** | **03 / VERIFY** |
|:--|:--|:--|
| Understand the science, the limits of existing experiments, and the open questions. | See how the two PG-01 stations would be instrumented and built safely. | Understand how we document sources, calibration, controls and real experimental evidence. |
| **[Explore the science →](docs/physics/baseline.md)** | **[Open hardware design →](docs/engineering/PG-01-architecture.md)** | **[Open the evidence model →](data/README.md)** |
| [Research questions](docs/physics/questions.md) · [2025 scientific debate](docs/physics/2025-wormhole-scrutiny.md) | [Bill of materials](docs/engineering/PG-01-bom.csv) · [PG-01 implementation plan](docs/engineering/PG01-IMPLEMENTATION-PLAN.md) | [Safety standards](docs/safety/safety.md) · [Proposed null test](docs/protocols/PG-PROT-NULL-001.md) |

### System blueprint · PG-01

<img src="assets/pg01-system.svg" alt="Two independent instrumented stations send sensor and video evidence to a local research console. No matter-transfer connection exists." width="100%">

**Station A and Station B** are planned as independently observable, low-voltage measurement systems. Their data would be collected by a research console for timing, calibration and evidence integrity.

**[Full technical architecture →](docs/engineering/PG-01-architecture.md)** · **[Requirements →](docs/engineering/requirements.md)**

### The development path

<img src="assets/phasegate-roadmap.svg" alt="Research foundation established, PG-01 engineering in design, calibration trials not performed, physical transfer unverified" width="100%">

| Stage | Current position | Next meaningful gate |
|:--|:--|:--|
| **R0 — Research foundation** | Established · literature records, issues and data checks | Keep sources and evidence limitations current |
| **R1/R2 — Scientific review & PG-01 design** | In progress · candidate architecture, no purchased parts | Approve measurement requirements and qualified safety review |
| **R3 — Bench validation** | Not started · no experiments recorded | Calibrate, preregister and document safe null trials |
| **R4+ — New-physics investigation** | Research goal only · mechanism unknown | Quantitative, falsifiable theory and independent expert review |

[Complete roadmap and release gates →](docs/roadmap.md)

### Research inventory

| Registered source records | Registered hypotheses | Conducted experiment records |
|:--:|:--:|:--:|
| **13** | **2** | **0** |
| [Literature register](data/literature/sources.json) | [Hypothesis register](data/hypotheses/hypotheses.json) | [Actual-run manifest](data/experiments/manifest.json) |

<sub>Inventory snapshot: 2026-10-22. Counts represent repository records, not proof of physical transfer. Synthetic examples are excluded from actual experimental results.</sub>

### Run the offline integrity checks

Python 3.12 or later; no extra packages or paid AI API tokens are required for these local commands.

```bash
python tools/validate_research.py
python -m unittest discover -s tests -v
python tools/validate_readme.py
python tools/pg01_calibration.py calibrate examples/SYNTHETIC-pg01-calibration.csv
```

The calibration sample is **synthetic** and does not represent a real experiment.

### Project directory

| Area | Purpose |
|:--|:--|
| [docs/PROJECT-OVERVIEW.md](docs/PROJECT-OVERVIEW.md) | Plain-English research mission, boundaries and next decisions |
| [docs/physics/](docs/physics/baseline.md) | Evidence levels, core papers, theory, conflicting interpretations |
| [docs/engineering/](docs/engineering/PG-01-architecture.md) | PG-01 measurement architecture and component planning |
| [docs/protocols/](docs/protocols/PG-PROT-NULL-001.md) | Draft test protocols, preregistration and controls |
| [data/](data/README.md) | Literature, hypotheses and genuine run manifests |
| [tools/](tools/validate_research.py) | Data-validation, calibration and integrity utilities |
| [.github/](.github/workflows/research-integrity.yml) | Workflow green gates and structured project issue forms |

**Research contribution:** Start with [START HERE](docs/START-HERE.md), open a [research question](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/issues/new/choose) and use [contribution standards](CONTRIBUTING.md). No unsafe experiments or unsupported teleportation claims.

---

<div align="center">

<img src="assets/phasegate-footer.svg" alt="DPN Technology — Develop · Pioneer · Navigate" width="100%">

<sub>© 2026 DPN Technology · All rights reserved · Research program, not an operating teleportation device.</sub>

</div>
