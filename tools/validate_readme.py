#!/usr/bin/env python3
"""DPN PhaseGate README and vector-asset integrity checker.

No dependencies. Ensures navigation/illustrations render safely; NOT physics validation.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE_PATHS = (
    "README.md",
    "docs/VISUAL-ATLAS.md",
    "docs/engineering/PG-01-BLUEPRINTS.md",
    "docs/engineering/PG01-CALIBRATION-AND-WITNESS-v0.8.md",
    "docs/physics/PHYSICS-COMMAND.md",
    "docs/physics/EVIDENCE-WORKFLOW.md",
    "docs/safety/SAFETY-COMMAND.md",
    "docs/physics/baseline.md",
    "docs/physics/2025-wormhole-scrutiny.md",
    "docs/physics/feasibility.md",
    "docs/engineering/PG-01-architecture.md",
    "docs/engineering/PG01-IMPLEMENTATION-PLAN.md",
    "docs/safety/safety.md",
    "docs/protocols/PG-PROT-NULL-001.md",
    "data/README.md",
    "docs/qa/validation.md",
    "docs/qa/PG01-calibration.md",
    "docs/governance/decisions.md",
    "docs/charter.md",
    "docs/roadmap.md",
    "docs/PROJECT-OVERVIEW.md",
    "docs/START-HERE.md",
    "docs/engineering/PG01-IMPLEMENTATION-PLAN.md",
    "docs/brand/DPN-IDENTITY.md",
    "docs/GITHUB-ABOUT.md",
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]+\]\(([^)\s]+)(?:\s+['\"][^)]*['\"])?\)")
HTML_IMAGE = re.compile(r"<img\s+[^>]*?\bsrc\s*=\s*['\"]([^'\"]+)['\"]", flags=re.IGNORECASE)
SVG_NS = "{http://www.w3.org/2000/svg}"


def check_repo(root=ROOT, pages=PAGE_PATHS):
    root = Path(root).resolve()
    errors = []

    def error(path, msg):
        errors.append(f"{path}: {msg}")

    for rel in pages:
        page = root / rel
        if not page.is_file():
            error(rel, "missing required documentation page")
            continue
        content = page.read_text(encoding="utf-8")
        if rel == "README.md":
            for token in ("PHASEGATE", "unverified", "measurement", "DPN"):
                if token.casefold() not in content.casefold():
                    error(rel, f"README must state research context: {token}")
        links = MARKDOWN_LINK.findall(content) + HTML_IMAGE.findall(content)
        for raw in links:
            if raw.startswith(("#", "//")):
                continue
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                if parsed.scheme.lower() not in ("https", "mailto"):
                    error(rel, f"nonapproved external link scheme: {raw}")
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                error(rel, f"link escapes repository: {raw}")
                continue
            if not target.is_file():
                error(rel, f"broken internal link or image: {raw}")

    asset_dir = root / "assets"
    if not asset_dir.is_dir():
        error("assets/", "missing branding asset directory")
    else:
        vectors = list(asset_dir.glob("*.svg"))
        if not vectors:
            error("assets/", "no branding vectors")
        for path in vectors:
            rel = path.relative_to(root).as_posix()
            try:
                tree = ET.parse(path)
                svg = tree.getroot()
            except ET.ParseError as exc:
                error(rel, f"malformed SVG XML: {exc}")
                continue
            if svg.tag != SVG_NS + "svg":
                error(rel, "root must be SVG")
            if "viewBox" not in svg.attrib:
                error(rel, "SVG missing responsive viewBox")
            for node in svg.iter():
                name = node.tag.rsplit("}", 1)[-1].lower()
                if name in ("script", "foreignobject", "iframe", "image", "use"):
                    error(rel, f"unsafe/externally dependent SVG node: {name}")
                for key, val in node.attrib.items():
                    attr = key.rsplit("}", 1)[-1].lower()
                    if attr.startswith("on") or attr in ("href", "src"):
                        error(rel, f"inline or external asset reference not allowed: {attr}")
                    if "javascript:" in val.lower() or "url(http" in val.lower():
                        error(rel, f"remote/script value is not allowed: {attr}")
    return errors


def main():
    errors = check_repo()
    if errors:
        for issue in errors:
            print("README INTEGRITY FAIL:", issue, file=sys.stderr)
        return 1
    print("README INTEGRITY PASS: links, DPN branding and SVG structure (not scientific proof)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
