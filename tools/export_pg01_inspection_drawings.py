#!/usr/bin/env python3
"""Generate printable vector first-article trial inspection sheets.

Each drawing is machine-sourced from PG-01 CAD/assembly manifests, with measured
dimension table, explicit inspection controls and a NO FABRICATION APPROVAL
watermark. SVG is vector text and geometry, not a screenshot or proof of fit.
"""
from __future__ import annotations
import argparse
import csv
import html
import io
import math
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from desktop.first_article import read_plan, inspection_csv
from desktop.build_plan import read_progress

def escape(t):
    return html.escape(str(t),quote=True)


def specimen_svg(part):
    title=escape(part["name"])
    checks=part["checks"]
    lines=[
        '<svg xmlns="http://www.w3.org/2000/svg" width="1123" height="794" viewBox="0 0 1123 794">',
        '<title>DPN PG-01 '+title+' / candidate manufacturing inspection study</title>',
        '<desc>Unapproved preliminary first article, with proposed dimensions and independent measurement slots</desc>',
        '<rect width="1123" height="794" fill="#ffffff"/>',
        '<rect x="24" y="24" width="1075" height="746" fill="none" stroke="#131b31" stroke-width="3"/>',
        '<rect x="24" y="24" width="1075" height="88" fill="#102344"/>',
        '<g font-family="Arial,sans-serif">',
        '<text x="47" y="65" fill="#ffffff" font-size="24" font-weight="bold">DPN TECHNOLOGY  /  PHASEGATE  PG-01</text>',
        '<text x="47" y="94" fill="#a9e9fc" font-size="16">REV 1.6  /  PROVISIONAL FIRST-ARTICLE INSPECTION</text>',
        '<text x="44" y="150" fill="#102344" font-weight="bold" font-size="23">'+escape(part["id"])+' — '+title+'</text>',
        '<text x="44" y="174" fill="#485774" font-size="14">'+escape(part["purpose"])+'</text>',
        '<rect x="45" y="196" width="477" height="270" rx="8" fill="#f0f4fa" stroke="#8aa1bb" stroke-width="2"/>',
        '<text x="62" y="224" font-size="13" font-weight="bold" fill="#16335e">CONCEPT GEOMETRY  /  NOMINAL, NOT TO SCALE</text>',
    ]
    part_id=part["id"]
    if part_id=="FA-04":
        # Draw true 60-degree parent annular wedge with 360/260 parent diameters.
        cx,cy=281,390
        theta=math.radians(60)
        r_outer,r_inner=135,97.5
        outer0=(cx+r_outer,cy)
        outer1=(cx+r_outer*math.cos(theta),cy-r_outer*math.sin(theta))
        inner1=(cx+r_inner*math.cos(theta),cy-r_inner*math.sin(theta))
        inner0=(cx+r_inner,cy)
        d=(f'M {outer0[0]:.1f} {outer0[1]:.1f} A {r_outer} {r_outer} 0 0 0 {outer1[0]:.1f} {outer1[1]:.1f} '
           f'L {inner1[0]:.1f} {inner1[1]:.1f} A {r_inner} {r_inner} 0 0 1 {inner0[0]:.1f} {inner0[1]:.1f} Z')
        lines += [f'<path d="{d}" fill="#d9e3f3" stroke="#193e68" stroke-width="3"/>',
                 '<text x="90" y="360" font-size="15" fill="#193e68">60° SEGMENT</text>',
                 '<text x="90" y="382" font-size="13" fill="#354d6c">PARENT OD 360 / ID 260</text>']
    else:
        dims={x["id"]:x["nominal_mm"] for x in checks}
        # Dimensional rectangles are symbolic orthographic views; no hidden
        # mating fit or thread profile inferred from this image.
        rectw=300
        recth=125
        if part_id=="FA-03":recth=95
        lines += [
            f'<rect x="126" y="281" width="{rectw}" height="{recth}" rx="5" fill="#d7e4f0" stroke="#153962" stroke-width="3"/>',
            '<line x1="126" y1="260" x2="426" y2="260" stroke="#263e66" stroke-width="2"/>',
            '<line x1="126" y1="250" x2="126" y2="270" stroke="#263e66" stroke-width="2"/>',
            '<line x1="426" y1="250" x2="426" y2="270" stroke="#263e66" stroke-width="2"/>',
            f'<text x="276" y="253" text-anchor="middle" fill="#102344" font-size="16">L {escape(dims.get("L","—"))} mm</text>',
            '<line x1="448" y1="281" x2="448" y2="406" stroke="#263e66" stroke-width="2"/>',
            f'<text x="457" y="348" font-size="15" fill="#102344">W {escape(dims.get("W","—"))} mm</text>'
        ]
        if part_id in ("FA-01","FA-02","FA-03"):
            for x in (203,349):
                lines.append(f'<circle cx="{x}" cy="345" r="10" fill="#ffffff" stroke="#294d76" stroke-width="2"/>')
            lines.append('<text x="279" y="447" fill="#153962" text-anchor="middle" font-size="15">HOLE PITCH: '+escape(dims.get("P","—"))+' mm</text>')
            lines.append('<text x="285" y="463" fill="#4b6280" text-anchor="middle" font-size="12">Symbolic, verify STL/actual fixture</text>')
    lines += [
        '<rect x="547" y="195" width="527" height="270" rx="8" fill="#ffffff" stroke="#91a4bc" stroke-width="2"/>',
        '<text x="568" y="224" font-size="14" font-weight="bold" fill="#182d4c">PROVISIONAL MEASUREMENT PLAN (mm)</text>',
        '<line x1="568" y1="237" x2="1054" y2="237" stroke="#7c8eab" />',
        '<text x="570" y="258" font-weight="bold" font-size="12" fill="#253c59">ID / CHARACTERISTIC</text>',
        '<text x="888" y="258" font-weight="bold" font-size="12" fill="#253c59">NOMINAL</text>',
        '<text x="985" y="258" font-weight="bold" font-size="12" fill="#253c59">TRIAL ±</text>',
    ]
    for i,c in enumerate(checks):
        y=281+i*35
        lines += [f'<text x="570" y="{y}" font-size="12" fill="#334860">{escape(c["id"])} — {escape(c["label"][:32])}</text>',
                  f'<text x="886" y="{y}" font-size="12" fill="#152d4c">{escape(c["nominal_mm"])}</text>',
                  f'<text x="989" y="{y}" font-size="12" fill="#152d4c">{escape(c["tolerance_mm"])}</text>',
                  f'<line x1="566" y1="{y+9}" x2="1054" y2="{y+9}" stroke="#d9e2ee"/>']
    lines += [
        '<text x="49" y="511" font-size="17" font-weight="bold" fill="#17304f">FIRST-ARTICLE PHYSICAL INSPECTION / BLANK TEMPLATE</text>',
        '<text x="50" y="540" font-size="13" fill="#3e4e6a">Specimen ID __________________  Inspector __________________  Caliper/tool ID __________________</text>',
        '<text x="50" y="565" font-size="13" fill="#3e4e6a">Date / time __________________  Drawing revision __________________  Record / photo ref ______________</text>',
        '<rect x="45" y="580" width="1028" height="46" rx="6" fill="#f2f5fa" stroke="#b6c1d2"/>',
        '<text x="57" y="598" font-size="12" fill="#183a63">MEASURE EACH FEATURE TWICE. RECORD BOTH VALUES IN THE NATIVE GATE ENGINEERING LAB.</text>',
        '<text x="57" y="616" font-size="12" fill="#183a63">Any missing/out-of-range observation = HOLD. Both in range = OPERATOR REVIEW, not release.</text>',
        '<text x="49" y="653" font-size="13" font-weight="bold" fill="#17304f">HOLD POINTS</text>'
    ]
    for i,note in enumerate(part["hold_points"][:2]):
        lines.append(f'<text x="53" y="{675+i*20}" font-size="12" fill="#333f55">• {escape(note[:130])}</text>')
    lines += [
        '<rect x="45" y="720" width="1028" height="33" rx="5" fill="#692838"/>',
        '<text x="559" y="741" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="bold">TRIAL INSPECTION ONLY / NOT APPROVED FOR FABRICATION OR LOADING</text>',
        '</g></svg>',
    ]
    return "\n".join(lines)+"\n"


def blank_template(plan):
    rows=io.StringIO()
    writer=csv.writer(rows)
    writer.writerow(["part_id","specimen_id","check_id","characteristic",
                     "nominal_mm","candidate_tolerance_mm","measured_1_mm","measured_2_mm",
                     "equipment_id","operator","evidence_reference","independent_approval"])
    for part in plan["items"]:
        for c in part["checks"]:
            writer.writerow([part["id"],"",c["id"],c["label"],c["nominal_mm"],
                             c["tolerance_mm"],"","","","","","NO"])
    return rows.getvalue()


def export_drawings(destination,root=None):
    plan=read_plan(root)
    target=Path(destination)
    target.mkdir(parents=True,exist_ok=True)
    result=[]
    for part in plan["items"]:
        file=target/(part["id"]+"-TRIAL-INSPECTION.svg")
        with file.open("x",encoding="utf-8") as f:
            f.write(specimen_svg(part))
        result.append(file)
    output=target/"PG01-Blank-First-Article-Inspection.csv"
    with output.open("x",encoding="utf-8-sig",newline="") as f:
        f.write(blank_template(plan))
    result.append(output)
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description="PG-01 first-article design inspection sheets")
    p.add_argument("--out",type=Path,default=Path("build/pg01-first-article"))
    p.add_argument("--check",action="store_true")
    args=p.parse_args(argv)
    plan=read_plan()
    if args.check:
        print("PG-01 TRIAL DRAWINGS CHECK: parts=%d features=%d" %
              (len(plan["items"]),sum(len(x["checks"]) for x in plan["items"])))
    else:
        made=export_drawings(args.out)
        print("Created %d SVG / CSV inspection documents" % len(made))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
