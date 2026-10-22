"""PG-01 bench scale regression — unreviewed estimates, NEVER physics validation.

The fit is for reference-mass readings recorded externally. No real calibration is
performed by software alone; source authenticity, traceability, instrument drift,
hysteresis, repeatability, and combined uncertainty require physical assessment.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROFILE_SCHEMA = "PG01-BENCH-CAL-1"
MAX_ROWS = 2500


class CalibrationError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc)


def canonical_bytes(payload):
    return json.dumps(payload, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def checksum(payload):
    """Detect accidental profile edits. SHA-256 is not a signature."""
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _number(value, label):
    if isinstance(value, bool):
        raise CalibrationError(label + " is not numeric")
    try:
        n = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise CalibrationError(label + " is not numeric") from exc
    if not math.isfinite(n):
        raise CalibrationError(label + " must be finite")
    return n


def parse_worksheet(path):
    """CSV header: reference_g,raw_counts. All data is operator-provided."""
    path = Path(path)
    if path.suffix.lower() != ".csv" or path.stat().st_size > 125_000:
        raise CalibrationError("expected small .csv worksheet (<=125 KB)")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, strict=True)
        if reader.fieldnames != ["reference_g", "raw_counts"]:
            raise CalibrationError("CSV headers must be reference_g,raw_counts")
        rows = []
        for idx, item in enumerate(reader, 2):
            if idx > MAX_ROWS+1:
                raise CalibrationError("worksheet is too long")
            grams = _number(item.get("reference_g"), "reference mass")
            raw_value = _number(item.get("raw_counts"), "raw ADC counts")
            if grams < 0 or grams > 100_000:
                raise CalibrationError("reference mass outside supported lab range")
            if int(raw_value) != raw_value or not -(1<<23) <= raw_value < 1<<23:
                raise CalibrationError("raw counts not a signed 24-bit integer")
            rows.append((grams, int(raw_value)))
    return rows, hashlib.sha256(path.read_bytes()).hexdigest()


def fit(rows, station, uncertainty_g, reference_id, operator, expiration_days=30,
        source_sha256=None, at=None):
    if station not in ("A", "B"):
        raise CalibrationError("station must be A or B")
    u = _number(uncertainty_g, "reference-mass uncertainty")
    if u <= 0 or u > 1000:
        raise CalibrationError("positive external reference uncertainty in grams required")
    if not isinstance(reference_id, str) or not 4 <= len(reference_id.strip()) <= 120:
        raise CalibrationError("identify physical reference mass set or certificate")
    if not isinstance(operator, str) or not 2 <= len(operator.strip()) <= 120:
        raise CalibrationError("record operator responsible for observations")
    if not isinstance(expiration_days, int) or isinstance(expiration_days, bool) or not 1 <= expiration_days <= 365:
        raise CalibrationError("validity interval 1–365 days")
    if not 6 <= len(rows) <= MAX_ROWS:
        raise CalibrationError("at least six readings are required")
    masses, counts = [], []
    for mass, raw in rows:
        m=_number(mass, "reference mass")
        if m < 0 or m > 100_000:
            raise CalibrationError("reference mass out of range")
        v=_number(raw, "raw counts")
        if int(v) != v or not -(1<<23) <= v < 1<<23:
            raise CalibrationError("raw counts out of range")
        masses.append(m)
        counts.append(int(v))
    repeats=Counter(masses)
    if len(repeats)<3 or any(q<2 for q in repeats.values()):
        raise CalibrationError("use at least 3 distinct reference masses, with >=2 readings at each mass")
    mean_x=sum(counts)/len(counts)
    mean_y=sum(masses)/len(masses)
    xx=sum((x-mean_x)**2 for x in counts)
    yy=sum((y-mean_y)**2 for y in masses)
    if xx <= 0 or yy <= 0:
        raise CalibrationError("degenerate calibration: no change in raw counts or mass")
    slope=sum((x-mean_x)*(y-mean_y) for x,y in zip(counts,masses))/xx
    offset=mean_y-slope*mean_x
    if slope == 0 or not math.isfinite(slope) or not math.isfinite(offset):
        raise CalibrationError("invalid sensor response")
    residuals=[(slope*x+offset)-y for x,y in zip(counts,masses)]
    rmse=math.sqrt(sum(e*e for e in residuals)/(len(rows)-2))
    r2=1-sum(e*e for e in residuals)/yy
    if not 0 <= r2 <= 1 or not math.isfinite(rmse):
        raise CalibrationError("no credible linear regression")
    at=at or _now()
    if at.tzinfo is None:
        raise CalibrationError("timestamp requires UTC offset")
    utc=at.astimezone(timezone.utc)
    data={
        "schema":PROFILE_SCHEMA,
        "stage":"BENCH_ESTIMATE_UNREVIEWED",
        "station":station,
        "created_utc":utc.isoformat().replace("+00:00","Z"),
        "expires_utc":(utc+timedelta(days=expiration_days)).isoformat().replace("+00:00","Z"),
        "operator":operator.strip(),
        "reference_id":reference_id.strip(),
        "operator_declared_reference_uncertainty_g":u,
        "source_csv_sha256":source_sha256,
        "sample_count":len(rows),
        "distinct_masses_g":sorted(repeats),
        "raw_min":min(counts),
        "raw_max":max(counts),
        "slope_g_per_count":slope,
        "offset_g":offset,
        "fit_residual_rmse_g":rmse,
        "fit_r_squared":r2,
        "warnings":[
            "UNCALIBRATED OR UNVERIFIED REFERENCE SOURCES MAY INVALIDATE THIS FIT",
            "Regression residual is not total expanded measurement uncertainty",
            "Clock drift, sensor hysteresis, mounting, thermal noise and zero drift are not certified",
            "No matter transfer or object identity can be established by this profile",
        ],
    }
    return {**data,"sha256":checksum(data)}


def validate_profile(profile, station=None, now=None):
    if not isinstance(profile, dict) or profile.get("schema")!=PROFILE_SCHEMA:
        raise CalibrationError("unknown calibration schema")
    if station is not None and profile.get("station")!=station:
        raise CalibrationError("calibration profile station mismatch")
    if profile.get("stage")!="BENCH_ESTIMATE_UNREVIEWED":
        raise CalibrationError("unapproved calibration stage")
    expected=checksum({key:value for key,value in profile.items() if key!="sha256"})
    if profile.get("sha256")!=expected:
        raise CalibrationError("calibration checksum does not match contents")
    try:
        started=datetime.fromisoformat(profile["created_utc"].replace("Z","+00:00"))
        expires=datetime.fromisoformat(profile["expires_utc"].replace("Z","+00:00"))
    except (KeyError,ValueError,AttributeError) as exc:
        raise CalibrationError("invalid UTC validity timestamp") from exc
    now=now or _now()
    if started.tzinfo is None or expires.tzinfo is None or started > now or expires <= now:
        raise CalibrationError("calibration is not current: expired, future or malformed")
    if profile.get("station") not in ("A","B"):
        raise CalibrationError("invalid station")
    a=_number(profile.get("raw_min"), "raw minimum")
    b=_number(profile.get("raw_max"), "raw maximum")
    if not -(1<<23) <= a < b < 1<<23:
        raise CalibrationError("invalid ADC calibration range")
    if not (0 < abs(_number(profile.get("slope_g_per_count"),"slope")) < 1e4):
        raise CalibrationError("invalid calibration slope")
    _number(profile.get("offset_g"),"offset")
    _number(profile.get("fit_residual_rmse_g"),"RMSE")
    if profile.get("sample_count",0)<6:
        raise CalibrationError("insufficient calibration observations")
    return profile


def estimate(profile, raw, station=None, now=None):
    validate_profile(profile, station, now)
    count=_number(raw, "raw ADC count")
    if int(count)!=count or not -(1<<23)<=count<1<<23:
        raise CalibrationError("invalid sensor count")
    if not profile["raw_min"] <= count <= profile["raw_max"]:
        raise CalibrationError("raw count outside reference-tested range — estimate suppressed")
    val=profile["slope_g_per_count"]*count+profile["offset_g"]
    if not math.isfinite(val):
        raise CalibrationError("invalid derived estimate")
    return {"estimate_g":val, "label":"BENCH ESTIMATE / UNREVIEWED / NOT CERTIFIED",
            "fit_rmse_g":profile["fit_residual_rmse_g"],
            "profile_checksum":profile["sha256"],
            "note":"Fit RMSE is NOT total uncertainty. No physical transfer evidence."}


def load_profile(path, station=None):
    try:
        with Path(path).open("r", encoding="utf-8") as f:
            data=json.load(f)
    except (OSError,ValueError) as exc:
        raise CalibrationError("could not load calibration profile") from exc
    return validate_profile(data, station)


def save_profile(profile, path):
    path=Path(path)
    if not path.name.startswith("BENCH_CAL_") or path.suffix.lower()!=".json":
        raise CalibrationError("profile file must be named BENCH_CAL_*.json")
    validate_profile(profile)
    with path.open("x",encoding="utf-8") as stream:
        stream.write(json.dumps(profile,indent=2,ensure_ascii=True,allow_nan=False)+"\n")
    return path
