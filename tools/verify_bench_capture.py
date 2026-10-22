#!/usr/bin/env python3
"""Offline inspection of PG-01 unverified USB bench captures.

Verifies file bytes and record sequencing; it does NOT verify science or
instrument accuracy. Python standard-library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


def verify(path: Path):
    path=Path(path)
    if not path.name.startswith("BENCH_") or path.suffix!=".jsonl":
        raise ValueError("only BENCH_*.jsonl files are accepted")
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    sidecar=path.with_suffix(".sha256")
    digest_text=sidecar.read_text(encoding="ascii").strip()
    if digest_text != digest+"  "+path.name:
        raise ValueError("missing or mismatched original SHA-256 sidecar")
    rows=[]
    for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():
            raise ValueError(f"empty record line {number}")
        rows.append(json.loads(line))
        if not isinstance(rows[-1],dict):
            raise ValueError("non-object record")
    if len(rows)<2 or rows[0].get("kind")!="header" or rows[-1].get("kind")!="footer":
        raise ValueError("missing signed-off header/footer")
    if rows[0].get("provenance")!="LIVE_USB_RAW_UNCALIBRATED_NOT_AN_APPROVED_EXPERIMENT":
        raise ValueError("wrong evidence provenance: not a real uncalibrated capture")
    if rows[0].get("schema")!="PG-BENCH-1":
        raise ValueError("unknown bench schema")
    seq={}
    counts={"A":0,"B":0}
    errors=0
    for number,record in enumerate(rows[1:-1],2):
        kind=record.get("kind")
        if kind not in ("sample","error","connection","ended"):
            raise ValueError(f"unknown event on line {number}")
        sid=record.get("station")
        if sid not in ("A","B") or not isinstance(record.get("port"),str):
            raise ValueError(f"invalid station/port on line {number}")
        if not isinstance(record.get("connection_session"),str) or not record["connection_session"]:
            raise ValueError(f"missing session provenance on line {number}")
        when=record.get("host_utc")
        if not isinstance(when,str) or not when.endswith("Z"):
            raise ValueError(f"missing UTC host timestamp on line {number}")
        datetime.fromisoformat(when.replace("Z","+00:00"))
        if not isinstance(record.get("host_monotonic_ns"),int) or record["host_monotonic_ns"]<0:
            raise ValueError(f"invalid monotonic timestamp on line {number}")
        if kind!="sample":
            if kind=="error":
                errors+=1
            continue
        sample=record.get("sample")
        if not isinstance(sample,dict) or sample.get("station")!=sid:
            raise ValueError(f"missing or mismatched sample on line {number}")
        if not isinstance(sample.get("raw_counts"),int) or not -(1<<23)<=sample["raw_counts"]<1<<23:
            raise ValueError(f"invalid ADC counts on line {number}")
        sequence=sample.get("sequence")
        key=(sid,record["connection_session"])
        if not isinstance(sequence,int) or sequence<0 or (key in seq and sequence<=seq[key]):
            raise ValueError(f"non-monotonic USB sample sequence on line {number}")
        seq[key]=sequence
        counts[sid]+=1
    if rows[-1].get("sample_count")!=sum(counts.values()):
        raise ValueError("footer sample_count does not match real sample records")
    return {"result":"STRUCTURAL BENCH INTEGRITY PASS (NOT SCIENTIFIC VALIDATION)",
            "sha256":digest,"A_samples":counts["A"],"B_samples":counts["B"],
            "reported_errors":errors,"total_records":len(rows)}


def main(argv=None):
    parser=argparse.ArgumentParser(description="Verify PG-01 uncalibrated bench JSONL and hash")
    parser.add_argument("file",type=Path)
    args=parser.parse_args(argv)
    try:
        print(json.dumps(verify(args.file),indent=2))
    except (OSError,ValueError,TypeError,json.JSONDecodeError) as exc:
        parser.exit(1,f"BENCH CAPTURE FAIL: {exc}\n")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
