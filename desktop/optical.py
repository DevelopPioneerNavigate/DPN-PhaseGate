"""DPN PG-01 optical evidence recorder and timebase health audit.

The camera is NEVER opened by import, startup, page navigation, or enumeration.
A Qt worker calls capture_frames only after informed operator action.
Post-read host timestamps are NOT exposure timestamps nor synchronized station time.
All recordings are unapproved BENCH evidence; no scientific claims inferred.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "PG01-OPTICAL-BENCH-1"
MAX_RECORDED_FRAMES = 1200
MIN_INTERVAL_NS = 250_000_000  # at most 4 still-image frames per second
MAX_JPEG_BYTES = 3_000_000
MAX_SOURCE_BYTES = 5_000_000
STATION_IDS = frozenset(("A", "B"))


class OpticalError(ValueError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _ensure_station(station):
    if station not in STATION_IDS:
        raise OpticalError("station must be A or B")


def _ensure_device(device):
    if not isinstance(device, int) or isinstance(device, bool) or not 0 <= device <= 7:
        raise OpticalError("camera device index must be 0 through 7")


@dataclass(frozen=True)
class Arrival:
    station: str
    device_index: int
    host_utc_after_read: str
    host_monotonic_ns_after_read: int

    def __post_init__(self):
        _ensure_station(self.station)
        _ensure_device(self.device_index)
        if not isinstance(self.host_monotonic_ns_after_read, int) or self.host_monotonic_ns_after_read < 0:
            raise OpticalError("invalid host monotonic receive counter")
        if not self.host_utc_after_read.endswith("Z"):
            raise OpticalError("expected timezone-labelled UTC receipt timestamp")


class TimebaseHealth:
    """Host frame arrival intervals only. Does not estimate camera sensor clocks."""
    def __init__(self, target_fps=4):
        if not 1 <= target_fps <= 12:
            raise ValueError("frame rate outside supported lab preview bounds")
        self.period_ns = int(1_000_000_000/target_fps)
        self.receipts = []
        self.faults = 0

    def note(self, host_monotonic_ns):
        if not isinstance(host_monotonic_ns, int) or host_monotonic_ns < 0:
            raise OpticalError("invalid monotonic host timestamp")
        if self.receipts and host_monotonic_ns <= self.receipts[-1]:
            self.faults += 1
            return False
        self.receipts.append(host_monotonic_ns)
        if len(self.receipts) > 500:
            del self.receipts[:len(self.receipts)-500]
        return True

    def summary(self):
        n=len(self.receipts)
        if n < 3:
            return {"state":"INSUFFICIENT FRAMES","frame_count":n,
                    "host_arrival_jitter_ms":None, "delayed_intervals":0,
                    "sensor_time_offset_known":False,"synchronized":False}
        intervals=[(b-a)/1e6 for a,b in zip(self.receipts,self.receipts[1:])]
        nominal=self.period_ns/1e6
        return {"state":"HOST ARRIVALS ONLY","frame_count":n,
                "mean_host_interval_ms":round(statistics.mean(intervals),3),
                "host_arrival_jitter_ms":round(statistics.pstdev(intervals),3),
                "delayed_intervals":sum(dt > 1.8*nominal for dt in intervals),
                "rejected_clock_order":self.faults,
                "sensor_time_offset_known":False,"synchronized":False,
                "limitations":"USB/driver buffer and post-read delays unknown; "
                              "this cannot establish frame exposure time or cross-camera event synchronization."}


def compare_receive_cadence(health_a: TimebaseHealth, health_b: TimebaseHealth):
    """Characterize independent camera host arrival streams without fake offset."""
    a,b=health_a.summary(),health_b.summary()
    return {"station_a":a,"station_b":b,
            "shared_host_monotonic_clock":True,
            "camera_exposure_offset_ns":None,
            "cross_station_synchronized":False,
            "review":"Shared PC clock timestamps receipt only, not sensor exposure or event causality."}


class OpticalBenchWriter:
    """Write original JPEG evidence into a new BENCH_OPTICAL directory.

    Saves every individual JPEG with a SHA-256 audit trail. Frames must be
    explicitly initiated by operator camera and recording controls.
    The output is never uploaded or merged into the approved run manifest.
    """
    def __init__(self, destination, station, camera_index, operator):
        self.root=Path(destination)
        _ensure_station(station)
        _ensure_device(camera_index)
        if not isinstance(operator,str) or not 2 <= len(operator.strip()) <= 100:
            raise OpticalError("operator identifier required")
        if not self.root.name.startswith("BENCH_OPTICAL_"):
            raise OpticalError("recording directory must start BENCH_OPTICAL_")
        self.station=station
        self.camera_index=camera_index
        self.operator=operator.strip()
        self.frames=[]
        self.last_time=None
        self.started_utc=utc_now()
        self.closed=False
        self.root.mkdir(parents=False,exist_ok=False)
        if self.root.is_symlink():
            raise OpticalError("recording directory cannot be a symlink")

    def append(self, jpeg, observed: Arrival):
        if self.closed:
            raise OpticalError("capture already closed")
        if observed.station != self.station or observed.device_index != self.camera_index:
            raise OpticalError("optical source assignment mismatch")
        if not isinstance(jpeg,bytes) or not 24 <= len(jpeg) <= MAX_JPEG_BYTES:
            raise OpticalError("JPEG frame byte count not supported")
        if jpeg[:2] != b"\xff\xd8" or jpeg[-2:] != b"\xff\xd9":
            raise OpticalError("malformed JPEG boundary")
        if len(self.frames) >= MAX_RECORDED_FRAMES:
            raise OpticalError("maximum optical capture length reached (1200 frames)")
        when=observed.host_monotonic_ns_after_read
        if self.last_time is not None:
            if when <= self.last_time:
                raise OpticalError("host clock rolled back or duplicated; stop recording")
            if when-self.last_time < MIN_INTERVAL_NS:
                return False  # Preview frames never imply a stored recorded frame.
        index=len(self.frames)
        name=f"frame_{index:05d}.jpg"
        path=self.root/name
        with path.open("xb") as f:
            f.write(jpeg)
        self.frames.append({
            "frame":index,"file":name,"sha256":checksum(jpeg),
            "bytes":len(jpeg),
            "host_utc_after_read":observed.host_utc_after_read,
            "host_monotonic_ns_after_read":when,
            "sensor_exposure_time_known":False,
            "witness_synchronized":False,
        })
        self.last_time=when
        return True

    def close(self,reason="OPERATOR_STOP"):
        if self.closed:
            return None
        self.closed=True
        manifest={
            "schema":SCHEMA,"classification":"UNVERIFIED_LOCAL_OPTICAL_BENCH",
            "station":self.station,"camera_index":self.camera_index,
            "operator":self.operator,"started_utc":self.started_utc,
            "ended_utc":utc_now(),"stop_reason":str(reason)[:100],
            "frame_count":len(self.frames),"frames":self.frames,
            "privacy":"OPERATOR_GRANTED_CAMERA_ACCESS_LOCAL_ONLY",
            "sensor_exposure_timestamps_available":False,
            "clock_sync_certified":False,
            "recorded_audio":False,
            "limitations":[
                "Post-read host arrival is not frame exposure timestamp",
                "Frame SHA-256 does not authenticate original scene",
                "No independent optical clock offset has been measured",
                "No apparatus capable of physical object teleportation is demonstrated",
            ]
        }
        raw=(json.dumps(manifest,indent=2,ensure_ascii=True,allow_nan=False)+"\n").encode("utf-8")
        with (self.root/"manifest.json").open("xb") as f:
            f.write(raw)
        digest=checksum(raw)
        with (self.root/"manifest.sha256").open("x",encoding="ascii") as f:
            f.write(digest+"  manifest.json\n")
        return {"directory":str(self.root),"frame_count":len(self.frames),
                "manifest_sha256":digest}


def verify_optical_bench(root):
    """Check frame/manifest integrity, order and absence of fabricated metadata."""
    folder=Path(root)
    if not folder.name.startswith("BENCH_OPTICAL_") or not folder.is_dir() or folder.is_symlink():
        raise OpticalError("invalid optical bench capture directory")
    raw=(folder/"manifest.json").read_bytes()
    expected=(folder/"manifest.sha256").read_text(encoding="ascii").strip()
    if expected != checksum(raw)+"  manifest.json":
        raise OpticalError("manifest changed or digest missing")
    manifest=json.loads(raw)
    if manifest.get("schema")!=SCHEMA or manifest.get("classification")!="UNVERIFIED_LOCAL_OPTICAL_BENCH":
        raise OpticalError("optical evidence schema or classification mismatch")
    frames=manifest.get("frames")
    if not isinstance(frames,list) or len(frames)!=manifest.get("frame_count"):
        raise OpticalError("optical frame count mismatch")
    prev=-1
    for i,meta in enumerate(frames):
        if meta.get("frame")!=i or meta.get("file")!=f"frame_{i:05d}.jpg":
            raise OpticalError("frame index or filename mismatch")
        when=meta.get("host_monotonic_ns_after_read")
        if not isinstance(when,int) or when<=prev:
            raise OpticalError("non-monotonic arrival timestamps")
        prev=when
        frame_file=folder/meta["file"]
        if frame_file.is_symlink():
            raise OpticalError("symlink evidence frame not allowed")
        data=frame_file.read_bytes()
        if len(data)!=meta.get("bytes") or checksum(data)!=meta.get("sha256"):
            raise OpticalError("optical frame missing, altered or truncated")
    if manifest.get("clock_sync_certified") is not False or manifest.get("recorded_audio") is not False:
        raise OpticalError("unsupported certification/audio claim")
    return {"state":"STRUCTURAL BENCH CHECK ONLY; NOT PHYSICS VALIDATION",
            "station":manifest["station"],"frames":len(frames),
            "manifest_sha256":checksum(raw),
            "camera_exposure_timing_verified":False}
