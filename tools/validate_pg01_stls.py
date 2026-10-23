#!/usr/bin/env python3
"""Simple offline mesh envelope audit for generated OpenSCAD STL CAD artifacts.

Sanity checks only; not finite element analysis, print strength or safety approval.
"""
from __future__ import annotations

import argparse
import math
import re
from pathlib import Path


class MeshError(ValueError):
    pass


POINT=re.compile(r"^\s*vertex\s+([-+.0-9eE]+)\s+([-+.0-9eE]+)\s+([-+.0-9eE]+)",re.M)


def check_ascii_stl(file,maximum_mm=250):
    path=Path(file)
    if not path.is_file() or not 512<path.stat().st_size<25_000_000:
        raise MeshError("missing or implausible STL size")
    try:
        data=path.read_text(encoding="ascii")
    except UnicodeError as exc:
        raise MeshError("STL expected ASCII encoding") from exc
    if not data.lstrip().startswith("solid ") or "endsolid" not in data:
        raise MeshError("invalid ASCII STL envelope")
    points=[]
    for m in POINT.finditer(data):
        point=tuple(float(x) for x in m.groups())
        if not all(math.isfinite(x) for x in point):
            raise MeshError("nonfinite STL coordinates")
        points.append(point)
    if len(points)<12 or len(points)%3:
        raise MeshError("STL missing a plausible triangle mesh")
    bound=[(min(p[i] for p in points),max(p[i] for p in points)) for i in range(3)]
    size=tuple(hi-lo for lo,hi in bound)
    if any(n<0.5 or n>maximum_mm for n in size):
        raise MeshError("STL exceeds sanity envelope or is degenerate: "+str(size))
    return {"filename":path.name,"triangle_count":len(points)//3,
            "bounds_mm":list(round(x,2) for x in size),
            "interpretation":"PRELIMINARY STL GEOMETRY ONLY / NOT MANUFACTURING APPROVED"}


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("files",type=Path,nargs="+")
    options=ap.parse_args(argv)
    for filename in options.files:
        print(check_ascii_stl(filename))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
