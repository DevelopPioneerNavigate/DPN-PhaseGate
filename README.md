# DPN PHASEGATE
### DPN Technology | Advanced Research & Development | PG Program
**Project goal:** Investigate whether the *same intact macroscopic physical object* can enter station A and emerge from spatially separated station B, then repeat from B to A.

> **Status (2026-10-22):** Concept/literature stage. **No verified physical-object teleportation. No verified physical traversable wormhole. No functioning PhaseGate prototype.** Quantum teleportation transfers quantum information, not physical matter. An analogue/simulation/optical effect must never be reported as macroscopic transfer.

## Research navigation
- [Program charter](docs/charter.md) · [Roadmap](docs/roadmap.md) · [Physics evidence](docs/physics/baseline.md) · [Feasibility register](docs/physics/feasibility.md)
- [Research questions](docs/physics/questions.md) · [Literature review rules](docs/physics/review-protocol.md)
- [Engineering requirements](docs/engineering/requirements.md) · [PG-01 instrumentation](docs/engineering/PG-01.md)
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

## Primary literature
- [Bennett et al., PRL 1993](https://doi.org/10.1103/PhysRevLett.70.1895) — quantum-state teleportation.
- [IBM Quantum learning module](https://qiskit.qotlabs.org/learning/courses/basics-of-quantum-information/entanglement-in-action/quantum-teleportation) — information ≠ physical matter.
- [Gao/Jafferis/Wall, JHEP 2017](https://doi.org/10.1007/JHEP12(2017)151) — theoretical wormholes in a specific model.
- [Jafferis et al., Nature 2022](https://doi.org/10.1038/s41586-022-05424-3) — quantum-processor wormhole-like dynamics.
- [Caltech experiment Q&A](https://inqnet.caltech.edu/wormhole2022/) — explicitly no physical spacetime rupture.
- [NASA wormhole explainer](https://science.gsfc.nasa.gov/attic/cosmicopia.gsfc.nasa.gov/qa_sp_sl.html) — no evidence for physical wormholes or method to construct one.

**Governance:** Private scientific notebook, immutable research history through Git commits. Do not commit source PDFs without redistribution rights, secrets, sensitive data, or unreviewed hazardous plans.

© 2026 DPN Technology. All rights reserved. No license to copy or distribute is granted.
