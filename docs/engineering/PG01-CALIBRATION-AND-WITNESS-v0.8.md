# PG-01 v0.8 — Calibration & Witness Evidence Laboratory

**[← Main repository](../../README.md)** · [PG-01 blueprints](PG-01-BLUEPRINTS.md) · [Native Windows guide](../../desktop/README.md) · [Scientific evidence rules](../physics/EVIDENCE-WORKFLOW.md)

> **This is NOT a physical-transfer device or approved scientific experiment.** The software supports *unreviewed* mass estimates, USB timing-quality diagnostics and external witness-media inventory. No actual hardware calibration, synchronized clocks, camera capture or object teleportation has been demonstrated.

<img src="../../assets/pg01-calibration-evidence-v0.8.svg" width="100%" alt="DPN PhaseGate v0.8 visual evidence pipeline: raw USB, calibration, witness media and separate bench records"/>

## 01 / Practical bench calibration workflow

| Step | Operator provides | Software handles | Unverified condition |
|---|---|---|---|
| 1. Physical setup | Qualified safety review and approved measurement apparatus | No automatic wiring or powering | Not built by this release |
| 2. Reference observations | At least 3 distinct masses with 2 readings each | Parses two-column CSV: reference_g,raw_counts | Source measurements require independent review |
| 3. Provenance | Operator, reference mass set ID and declared reference uncertainty | Fits line; reports R² and residual RMSE | These are not total scale uncertainty |
| 4. Profile generation | Station A or B and recheck interval | Creates exclusive BENCH_CAL_*.json file and digest, with range and expiration | BENCH ESTIMATE / UNREVIEWED |
| 5. In Hardware Lab | Manually load correct station profile | Only converts raw sensor counts inside measured range | Suppresses values if invalid/expired |
| 6. Independent acceptance | Reference certificates and full uncertainty budget | **Future** scientific process | No calibration is certified by code |

Sample synthetic-only data is included: [Reference worksheet](../../examples/SYNTHETIC-pg01-v0.8-reference-worksheet.csv). It cannot be called experimental evidence.

### Calibration software cannot establish
- Full uncertainty, repeatability, hysteresis, environmental drift, mounting or reference traceability.
- Physical identity of USB source or station equipment.
- A causal event from timestamped observations.
- Intact physical-object teleportation.

## 02 / Clock-quality drawing

Host reception times and Pico uptime are different clocks. Arrival-interval jitter and packet gaps can reveal recording problems, but **absolute clock offset remains unknown**. Host USB buffering introduces uncertain delay. Hardware Lab explicitly labels station clocks as **UNSYNCHRONIZED**, and does not compare A/B event times to make physics claims.

| Clock source | Can establish | Cannot establish |
|---|---|---|
| Pico millisecond tick | Device-relative intervals | Absolute UTC occurrence |
| PC monotonic arrival timestamp | Host packet ordering | Exact sensor sample instant |
| Host UTC timestamp | Receipt bookkeeping | True station-to-station time synchronization |
| Arrival-cadence jitter | Transmission/arrival inconsistency | Cross-station causality or simultaneity |

## 03 / Witness recording audit

Calibration & Evidence Lab selects **already recorded** local camera/photo/audio files. It does not operate a live camera or cloud service. The operator must confirm permission and document camera origin/vantage/timestamp limitations.

For each input, an exclusive BENCH_WITNESS_*.json manifest stores local basename only, SHA-256 of media content, source byte size, modified-time metadata, station and operator, and a provenance note. A separate SHA-256 checksum sidecar covers the inventory JSON. **The footage itself is not uploaded, re-encoded or copied.**

These hashes can help detect later file changes. They **cannot authenticate prior recording edits, camera identity, consent validity or a physics event**.

## 04 / Strict evidence categories

- **SYNTHETIC** — old Command Center/Signal Analytics waveforms.
- **REAL USB RAW** — operator-connected Pico 2 sensor counts; no grams inferred.
- **BENCH ESTIMATE / UNREVIEWED** — station-specific regression estimate, limited to tested raw range.
- **BENCH WITNESS** — independently recorded local media index with hashes; not auto-verified.
- **APPROVED EXPERIMENT** — not implemented, no records inserted by the native app.

No v0.8 desktop operation edits the scientific experiment manifest.

## 05 / Test the software

Run in Windows PowerShell after installing the dependencies:

    python -m pip install -r desktop/requirements.txt
    python tools/validate_research.py
    python -m unittest discover -s tests -v
    python tools/validate_readme.py
    python -m desktop

The Windows CI also generates native screenshots and builds and launches the standalone EXE.

## 06 / Physical next steps (not completed)

Qualified electronics review, actual reference weights, uncertainty-budget design, timebase testing with a shared physical event, authorized video capture with privacy controls, and preregistered null controls. No working portal mechanism is claimed.
