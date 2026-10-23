"""DPN PhaseGate PG-01 assembly design validation — OFFLINE mathematical fit.

No claimed machine is built. The 3D coordinates are provisional *design*
envelopes. A passing check cannot establish load capacity, safe machining,
mechanical fastening, structural integrity, or an experimental portal field.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from desktop.build_plan import read_manifest, RigError
from desktop.model import repository_root

SCHEMA="PG01-MECHANICAL-ASSEMBLY-1"
STAGES=frozenset(("STRUCTURE","MOTION","OPTICS","ROUTING","SENSORS","GUARDING"))
MAX_BYTES=160_000


def read_assembly(root=None):
    base=Path(root) if root else repository_root()
    path=base/"data/engineering/pg01-assembly-v1.5.json"
    if path.stat().st_size>MAX_BYTES:
        raise RigError("oversized assembly file")
    return validate_assembly(json.loads(path.read_text(encoding="utf-8")),read_manifest(base))


def _finite_positive(n,label):
    if type(n) not in (int,float) or not math.isfinite(n) or n<=0:
        raise RigError("invalid engineering dimension: "+label)
    return float(n)


def validate_assembly(d,rig):
    if not isinstance(d,dict) or d.get("schema")!=SCHEMA:
        raise RigError("unknown assembly design schema")
    layers=d.get("view_layers")
    if set(layers or [])!=STAGES or len(layers)!=len(STAGES):
        raise RigError("assembly drawing layers missing or repeated")
    source=rig["dimensions_mm"]
    expected=d.get("reference_dimensions_mm",{})
    mapping={
        "gate_outer_diameter":"gate_outer_diameter",
        "gate_clear_aperture_diameter":"clear_aperture_diameter",
        "gate_center_z":"gate_center_height",
        "gate_center_separation":"gate_centers_separation",
        "rail_length":"rail_length",
        "payload_platform_width":"shuttle_platform_width",
        "payload_platform_length":"shuttle_platform_length",
    }
    for assembly_key,source_key in mapping.items():
        n=_finite_positive(expected.get(assembly_key),assembly_key)
        if abs(n-source[source_key])>.001:
            raise RigError("assembly/rig mismatch: "+assembly_key)
    g=d.get("geometry_mm",{})
    for key in ("gate_a_y","gate_b_y","rail_z","carriage_tray_surface_z",
                "payload_envelope_width","payload_envelope_height",
                "payload_bottom_z","min_design_radial_clearance_mm",
                "rail_x_extent"):
        v=g.get(key)
        if type(v) not in (int,float) or not math.isfinite(v):
            raise RigError("invalid assembly geometry: "+key)
    if g["gate_a_y"] >= g["gate_b_y"]:
        raise RigError("station order reversed")
    if abs(g["gate_a_y"]+g["gate_b_y"])>.001 or \
        abs(g["gate_b_y"]-g["gate_a_y"]-expected["gate_center_separation"])>.001:
        raise RigError("station coordinates do not match rig spacing")
    if abs(g["carriage_tray_surface_z"]-g["payload_bottom_z"])>.001:
        raise RigError("payload datum differs from tray top")
    if g["payload_envelope_width"]>expected["payload_platform_width"]:
        raise RigError("payload wider than tray")
    if g["payload_envelope_height"]<=0 or g["min_design_radial_clearance_mm"]<=0:
        raise RigError("invalid payload clearance goal")
    if source["rail_travel_design_goal"]<source["gate_centers_separation"]:
        raise RigError("design rail travel cannot move from Station A center to B center")
    # Rail endpoints must bracket two gates AND planned centered carriage travel.
    if expected["rail_length"]/2 < max(abs(g["gate_a_y"]),abs(g["gate_b_y"])):
        raise RigError("rail envelope does not reach both gates")
    items=d.get("assemblies")
    if not isinstance(items,list) or len(items)<12 or len(items)>35:
        raise RigError("missing machine assembly components")
    seen=set()
    for part in items:
        pid=part.get("id")
        if not isinstance(pid,str) or not pid or pid in seen:
            raise RigError("assembly IDs invalid or repeated")
        seen.add(pid)
        if part.get("layer") not in STAGES:
            raise RigError("unsupported assembly layer "+pid)
        pos=part.get("center_mm") if part.get("shape")!="route" else part.get("points_mm")
        if part.get("shape")=="route":
            if not isinstance(pos,list) or len(pos)<2:
                raise RigError("missing routed cable geometry")
            all_points=pos
        else:
            all_points=[pos]
        for point in all_points:
            if not isinstance(point,list) or len(point)!=3 or any(
                type(v) not in (int,float) or not math.isfinite(v) for v in point
            ):
                raise RigError("invalid 3D coordinate "+pid)
        if part.get("shape")=="ring":
            if part.get("diameter_mm")!=source["gate_outer_diameter"] or \
               part.get("clear_diameter_mm")!=source["clear_aperture_diameter"]:
                raise RigError("inconsistent ring dimensions "+pid)
        elif part.get("shape") in ("box","rail"):
            dims=part.get("extent_mm")
            if not isinstance(dims,list) or len(dims)!=3 or any(
                type(v) not in (int,float) or v<=0 or not math.isfinite(v) for v in dims):
                raise RigError("invalid part bounding box "+pid)
        elif part.get("shape")!="route":
            raise RigError("unknown part renderer geometry "+pid)
    if len(d.get("interfaces",[]))<3 or len(d.get("inspection_gates",[]))<4:
        raise RigError("incomplete joint and inspection study")
    checks=fit_checks(d,source)
    for item in checks:
        if not item["passed"]:
            raise RigError("PG-01 geometry design hold: "+item["name"]+
                           " ("+str(item["measured"])+")")
    return d


def fit_checks(d,source):
    """Checks envelope arithmetic only, not real collision or stress FEA."""
    g=d["geometry_mm"]
    outer=float(source["gate_outer_diameter"])
    aperture=float(source["clear_aperture_diameter"])/2
    center=float(source["gate_center_height"])
    width=float(g["payload_envelope_width"])/2
    low=float(g["payload_bottom_z"])
    high=low+float(g["payload_envelope_height"])
    # Entire proposed payload AABB must fit inside the circular clear opening
    # at either gate plane. Box is only the design envelope, not an observed object.
    max_distance=math.hypot(width,max(abs(low-center),abs(high-center)))
    payload_clearance=aperture-max_distance
    minrad=float(g["min_design_radial_clearance_mm"])
    railbottom=g["rail_z"]-19/2
    railmax=math.hypot(abs(g["rail_x_extent"]),abs(railbottom-center))
    rail_clearance=aperture-railmax
    target=float(source["rail_travel_design_goal"])
    spacing=float(source["gate_centers_separation"])
    rail_length=float(source["rail_length"])
    tray_length=float(source["shuttle_platform_length"])
    # With a symmetric, centered carriage, half stroke+half tray
    # must fit inside rail length with 20mm design reserve at both ends.
    end_reserve=(rail_length-target-tray_length)/2
    return [
        {"name":"Payload bounding box inside gate clear aperture",
         "measured":round(payload_clearance,2),"target":minrad,"unit":"mm",
         "passed":payload_clearance>=minrad},
        {"name":"Rail bounding edge inside gate clear aperture",
         "measured":round(rail_clearance,2),"target":minrad,"unit":"mm",
         "passed":rail_clearance>=minrad},
        {"name":"Carriage travel reaches both station centers",
         "measured":round(target-spacing,2),"target":0,"unit":"mm",
         "passed":target>=spacing},
        {"name":"Carriage end reserve in proposed rail",
         "measured":round(end_reserve,2),"target":20,"unit":"mm",
         "passed":end_reserve>=20},
    ]


def component_detail(design,part_id):
    for part in design["assemblies"]:
        if part["id"]==part_id:
            return part
    raise RigError("unknown physical assembly item")
