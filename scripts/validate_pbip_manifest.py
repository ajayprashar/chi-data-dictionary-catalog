#!/usr/bin/env python3
"""Compare data/pbip_report_manifest.py VISUALS to live PBIP visual.json projections."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
from pbip_paths import report_definition  # noqa: E402

REPORT_PAGES = report_definition(REPO) / "pages"

sys.path.insert(0, str(REPO / "data"))
sys.path.insert(0, str(REPO / "scripts"))
from pbip_layout_constants import WALKTHROUGH_PAGE_ID  # noqa: E402
from pbip_report_manifest import (  # noqa: E402
    PAGE_FIELD_GUIDE,
    PAGE_START_HERE,
    VISUALS,
)

SKIP_PAGES = {PAGE_START_HERE, PAGE_FIELD_GUIDE, WALKTHROUGH_PAGE_ID}


@dataclass(frozen=True)
class PbipVisual:
    page_id: str
    visual_type: str
    title: str
    entity: str | None
    columns: tuple[str, ...]


def _literal_text(expr: dict) -> str:
    return str(expr.get("Literal", {}).get("Value", "")).strip("'")


def visual_title(container: dict) -> str:
    for block in container.get("visual", {}).get("visualContainerObjects", {}).get("title", []):
        text = block.get("properties", {}).get("text", {}).get("expr", {})
        if text:
            return _literal_text(text)
    return ""


def visual_title_base(title: str) -> str:
    """Primary title before subtitle (newline or hyphen separator)."""
    base = title.split("\n", 1)[0]
    if " - " in base:
        base = base.split(" - ", 1)[0]
    return base


def titles_match(expected: str, actual: str) -> bool:
    if actual == expected:
        return True
    return visual_title_base(actual) == expected


def projection_field(projection: dict) -> tuple[str | None, str | None, bool]:
    field = projection.get("field", {})
    if "Column" in field:
        col = field["Column"]
        entity = col["Expression"]["SourceRef"]["Entity"]
        return entity, col["Property"], False
    if "Measure" in field:
        meas = field["Measure"]
        entity = meas["Expression"]["SourceRef"]["Entity"]
        return entity, meas["Property"], True
    return None, None, False


def extract_pbip_visuals() -> list[PbipVisual]:
    found: list[PbipVisual] = []
    if not REPORT_PAGES.is_dir():
        return found
    for page_dir in sorted(REPORT_PAGES.iterdir()):
        if not page_dir.is_dir() or page_dir.name in SKIP_PAGES:
            continue
        visuals_dir = page_dir / "visuals"
        if not visuals_dir.is_dir():
            continue
        for visual_path in sorted(visuals_dir.glob("*/visual.json")):
            data = json.loads(visual_path.read_text(encoding="utf-8"))
            vtype = data.get("visual", {}).get("visualType", "")
            if vtype not in ("tableEx", "card", "clusteredBarChart"):
                continue
            title = visual_title(data)
            query = data.get("visual", {}).get("query", {}).get("queryState", {})
            entity: str | None = None
            columns: list[str] = []
            if vtype == "clusteredBarChart":
                for projection in query.get("Category", {}).get("projections", []):
                    ent, prop, _ = projection_field(projection)
                    if ent and prop:
                        entity = ent
                        columns.append(prop)
            else:
                for projection in query.get("Values", {}).get("projections", []):
                    ent, prop, _ = projection_field(projection)
                    if ent and prop:
                        entity = ent
                        columns.append(prop)
            found.append(
                PbipVisual(
                    page_id=page_dir.name,
                    visual_type=vtype,
                    title=title,
                    entity=entity,
                    columns=tuple(columns),
                )
            )
    return found


def _card_columns_by_page_entity(pbip: list[PbipVisual]) -> dict[tuple[str, str], set[str]]:
    grouped: dict[tuple[str, str], set[str]] = {}
    for v in pbip:
        if v.visual_type != "card" or not v.entity or not v.columns:
            continue
        key = (v.page_id, v.entity)
        grouped.setdefault(key, set()).update(v.columns)
    return grouped


def validate_manifest() -> list[str]:
    errors: list[str] = []
    pbip = extract_pbip_visuals()
    card_groups = _card_columns_by_page_entity(pbip)

    tables_and_charts = [
        v for v in pbip if v.visual_type in ("tableEx", "clusteredBarChart")
    ]

    for manifest in VISUALS:
        page_id = manifest["page_id"]
        title = manifest["visual_title"]
        entity = manifest["semantic_model_table"]
        expected_cols = tuple(manifest["columns"])

        if manifest.get("is_measure"):
            actual = card_groups.get((page_id, entity), set())
            expected = set(expected_cols)
            if actual != expected:
                missing = sorted(expected - actual)
                extra = sorted(actual - expected)
                msg = f"{page_id} card group '{title}' ({entity}):"
                if missing:
                    msg += f" missing {missing}"
                if extra:
                    msg += f" extra {extra}"
                errors.append(msg)
            continue

        match = next(
            (
                v
                for v in tables_and_charts
                if v.page_id == page_id and titles_match(title, v.title)
            ),
            None,
        )
        if match is None:
            candidates = [v.title for v in tables_and_charts if v.page_id == page_id]
            errors.append(
                f"{page_id}: no PBIP visual titled '{title}'. On page: {candidates or '(none)'}"
            )
            continue
        if match.entity != entity:
            errors.append(
                f"{page_id} '{title}': entity {match.entity!r} != manifest {entity!r}"
            )
        if match.columns != expected_cols:
            errors.append(
                f"{page_id} '{title}': columns {list(match.columns)} != manifest {list(expected_cols)}"
            )

    return errors


def main() -> None:
    errors = validate_manifest()
    if errors:
        print("PBIP manifest validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)
    print("PBIP manifest validation: OK")


if __name__ == "__main__":
    main()
