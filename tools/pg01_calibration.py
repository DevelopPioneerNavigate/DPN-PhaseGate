#!/usr/bin/env python3
"""PG-01 offline load-cell calibration assistant.

Does not control hardware and does not classify physical object transfer.
Regression residuals are descriptive, not a complete uncertainty budget.
Python standard library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path


def fit_calibration(rows):
    """Fit raw_counts = slope * reference_g + intercept using least squares.

    Require >= 4 rows and >= 3 distinct reference levels, with an explicit
    nonzero reference span. Never claim results establish physical transport.
    """
    points = []
    for i, row in enumerate(rows, 1):
        try:
            x = float(row["reference_g"])
            y = float(row["raw_counts"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"calibration row {i} lacks numeric reference_g/raw_counts") from exc
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError(f"calibration row {i} has nonfinite values")
        if x < 0:
            raise ValueError(f"calibration row {i} has a negative reference mass")
        points.append((x, y))
    if len(points) < 4 or len({x for x, _ in points}) < 3:
        raise ValueError("requires at least four rows and three distinct reference masses")
    n = len(points)
    mean_x = sum(x for x, _ in points) / n
    mean_y = sum(y for _, y in points) / n
    sxx = sum((x - mean_x) ** 2 for x, _ in points)
    if sxx <= 0:
        raise ValueError("insufficient reference-mass variation")
    slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / sxx
    if not math.isfinite(slope) or slope == 0:
        raise ValueError("invalid calibration slope")
    intercept = mean_y - slope * mean_x
    residuals = [y - (slope * x + intercept) for x, y in points]
    sse = sum(residual ** 2 for residual in residuals)
    syy = sum((y - mean_y) ** 2 for _, y in points)
    residual_rms_counts = math.sqrt(sse / n)
    return {
        "sample_count": n,
        "reference_levels": len({x for x, _ in points}),
        "reference_min_g": min(x for x, _ in points),
        "reference_max_g": max(x for x, _ in points),
        "slope_counts_per_g": slope,
        "intercept_counts": intercept,
        "residual_rms_counts": residual_rms_counts,
        "residual_rms_g_equivalent": residual_rms_counts / abs(slope),
        "r_squared": (1.0 - sse / syy) if syy > 0 else None,
        "method": "ordinary_least_squares_descriptive_only",
        "warning": "No uncertainty certification, no object teleportation or arrival detection.",
    }


def calibration_file(path):
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or not {"reference_g", "raw_counts"}.issubset(reader.fieldnames):
            raise ValueError("CSV must include reference_g and raw_counts columns")
        return fit_calibration(list(reader))


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description="DPN PhaseGate PG-01 offline measurement calibration: not a portal.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("calibrate", help="fit a plain CSV calibration, with descriptive residuals").add_argument("file", type=Path)
    sub.add_parser("sha256", help="compute source file SHA-256").add_argument("file", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "calibrate":
            print(json.dumps(calibration_file(args.file), indent=2, allow_nan=False))
        else:
            print(f"{file_sha256(args.file)}  {args.file}")
    except (OSError, ValueError, OverflowError) as exc:
        print(f"PG-01 CALIBRATION ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
