"""PG-01 fabrication readiness — dimension controls, receiving log and fit report.

Records operator observations, not approved engineering measurements. All
purchases and dimensions start unverified. Never changes the experiment registry.
"""
from __future__ import annotations
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from desktop.build_plan import RigError, progress_path, read_manifest, _canonical, _hash, save_progress, read_progress

MEASUREMENTS={
 "gate_outer_diameter":(360.0,1.0),
 "clear_aperture_diameter":(260.0,1.0),
 "gate_centers_separation":(800.0,2.0),
 "rail_length":(1200.0,3.0),
 "rail_travel_design_goal":(900.0,3.0),
}
RECEIVING={"not_ordered","quoted","ordered","received_uninspected","inspected_accepted","rejected"}
MAX_HISTORY=80

def prepare(progress):
    progress.setdefault("component_receiving",{})
    progress.setdefault("dimensional_inspections",{})
    return progress

def update_receiving(manifest,progress,component_id,state,operator,reference):
    ids={x["id"] for x in manifest["components"]}
    if component_id not in ids: raise RigError("unknown component ID")
    if state not in RECEIVING: raise RigError("invalid receiving state")
    if len(operator.strip())<2 or len(reference.strip())<10: raise RigError("operator and evidence reference required")
    prepare(progress)
    prior=progress["component_receiving"].get(component_id,{})
    history=list(prior.get("history",[]))
    if len(history)>=MAX_HISTORY: raise RigError("receiving audit full")
    history.append({"at":datetime.now(timezone.utc).isoformat(),"operator":operator.strip(),
       "state":state,"reference":reference.strip(),"verified_independently":False})
    progress["component_receiving"][component_id]={"status":state,"history":history}
    return progress

def inspect_dimension(manifest,progress,name,actual_mm,operator,reference):
    if name not in MEASUREMENTS: raise RigError("unsupported dimension")
    if type(actual_mm) not in (float,int) or not math.isfinite(actual_mm) or actual_mm<=0:
        raise RigError("measurement must be finite positive mm")
    if len(operator.strip())<2 or len(reference.strip())<10: raise RigError("operator and inspection evidence required")
    nominal,tolerance=MEASUREMENTS[name]
    if abs(float(manifest["dimensions_mm"][name])-nominal)>0.0001: raise RigError("design revision requires tolerance review")
    prepare(progress)
    old=progress["dimensional_inspections"].get(name,{})
    history=list(old.get("history",[]))
    if len(history)>=MAX_HISTORY:raise RigError("inspection log full")
    deviation=round(float(actual_mm)-nominal,4)
    within=abs(deviation)<=tolerance
    history.append({"at":datetime.now(timezone.utc).isoformat(),
        "operator":operator.strip(),"reference":reference.strip(),
        "nominal_mm":nominal,"candidate_tolerance_mm":tolerance,
        "observed_mm":float(actual_mm),"deviation_mm":deviation,
        "within_candidate_range":within,
        "independently_verified":False,
        "interpretation":"TRIAL DESIGN CHECK ONLY, NOT APPROVED FABRICATION TOLERANCE"})
    progress["dimensional_inspections"][name]={"history":history}
    return progress

def fabrication_summary(manifest,progress):
    components=progress.get("component_receiving",{})
    received=sum(v.get("status")=="inspected_accepted" for v in components.values())
    verified=sum(bool(v.get("history")) for v in progress.get("dimensional_inspections",{}).values())
    return {"components_total":len(manifest["components"]),"operator_reported_receipt":received,
            "dimensions_inspected":verified,"dimensions_total":len(MEASUREMENTS),
            "independent_approval":False,"physical_field_verification":False}
