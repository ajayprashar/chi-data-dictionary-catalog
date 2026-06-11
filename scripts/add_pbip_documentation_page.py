#!/usr/bin/env python3
"""Add or refresh PBIP Field guide page and application_guide semantic model table.

Run after layout changes:
  python scripts/generate_pbip_model_guide.py
  python scripts/add_pbip_documentation_page.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "data"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from enhance_pbip_report import (  # noqa: E402
    PAGE_PROFILE_H,
    PAGE_PROFILE_W,
    PRIMARY_BLUE,
    PRIMARY_YELLOW,
    REPORT,
    SEMANTIC_MODEL,
    TABLES_DIR,
    TEXT_BLACK,
    TEXT_WHITE,
    card,
    container_title,
    lit_bool,
    lit_pt,
    lit_str,
    projection,
    shape_rect,
    table_format,
    textbox,
    vid,
    visual_container,
    write_page_json,
    write_text_utf8_no_bom,
    write_visual,
)
from generate_pbip_model_guide import generate as generate_guide  # noqa: E402
from generate_pbip_model_guide import generate_gaps  # noqa: E402
from pbip_layout_constants import DEFAULT_LANDING_PAGE_ID, TAB_FIELD_GUIDE  # noqa: E402
from pbip_report_manifest import (  # noqa: E402
    GUIDE_COLUMNS,
    GUIDE_PARQUET,
    GUIDE_TABLE,
    PAGE_FIELD_GUIDE,
    PAGE_START_HERE,
    PUBLISH_RITUAL,
)
from pilot_curation_checks import (  # noqa: E402
    GUIDE_GAPS_COLUMNS,
    GUIDE_GAPS_PARQUET,
    GUIDE_GAPS_TABLE,
)

GUIDE = GUIDE_TABLE
REPO_PARQUET = r"C:\AI\chi-data-dictionary-catalog"
FIELD_GUIDE_DISPLAY_NAME = TAB_FIELD_GUIDE

DETAIL_COLUMNS = [
    "column_name",
    "layer",
    "editable_in_excel",
    "excel_sheet",
    "steward_action",
    "review_on_page",
    "purpose_short",
    "interop_role",
    "standards_url",
    "pilot_example",
]

GAPS_COLUMNS = [
    "semantic_id",
    "pilot_scope",
    "report_column",
    "gap_reason",
    "excel_sheet",
    "steward_action",
]


def write_guide_table_tmdl() -> None:
    lines = [f"table {GUIDE}", f"\tlineageTag: {vid()}", ""]
    for col in GUIDE_COLUMNS:
        tag = vid()
        lines.extend(
            [
                f"\tcolumn {col}",
                "\t\tdataType: string",
                f"\t\tlineageTag: {tag}",
                "\t\tsummarizeBy: none",
                f"\t\tsourceColumn: {col}",
                "",
                "\t\tannotation SummarizationSetBy = Automatic",
                "",
            ]
        )
    lines.extend(
        [
            f"\tpartition {GUIDE} = m",
            "\t\tmode: import",
            "\t\tsource =",
            "\t\t\t\tlet",
            f'\t\t\t\t    Source = Parquet.Document(File.Contents("{REPO_PARQUET}\\{GUIDE_PARQUET}"), [Compression=null, LegacyColumnNameEncoding=false, MaxDepth=null])',
            "\t\t\t\tin",
            "\t\t\t\t    Source",
            "",
            "\tannotation PBI_NavigationStepName = Navigation",
            "",
            "\tannotation PBI_ResultType = Table",
            "",
        ]
    )
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    write_text_utf8_no_bom(TABLES_DIR / f"{GUIDE}.tmdl", "\n".join(lines))


def write_gaps_table_tmdl() -> None:
    table = GUIDE_GAPS_TABLE
    lines = [f"table {table}", f"\tlineageTag: {vid()}", ""]
    for col in GUIDE_GAPS_COLUMNS:
        tag = vid()
        lines.extend(
            [
                f"\tcolumn {col}",
                "\t\tdataType: string",
                f"\t\tlineageTag: {tag}",
                "\t\tsummarizeBy: none",
                f"\t\tsourceColumn: {col}",
                "",
                "\t\tannotation SummarizationSetBy = Automatic",
                "",
            ]
        )
    lines.extend(
        [
            f"\tpartition {table} = m",
            "\t\tmode: import",
            "\t\tsource =",
            "\t\t\t\tlet",
            f'\t\t\t\t    Source = Parquet.Document(File.Contents("{REPO_PARQUET}\\{GUIDE_GAPS_PARQUET}"), [Compression=null, LegacyColumnNameEncoding=false, MaxDepth=null])',
            "\t\t\t\tin",
            "\t\t\t\t    Source",
            "",
            "\tannotation PBI_NavigationStepName = Navigation",
            "",
            "\tannotation PBI_ResultType = Table",
            "",
        ]
    )
    write_text_utf8_no_bom(TABLES_DIR / f"{table}.tmdl", "\n".join(lines))


def sync_model_tmdl() -> None:
    model_path = SEMANTIC_MODEL / "model.tmdl"
    lines = model_path.read_text(encoding="utf-8").splitlines()
    ref_line = f"ref table {GUIDE}"
    if ref_line not in lines:
        idx = lines.index("ref cultureInfo en-US")
        lines.insert(idx, ref_line)
    for i, line in enumerate(lines):
        if line.startswith("annotation PBI_QueryOrder"):
            order = json.loads(line.split("=", 1)[1].strip())
            if GUIDE not in order:
                order.append(GUIDE)
            lines[i] = f"annotation PBI_QueryOrder = {json.dumps(order)}"
            break
    gaps_ref = f"ref table {GUIDE_GAPS_TABLE}"
    if gaps_ref not in lines:
        idx = lines.index("ref cultureInfo en-US")
        lines.insert(idx, gaps_ref)
    for i, line in enumerate(lines):
        if line.startswith("annotation PBI_QueryOrder"):
            order = json.loads(line.split("=", 1)[1].strip())
            if GUIDE_GAPS_TABLE not in order:
                order.append(GUIDE_GAPS_TABLE)
            lines[i] = f"annotation PBI_QueryOrder = {json.dumps(order)}"
            break
    write_text_utf8_no_bom(model_path, "\n".join(lines) + "\n")


def guide_slicer(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    prop: str,
    title: str,
    *,
    default_value: str | None = None,
) -> dict:
    objects: dict = {
        "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
        "header": [{"properties": {"show": lit_bool(False)}}],
        "items": [{"properties": {"fontSize": lit_pt(13), "fontColor": {"solid": {"color": lit_str(TEXT_BLACK)}}}}],
        "selection": [{"properties": {"selectAllCheckboxEnabled": lit_bool(True)}}],
    }
    if default_value:
        objects["general"] = [{
            "properties": {
                "filter": {
                    "filter": {
                        "Version": 2,
                        "From": [{"Name": "g", "Entity": GUIDE, "Type": 0}],
                        "Where": [{
                            "Condition": {
                                "In": {
                                    "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "g"}}, "Property": prop}}],
                                    "Values": [[{"Literal": {"Value": f"'{default_value}'"}}]],
                                }
                            }
                        }],
                    }
                }
            }
        }]
    return visual_container(
        name, x, y, w, h, z,
        {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [{**projection(GUIDE, prop), "active": True}]}}},
            "objects": objects,
            "visualContainerObjects": container_title(title, bg=PRIMARY_YELLOW, fg=TEXT_BLACK, size=13, pad=10),
            "drillFilterOtherVisuals": True,
        },
    )


def guide_gaps_table(name: str, x: float, y: float, w: float, h: float, z: int) -> dict:
    return visual_container(
        name, x, y, w, h, z,
        {
            "visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": [projection(GUIDE_GAPS_TABLE, p) for p in GAPS_COLUMNS]}}},
            "objects": table_format(header_pt=11, value_pt=11, word_wrap=True),
            "visualContainerObjects": container_title(
                "Concept Profile curation gaps (pilots + non-Approved concepts)",
                bg=PRIMARY_YELLOW,
                fg=TEXT_BLACK,
                size=13,
                pad=10,
            ),
            "drillFilterOtherVisuals": True,
        },
    )


def guide_detail_table(name: str, x: float, y: float, w: float, h: float, z: int) -> dict:
    return visual_container(
        name, x, y, w, h, z,
        {
            "visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": [projection(GUIDE, p) for p in DETAIL_COLUMNS]}}},
            "objects": table_format(header_pt=11, value_pt=11, word_wrap=True),
            "visualContainerObjects": container_title(
                "Column reference (filtered by slicers above)",
                bg=PRIMARY_BLUE,
                fg=TEXT_WHITE,
                size=13,
                pad=10,
            ),
            "drillFilterOtherVisuals": True,
        },
    )


def build_field_guide_page(page_dir: Path) -> None:
    from enhance_pbip_report import clear_visuals

    clear_visuals(page_dir)
    w, h = PAGE_PROFILE_W, PAGE_PROFILE_H
    margin = 32
    content_w = w - (margin * 2)
    header_h = 128
    slicer_y = header_h + 12
    slicer_h = 92
    workflow_y = slicer_y + slicer_h + 8
    workflow_h = 40
    card_y = workflow_y + workflow_h + 8
    card_h = 100
    legend_y = card_y + card_h + 6
    legend_h = 36
    table_y = legend_y + legend_h + 10
    table_h = 360
    gaps_y = table_y + table_h + 12
    gaps_h = h - gaps_y - 64
    third_w = (content_w - 32) // 3
    purpose_w = int(content_w * 0.50)
    interop_w = content_w - purpose_w - 16
    audience_w = 220
    footer_h = 52

    visuals = [
        shape_rect(vid(), 0, 0, w, header_h, 0, PRIMARY_BLUE),
        textbox(
            vid(), margin, 20, 1200, 56, 1,
            "Report field guide",
            bold=True, size="28pt", color=TEXT_WHITE, transparent=True,
        ),
        textbox(
            vid(), margin, 80, 1750, 40, 2,
            "Steward workflow + column reference — links Excel sheets to Concept Profile and curation gaps",
            size="13pt", color=TEXT_WHITE, transparent=True,
        ),
        guide_slicer(
            vid(), margin, slicer_y, third_w, slicer_h, 3,
            "page_display_name", "Filter by report page", default_value="Concept Profile",
        ),
        guide_slicer(
            vid(), margin + third_w + 16, slicer_y, third_w, slicer_h, 4,
            "visual_title", "Filter by table / visual",
        ),
        guide_slicer(
            vid(), margin + (third_w + 16) * 2, slicer_y, third_w, slicer_h, 5,
            "editable_in_excel", "Editable in Excel?",
        ),
        textbox(
            vid(), margin, workflow_y, content_w, workflow_h, 6,
            PUBLISH_RITUAL + " | Concept Profile: pick semantic_id slicer after publish | docs/excel-workbook-guide.md",
            size="11pt", color=TEXT_BLACK,
        ),
        card(vid(), margin, card_y, purpose_w, card_h, 7, GUIDE, "page_purpose", value_pt=13),
        card(vid(), margin + purpose_w + 16, card_y, interop_w - audience_w - 16, card_h, 8, GUIDE, "page_interop_summary", value_pt=12),
        card(vid(), margin + purpose_w + 16 + interop_w - audience_w, card_y, audience_w, card_h, 9, GUIDE, "primary_audience", value_pt=14),
        textbox(
            vid(), margin, legend_y, content_w, legend_h, 10,
            "Layers: Catalog = WHAT | Dictionary = HOW | Terminology/Crosswalk = WHICH | Message context = WHERE | Sources = coverage",
            size="11pt", color=TEXT_BLACK,
        ),
        guide_detail_table(vid(), margin, table_y, content_w, table_h, 11),
        guide_gaps_table(vid(), margin, gaps_y, content_w, gaps_h, 12),
        shape_rect(vid(), 0, h - footer_h, w, footer_h, 13, PRIMARY_YELLOW),
        textbox(
            vid(), margin, h - footer_h + 10, content_w, 36, 14,
            "Gaps from live parquet | docs/demographics-pilot-plan.md | validate: scripts/validate_pbip_manifest.py",
            size="11pt", color=TEXT_BLACK, transparent=True,
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def update_pages_json() -> None:
    pages_json = REPORT / "pages" / "pages.json"
    data = json.loads(pages_json.read_text(encoding="utf-8"))
    order = [p for p in data.get("pageOrder", []) if p != PAGE_FIELD_GUIDE]
    if PAGE_START_HERE in order:
        idx = order.index(PAGE_START_HERE) + 1
        order.insert(idx, PAGE_FIELD_GUIDE)
    else:
        order.insert(0, PAGE_FIELD_GUIDE)
    data["pageOrder"] = order
    data["activePageName"] = DEFAULT_LANDING_PAGE_ID
    if "landingPageName" in data:
        data["landingPageName"] = DEFAULT_LANDING_PAGE_ID
    write_text_utf8_no_bom(pages_json, json.dumps(data, indent=2))


def main() -> None:
    generate_guide()
    generate_gaps()
    write_guide_table_tmdl()
    write_gaps_table_tmdl()
    sync_model_tmdl()
    page_dir = REPORT / "pages" / PAGE_FIELD_GUIDE
    page_dir.mkdir(parents=True, exist_ok=True)
    write_page_json(
        page_dir,
        PAGE_FIELD_GUIDE,
        FIELD_GUIDE_DISPLAY_NAME,
        width=PAGE_PROFILE_W,
        height=PAGE_PROFILE_H,
        informational=True,
    )
    build_field_guide_page(page_dir)
    update_pages_json()
    print(f"Wrote {GUIDE_PARQUET} and PBIP page: {FIELD_GUIDE_DISPLAY_NAME} ({PAGE_FIELD_GUIDE})")
    print("  Re-open chi-data-dictionary-catalog.pbip in Power BI Desktop and Refresh.")


if __name__ == "__main__":
    main()
