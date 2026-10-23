"""DPN PG-01 independent mechanical fit-check.

This analyzes an idealized, static CAD design envelope before fabrication.
It is not load/stress analysis, collision analysis of full CAD or safety signoff.
No equipment is operated.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

from desktop.model import repository_root
from desktop.build_plan import read_manifest

RELATIVE="data/engineering/pg01-manufacturing-v0.2.json"
SCHEMA="DPN-PG01-MECH-ICD-2"


class InterfaceError(ValueError):
    pass


def load_interface(root=None):
    base=Path(root) if root is not None else repository_root()
    file=base/RELATIVE
    if file.stat().st_size>128_000:
        raise InterfaceError("unexpectedly large mechanical interface contract")
    return json.loads(file.read_text(encoding="utf-8"))


def _number(mapping,name):
    n=mapping.get(name)
    if type(n) not in (int,float) or not math.isfinite(n):
        raise InterfaceError("invalid or missing dimension: "+name)
    return float(n)


def evaluate_geometry(geometry):
    """Return individual check results; no simulated completion or signoff."""
    g=geometry
    if not isinstance(g,dict):
        raise InterfaceError("geometry must be an object")
    vals={k:_number(g,k) for k in (
        "gate_ring_center_height_mm","aperture_radius_mm","rail_length_mm",
        "rail_guide_center_height_mm","rail_guide_width_mm","rail_guide_height_mm",
        "shuttle_platform_width_x_mm","shuttle_platform_length_y_mm",
        "shuttle_tray_bottom_z_mm","shuttle_tray_thickness_mm",
        "sample_height_allowance_mm","safety_clearance_required_mm"
    )}
    r=vals["aperture_radius_mm"]
    safe=vals["safety_clearance_required_mm"]
    if r<=0 or safe<=0 or any(v<=0 for v in vals.values()):
        raise InterfaceError("all physical dimensions must be positive")
    stations=g.get("gate_centres_y_mm")
    travel=g.get("shuttle_center_span_y_mm")
    guide_x=g.get("rail_guide_centres_x_mm")
    stops=g.get("rail_endstop_centres_y_mm")
    for name,vector in [("gate_centres_y_mm",stations),
                        ("shuttle_center_span_y_mm",travel),
                        ("rail_guide_centres_x_mm",guide_x),
                        ("rail_endstop_centres_y_mm",stops)]:
        if not isinstance(vector,list) or len(vector)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in vector):
            raise InterfaceError(name+" must be two finite numbers")
        if vector[0]>=vector[1]:raise InterfaceError(name+" must be ordered")
    if not (g["rail_length_mm"]>0 and g["shuttle_tray_thickness_mm"]>0):
        raise InterfaceError("invalid rail or tray thickness")
    # Maximum radial excursion in X-Z plane at gate crossing.
    ring_z=vals["gate_ring_center_height_mm"]
    xedge=max(abs(x) for x in guide_x)+vals["rail_guide_width_mm"]/2
    rail_low=vals["rail_guide_center_height_mm"]-vals["rail_guide_height_mm"]/2
    rail_high=vals["rail_guide_center_height_mm"]+vals["rail_guide_height_mm"]/2
    rail_radial=max(math.hypot(xedge,rail_low-ring_z),
                    math.hypot(xedge,rail_high-ring_z))
    rail_clearance=r-rail_radial
    tray_x=vals["shuttle_platform_width_x_mm"]/2
    tray_bottom=vals["shuttle_tray_bottom_z_mm"]
    top=tray_bottom+vals["shuttle_tray_thickness_mm"]+vals["sample_height_allowance_mm"]
    payload_radial=max(math.hypot(tray_x,tray_bottom-ring_z),
                       math.hypot(tray_x,top-ring_z))
    payload_clearance=r-payload_radial
    centers_travel=stations[1]-stations[0]
    travel_width=travel[1]-travel[0]
    end_margin=min(travel[0]-stops[0],stops[1]-travel[1])-vals["shuttle_platform_length_y_mm"]/2
    rail_end_margin=(vals["rail_length_mm"]/2)-max(abs(y) for y in stops)
    station_reach_margin=min(stations[0]-travel[0],travel[1]-stations[1])
    checks=[
        {"id":"M1","title":"Station-to-station carriage reach",
         "value_mm":round(travel_width-centers_travel,3),
         "threshold_mm":0.0,
         "pass":travel[0]<=stations[0] and travel[1]>=stations[1],
         "detail":"proposed carriage center span includes both gate center planes"},
        {"id":"M2","title":"Rail section inside the circular opening",
         "value_mm":round(rail_clearance,3),"threshold_mm":round(safe,3),
         "pass":rail_clearance>=safe,
         "detail":"worst radial distance using full rail half-width/half-height at gate planes"},
        {"id":"M3","title":"Tray and bounded sample clear the opening",
         "value_mm":round(payload_clearance,3),"threshold_mm":round(safe,3),
         "pass":payload_clearance>=safe,
         "detail":"bounding X-Z corners for nominal tray and 80mm sample; no wiring envelope"},
        {"id":"M4","title":"Carriage envelope between passive end stops",
         "value_mm":round(end_margin,3),"threshold_mm":round(safe,3),
         "pass":end_margin>=safe and rail_end_margin>=safe,
         "detail":"endstop/carriage half-length and physical rail limits (no load/dynamics)"},
        {"id":"M5","title":"Rail within design envelope",
         "value_mm":round(rail_end_margin,3),"threshold_mm":round(safe,3),
         "pass":rail_end_margin>=safe,"detail":"nominal stops inside full rail length"},
    ]
    return {"classification":"GEOMETRIC FIT CHECK ONLY / NOT FABRICATION APPROVAL",
            "status":"PASS PRELIMINARY FIT CHECK" if all(x["pass"] for x in checks) else "BLOCK DESIGN",
            "checks":checks,
            "gate_aperture_radius_mm":r,
            "payload_nominal_height_mm":vals["sample_height_allowance_mm"],
            "station_reach_margin_mm":round(station_reach_margin,3),
            "rail_clearance_mm":round(rail_clearance,3),
            "payload_clearance_mm":round(payload_clearance,3),
            "endstop_margin_mm":round(end_margin,3),
            "independent_mechanical_review_complete":False,
            "independent_electrical_review_complete":False}


def evaluate_project(root=None):
    contract=load_interface(root)
    rig=read_manifest(root)
    if contract.get("schema")!=SCHEMA or contract.get("unit")!="mm":
        raise InterfaceError("unknown interface revision or units")
    g=contract.get("geometry",{})
    d=rig["dimensions_mm"]
    refs={
        "gate_ring_center_height_mm":"gate_center_height",
        "rail_length_mm":"rail_length",
        "shuttle_platform_width_x_mm":"shuttle_platform_width",
        "shuttle_platform_length_y_mm":"shuttle_platform_length"
    }
    for contract_name,rig_name in refs.items():
        if g.get(contract_name)!=d.get(rig_name):
            raise InterfaceError("engineering manifest and CAD interface disagree on "+contract_name)
    if g.get("aperture_radius_mm")*2!=d["clear_aperture_diameter"]:
        raise InterfaceError("clear aperture mismatch")
    if (g["gate_centres_y_mm"][1]-g["gate_centres_y_mm"][0])!=d["gate_centers_separation"]:
        raise InterfaceError("gate center spacing mismatch")
    if (g["shuttle_center_span_y_mm"][1]-g["shuttle_center_span_y_mm"][0])!=d["rail_travel_design_goal"]:
        raise InterfaceError("manual shuttle travel mismatch")
    result=evaluate_geometry(g)
    result["interface_revision"]=contract["revision"]
    result["gate_design_revision"]=rig["revision"]
    return result


def cutlist_report(root=None):
    contract=load_interface(root)
    rig=read_manifest(root)
    # These are ESTIMATED reference quantities only; actual supplier profiles,
    # support lengths and drill specifications must be measured after fit checks.
    return {"classification":"ESTIMATED PROCUREMENT/GEOMETRY REFERENCE — NOT SHOP DRAWING",
            "revision":contract["revision"],
            "frame_count":2,"segments_per_frame":6,
            "total_ring_segments":12,
            "outer_diameter_mm":rig["dimensions_mm"]["gate_outer_diameter"],
            "clear_aperture_mm":rig["dimensions_mm"]["clear_aperture_diameter"],
            "ring_annulus_radial_width_mm":(
                rig["dimensions_mm"]["gate_outer_diameter"]-
                rig["dimensions_mm"]["clear_aperture_diameter"])/2,
            "manual_guide_length_mm":rig["dimensions_mm"]["rail_length"],
            "actual_extrusion_cut_schedule":"UNASSIGNED — depends on CAD detail and supplier profiles",
            "drawing_approval":"NOT APPROVED",
            "electronics_approval":"NOT APPROVED"}


if __name__=="__main__":
    report=evaluate_project()
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report["status"].startswith("PASS") else 1)
