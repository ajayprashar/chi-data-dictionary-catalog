#!/usr/bin/env python3
"""Fail if PBIP tree has OPC-risky *directory* paths or spaces in any path segment."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from pbip_paths import PBIP_REPORT_DIR, pbip_root  # noqa: E402

_DIR_UNSAFE = re.compile(r"[^A-Za-z0-9.]")  # .Report / .SemanticModel suffix


def _dir_segment_ok(part: str) -> bool:
    if part in {".", "..", ".pbi"}:
        return True
    if "." in part and (part.endswith(".Report") or part.endswith(".SemanticModel") or part.endswith(".pbip")):
        return part.split(".", 1)[0].isalnum()
    return part.isalnum()


def main() -> None:
    pbip = pbip_root(REPO)
    if not pbip.is_dir():
        raise SystemExit(f"PBIP folder not found: {pbip}")

    violations: list[str] = []

    for path in pbip.rglob("*"):
        rel = path.relative_to(pbip)
        for part in rel.parts:
            if " " in part:
                violations.append(f"{rel} (space in {part!r})")
                break
        if path.is_dir():
            for part in rel.parts:
                if not _dir_segment_ok(part):
                    violations.append(f"{rel}/ (unsafe directory segment {part!r})")
                    break

    report_json = pbip / PBIP_REPORT_DIR / "definition" / "report.json"
    if report_json.is_file():
        data = json.loads(report_json.read_text(encoding="utf-8"))
        for pkg in data.get("resourcePackages", []):
            for item in pkg.get("items", []):
                resource_path = item.get("path", "")
                for seg in Path(resource_path).parts:
                    if " " in seg or not seg.replace(".", "").isalnum():
                        violations.append(f"report.json resource path segment {seg!r} in {resource_path}")

    if violations:
        print("PBIP path validation FAILED:", file=sys.stderr)
        for v in sorted(set(violations)):
            print(f"  - {v}", file=sys.stderr)
        raise SystemExit(1)

    print("PBIP path validation: OK (no spaces; OPC-safe directory segments)")


if __name__ == "__main__":
    main()
