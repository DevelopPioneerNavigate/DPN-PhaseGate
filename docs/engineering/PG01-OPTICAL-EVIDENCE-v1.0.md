# DPN PhaseGate v1.0 — Optical Evidence & Timebase Lab

[← PhaseGate README](../../README.md) · [Native Windows guide](../../desktop/README.md) · [PG-01 blueprint gallery](PG-01-BLUEPRINTS.md) · [Evidence integrity standards](../physics/EVIDENCE-WORKFLOW.md)

> **Design boundary:** PhaseGate has not built a physical teleportation mechanism, demonstrated physical-object transport, or connected/validated cameras during this software development. This program is for safe bench observation and data integrity, not matter transfer.

<img src="../../assets/pg01-optical-evidence-v1.0.svg" width="100%" alt="V1.0 native optical evidence system: two operator-permission cameras, a Qt preview, local bench media hashes and non-sync timing indicators"/>

## Optical system block diagram

```text
                   OPERATOR CONSENT
                          |
           +--------------+-------------+
           |                            |
    USB CAMERA A                  USB CAMERA B
    Camera index 0..7             Camera index 0..7
           |                            |
       Preview only                  Preview only
           |                            |
    User clicks Record           User clicks Record
           |                            |
    BENCH_OPTICAL_A/...           BENCH_OPTICAL_B/...
       frame_00000.jpg               frame_00000.jpg
       frame_00001.jpg               frame_00001.jpg
       manifest.json                 manifest.json
       manifest.sha256               manifest.sha256
           |                            |
        Per-frame hash                Per-frame hash
           |                            |
           +---------------+------------+
                           |
             HOST ARRIVAL-TIME DIAGNOSTICS
           (NOT camera exposure timestamps)
                           |
                 NO VERIFIED SYNC
                 NO EXPERIMENT CLAIM
```

This is a functional **local camera capture workflow**, not an illustration of a physical portal or a fully approved experimental protocol.

## What's genuinely implemented

| Capability | Implementation | Important limitation |
|---|---|---|
| Camera access | Open/close explicitly selected local OpenCV camera indices 0–7 | The operator must confirm permission; no device auto-opens |
| Live native preview | Qt display of local JPEG frames emitted by background worker | Not a calibrated instrument or authenticated witness |
| Dual camera assignment | A and B must select distinct indices | USB device index isn't cryptographically tied to a specific physical unit |
| Local still recording | Separate permission dialog, user-selected folder and new unique BENCH_OPTICAL directory | Video stream isn't saved; it saves JPEG stills at up to 4/s, max 1,200 frames |
| Original frame evidence | Each frame stored independently with SHA-256, byte count, host UTC and monotonic post-read timestamp | Hashes detect later changes; they do not authenticate the initial scene |
| Capture end audit | `manifest.json` and `manifest.sha256` written on stop/disconnect | A power failure can leave a partial directory without a closed manifest |
| Verify stored capture | Recheck per-frame hashes, byte lengths, sequence/order and manifest checksum | Not a scientific validity assessment |
| Arrival jitter diagnostics | Track independent A/B USB frame receipt intervals and apparent delays | Does not measure camera exposure time, true clock offset or actual cross-station synchronization |
| Windows EXE | Onefile PyInstaller with Qt and bundled OpenCV | Build/download artifact must pass CI; no paid service required |

The app does not capture audio, recognize faces, record in the background without permission, auto-post data, read the experiment manifest for writes, or open its cameras during CI smoke tests.

## Privacy-first operator instructions

1. Make sure everyone in view is authorized to be recorded. Protect the privacy of workspaces and other individuals.
2. Open **Optical Evidence** from the native PhaseGate sidebar or Ctrl+K palette.
3. Choose the actual local camera index for Station A or B; check the physical feed. Never infer an index maps to a particular physical location without inspection.
4. Click **OPEN PREVIEW**, read the consent prompt, and confirm. The app opens that camera only after confirmation.
5. To write files, separately click **RECORD STILLS**, approve and select a private local parent directory.
6. Click **STOP / HASH** to close manifest and frame hashes; or **CLOSE** to stop camera access.
7. Use **VERIFY EXISTING BENCH FOLDER** to check the frame hashes and local manifest later.

**No permanent automatic capture, no audio, no webcam autostart, no uploading.** Directory names begin with `BENCH_OPTICAL_`; files live wherever the operator selected. A new recording directory is exclusive-create; it never silently overwrites old bench evidence.

## What timing diagnostics actually establish

The camera worker calls `cv2.VideoCapture.read()` and then records `time.monotonic_ns()` and a host UTC string. These times are **after** the driver's blocking read returns and after USB buffering, so they are *arrival/receipt times*, not the instant sensor exposure occurred.

The `TimebaseHealth` class computes displayed host-arrival interval variability, obvious frame delays and clock-order failures for each camera. The two camera streams use the same PC monotonic clock but their **exposure delays are unknown**. Thus:

- **A/B exposure offset: UNKNOWN**
- **Station event simultaneity: NOT VALIDATED**
- **Cross-station optical clock sync: NOT VERIFIED**
- **No transfer inference is derived from timing alone**

A later experiment may use a physical reference flash visible on both independent cameras, externally measured event times, instrument latency tests and a defensible uncertainty interval. That work is not implemented or claimed here.

## Actual science versus bench evidence

The optical BENCH directory is separate from the read-only real experiment registry at `data/experiments/manifest.json`. The existing Dashboard and Station Matrix visuals still display **SYNTHETIC** artwork. USB sensor values in Hardware Lab are live **RAW COUNTS** when explicitly connected. Calibrated station mass values remain **unreviewed** estimates. Camera files are **UNVERIFIED OPTICAL BENCH** until physical provenance and protocols are assessed.

## Verify code and executable

On Windows, after `python -m pip install -r desktop/requirements.txt`:

```powershell
python -m unittest discover -s tests -v
python tools/validate_research.py
python tools/validate_readme.py
python -m desktop
```

The GitHub Windows workflow also visits every native screen, asserts that zero cameras were automatically opened, captures an Optical Lab screenshot, builds the EXE and launches the final bundle for a packaged self-test.

## Next physical gates

An actual authorized bench system still needs approved cameras, documented lighting/frame rate, stable physical mounting, a common witnessed reference stimulus, independently measured USB/driver latency, operator consent/retention policy and independent review. No intact-object physical transport result exists.
