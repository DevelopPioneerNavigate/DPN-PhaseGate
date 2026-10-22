# PhaseGate research data
- literature/sources.json: source IDs, bibliographies, supported narrow claims and explicit non-claims.
- hypotheses/hypotheses.json: falsifiable statement/prediction with source cross-references.
- experiments/manifest.json: **actual conducted runs only** (starts with zero).
- experiments/PG-YYYYMMDD-NNN.json: individual run record after approved safe conduct, linked by manifest.
- templates/experiment.example.json: fabricated synthetic illustration **only**, intentionally outside real manifest.

## Raw evidence
Store large or sensitive data outside Git in access-controlled immutable storage; reference stable internal URI and SHA-256 digest. Preserve raw originals, calibration and clock logs, sham controls, witnesses, experiment safety approval and amendments. Never commit secrets or proprietary external documents without rights. CI verifies format and traceability, **not truth of claims**.
