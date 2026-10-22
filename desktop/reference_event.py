"""PG-01 reference-light event analysis of local, unverified optical BENCH images.

Never calculates actual camera exposure offset. Works only on independently
captured BENCH_OPTICAL directories whose bytes pass SHA-256 integrity checks.
Uses illumination changes in existing JPEGs, NOT tracking or identification.
Camera images are never uploaded or recorded by this module.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

from desktop.optical import verify_optical_bench

SCHEMA="PG01-REFERENCE-REVIEW-1"
REGIONS={"CENTER","FULL","TOP","BOTTOM","LEFT","RIGHT"}
MAX_FRAMES=1200
MIN_BACKGROUND=5


class ReferenceError(ValueError):
    pass


def brightness(jpeg: bytes,region="CENTER") -> float:
    """Decode local JPEG; measure normalized grayscale brightness on a selected area."""
    if region not in REGIONS:
        raise ReferenceError("invalid observed region")
    try:
        import cv2
        import numpy as np
        frame=cv2.imdecode(np.frombuffer(jpeg,dtype=np.uint8),cv2.IMREAD_GRAYSCALE)
    except Exception as exc:
        raise ReferenceError("OpenCV could not decode witness frame") from exc
    if frame is None or frame.size < 64 or len(frame.shape)!=2:
        raise ReferenceError("image is not a usable local grayscale frame")
    h,w=frame.shape
    bounds={
        "CENTER":(h//4,3*h//4,w//4,3*w//4),
        "FULL":(0,h,0,w),
        "TOP":(0,max(1,h//2),0,w),
        "BOTTOM":(h//2,h,0,w),
        "LEFT":(0,h,0,max(1,w//2)),
        "RIGHT":(0,h,w//2,w),
    }
    y0,y1,x0,x1=bounds[region]
    selected=frame[y0:y1,x0:x1]
    if selected.size < 16:
        raise ReferenceError("selected image region is too small")
    return float(selected.mean())


def inspect_capture(folder,region="CENTER"):
    """Hash-verify all frames first, then compute luminance/receipt-time series."""
    if region not in REGIONS:
        raise ReferenceError("unknown region")
    root=Path(folder)
    try:
        verify_optical_bench(root)
        payload=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
        if payload.get("classification")!="UNVERIFIED_LOCAL_OPTICAL_BENCH":
            raise ReferenceError("input is not a bench recording")
        frames=payload["frames"]
        if not 1 <= len(frames) <= MAX_FRAMES:
            raise ReferenceError("recording contains no reviewable stills")
        data=[]
        for meta in frames:
            image=(root/meta["file"]).read_bytes()
            data.append({"index":meta["frame"],
                         "host_after_read_ns":meta["host_monotonic_ns_after_read"],
                         "brightness":round(brightness(image,region),5)})
        return {"schema":"PG01-OBSERVATION-SERIES-1",
                "station":payload["station"],
                "source_dir_name":root.name,
                "source_manifest_sha256":hashlib.sha256((root/"manifest.json").read_bytes()).hexdigest(),
                "region":region,
                "frames":data,
                "camera_exposure_time_known":False,
                "source_validity":"STRUCTURALLY VERIFIED BENCH DATA; SOURCE AUTHENTICITY UNVERIFIED"}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        raise ReferenceError("cannot inspect BENCH capture: "+str(exc)[:200]) from exc


def find_flash(series, contrast=22.0, min_consecutive=2):
    """Detect sustained positive change after a dark baseline.

    Rejects no-baseline, single-frame spikes and uncertain onsets; no
    extrapolation to camera exposure time is performed.
    """
    if not isinstance(series,dict) or series.get("schema")!="PG01-OBSERVATION-SERIES-1":
        raise ReferenceError("invalid observation series")
    if not isinstance(contrast,(int,float)) or isinstance(contrast,bool) or not math.isfinite(contrast) or not 5 <= contrast <= 100:
        raise ReferenceError("contrast must be finite and within 5–100 brightness levels")
    if min_consecutive not in (2,3,4):
        raise ReferenceError("require 2–4 sustained bright frames")
    frames=series["frames"]
    if not isinstance(frames,list) or len(frames) < MIN_BACKGROUND+min_consecutive+1:
        raise ReferenceError("not enough frames for baseline plus persistent onset")
    vals=[float(f["brightness"]) for f in frames]
    if any(not math.isfinite(v) or v<0 or v>255 for v in vals):
        raise ReferenceError("invalid luminance values")
    stamps=[f["host_after_read_ns"] for f in frames]
    if any(not isinstance(t,int) or t<0 for t in stamps) or any(b<=a for a,b in zip(stamps,stamps[1:])):
        raise ReferenceError("recording receipt timestamps are not strictly increasing")
    baseline=statistics.median(vals[:MIN_BACKGROUND])
    if baseline > 230:
        return {"state":"INCONCLUSIVE","reason":"Initial baseline saturated/bright",
                "baseline":baseline,"threshold":None,"onset":None}
    # Robust baseline variability from explicitly pre-event first frames.
    mad=statistics.median(abs(v-baseline) for v in vals[:MIN_BACKGROUND])
    threshold=baseline+max(float(contrast),8.0*1.4826*mad)
    if threshold>255:
        return {"state":"INCONCLUSIVE","reason":"Bright baseline/unstable lighting",
                "baseline":baseline,"threshold":threshold,"onset":None}
    dark_required=MIN_BACKGROUND
    start=None
    for j in range(MIN_BACKGROUND,len(vals)-min_consecutive+1):
        if vals[j-1] < threshold and all(v >= threshold for v in vals[j:j+min_consecutive]):
            start=j
            break
    if start is None:
        return {"state":"NO SUSTAINED REFERENCE EVENT","reason":"No persistent bright transition",
                "baseline":baseline,"threshold":round(threshold,5),
                "onset":None}
    last_dark=frames[start-1]
    first_bright=frames[start]
    return {"state":"HOST RECEIPT ONSET BRACKET ONLY",
            "reason":"Sustained brightness rise in operator-selected ROI",
            "baseline":round(baseline,5),
            "threshold":round(threshold,5),
            "onset":{"first_bright_index":start,
                     "last_dark_host_after_read_ns":last_dark["host_after_read_ns"],
                     "first_bright_host_after_read_ns":first_bright["host_after_read_ns"],
                     "host_receipt_bracket_width_ms":round(
                        (first_bright["host_after_read_ns"]-last_dark["host_after_read_ns"])/1e6,3),
                     "first_bright_brightness":first_bright["brightness"]}}


def compare_reference_events(series_a,series_b,contrast=22.0):
    """Return post-read host interval comparisons, NOT physical camera offset."""
    if series_a["station"]!="A" or series_b["station"]!="B":
        raise ReferenceError("comparison requires Station A and B independently")
    fa=find_flash(series_a,contrast)
    fb=find_flash(series_b,contrast)
    result={"schema":SCHEMA,"mode":"UNVERIFIED BENCH / HOST RECEIPT ONLY",
            "station_a":fa,"station_b":fb,
            "a_manifest_sha256":series_a["source_manifest_sha256"],
            "b_manifest_sha256":series_b["source_manifest_sha256"],
            "regions":{"A":series_a["region"],"B":series_b["region"]},
            "declared_shared_light_event_confirmed":False,
            "actual_exposure_offset_ms":None,
            "physical_event_time_difference_ms":None,
            "camera_clocks_synchronized":False,
            "warning":"The two bright events may be unrelated. Even if both cameras witnessed "
                      "one flash, USB/driver latency and exposure timing remain unknown.",
            "review_action":"Physically validate a common flash and measure exposure/driver latency "
                            "under a pre-registered reference protocol before time-offset claims."}
    if fa["onset"] is None or fb["onset"] is None:
        result["state"]="INCONCLUSIVE / NO PAIR OF VALID TRANSITIONS"
        result["host_receipt_bracket_delta_ms"]=None
        return result
    a,b=fa["onset"],fb["onset"]
    # For apparent host after-read timings t_B - t_A, with possible receipt
    # onset between last-dark and first-bright. This is NOT an exposure bracket.
    lower=(b["last_dark_host_after_read_ns"]-a["first_bright_host_after_read_ns"])/1e6
    upper=(b["first_bright_host_after_read_ns"]-a["last_dark_host_after_read_ns"])/1e6
    result["state"]="PAIR OF UNVERIFIED HOST RECEIPT TRANSITIONS"
    result["host_receipt_bracket_delta_ms"]={"lower":round(lower,3),"upper":round(upper,3)}
    result["host_first_bright_delta_ms"]=round(
        (b["first_bright_host_after_read_ns"]-a["first_bright_host_after_read_ns"])/1e6,3)
    return result


def build_review(source_a,source_b,region_a="CENTER",region_b="CENTER",contrast=22.0):
    a=inspect_capture(source_a,region_a)
    b=inspect_capture(source_b,region_b)
    result=compare_reference_events(a,b,contrast)
    result["created_utc"]=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    result["calculation"]=(
        "Each ROI's grayscale mean; first five frames set a robust dark baseline; "
        ">=2 consecutive bright frames identify a host arrival transition. "
        "No physical camera timing or matter transfer estimated."
    )
    return {"comparison":result,"trace_a":a,"trace_b":b}


def save_review(review,output):
    """Exclusive-write analysis separate from originals and real experiment records."""
    path=Path(output)
    if not path.name.startswith("BENCH_REFERENCE_") or path.suffix.lower()!=".json":
        raise ReferenceError("analysis filename must be BENCH_REFERENCE_*.json")
    if review.get("comparison",{}).get("schema")!=SCHEMA:
        raise ReferenceError("cannot save unknown analysis schema")
    data=(json.dumps(review,indent=2,allow_nan=False,ensure_ascii=True)+"\n").encode()
    with path.open("xb") as f:
        f.write(data)
    digest=hashlib.sha256(data).hexdigest()
    with path.with_suffix(".sha256").open("x",encoding="ascii") as f:
        f.write(digest+"  "+path.name+"\n")
    return digest
