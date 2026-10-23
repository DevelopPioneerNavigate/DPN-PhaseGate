# DPN PhaseGate v1.6 — First-Article Inspection Lab

Under **Gate Engineering → 05 FIRST ARTICLE**, select a trial CAD part and a physical specimen, record **two actually observed dimensions** for a feature with a responsible operator, measurement-tool ID and physical evidence reference. Missing/failed observations remain HOLD. Even with all readings in the candidate range, the part is labelled **TRIAL DIMENSIONS RECORDED / PHYSICAL REVIEW REQUIRED**, not manufactured or independently certified.

The related source-controlled engineering sheets and printable SVG inspection cards are documented in [PG-01 First-Article v1.6](../hardware/assembly/PG01-FIRST-ARTICLE-v1.6.md). The free OpenSCAD GitHub workflow exports the candidate parts alongside inspection sheets and empty measurement templates. The displayed figures are **proposed dimensions**, not physical test results.

---

# DPN PhaseGate v1.5 — Assembly Studio / Physical Gate Engineering

**New 13th native workspace:** an interactive XYZ-based assembly view of the two-gate PG-01 Rev B machine. Hide/show six engineering groups, select 15 physical part envelopes, explode the assembly and switch between isometric, front and top views. The view is derived from source-controlled engineering geometry and checked against the existing physical rig manifest.

**Corrected geometry:** proposed rail travel is 900 mm rather than the earlier 680 mm, so it spans Gate A and Gate B centers 800 mm apart. The passive rail has been lifted into the gate clear opening; automated radial clearance and end-reserve checks fail if these design relationships become invalid.

[Detailed dimensions and joint interfaces](../hardware/assembly/PG01-REV-B-INTERFACES-v1.5.md) · [Interactive assembly source](assembly_page.py) · [New OpenSCAD interface CAD](../hardware/cad/pg01_assembly_v1_5.scad) · [GitHub release artifacts](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml)

The viewer is an **unbuilt engineering design**; no instrument control, automatic fabrication, proof of a portal field, or physical safety approval is implied.

---

# DPN PhaseGate v1.4 — Fabrication Readiness

The native Gate Engineering workspace now includes a **FIT & RECEIVING** tab to enter actual measurements from manufactured parts and log component receiving states. All entries require human operator identification and an evidence reference, remain marked **not independently verified**, and persist locally. Actual parts are not assumed bought or assembled.

Use a qualified mechanical review to approve fabrication tolerance and measurement tools before treating trial ranges as manufacturing limits.

# DPN PhaseGate v1.3 — Gate Engineering & Physical Build Workbench

**The native Windows EXE now has a twelfth workspace — Gate Engineering.** It loads the actual PG-01 project specification directly from the bundled source-controlled engineering manifest, draws the dimensioned Gate A/B rig, shows all 12 component groups and 9 dependency-linked build work packages, and allows responsible operators to record progress with an evidence note. All assembly progress begins as **planned**, and review gates never auto-approve safety.

[Physical rig proposal](../hardware/README.md) · [Assembly instructions](../hardware/assembly/PG01-ASSEMBLY-PLAN.md) · [Free OpenSCAD CAD](../hardware/cad/pg01_bench.scad) · [Download printable trial parts](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/pg01-cad.yml)

**Windows download:** open the [v1.3 native EXE workflow](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml), select a green run and download `DPN-PhaseGate-Native-Windows-v1.3`. There is an extra real Qt screenshot of Gate Engineering in the v1.3 preview bundle.

**Actual fabrication and safety review are still ahead.** An approved electrical/structural prototype and a scientifically established transport mechanism cannot be inferred from a concept drawing. This software provides a practical path to measure and verify the assembly.

---

# DPN PhaseGate v1.2 — NEXUS Native Windows Mission Cockpit

**Complete native Qt visual reconstruction:** new compact station-workspace dock, dramatic procedural concept-field illustration, interactive operator console, condensed research data row, permanent safety footer and a redesigned Station Matrix. The application still has all 11 fully functional workspaces and a standalone EXE—**no web browser or Python installation required** at runtime.

[**Visual architecture / keyboard navigation →**](../docs/design/NEXUS-v1.2.md) · [**Download latest successful Windows v1.2 EXE →**](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml)

Use `Ctrl+K` for workspace search, `Ctrl+B` to show or hide the dock, or `F11` to present NEXUS fullscreen. Existing USB port/camera features remain deliberately opt-in, and research data categories remain separated.

**Truth in visuals:** Glowing NEXUS structure and station fields are synthetic concept design, not a physical portal or a sensor waveform. There are still no verified object-transfer experiments.

---

## v1.1 optical research foundation

# DPN PhaseGate v1.1 — Reference Event & Timing Analysis

<img src="../assets/pg01-reference-event-v1.1.svg" width="100%" alt="DPN Technology PG-01 reference flash event analysis system"/>

**Eleventh native AURORA workstation: Reference Events.** Cross-camera time subtraction is **OFF by default** and requires an explicit operator declaration of a shared, uninterrupted computer monotonic epoch with overlapping recording windows; still not verified camera synchronization.  Select two operator-recorded and SHA-256 verified `BENCH_OPTICAL_*` directories, choose an image region for each camera, detect a sustained bright flash after baseline, view separate brightness traces and report bounded **HOST POST-READ RECEIPT intervals only**.

**Download the native Windows EXE:** open [PhaseGate Windows build artifacts](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml), select the latest **successful** run, download `DPN-PhaseGate-Native-Windows-v1.1`, extract `DPN-PhaseGate.exe` and launch it. The `DPN-PhaseGate-Native-Preview-v1.1` artifact also contains a screenshot of the new native Reference Event Lab.

**Scientific boundary:** Camera source, exposure, USB/driver latency and simultaneity remain unknown. An apparent difference between flash arrivals is **NOT physical event-time difference** and is not proof of a portal, transport or synchronized cameras. Only independently sourced recordings are accepted; no camera is opened by this analysis page.

[Full Reference Events operator procedure and limitations →](../docs/engineering/PG01-REFERENCE-EVENT-v1.1.md)

---

## v1.0 Optical Evidence foundation

# DPN PhaseGate v1.0 — Optical Evidence and Timebase Lab

<img src="../assets/pg01-optical-evidence-v1.0.svg" width="100%" alt="DPN v1.0 native optical evidence and bench timebase pipeline"/>

**New Optical Evidence screen (ten total):** operator-confirmed local Camera A/B previews, independently consented JPEG frame capture, hash/audit manifest per station and actual host frame-arrival jitter diagnostics. No webcam automatically starts, and camera source/exposure time synchronization is **not** claimed.

**Download:** open [PhaseGate Windows EXE builds](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml), choose the latest successful run and download `DPN-PhaseGate-Native-Windows-v1.0` from Artifacts. The matching preview bundle includes the new Optical Lab screenshot. Unzip and double-click `DPN-PhaseGate.exe`; Python and a browser are not required on the user's PC.

**Permissions:** Only allow cameras you own or are authorized to view. A second approval is required before recording. The app stores JPEG stills locally in user-chosen `BENCH_OPTICAL_*` directories, with hashes. There is no cloud upload, automatic webcam recording, audio, object tracking or actual physical experiment.

[**Full operator guide and timebase limitations →**](../docs/engineering/PG01-OPTICAL-EVIDENCE-v1.0.md)

---

## v0.9 AURORA interface foundation

# DPN PhaseGate v0.9 — AURORA Native Research Command Center

**The interface has been extensively rebuilt and is still a native Windows EXE, not a browser wrapper.**

[**Explore the complete AURORA design guide**](../docs/design/AURORA-v0.9.md) · [GitHub Actions Windows Downloads](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml)

The primary experience now includes a multi-layer hand-drawn AURORA research field, new cinematic research mission hero, richer station illustrations, redesigned application navigation, and a four-stage research-readiness rail. Use **Ctrl+K** to open the keyboard command palette, **Ctrl+1–9** to switch workspaces, or **F11** for an immersive presentation.

**Standalone EXE:** download `DPN-PhaseGate-Native-Windows-v0.9` from the latest successful Windows workflow run (under Artifacts), unzip and launch `DPN-PhaseGate.exe`. The screenshot bundle is `DPN-PhaseGate-Native-Preview-v0.9`. Neither requires a browser, external API token or Python installation at runtime.

**Scientific boundary:** AURORA's glowing geometry is **concept artwork, not a real portal**. The Command Center/Station Matrix/Signal Analytics are SYNTHETIC; only an explicitly connected Hardware Lab displays live, uncalibrated USB RAW counts. Calibration profiles are unreviewed estimates, recordings remain operator-selected witness inventories, and no physical transport experiment has been performed.

---

## v0.8 foundation — Calibration, USB Quality & Witness Evidence

# DPN PhaseGate v0.8 — Calibration, USB Quality & Witness Evidence

[**New: v0.8 Illustrated Calibration + Witness Guide**](../docs/engineering/PG01-CALIBRATION-AND-WITNESS-v0.8.md)

<img src="../assets/pg01-calibration-evidence-v0.8.svg" width="100%" alt="Native PhaseGate calibration, raw USB, witness and unverified evidence pathways"/>

**What is new in the native Windows EXE:** ninth screen **Calibration & Evidence**, station-specific CSV-to-bench-calibration profiles with checksummed parameters and expiration, honest range-limited estimated grams displayed separately from real raw USB counts, USB arrival-jitter diagnostics, and a consent-gated locally selected witness file inventory with SHA-256. Videos are never copied or uploaded and cameras are not activated.

**Get the native Windows v0.8 EXE:** open the [Windows build workflow](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml) and download the `DPN-PhaseGate-Native-Windows-v0.8` artifact from the latest successful run. The preview artifact includes three actual Qt screenshots (main, Hardware Lab and Calibration & Evidence Lab). Hardware calibration and timing alignment remain physically unverified.

---

## v0.7 Foundation — Real USB Instrument Monitoring

[Main repository](../README.md) · [Firmware and flashing](../firmware/pico2_hx711/README.md) · [PG-01 electrical design review](../docs/engineering/PG01-PROTOTYPE-SPECS-v0.5.md) · [Visual atlas](../docs/VISUAL-ATLAS.md)

**What is real in this release:** the native Windows application can now enumerate COM ports, manually connect one port to Station A and another to Station B, read/check raw MicroPython HX711 frames, detect corrupted/out-of-order/stale data and intentionally save unverified bench captures.

**What remains unbuilt/unverified:** the physical sensor stations, camera installation, sensor calibration, independent clock synchronization, laboratory safety approval, real PhaseGate experiments, and any physical-object teleportation mechanism. The old animated orbital visualizations and charts remain **SYNTHETIC ONLY** and never show real bench samples.

## 1 — Download the native EXE

Open the [PhaseGate Windows EXE workflow](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml), choose a **green** run with this v0.7 branch or later merged main, and download **DPN-PhaseGate-Native-Windows-v0.7** from its Artifacts section. Extract and double-click `DPN-PhaseGate.exe` on Windows; it does not require a browser or Python installation. The app is not code-signed; verify its GitHub origin and Windows warning details before opening.

The app uses `PySide6-Essentials==6.12.0`, `pyserial==3.5` and a pinned PyInstaller build on Windows. Bundled dependencies stay inside the EXE. No background cloud services, remote network ports, tokens or subscriptions.

## 2 — Operator workflow (hardware not included)

1. **Do not connect an improvised circuit.** Review the actual breakout board's VCC/VDD logic levels, rated 3.3V GPIO, strain gauge wiring and certified low-voltage power with a qualified electrical reviewer.
2. Install the [official Pico 2 MicroPython firmware](https://micropython.org/download/RPI_PICO2/), then review and save `firmware/pico2_hx711/main.py` on one controller with `STATION_ID="A"` and another with `STATION_ID="B"`. Review the [dedicated firmware guide](../firmware/pico2_hx711/README.md).
3. Once assembled and physically inspected, plug both Pico USB connectors into the PC. Note the actual Windows COM numbers and independent physical stations.
4. Open **Hardware Lab** (the eighth native screen), click **REFRESH PORTS**, select the correct COM device for A and B and **CONNECT** each. No device opens automatically.
5. Live frames display **signed 24-bit RAW COUNTS only**. Status changes to **LIVE USB / RAW**, **STALE**, **FAULT**, or **PORT CLOSED**. A frame whose claimed station does not match your selected port mapping is rejected.
6. For a real bench capture, select **START BENCH RECORDING** and confirm the warning. Save to a new `BENCH_*.jsonl` path of your choice. Stop recording to close, count samples and generate `BENCH_*.sha256` alongside it.
7. Optional offline check: `python tools/verify_bench_capture.py BENCH_example.jsonl`. A passing check confirms structural integrity, not calibration, equipment authenticity or science.

## 3 — Separate scientific data states

| Source | Native view | Unit | Scientific status |
|---|---|---|---|
| Demo math generator | Command Center, Station Matrix, Signal Analytics | Fictional grams | SYNTHETIC / not evidence |
| Operator-connected Pico USB | **Hardware Lab only** | Raw signed ADC counts | LIVE USB RAW / uncalibrated |
| Explicit `BENCH_*.jsonl` | Raw bench capture outside experiment manifest | Counts and time metadata | UNVERIFIED BENCH |
| Approved actual run manifest | Experiment Ledger, read-only | Traceable completed studies | Empty until a real approved experiment |

**Never mistake bench readings for successful physical transfer.** No proof of object identity, instrument calibration, security provenance or temporal causality is implied by live data.

## 4 — Robustness and scientific traceability

- One manually selected USB COM port per station; duplicate port assignments are blocked.
- Per-connection random session IDs protect against queued events from a previous port session appearing as new data.
- Protocol `PG1|station|sequence|uptime_ms|signed24_counts|RAW|xor_hex\n` (maximum 160 bytes, strict ASCII and checksum, station match and 24-bit bounds).
- Sequence gaps, counter rollbacks, packet corruption, loss of USB and silent/stale links are surfaced as faults rather than synthesized readings.
- Host captures include UTC with milliseconds and monotonic nanosecond clock, but **Pico and PC clocks are not synchronized** and the current implementation does not estimate offset/drift. These timestamps must not be used to conclude cross-station timing.
- Serial XOR checksum is **not cryptographic authentication**. SHA-256 sidecars detect post-capture modification but cannot verify sensor provenance or a physical effect.
- Real USB acquisition is strictly **read-only at the protocol level**: no serial commands or hardware actuation. The optional local capture feature writes only user-requested BENCH files.
- No application feature writes to `data/experiments/manifest.json`; experimental claims require independent scientific protocol, safety review and evidence.

## 5 — Windows development checks

```powershell
python -m pip install -r desktop/requirements.txt
python tools/validate_research.py
python -m unittest discover -s tests -v
python tools/validate_readme.py
python -m desktop
```

Firmware syntax validation runs in CI without requiring a physical Pico, but **does not prove electrical compatibility or correct sensor operation**.

## 6 — Development order after v0.7

1. Confirm exact board revisions, select safe rated power and obtain qualified hardware safety review.
2. Bench-test a single approved load cell with documented reference masses and noise/linearity measurements.
3. Add a separate validated calibration profile UI with explicit units, measured uncertainty and expiry, without changing original raw records.
4. Add separate local camera capture and device clock-offset characterization.
5. Continue falsifiable physics hypotheses and preregistered sham controls independently of the station interface.
