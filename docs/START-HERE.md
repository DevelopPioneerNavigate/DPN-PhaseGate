# Start here | Find what matters in 30 seconds
[← Back to PhaseGate](../README.md) · [Full overview](PROJECT-OVERVIEW.md)

<img src="../assets/phasegate-research-pipeline.svg" alt="How PhaseGate links research sources to approved experiment records" width="100%">

**Prefer pictures?** [Open the Visual Research Atlas](VISUAL-ATLAS.md) for engineering blueprints, research diagrams, and a guided route through the repository.

PhaseGate is an **R&D program**, not an existing matter-transmitting machine. Pick the task you came here to do:

| I want to... | Open this | First thing to check |
|---|---|---|
| Understand the project | [Project overview](PROJECT-OVERVIEW.md) | Vision vs. demonstrated science |
| Review quantum/wormhole claims | [Physics baseline](physics/baseline.md) | What experiments actually demonstrated |
| Browse **actual illustrations** and vendor equipment photos | [Blueprint gallery](engineering/PG-01-BLUEPRINTS.md) | Explicitly labelled conceptual drawings and sourced component references |
| See the device concept | [PG-01 architecture](engineering/PG-01-architecture.md) | Station A/B measurement pathways |
| Plan hardware | [Implementation plan](engineering/PG01-IMPLEMENTATION-PLAN.md) | Dependencies and unresolved requirements |
| Check instrument candidates | [Selection matrix](engineering/PG-01-bom.csv) | Compatibility and calibration requirements |
| Follow project progress | [Roadmap](roadmap.md) | Stages, blockers, exit criteria |
| Verify an experimental claim | [Evidence policy](../data/README.md) | Original records, controls, uncertainties and hashes |
| Help research | [Issues](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/issues) | Source-backed, falsifiable questions |
| Run test checks locally | [Validation guide](qa/validation.md) | Software green ≠ physics confirmed |

## Quick local setup

```bash
git clone https://github.com/DevelopPioneerNavigate/DPN-PhaseGate.git
cd DPN-PhaseGate
python tools/validate_research.py
python -m unittest discover -s tests -v
python tools/validate_readme.py
```

No hardware required; the data fixtures are **synthetic**. No external Python dependencies are needed. A real prototype, when approved and developed, will receive separate setup instructions.

## Evidence levels

**Theory** is not a **simulation**, a simulation is not an **observed lab effect**, and an observed lab effect is not **independently replicated object teleportation**. See the [evidence baseline](physics/baseline.md).

## Before proposing experimental hardware

Read [safety rules](safety/safety.md), [engineering requirements](engineering/requirements.md), and [protocol draft](protocols/PG-PROT-NULL-001.md). No experiments are authorized by simply opening a GitHub issue.
