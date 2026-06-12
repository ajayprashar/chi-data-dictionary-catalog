#!/usr/bin/env python3
"""Apply readability layout to existing PBIP visuals without full report regeneration.

Updates slicer width, FHIR table columns/height, and table word wrap. Safe to re-run.
Layout constants: scripts/pbip_layout_constants.py (keep in sync with enhance_pbip_report.py).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
from pbip_paths import report_definition  # noqa: E402

REPORT_VISUALS = report_definition(REPO) / "pages"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pbip_layout_constants import (  # noqa: E402
    ADT_CONTEXT_COLUMNS,
    ADT_CONTEXT_TITLE,
    CCDA_STANDARDS_COLUMNS,
    CCDA_TITLE,
    DICT_PROFILE_TITLE,
    FHIR_STANDARDS_COLUMNS,
    FHIR_STANDARDS_TABLE_H,
    FHIR_STANDARDS_TITLE,
    GOVERNED_CODES_COLUMNS,
    GOVERNED_CODES_SUBTITLE,
    GOVERNED_CODES_TITLE,
    SLICER_H_PROFILE,
    SLICER_H_STANDARDS,
    SLICER_TITLE,
    SLICER_W,
    SOURCE_XW_SUBTITLE,
    SOURCE_XW_TITLE,
    STANDARDS_ADT_TABLE_H,
    standards_page_y_positions,
)


def _visual_title(visual: dict) -> str:
    for block in visual.get("visualContainerObjects", {}).get("title", []):
        props = block.get("properties", {})
        text = props.get("text", {}).get("expr", {}).get("Literal", {}).get("Value", "")
        if text.startswith("'") and text.endswith("'"):
            return text[1:-1]
        return text
    return ""


def _entity_prop(query_ref: str) -> tuple[str, str] | None:
    if "." not in query_ref:
        return None
    entity, prop = query_ref.rsplit(".", 1)
    return entity, prop


def _projection(entity: str, prop: str) -> dict:
    return {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": entity}},
                "Property": prop,
            }
        },
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop,
    }


def _set_table_columns(visual: dict, entity: str, props: list[str]) -> None:
    visual.setdefault("query", {}).setdefault("queryState", {}).setdefault("Values", {})["projections"] = [
        _projection(entity, p) for p in props
    ]


def _enable_word_wrap(visual: dict) -> None:
    objects = visual.setdefault("objects", {})
    values = objects.get("values", [])
    if not values:
        objects["values"] = [{"properties": {"wordWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
        return
    props = values[0].setdefault("properties", {})
    props["wordWrap"] = {"expr": {"Literal": {"Value": "true"}}}


def patch_visual(container: dict) -> list[str]:
    changes: list[str] = []
    visual = container.get("visual", {})
    vtype = visual.get("visualType", "")
    title = _visual_title(visual)
    name = container.get("name", "?")

    if vtype == "slicer" and SLICER_TITLE in title:
        pos = container.setdefault("position", {})
        if pos.get("width") != SLICER_W:
            pos["width"] = SLICER_W
            changes.append(f"slicer {name}: width -> {SLICER_W}")
        # Standards page sits lower on canvas; either height is fine.
        target_h = SLICER_H_STANDARDS if pos.get("y", 0) > 200 else SLICER_H_PROFILE
        if pos.get("height", 0) > target_h + 8:
            pos["height"] = target_h
            changes.append(f"slicer {name}: height -> {target_h}")

    if vtype == "tableEx":
        if title.startswith(FHIR_STANDARDS_TITLE):
            layout = standards_page_y_positions()
            _set_table_columns(visual, "ddc-master_patient_dictionary", FHIR_STANDARDS_COLUMNS)
            pos = container.setdefault("position", {})
            if pos.get("y") != layout["fhir_y"]:
                pos["y"] = layout["fhir_y"]
                changes.append(f"FHIR table {name}: y -> {layout['fhir_y']}")
            if pos.get("height", 0) < FHIR_STANDARDS_TABLE_H:
                pos["height"] = FHIR_STANDARDS_TABLE_H
                changes.append(f"FHIR table {name}: height -> {FHIR_STANDARDS_TABLE_H}")
            _enable_word_wrap(visual)
            changes.append(f"FHIR table {name}: columns + word wrap")

        elif title == DICT_PROFILE_TITLE:
            _enable_word_wrap(visual)
            changes.append(f"dictionary table {name}: word wrap")

        elif title.startswith(GOVERNED_CODES_TITLE) or title.startswith(SOURCE_XW_TITLE):
            layout = standards_page_y_positions()
            pos = container.setdefault("position", {})
            if title.startswith(GOVERNED_CODES_TITLE):
                _set_table_columns(visual, "ddc-value_set_member", GOVERNED_CODES_COLUMNS)
            if pos.get("y") != layout["codes_y"]:
                pos["y"] = layout["codes_y"]
                changes.append(f"{title[:24]}… {name}: y -> {layout['codes_y']}")
            if pos.get("height", 0) < layout["codes_h"]:
                pos["height"] = layout["codes_h"]
                changes.append(f"{title[:24]}… {name}: height -> {layout['codes_h']}")
            _enable_word_wrap(visual)

        elif title.startswith(ADT_CONTEXT_TITLE) or title == CCDA_TITLE:
            layout = standards_page_y_positions()
            pos = container.setdefault("position", {})
            if pos.get("y") != layout["adt_y"]:
                pos["y"] = layout["adt_y"]
                changes.append(f"{title[:24]}… {name}: y -> {layout['adt_y']}")
            if pos.get("height", 0) < STANDARDS_ADT_TABLE_H:
                pos["height"] = STANDARDS_ADT_TABLE_H
                changes.append(f"{title[:24]}… {name}: height -> {STANDARDS_ADT_TABLE_H}")
            if title.startswith(ADT_CONTEXT_TITLE):
                _set_table_columns(visual, "ddc-hl7_adt_catalog", ADT_CONTEXT_COLUMNS)
                _enable_word_wrap(visual)
                changes.append(f"ADT table {name}: columns include field_id + hl7_ce_encoding")
            elif title.startswith(CCDA_TITLE):
                _set_table_columns(visual, "ddc-ccda_catalog", CCDA_STANDARDS_COLUMNS)
                _enable_word_wrap(visual)
                changes.append(f"CCDA table {name}: slim columns")

    return changes


def main() -> None:
    if not REPORT_VISUALS.is_dir():
        print(f"Report visuals not found: {REPORT_VISUALS}")
        sys.exit(1)

    total = 0
    for visual_path in sorted(REPORT_VISUALS.glob("*/visuals/*/visual.json")):
        raw = visual_path.read_text(encoding="utf-8")
        container = json.loads(raw)
        changes = patch_visual(container)
        if changes:
            visual_path.write_bytes(json.dumps(container, indent=2).encode("utf-8"))
            for line in changes:
                print(f"  {visual_path.parent.name}: {line}")
            total += len(changes)

    print(f"Patched {total} layout change(s). Re-open PBIP and Refresh.")


if __name__ == "__main__":
    main()
