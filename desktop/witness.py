"""Independent witness-file inventory for unverified PG-01 bench observations.

Metadata and SHA-256 only. No camera control, video capture, cloud upload, or
automatic inference. Uses locally selected files already recorded by an operator.
"""
from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

PERMITTED={".mp4",".mov",".avi",".mkv",".jpg",".jpeg",".png",".wav"}
SCHEMA="PG01-WITNESS-1"
MAX_SOURCE_BYTES=8 * 1024**3


class WitnessError(ValueError):
    pass


def _digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        while piece:=f.read(1<<20):
            h.update(piece)
    return h.hexdigest()


def inventory_source(source,station,operator,note,consent_confirmed=False,at=None):
    """Document operator-selected recording; never copy footage or edit original."""
    source=Path(source)
    if station not in ("A","B","BOTH"):
        raise WitnessError("witness station must be A/B/BOTH")
    if not consent_confirmed:
        raise WitnessError("operator must confirm permission to inventory recording")
    if not isinstance(operator,str) or not 2 <= len(operator.strip()) <= 120:
        raise WitnessError("identify an operator")
    if not isinstance(note,str) or not 12 <= len(note.strip()) <= 600:
        raise WitnessError("describe origin, vantage and time source, with uncertainty")
    if source.suffix.lower() not in PERMITTED:
        raise WitnessError("unsupported witness file type")
    if not source.is_file() or source.is_symlink():
        raise WitnessError("source must be a real local file")
    stat_before=source.stat()
    if not 1 <= stat_before.st_size <= MAX_SOURCE_BYTES:
        raise WitnessError("empty or excessively large source recording")
    digest=_digest(source)
    stat_after=source.stat()
    if (stat_before.st_size,stat_before.st_mtime_ns)!=(stat_after.st_size,stat_after.st_mtime_ns):
        raise WitnessError("source file was modified during inventory")
    at=at or datetime.now(timezone.utc)
    if at.tzinfo is None:
        raise WitnessError("timestamp requires timezone")
    record={
        "schema":SCHEMA,
        "provenance":"OPERATOR_SELECTED_UNVERIFIED_WITNESS",
        "station":station,
        "created_utc":at.astimezone(timezone.utc).isoformat().replace("+00:00","Z"),
        "operator":operator.strip(),
        "note":note.strip(),
        "filename_only":source.name,
        "media_sha256":digest,
        "bytes":stat_before.st_size,
        "source_modified_ns":stat_before.st_mtime_ns,
        "recording_time_verified":False,
        "device_clock_synchronized":False,
        "contents_copied":False,
        "warning":"Hash does not authenticate the recording, prove it unedited before import, "
                  "establish object identity, or validate physical transfer.",
    }
    return record


def save_inventory(record,destination):
    dest=Path(destination)
    if not dest.name.startswith("BENCH_WITNESS_") or dest.suffix.lower()!=".json":
        raise WitnessError("output must be named BENCH_WITNESS_*.json")
    if not isinstance(record,dict) or record.get("schema")!=SCHEMA:
        raise WitnessError("unrecognized witness record")
    raw=(json.dumps(record,indent=2,allow_nan=False,ensure_ascii=True)+"\n").encode("utf-8")
    # Exclusive file creation avoids accidentally overwriting an earlier record.
    with dest.open("xb") as f:
        f.write(raw)
    digest=hashlib.sha256(raw).hexdigest()
    with dest.with_suffix(".sha256").open("x",encoding="ascii") as f:
        f.write(f"{digest}  {dest.name}\n")
    return digest


def verify_inventory(destination, original=None):
    dest=Path(destination)
    if not dest.name.startswith("BENCH_WITNESS_") or dest.suffix.lower()!=".json":
        raise WitnessError("invalid manifest name")
    raw=dest.read_bytes()
    h=hashlib.sha256(raw).hexdigest()
    expected=dest.with_suffix(".sha256").read_text(encoding="ascii").strip()
    if expected != f"{h}  {dest.name}":
        raise WitnessError("witness manifest bytes changed since capture")
    record=json.loads(raw)
    if record.get("schema")!=SCHEMA or record.get("provenance")!="OPERATOR_SELECTED_UNVERIFIED_WITNESS":
        raise WitnessError("unknown witness provenance")
    if not re.fullmatch(r"[a-f0-9]{64}",record.get("media_sha256","")):
        raise WitnessError("invalid evidence file checksum")
    if original is not None:
        source=Path(original)
        if source.name!=record["filename_only"] or _digest(source)!=record["media_sha256"]:
            raise WitnessError("current media file does not match inventory")
    return {"result":"WITNESS INVENTORY HASH CHECK (NOT AUTHENTICITY OR PHYSICS VALIDATION)",
            "source_media_sha256":record["media_sha256"],
            "record_sha256":h,"source_media_verified_again":original is not None}
