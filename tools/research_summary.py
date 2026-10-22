#!/usr/bin/env python3
"""Print a factual Markdown research dashboard; no inference of portal progress."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main():
    src = read("data/literature/sources.json")["sources"]
    hypotheses = read("data/hypotheses/hypotheses.json")["hypotheses"]
    runs = read("data/experiments/manifest.json")["experiments"]
    print("# DPN PhaseGate | Research Integrity Snapshot")
    print("")
    print("| Measure | Count |")
    print("|---|---:|")
    for name, count in [
        ("Registered literature sources", len(src)),
        ("Registered hypotheses", len(hypotheses)),
        ("Completed/aborted run records registered", len(runs)),
        ("Verified physical object transfer demonstrations", 0),
    ]:
        print(f"| {name} | {count} |")
    print("")
    print("**Warning:** counts are record inventory, not scientific evidence of a portal.")
    print("Physical-object transfer remains unverified. A passing automated green gate validates structure only.")


if __name__ == "__main__":
    main()
