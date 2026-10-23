"""PG-01 first-article trial dimensional inspection, not safety certification.

The immutable plan is source-controlled and embedded in the Windows build.
Operators record two independent observed values per dimension with a physical
specimen ID and evidence reference. No observation is silently synthesized.
All checks are candidate fit-screen limits, not approved manufacturing
tolerances. Progress lives in the existing local checksum-protected build log.
"""
from __future__ import annotations
import csv
import io
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from desktop.build_plan import RigError, read_manifest
from desktop.assembly_model import read_assembly
from desktop.model import repository_root

PLAN_SCHEMA="PG01-FIRST-ARTICLE-1"
RECORD_SCHEMA="PG01-TRIAL-INSPECTION-1"
FILE_REL="data/engineering/pg01-first-article-v1.6.json"
SPECIMEN_RE=re.compile(r"^[A-Z0-9][A-Z0-9_-]{2,31}$")
MAX_SAMPLES=50


def validate_plan(plan,rig=None,assembly=None):
    if not isinstance(plan,dict) or plan.get("schema")!=PLAN_SCHEMA:
        raise RigError("unknown first-article plan schema")
    policy=plan.get("inspection_policy",{})
    if policy.get("replicates_required")!=2 or policy.get("independent_approval") is not False:
        raise RigError("first-article trial measurements require two observations without auto-approval")
    parts=plan.get("items",[])
    if not isinstance(parts,list) or not 3<=len(parts)<=20:
        raise RigError("missing part family drawings")
    used=set()
    for part in parts:
        pid=part.get("id")
        if not isinstance(pid,str) or not pid or pid in used:
            raise RigError("part ID missing or duplicated")
        used.add(pid)
        checks=part.get("checks")
        if not isinstance(checks,list) or not 3<=len(checks)<=15:
            raise RigError("part lacks dimensional checks")
        identifiers=set()
        for check in checks:
            cid=check.get("id")
            if not isinstance(cid,str) or not cid or cid in identifiers:
                raise RigError("check id missing or duplicated")
            identifiers.add(cid)
            for key in ("nominal_mm","tolerance_mm"):
                n=check.get(key)
                if type(n) not in (int,float) or not math.isfinite(n) or n<=0:
                    raise RigError("invalid "+key)
            if check["tolerance_mm"]>=check["nominal_mm"]:
                raise RigError("tolerance exceeds nominal dimension")
    if rig is not None and assembly is not None:
        # A single source-of-truth for sizing is essential: refuse an outdated
        # fabrication card when CAD geometry has been revised.
        ring=next(x for x in parts if x["id"]=="FA-04")
        vals={c["id"]:c["nominal_mm"] for c in ring["checks"]}
        d=rig["dimensions_mm"]
        if vals["OD"]!=d["gate_outer_diameter"] or vals["ID"]!=d["clear_aperture_diameter"]:
            raise RigError("printed ring card disagrees with mechanical drawing")
        if vals["Z"]!=d["gate_frame_thickness"]:
            raise RigError("ring thickness card disagrees with engineering manifest")
        if vals["R"]!=(vals["OD"]-vals["ID"])/2:
            raise RigError("radial wall mismatch")
        joints={x["trial_part"]:x for x in assembly["interfaces"]}
        # Must align with the Rev B source and newly corrected 34mm hole pattern.
        splice={c["id"]:c["nominal_mm"] for c in parts[0]["checks"]}
        clamp={c["id"]:c["nominal_mm"] for c in parts[1]["checks"]}
        clip={c["id"]:c["nominal_mm"] for c in parts[2]["checks"]}
        for trial,data in [("joint_splice",splice),("rail_clamp",clamp),("cable_clip",clip)]:
            if trial not in joints or abs(joints[trial]["nominal_hole_diameter_mm"]-data["D"])>.001:
                raise RigError("interface bore does not match trial part "+trial)
        if joints["joint_splice"]["hole_pitch_mm"]!=splice["P"]:
            raise RigError("joint center spacing source mismatch")
        if joints["rail_clamp"]["hole_pitch_mm"]!=clamp["P"]:
            raise RigError("clamp center spacing source mismatch")
    return plan


def read_plan(root=None):
    base=Path(root) if root is not None else repository_root()
    path=base/FILE_REL
    if path.stat().st_size>160000:
        raise RigError("first-article card file too large")
    doc=json.loads(path.read_text(encoding="utf-8"))
    return validate_plan(doc,read_manifest(base),read_assembly(base))


def specimen_key(part_id,specimen_id):
    if not isinstance(specimen_id,str) or not SPECIMEN_RE.fullmatch(specimen_id):
        raise RigError("specimen ID must use 3–32 uppercase letters, digits, - or _")
    return part_id+"::"+specimen_id


def record_pair(plan,progress,part_id,specimen_id,check_id,value1,value2,operator,
                equipment_id,reference):
    validate_plan(plan)
    part=next((p for p in plan["items"] if p["id"]==part_id),None)
    if part is None:
        raise RigError("unknown first-article part")
    spec=next((c for c in part["checks"] if c["id"]==check_id),None)
    if spec is None:
        raise RigError("unknown dimensional characteristic")
    # Scientific integrity: no nan, booleans, negative or wildly implausible
    # values can enter the stored record and later appear as measurements.
    for value in (value1,value2):
        if type(value) not in (int,float) or not math.isfinite(value) or not 0<value<10000:
            raise RigError("observations must be finite positive millimeters")
    if not isinstance(operator,str) or not 2<=len(operator.strip())<=120:
        raise RigError("responsible operator required")
    if not isinstance(equipment_id,str) or not 3<=len(equipment_id.strip())<=100:
        raise RigError("physical measuring tool ID required")
    if not isinstance(reference,str) or not 10<=len(reference.strip())<=400:
        raise RigError("specific measurement evidence reference required")
    key=specimen_key(part_id,specimen_id)
    entries=progress.setdefault("first_article",{})
    existing=entries.get(key,{"schema":RECORD_SCHEMA,"part_id":part_id,
                              "specimen_id":specimen_id,"measurements":{}})
    measurements=existing["measurements"]
    if len(measurements.get(check_id,[]))>=MAX_SAMPLES:
        raise RigError("inspection history full")
    nominal=spec["nominal_mm"]
    tol=spec["tolerance_mm"]
    sample={"at_utc":datetime.now(timezone.utc).isoformat(),
            "operator":operator.strip(),"equipment_id":equipment_id.strip(),
            "evidence_reference":reference.strip(),
            "observations_mm":[round(float(value1),5),round(float(value2),5)],
            "nominal_mm":nominal,"candidate_tolerance_mm":tol,
            "mean_mm":round((value1+value2)/2,5),
            "range_mm":round(abs(value1-value2),5),
            "individual_within_trial_range":all(abs(v-nominal)<=tol for v in (value1,value2)),
            "independent_signoff":False,"source":"OPERATOR RECORDED / NOT VERIFIED"}
    measurements.setdefault(check_id,[]).append(sample)
    entries[key]=existing
    return sample


def review_specimen(plan,progress,part_id,specimen_id):
    validate_plan(plan)
    part=next((p for p in plan["items"] if p["id"]==part_id),None)
    if not part:raise RigError("unknown part")
    key=specimen_key(part_id,specimen_id)
    record=progress.get("first_article",{}).get(key,{"measurements":{}})
    rows=[]
    for c in part["checks"]:
        entries=record.get("measurements",{}).get(c["id"],[])
        latest=entries[-1] if entries else None
        matching=bool(latest) and latest.get("nominal_mm")==c["nominal_mm"] and \
             latest.get("candidate_tolerance_mm")==c["tolerance_mm"]
        within=matching and latest["individual_within_trial_range"]
        rows.append({"check_id":c["id"],"label":c["label"],
                     "nominal_mm":c["nominal_mm"],"candidate_tolerance_mm":c["tolerance_mm"],
                     "mean_mm":latest["mean_mm"] if matching else None,
                     "observations_recorded":matching,
                     "within_trial_range":bool(within)})
    ready=all(r["within_trial_range"] for r in rows)
    return {"specimen_key":key,"rows":rows,
            "status":"TRIAL DIMENSIONS RECORDED / PHYSICAL REVIEW REQUIRED" if ready
                     else "HOLD / MISSING OR OUT-OF-RANGE TRIAL OBSERVATIONS",
            "complete_candidate_fit_review":ready,
            "independently_approved":False,
            "warning":"No check authorizes manufacturing, procurement, loading or energized testing."}


def inspection_csv(plan,progress):
    validate_plan(plan)
    out=io.StringIO()
    writer=csv.writer(out)
    writer.writerow(["part","specimen","characteristic","nominal_mm",
                     "candidate_plusminus_mm","obs_1_mm","obs_2_mm","mean_mm",
                     "trial_range","equipment","operator","evidence","interpretation"])
    for part in plan["items"]:
        related=progress.get("first_article",{})
        keys=sorted(k for k in related if k.startswith(part["id"]+"::"))
        if not keys:
            keys=[part["id"]+"::UNINSPECTED"]
        for key in keys:
            record=related.get(key,{"measurements":{}})
            for c in part["checks"]:
                latest=record["measurements"].get(c["id"],[])
                last=latest[-1] if latest else None
                writer.writerow([part["id"],key.split("::",1)[1],c["label"],
                    c["nominal_mm"],c["tolerance_mm"],
                    last["observations_mm"][0] if last else "",
                    last["observations_mm"][1] if last else "",
                    last["mean_mm"] if last else "",
                    "WITHIN CANDIDATE RANGE" if last and last["individual_within_trial_range"]
                     else "HOLD / UNMEASURED",
                    last["equipment_id"] if last else "",last["operator"] if last else "",
                    last["evidence_reference"] if last else "",
                    "UNVERIFIED TRIAL DATA / NOT INDEPENDENTLY APPROVED"])
    return out.getvalue()
