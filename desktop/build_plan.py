"""PG-01 manufacturing workpack and build-gate ledger.

Construction is NOT simulated into existence: all items start planned. A human
must sign every reported completion with an evidence reference. These entries
record operator claims, not safety approval, test results, or material transfer.
No serial/camera/control port is opened by this module.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA="DPN-PG01-RIG-1"
PROGRESS_SCHEMA="DPN-PG01-BUILD-PROGRESS-1"
MAX_SIZE=256*1024
ENGINEERING_RELATIVE="data/engineering/pg01-rig-manifest.json"
VALID_STATUSES={"operator_reported_complete","blocked","in_progress"}
STAGES={"design","safety","structure","motion","instrumentation",
        "metrology","optical","experiments","science","software"}


class RigError(ValueError):
    pass


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")


def read_manifest(root=None):
    if root is None:
        from desktop.model import repository_root
        root=repository_root()
    path=Path(root)/ENGINEERING_RELATIVE
    if path.stat().st_size > MAX_SIZE:
        raise RigError("engineering manifest is too large")
    return validate_manifest(json.loads(path.read_text(encoding="utf-8")))


def validate_manifest(doc):
    if not isinstance(doc,dict) or doc.get("schema")!=SCHEMA:
        raise RigError("unknown PG-01 engineering manifest schema")
    d=doc.get("dimensions_mm",{})
    for key in ["gate_outer_diameter","clear_aperture_diameter","gate_centers_separation",
                "rail_length","rail_travel_design_goal"]:
        n=d.get(key)
        if type(n) not in (int,float) or not 0<n<10000:
            raise RigError("invalid dimension "+key)
    if d["clear_aperture_diameter"]>=d["gate_outer_diameter"]:
        raise RigError("ring outside diameter must exceed optical aperture")
    if d["rail_travel_design_goal"]>=d["rail_length"]:
        raise RigError("rail travel exceeds physical rail")
    parts=doc.get("components",[])
    tasks=doc.get("work_packages",[])
    gates=doc.get("gates",[])
    if not parts or not tasks or not gates:
        raise RigError("incomplete engineering workbreakdown")
    ids=set()
    for p in parts:
        if not isinstance(p,dict) or not p.get("id") or p["id"] in ids:
            raise RigError("duplicate or absent component ID")
        ids.add(p["id"])
        if type(p.get("quantity")) is not int or not 1<=p["quantity"]<=500:
            raise RigError("invalid component quantity")
        if p.get("stage") not in STAGES or not p.get("name") or not p.get("specification"):
            raise RigError("invalid component stage/description")
    tids=set()
    for t in tasks:
        if not isinstance(t,dict) or t.get("id") in tids or not t.get("id"):
            raise RigError("duplicate or absent work-package ID")
        tids.add(t["id"])
        if t.get("stage") not in STAGES or t.get("status")!="planned":
            raise RigError("only unstarted verified workpackages are allowed in repo reference manifest")
        if not t.get("acceptance") or not isinstance(t.get("deliverables"),list):
            raise RigError("missing acceptance or deliverables")
    for t in tasks:
        deps=t.get("depends_on")
        if not isinstance(deps,list) or t["id"] in deps or not set(deps)<=tids:
            raise RigError("unresolvable work-package dependency")
    seen=set()
    def visit(tid,stack):
        if tid in stack: raise RigError("cyclic build-plan dependency")
        if tid in seen:return
        item=next(t for t in tasks if t["id"]==tid)
        for dep in item["depends_on"]:visit(dep,stack|{tid})
        seen.add(tid)
    for tid in tids:visit(tid,set())
    for gate in gates:
        if not set(gate.get("requires",[]))<=tids:
            raise RigError("unresolvable engineering gate")
    return doc


def progress_path(root=None):
    """Never writes to the packaged application or scientific experiment data."""
    if root is not None:
        return Path(root)/"pg01-build-progress.json"
    home=os.environ.get("LOCALAPPDATA")
    return (Path(home) if home else Path.home()/".local"/"share")/"DPN Technology"/"PhaseGate"/"pg01-build-progress.json"


def _canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()


def _hash(data):
    return hashlib.sha256(_canonical(data)).hexdigest()


def _state_empty():
    return {"schema":PROGRESS_SCHEMA,"created_utc":utc(),"updated_utc":utc(),
            "classification":"OPERATOR-RECORDED BUILD LOG / UNVERIFIED",
            "work_packages":{},"revision":1}


def read_progress(path=None):
    path=Path(path) if path is not None else progress_path()
    if not path.exists():
        return _state_empty()
    if path.stat().st_size>MAX_SIZE:raise RigError("progress file too large")
    try:
        doc=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        raise RigError("build progress cannot be read") from exc
    if not isinstance(doc,dict) or doc.get("schema")!=PROGRESS_SCHEMA:
        raise RigError("unsupported build progress schema")
    digest=doc.get("checksum")
    body={k:v for k,v in doc.items() if k!="checksum"}
    if not isinstance(digest,str) or digest!=_hash(body):
        raise RigError("build progress changed or missing checksum")
    if not isinstance(doc.get("work_packages"),dict):
        raise RigError("invalid build work packages")
    return doc


def save_progress(doc,path=None):
    path=Path(path) if path is not None else progress_path()
    if path.suffix.lower()!=".json":
        raise RigError("build progress must be JSON")
    data={k:v for k,v in doc.items() if k!="checksum"}
    data["updated_utc"]=utc()
    data["checksum"]=_hash(data)
    raw=json.dumps(data,indent=2,ensure_ascii=True,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_SIZE:
        raise RigError("build evidence log exceeded capacity")
    path.parent.mkdir(parents=True,exist_ok=True)
    descriptor,tmp=tempfile.mkstemp(prefix=".pg01-",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(descriptor,"w",encoding="utf-8",newline="\n") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return path


def task_status(task_id,progress):
    item=progress.get("work_packages",{}).get(task_id,{})
    return item.get("status","planned")


def report_status(manifest,progress,task_id,status,operator,evidence):
    """A label alone never satisfies engineering requirements; all changes audited."""
    validate_manifest(manifest)
    if status not in VALID_STATUSES:
        raise RigError("unsupported or fake completion state")
    tasks={x["id"]:x for x in manifest["work_packages"]}
    if task_id not in tasks:
        raise RigError("unknown work package")
    if not isinstance(operator,str) or not 2<=len(operator.strip())<=120:
        raise RigError("operator ID required")
    if not isinstance(evidence,str) or not 10<=len(evidence.strip())<=400:
        raise RigError("specific note / evidence reference required (10-400 chars)")
    if status=="operator_reported_complete":
        dependencies=tasks[task_id]["depends_on"]
        blocked=[dep for dep in dependencies if task_status(dep,progress)!="operator_reported_complete"]
        if blocked:
            raise RigError("dependencies not operator-reported complete: "+", ".join(blocked))
    if not isinstance(progress.get("work_packages"),dict):
        raise RigError("invalid progress record")
    old=progress["work_packages"].get(task_id,{})
    history=list(old.get("history",[]))
    if len(history)>=100:raise RigError("work package review history full")
    history.append({"timestamp_utc":utc(),"operator":operator.strip(),
                    "status":status,"evidence_note":evidence.strip(),
                    "claim":"OPERATOR SELF-REPORT ONLY / NOT INDEPENDENTLY VERIFIED"})
    progress["work_packages"][task_id]={"status":status,"history":history}
    return progress


def gate_review(manifest,progress):
    """A gate can be *operator-reported satisfied*, never unconditionally approved."""
    rows=[]
    for gate in manifest["gates"]:
        statuses={dep:task_status(dep,progress) for dep in gate["requires"]}
        ready=all(status=="operator_reported_complete" for status in statuses.values())
        rows.append({"id":gate["id"],"name":gate["name"],"operator_reported_ready":ready,
                     "independently_approved":False,"requirements":statuses})
    return rows


def export_bom_csv(manifest):
    validate_manifest(manifest)
    buffer=io.StringIO()
    writer=csv.writer(buffer)
    writer.writerow(["component_id","item","quantity","unit","stage","category",
                     "proposed_specification","procurement_status"])
    for p in manifest["components"]:
        writer.writerow([p["id"],p["name"],p["quantity"],p["unit"],p["stage"],
                         p["category"],p["specification"],p["procurement"]])
    return buffer.getvalue()
