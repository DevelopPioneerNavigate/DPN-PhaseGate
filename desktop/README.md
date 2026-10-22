# DPN PhaseGate v0.6 — Native Windows Research Console

[Main repository](../README.md) · [Research atlas](../docs/VISUAL-ATLAS.md) · [PG-01 specs](../docs/engineering/PG01-PROTOTYPE-SPECS-v0.5.md)

**Windows-native Qt application, not a browser page, Electron wrapper or localhost server.** The previous web prototype is retained separately in `console/` as historical reference.

> **Scientific limitation:** All station readings are SYNTHETIC. No sensors, cameras or portal hardware are connected; no actual experiment or physical-object transfer is claimed.

## Download the .exe

Open **[GitHub Actions: PhaseGate Native Windows EXE](https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/actions/workflows/native-windows-exe.yml)**. Choose the latest **successful** run and download the **DPN-PhaseGate-Native-Windows-v0.6** artifact under Artifacts. Extract `DPN-PhaseGate.exe` and double-click it. **No Python installation or browser is needed to run the built EXE.**

The same workflow also publishes **DPN-PhaseGate-Native-Preview-v0.6**, an actual screenshot rendered by Qt during the Windows smoke test. These artifacts expire after 30 days; new successful runs create fresh downloadable artifacts.

**Windows SmartScreen:** An unsigned executable can show a caution prompt. Verify the origin, commit, CI run and file hash before launch. Do not disable antivirus to bypass security warnings. Code signing will require a later authenticated release process.

## Build or run from source

Install Python 3.12+ on Windows:

```powershell
python -m pip install -r desktop/requirements.txt
python -m desktop
```

Build on Windows:

```powershell
python tools/generate_desktop_icon.py
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "DPN-PhaseGate" --icon build/phasegate.ico --add-data "data;data" launch_phasegate.py
```

The resulting application lives at `dist/DPN-PhaseGate.exe`.

## Native screens

| Desktop screen | Working functionality |
|---|---|
| Command Center | Animated DPN orbital emblem, metrics, signal trace and navigation |
| Station Matrix | Independent A/B station cards, mock telemetry, real readiness disclosure |
| Signal Analytics | Hand-painted waveform plots and deterministic demo values |
| Research Vault | Real bundled primary-literature bibliography with source opening |
| Experiment Ledger | Read-only real-run count, explicit evidence and control requirements |
| System Diagnostics | Qt/Python/OS information, integrity check and labeled mock JSON export |
| Preferences | Actual animation toggle, data refresh interval and demo export |

## Security and data integrity

- Desktop application uses **no HTTP server**, open TCP ports, accounts or background services.
- Read-only bundled scientific data is included via PyInstaller `--add-data "data;data"`.
- Actual run manifest remains unchanged; export explicitly requires `SYNTHETIC_` names and provenance.
- A validated Python/QPainter desktop UI does not demonstrate matter teleportation.
- No live USB connection, physical hardware control, device drivers or camera capture.
- Before commercial/proprietary redistribution, evaluate the LGPL obligations of Qt/PySide6 and dependency terms; the project does not grant others a license to DPN intellectual property.

## Quality

```powershell
python tools/validate_research.py
python -m unittest discover -s tests -v
python tools/validate_readme.py
python launch_phasegate.py --smoke-test --screenshot build/test.png
```

GitHub Actions runs on a Windows host, creates a native UI screenshot, packages a true windowed single-file EXE, and performs a packaged self-test before publishing download artifacts.
