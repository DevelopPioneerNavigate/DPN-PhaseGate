#!/usr/bin/env python3
"""Offline structural integrity validator for DPN PhaseGate research records.

Python standard library only. Passing does not validate scientific claims.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = re.compile(r"^SRC-\d{3}$")
HYP_ID = re.compile(r"^H-PG-\d{3}$")
RUN_ID = re.compile(r"^PG-\d{8}-\d{3}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SOURCE_TYPES = {"peer_reviewed", "institutional_explainer", "preprint", "book", "other"}
HYP_STATUSES = {"proposed", "theoretical", "testing", "contradicted", "literature_supported", "replicated"}


def utc_timestamp(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamp must be UTC ISO 8601 ending Z")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp is not UTC")
    return parsed


def audit(root=ROOT):
    """Return textual errors, not a claim that any experiment is scientifically valid."""
    root = Path(root)
    errors = []

    def fail(path, detail):
        errors.append(f"{path}: {detail}")

    def load(path):
        try:
            with (root / path).open("r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError) as exc:
            fail(path, f"cannot load JSON: {exc}")
            return None

    def required(obj, keys, where):
        if not isinstance(obj, dict):
            fail(where, "expected object")
            return False
        missing = [key for key in keys if key not in obj]
        for key in missing:
            fail(where, f"missing {key}")
        return not missing

    literature_path = "data/literature/sources.json"
    hypothesis_path = "data/hypotheses/hypotheses.json"
    manifest_path = "data/experiments/manifest.json"
    literature = load(literature_path)
    hypotheses = load(hypothesis_path)
    manifest = load(manifest_path)
    source_ids = set()
    hypothesis_ids = set()

    if required(literature, ["version", "reviewed_on", "sources"], literature_path):
        if literature["version"] != 1:
            fail(literature_path, "unsupported registry version")
        try:
            date.fromisoformat(literature["reviewed_on"])
        except (TypeError, ValueError):
            fail(literature_path, "reviewed_on must be YYYY-MM-DD")
        if not isinstance(literature["sources"], list):
            fail(literature_path, "sources must be array")
        else:
            for index, item in enumerate(literature["sources"]):
                where = f"{literature_path}#{index}"
                keys = ["id", "title", "authors", "year", "type", "doi", "url", "claim", "non_claim"]
                if not required(item, keys, where):
                    continue
                sid = item["id"]
                if not isinstance(sid, str) or not SOURCE_ID.fullmatch(sid):
                    fail(where, "invalid source ID")
                if sid in source_ids:
                    fail(where, f"duplicate source {sid}")
                source_ids.add(sid)
                parsed = urlparse(item["url"]) if isinstance(item["url"], str) else None
                if parsed is None or parsed.scheme != "https" or not parsed.netloc:
                    fail(where, "source URL must be https and absolute")
                if item["type"] not in SOURCE_TYPES:
                    fail(where, "invalid source type")
                if item["doi"] is not None and (not isinstance(item["doi"], str) or not item["doi"].startswith("10.")):
                    fail(where, "invalid DOI field")
                if item["year"] is not None and (not isinstance(item["year"], int) or not 1600 <= item["year"] <= 2200):
                    fail(where, "invalid publication year")
                for field in ("title", "authors", "claim", "non_claim"):
                    if not isinstance(item[field], str) or len(item[field].strip()) < 5:
                        fail(where, f"missing meaningful {field}")

    if required(hypotheses, ["version", "hypotheses"], hypothesis_path):
        if hypotheses["version"] != 1:
            fail(hypothesis_path, "unsupported registry version")
        if not isinstance(hypotheses["hypotheses"], list):
            fail(hypothesis_path, "hypotheses must be array")
        else:
            for index, item in enumerate(hypotheses["hypotheses"]):
                where = f"{hypothesis_path}#{index}"
                keys = ["id", "title", "status", "source_ids", "statement", "falsifier", "prediction", "limitations"]
                if not required(item, keys, where):
                    continue
                hid = item["id"]
                if not isinstance(hid, str) or not HYP_ID.fullmatch(hid):
                    fail(where, "invalid hypothesis ID")
                if hid in hypothesis_ids:
                    fail(where, f"duplicate hypothesis {hid}")
                hypothesis_ids.add(hid)
                if item["status"] not in HYP_STATUSES:
                    fail(where, "invalid hypothesis status")
                if not isinstance(item["source_ids"], list) or not item["source_ids"]:
                    fail(where, "hypothesis must cite sources")
                else:
                    for sid in item["source_ids"]:
                        if sid not in source_ids:
                            fail(where, f"unknown source reference {sid}")
                for field in ("title", "statement", "falsifier", "prediction", "limitations"):
                    if not isinstance(item[field], str) or len(item[field].strip()) < 10:
                        fail(where, f"missing meaningful {field}")

    if required(manifest, ["version", "experiments"], manifest_path):
        if manifest["version"] != 1:
            fail(manifest_path, "unsupported registry version")
        if not isinstance(manifest["experiments"], list):
            fail(manifest_path, "experiments must be array")
        else:
            seen = set()
            for runid in manifest["experiments"]:
                where = f"data/experiments/{runid}.json"
                if not isinstance(runid, str) or not RUN_ID.fullmatch(runid):
                    fail(manifest_path, f"invalid run ID: {runid}")
                    continue
                if runid in seen:
                    fail(manifest_path, f"duplicate experiment {runid}")
                seen.add(runid)
                run = load(where)
                keys = ["id", "hypothesis_id", "protocol_path", "status", "started_at", "ended_at",
                        "operator", "witness", "safety_review", "calibration_ids", "controls",
                        "measurements", "evidence", "conclusion"]
                if not required(run, keys, where):
                    continue
                if run["id"] != runid:
                    fail(where, "run ID does not match filename/manifest")
                if run["hypothesis_id"] not in hypothesis_ids:
                    fail(where, "unknown hypothesis ID")
                if run["status"] not in ("completed", "aborted"):
                    fail(where, "real run status must be completed or aborted")
                path = run["protocol_path"]
                if not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts or not (root / path).is_file():
                    fail(where, "protocol_path must identify an existing repository file")
                try:
                    if utc_timestamp(run["ended_at"]) < utc_timestamp(run["started_at"]):
                        fail(where, "run ended before it started")
                except (TypeError, ValueError) as exc:
                    fail(where, f"invalid UTC times: {exc}")
                if not isinstance(run["operator"], str) or not run["operator"].strip():
                    fail(where, "operator is required")
                if not isinstance(run["witness"], str) or not run["witness"].strip():
                    fail(where, "independent witness is required")
                review = run["safety_review"]
                if not isinstance(review, dict) or review.get("approved") is not True or not review.get("review_id"):
                    fail(where, "real run requires actual approved safety review")
                for field in ("calibration_ids", "controls", "measurements", "evidence"):
                    if not isinstance(run[field], list) or not run[field]:
                        fail(where, f"{field} must not be empty")
                if isinstance(run["evidence"], list):
                    for evidence in run["evidence"]:
                        if not isinstance(evidence, dict) or not evidence.get("uri") or not isinstance(evidence.get("sha256"), str) or not SHA256.fullmatch(evidence["sha256"]):
                            fail(where, "evidence needs URI and lower-case SHA-256 digest")
                if not isinstance(run["conclusion"], str) or len(run["conclusion"].strip()) < 10:
                    fail(where, "record conclusion and limitations")
            actual = set()
            folder = root / "data/experiments"
            if folder.exists():
                actual = {p.stem for p in folder.glob("PG-*.json")}
            for orphan in sorted(actual - seen):
                fail(manifest_path, f"unregistered run file {orphan}")
    return errors


def main():
    errors = audit()
    if errors:
        for error in errors:
            print("FAIL:", error, file=sys.stderr)
        print(f"RESEARCH INTEGRITY: FAIL ({len(errors)} structural error(s))", file=sys.stderr)
        return 1
    print("RESEARCH INTEGRITY: PASS (structure only; no scientific finding verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
