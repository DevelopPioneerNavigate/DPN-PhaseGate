# PG-01 v1.1 — Reference Event & Timebase Review

[PhaseGate README](../../README.md) · [v1.0 Optical Capture](PG01-OPTICAL-EVIDENCE-v1.0.md) · [AURORA Windows Guide](../../desktop/README.md)

<img src="../../assets/pg01-reference-event-v1.1.svg" width="100%" alt="Two independently saved cameras feed hash-verified reference brightness event analysis, with unknown camera exposure offset and no physical transfer claim"/>

**STATUS — FUNCTIONAL OFFLINE REVIEW SOFTWARE; NO PHYSICAL FLASH TRIAL COMPLETED BY THIS RELEASE.** This is not an automatic clock synchronization procedure, scientifically approved experiment, or physical matter portal.

## Why v1.1

v1.0 stores operator-consented still frames (at most four images per second) with host **post-read** timestamps and independent integrity manifests. Matching receipt times cannot establish the true moment of camera exposure. v1.1 uses those existing **BENCH_OPTICAL** archives to find brightness changes from a prospective shared reference-light event, without inventing actual timing precision.

## Operator workflow

1. Use Optical Evidence Lab to record consented Station A and Station B stills as separate `BENCH_OPTICAL_*` directories, if actual cameras are installed. No live device is needed to explore code or run synthetic tests.
2. Arrange an authorized, safe, independent **common reference flash** so its onset might be visible from both views; ensure nobody sees an unsafe flash or laser. No electrical flash trigger is provided in this repository.
3. Open the **Reference Events** workstation in the native application (or press Ctrl+K and search). Select A and B archive folders; select a broad image region containing the reference stimulus (CENTER, FULL, TOP, BOTTOM, LEFT, RIGHT).
4. Adjust minimum brightness rise in grayscale levels, default 22. The algorithm uses the **first five frames as dark baseline** with a median/MAD noise estimate and requires at least **two sustained bright frames**. If event timing is too early, baseline is saturated, flashes are ambiguous or no sustained change occurs, the result is *inconclusive*.
5. Choose **Analyze Two Bench Captures**. The background worker verifies the SHA-256 of every source JPEG and its original manifest before calculating brightness. It then plots each channel's grayscale trace by **original frame index**. The chart does not use a fraudulent exposure-time axis.
6. If both transitions are found, the report gives a **B-minus-A host-receipt interval bracket** between the last dark and first bright stored frames. If not, it reports inconclusive detection.
7. Optionally export a new `BENCH_REFERENCE_*.json` and companion SHA-256. This does **not** modify original optical evidence or the approved experiment manifest.

## What is computed (and what is not)

| Field | Meaning | Limit |
|---|---|---|
| Baseline | Median brightness in selected ROI from first 5 source frames | Depends on the operator's region and physical illumination |
| Threshold | Baseline + max(user contrast, robust measured noise multiplier) | Heuristic; not a calibrated photometric instrument |
| Detected onset | First frame after dark baseline with 2 consecutive above-threshold frames | Low-frame-rate capture can miss fast events |
| Per-station interval | Stored host monotonic timestamps of adjacent *last-dark* and *first-bright* frames | Post-read camera arrival only, not actual exposure |
| Paired interval | B-minus-A possible **host receipt transition** interval bounds | NOT a certified camera exposure offset; driver latency remains unbounded |
| Physical event simultaneity | **UNKNOWN** | No ground-truth common event identity or camera latency calibration |
| Teleportation | **NO RESULT** | Light-flash reference alone cannot establish matter transfer |

A report of `[−300, +300] ms` (example only) is a **host receipt interval**, not a claim that the photons or physical objects moved between stations in that interval. Software alone cannot bound unknown camera exposure timing, rolling shutter delay, USB buffers or mechanical response.

## Integrity and retention

The reviewer verifies the original frame hashes, byte lengths, ordered receipt timestamps and manifest checksum before processing, and saves the source manifest SHA-256 identifiers with any later review. Tampered frames fail closed. Analysis files are created exclusively; old files are not overwritten. The review never copies the recordings, opens a camera, accesses audio, uploads media or creates an approved experimental record.

These checks are **integrity of bytes only**. A maliciously created/manipulated original file or spoofed station label can still be internally hash-consistent. Independent observers, physical mounting records, blinded controls, and an externally measured common optical event are required for stronger inference.

## Suggested real bench-validation protocol (not yet performed)

1. Qualified reviewer checks safe, commercially certified camera setup and permissions.
2. Place a high-contrast reference target within both fields of view with clearly visible before/after illumination.
3. Collect multiple **null controls** (no flash) and deliberate single-frame distractors; test false detections before attempting a shared flash.
4. Characterize driver latency and exposure timing under controlled conditions, ideally using a traceable high-speed electrical/optical reference separate from the PC.
5. Run repeated physical flash trials with documented ambient light, camera exposure controls, frame rate and witnessed synchronization control.
6. Pre-register the method, disclose dropped frames and uncertainty, and independently replicate before drawing any engineering timing conclusions.

**No reference-flash trial, clock calibration, or physical object transport was conducted in this code release.**

## Developer / Windows test

```powershell
python -m pip install -r desktop/requirements.txt
python -m unittest discover -s tests -v
python tools/validate_research.py
python tools/validate_readme.py
python -m desktop
```

GitHub Actions exercises synthetic JPEG fixtures (including tamper/flicker/null cases), opens all 11 native screens, captures a **Reference Events** screenshot, builds a standalone Windows EXE and launches its packaged self-test. `Ctrl+K` accesses every workstation.
