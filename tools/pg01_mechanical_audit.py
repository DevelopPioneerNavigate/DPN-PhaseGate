#!/usr/bin/env python3
"""Deterministic PG-01 geometry design gate for CAD CI and operators."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.manufacturing import evaluate_project, cutlist_report


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=None,
                        help="Optional JSON fit-check report; does not approve physical build")
    options=parser.parse_args(argv)
    report=evaluate_project()
    report["cutlist"]=cutlist_report()
    print(json.dumps(report,indent=2))
    if options.out:
        options.out.parent.mkdir(parents=True,exist_ok=True)
        options.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return 0 if report["status"]=="PASS PRELIMINARY FIT CHECK" else 2


if __name__=="__main__":
    raise SystemExit(main())
