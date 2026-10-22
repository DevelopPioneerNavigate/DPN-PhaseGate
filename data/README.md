# PhaseGate research data

**[Visual Atlas](../docs/VISUAL-ATLAS.md) · [Evidence workflow](../docs/physics/EVIDENCE-WORKFLOW.md) · [Run manifest](experiments/manifest.json)**

<img src="../assets/pg01-dataflow-diagram.svg" width="100%" alt="Raw evidence and manifest lifecycle"/>

> **Visual guide:** Hash evidence helps detect changes but cannot prove an original file was truthful. Real experimental runs and synthetic examples remain separate.

---

- literature/sources.json: source IDs, bibliographies, supported narrow claims and explicit non-claims.
- hypotheses/hypotheses.json: falsifiable statement/prediction with source cross-references.
- experiments/manifest.json: **actual conducted runs only** (starts with zero).
- experiments/PG-YYYYMMDD-NNN.json: individual run record after approved safe conduct, linked by manifest.
- templates/experiment.example.json: fabricated synthetic illustration **only**, intentionally outside real manifest.

## Raw evidence
Store large or sensitive data outside Git in access-controlled immutable storage; reference stable internal URI and SHA-256 digest. Preserve raw originals, calibration and clock logs, sham controls, witnesses, experiment safety approval and amendments. Never commit secrets or proprietary external documents without rights. CI verifies format and traceability, **not truth of claims**.
