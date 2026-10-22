# DPN PhaseGate v0.7 — Real USB Instrument Monitoring

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
