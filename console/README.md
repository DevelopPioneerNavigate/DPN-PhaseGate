# DPN PhaseGate | Local Research Console v0.5

[Main README](../README.md) | [Prototype specifications](../docs/engineering/PG01-PROTOTYPE-SPECS-v0.5.md) | [Visual Atlas](../docs/VISUAL-ATLAS.md)

## What works

A responsive DPN-themed UI with two synthetic measurement stations, live-refreshing mock mass traces, synthetic audit events, real repository research inventory counts and a clearly labelled demo JSON export. This is **NOT** a real physical experiment, device connection, camera capture, or working portal.

## Windows double-click

Run START_PHASEGATE_CONSOLE.bat from the project root (Python 3.12+ must be installed), or in PowerShell run:

    py -3 -m console.server --port 8765

Open http://127.0.0.1:8765 and stop with Ctrl+C. This is a local-only server, no packages or paid tokens needed.

## Routes

| Path | Response | Evidence? |
|---|---|---|
| / | DPN-themed interface | No |
| /api/overview | Research registry counts | Inventory only |
| /api/telemetry | **Synthetic** station A/B waveforms | No |
| /api/events | **Synthetic** audit messages | No |

Generated data is never saved to the actual experiment manifest. A simulated mass trace is not calibrated measurement uncertainty and cannot validate matter transfer.

## Tests

    python tools/validate_research.py
    python -m unittest discover -s tests -v
    python tools/validate_readme.py

**Security:** server binds 127.0.0.1 only, uses a static file allowlist, does not support POST writes, and has no hardware controls or authentication. Never expose this prototype to public networks. Future physical sensors and camera capture require a separate design/security review.
