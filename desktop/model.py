"""PhaseGate native application's read-only scientific state.

No sensor drivers, device control, or physical portal functionality exists here.
"""
from __future__ import annotations
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.9.0"
MODE = "SYNTHETIC"
DISCLAIMER = (
    "SIMULATED CHARTS — optional LIVE USB RAW bench measurements in Hardware Lab. "
    "NO OBJECT TELEPORTATION HAS BEEN OBSERVED OR VERIFIED."
)
DOC_BASE = "https://github.com/DevelopPioneerNavigate/DPN-PhaseGate/blob/main/"


def repository_root():
    """PyInstaller sets _MEIPASS for the extracted application bundle."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def read_registry(filename: str, key: str, root: Path | None = None):
    base = root if root is not None else repository_root()
    try:
        payload = json.loads((base / filename).read_text(encoding="utf-8"))
        values = payload.get(key)
        return values if isinstance(values, list) else None
    except (OSError, TypeError, json.JSONDecodeError):
        return None


def inventory(root: Path | None = None):
    sources = read_registry("data/literature/sources.json", "sources", root)
    hypotheses = read_registry("data/hypotheses/hypotheses.json", "hypotheses", root)
    experiments = read_registry("data/experiments/manifest.json", "experiments", root)
    return {
        "sources": len(sources) if sources is not None else None,
        "hypotheses": len(hypotheses) if hypotheses is not None else None,
        "experiments": len(experiments) if experiments is not None else None,
        "transfer_verified": False,
        "mode": MODE,
        "version": VERSION,
        "disclaimer": DISCLAIMER,
    }


def literature(root: Path | None = None):
    sources = read_registry("data/literature/sources.json", "sources", root)
    if sources is None:
        return []
    return [
        {"id": str(s.get("id", "?")), "title": str(s.get("title", "")),
         "type": str(s.get("type", "")), "url": str(s.get("url", ""))}
        for s in sources if isinstance(s, dict)
    ]


def simulated_samples(frame: int, count: int = 100):
    """Synthetic, deterministic graphical traces: no measurement implications."""
    if frame < 0 or not 1 <= count <= 1000:
        raise ValueError("invalid demo frame or sample count")
    samples = []
    for i in range(count):
        t = (frame - count + i + 1) * 0.17
        a = 42.0 + math.sin(t) * .33 + math.cos(t * .41) * .10
        b = math.sin(t * 1.27) * .028 + math.cos(t * .23) * .012
        samples.append((round(a, 4), round(b, 4)))
    return samples


def snapshot(frame: int = 120):
    points = simulated_samples(frame, 120)
    return {"mode": MODE, "version": VERSION, "frame": frame,
            "station_a_g": points[-1][0], "station_b_g": points[-1][1],
            "hardware_connected": False, "physical_transfer_verified": False,
            "samples": [{"a_g": a, "b_g": b} for a, b in points],
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "disclaimer": DISCLAIMER}


def export_demo(destination: Path, frame: int, root: Path | None = None):
    """Explicit user export, hard-coded SYNTHETIC name/content.

    Never touches data/experiments or the real run manifest.
    """
    if not destination.name.startswith("SYNTHETIC_"):
        raise ValueError("demonstration exports must start with SYNTHETIC_")
    if destination.suffix.lower() != ".json":
        raise ValueError("demonstration export must be JSON")
    data = {"provenance": "SOFTWARE-GENERATED DEMONSTRATION — NOT RESEARCH EVIDENCE",
            "inventory": inventory(root), "telemetry": snapshot(frame)}
    destination.write_text(json.dumps(data, indent=2, allow_nan=False), encoding="utf-8")
    return destination
