# DPN PHASEGATE
### DPN Technology | Advanced Research & Development | PG Program
**Project goal:** Investigate whether the *same intact macroscopic physical object* can enter station A and emerge from spatially separated station B, then repeat from B to A.

> **Status (2026-10-22):** Concept/literature stage. **No verified physical-object teleportation. No verified physical traversable wormhole. No functioning PhaseGate prototype.** Quantum teleportation transfers quantum information, not physical matter. An analogue/simulation/optical effect must never be reported as macroscopic transfer.

## Research navigation
- [Program charter](docs/charter.md) · [Roadmap](docs/roadmap.md) · [Physics evidence](docs/physics/baseline.md) · [Feasibility register](docs/physics/feasibility.md)
- [Research questions](docs/physics/questions.md) · [Literature review rules](docs/physics/review-protocol.md) · [2025 quantum-wormhole scrutiny](docs/physics/2025-wormhole-scrutiny.md)
- [Engineering requirements](docs/engineering/requirements.md) · [PG-01 instrumentation](docs/engineering/PG-01.md) · [PG-01 architecture](docs/engineering/PG-01-architecture.md) · [Equipment selection register](docs/engineering/PG-01-bom.csv)
- [Safety policy](docs/safety/safety.md) · [Risk register](docs/safety/risks.md) · [Decision register](docs/governance/decisions.md)
- [Research data registry](data/README.md) · [Sources](data/literature/sources.json) · [Hypotheses](data/hypotheses/hypotheses.json) · [Experiment manifest](data/experiments/manifest.json)

## Program dashboard
| Workstream | Status | Evidence boundary |
|---|---|---|
| Macroscopic object transfer | Unverified | No scientific demonstration or workable engineering mechanism |
| Quantum state teleportation | Established | Only quantum information/state transfer |
| Wormhole geometries | Theoretical | Mathematical models; no physical traversable portal observed |
| Quantum-processor wormhole dynamics | Experimental analogue | No rupture of ambient spacetime |
| PG-01 paired measurement stations | Paper design | Measurement rig, **not a portal** |
| Real PhaseGate experimental runs | **0** | Manifest remains empty; no fabricated runs |

## Workflow and green gates
1. Add primary sources to data/literature; record the precise supported claim and **non-claim**.
2. Register a falsifiable hypothesis linked to source IDs.
3. Open a research question or experiment proposal issue. Preregister protocol, controls, calibrated measurements, safety review and falsification thresholds.
4. If authorized and safe, conduct and log runs with raw evidence, SHA-256 checksums, witness and calibration IDs; **record failed/null results**.
5. Run: python tools/validate_research.py and python -m unittest discover -s tests -v.
6. Open a pull request; validation is structural, **not proof of scientific feasibility**.

## Research v0.2 additions (proposed)
- New 2025 paper correction, peer-reviewed critique and author response: SRC-007–009. These do **not** demonstrate a physical portal.
- PG-01 pair-station design, unselected component register, blinded null-trial draft (not authorized), and calibration procedures.
- Offline, standard-library-only calibration utility with synthetic-only fixtures. It cannot prove object transfer.
- Detailed safety and evidence-chain criteria; do not commit mock experiments to the real manifest.

Calibration commands:
```sh
python tools/pg01_calibration.py calibrate examples/SYNTHETIC-pg01-calibration.csv
python tools/pg01_calibration.py sha256 examples/SYNTHETIC-pg01-calibration.csv
```

## Primary literature
- [Bennett et al., PRL 1993](https://doi.org/10.1103/PhysRevLett.70.1895) — quantum-state teleportation.
- [IBM Quantum learning module](https://qiskit.qotlabs.org/learning/courses/basics-of-quantum-information/entanglement-in-action/quantum-teleportation) — information ≠ physical matter.
- [Gao/Jafferis/Wall, JHEP 2017](https://doi.org/10.1007/JHEP12(2017)151) — theoretical wormholes in a specific model.
- [Jafferis et al., Nature 2022](https://doi.org/10.1038/s41586-022-05424-3) — quantum-processor wormhole-like dynamics.
- [Caltech experiment Q&A](https://inqnet.caltech.edu/wormhole2022/) — explicitly no physical spacetime rupture.
- [Nature 2025 critique](https://doi.org/10.1038/s41586-025-08939-7) and [author reply](https://doi.org/10.1038/s41586-025-08995-z) — interpretation remains scientifically debated.
- [NASA wormhole explainer](https://science.gsfc.nasa.gov/attic/cosmicopia.gsfc.nasa.gov/qa_sp_sl.html) — no evidence for physical wormholes or method to construct one.

**Governance:** Private scientific notebook, immutable research history through Git commits. Do not commit source PDFs without redistribution rights, secrets, sensitive data, or unreviewed hazardous plans.

© 2026 DPN Technology. All rights reserved. No license to copy or distribute is granted.
