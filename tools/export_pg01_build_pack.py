#!/usr/bin/env python3
"""Free PG-01 build pack generator. Uses ONLY checked-in engineering data.

No purchases, equipment operations, test results or approved experiments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.build_plan import export_bom_csv, read_manifest, validate_manifest


def pack(target,root=None):
    doc=read_manifest(root)
    target=Path(target)
    target.mkdir(parents=True,exist_ok=True)
    bom=target/"PG01-proposed-BOM.csv"
    tasks=target/"PG01-workpackages.json"
    sources=target/"PG01-manifest-snapshot.json"
    for filename,content in (
        (bom,export_bom_csv(doc).encode("utf-8-sig")),
        (tasks,(json.dumps({
            "notice":"PROPOSED ENGINEERING / NO ASSEMBLY OR PROCUREMENT VERIFIED",
            "work_packages":doc["work_packages"],"gates":doc["gates"]},
            indent=2)+"\n").encode("utf-8")),
        (sources,(json.dumps(doc,indent=2)+"\n").encode("utf-8"))
    ):
        if filename.exists():
            raise FileExistsError("existing build pack file: "+str(filename))
        filename.write_bytes(content)
    digest=target/"SHA256SUMS.txt"
    with digest.open("x",encoding="ascii") as f:
        for path in (bom,tasks,sources):
            f.write(hashlib.sha256(path.read_bytes()).hexdigest()+
                    "  "+path.name+"\n")
    return target


def main(argv=None):
    parser=argparse.ArgumentParser(description="DPN PhaseGate offline construction evidence packet")
    parser.add_argument("--check",action="store_true",help="only validate engineering manifest")
    parser.add_argument("--out",type=Path,default=Path("build/pg01-engineering-pack"))
    args=parser.parse_args(argv)
    doc=read_manifest()
    if args.check:
        print("PG-01 ENGINEERING MANIFEST VALID: components=%d workpackages=%d gates=%d"%
              (len(doc["components"]),len(doc["work_packages"]),len(doc["gates"])))
        print("ALL PROCUREMENT/ASSEMBLY STATES REMAIN UNVERIFIED")
        return 0
    folder=pack(args.out)
    print("PG-01 engineering pack created:",folder)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
