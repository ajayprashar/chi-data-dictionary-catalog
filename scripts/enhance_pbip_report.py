#!/usr/bin/env python3
"""Regenerate CHI PBIP report layout (maintainer-only)."""

from __future__ import annotations

import json
import secrets
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PBIP = REPO / "workbooks" / "pbip"
REPORT = PBIP / "chi-data-dictionary-catalog.Report" / "definition"
THEME_DIR = PBIP / "chi-data-dictionary-catalog.Report" / "StaticResources" / "SharedResources" / "BaseThemes"

CATALOG = "ddc-master_patient_catalog"
DICTIONARY = "ddc-master_patient_dictionary"
SOURCES = "ddc-data_source_availability"
ADT = "ddc-hl7_adt_catalog"
CCDA = "ddc-ccda_catalog"
VALUE_MEMBER = "ddc-value_set_member"
SOURCE_XW = "ddc-source_value_crosswalk"

SEMANTIC_MODEL = PBIP / "chi-data-dictionary-catalog.SemanticModel" / "definition"
TABLES_DIR = SEMANTIC_MODEL / "tables"
REPO_PARQUET = r"C:\AI\chi-data-dictionary-catalog"

STANDARDS_LAYER_TEXT = (
    "USCDI = Catalog (what) | US Core + FHIR = Dictionary (how) | Governed codes = Value_Set_Members | "
    "Source maps = Source_Value_Crosswalk | HL7 ADT + C-CDA = message context | Survivorship = chi_survivorship_logic"
)

# High-contrast primary palette (background vs text)
PRIMARY_BLUE = "#0047AB"
PRIMARY_RED = "#CC0000"
PRIMARY_YELLOW = "#FFC000"
TEXT_BLACK = "#000000"
TEXT_WHITE = "#FFFFFF"
BG_LIGHT = "#FFF9E6"
# Table visual: title band (dark) vs column header row (light) vs data rows (white/zebra)
TABLE_COL_HEADER_BG = "#C5D9F2"
TABLE_COL_HEADER_FG = "#003B7A"
TABLE_GRID_LINE = "#B8C4D4"

# Concept Profile: 1920x1080 (16:9) — room for a full-width concept slicer.
PAGE_PROFILE_W = 1920
PAGE_PROFILE_H = 1080
# Governance Overview: same canvas for consistency.
PAGE_OVERVIEW_W = 1920
PAGE_OVERVIEW_H = 1080

# Card visuals need measures (raw text columns render blank in programmatic PBIP).
PROFILE_CARD_MEASURES = [
    ("Profile USCDI Element", 30),
    ("Profile Classification", 22),
    ("Profile Approval Status", 22),
    ("Profile Data Steward", 20),
    ("Profile Domain", 20),
]


def vid() -> str:
    return secrets.token_hex(10)


def lit_str(value: str) -> dict:
    return {"expr": {"Literal": {"Value": f"'{value}'"}}}


def lit_bool(value: bool) -> dict:
    return {"expr": {"Literal": {"Value": "true" if value else "false"}}}


def lit_pt(points: int) -> dict:
    return {"expr": {"Literal": {"Value": f"{points}D"}}}


def col_field(entity: str, prop: str) -> dict:
    return {
        "Column": {
            "Expression": {"SourceRef": {"Entity": entity}},
            "Property": prop,
        }
    }


def measure_field(entity: str, prop: str) -> dict:
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": entity}},
            "Property": prop,
        }
    }


def projection(entity: str, prop: str, *, measure: bool = False) -> dict:
    field = measure_field(entity, prop) if measure else col_field(entity, prop)
    return {
        "field": field,
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop,
    }


def visual_container(name: str, x: float, y: float, w: float, h: float, z: int, visual: dict) -> dict:
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json",
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "height": h,
            "width": w,
            "tabOrder": z,
        },
        "visual": visual,
    }


def container_title(
    title: str,
    *,
    bg: str = PRIMARY_BLUE,
    fg: str = TEXT_WHITE,
    size: int = 14,
    pad: int = 12,
) -> dict:
    return {
        "title": [
            {
                "properties": {
                    "show": lit_bool(True),
                    "text": lit_str(title),
                    "fontSize": lit_pt(size),
                    "fontColor": {"solid": {"color": lit_str(fg)}},
                    "background": {"solid": {"color": lit_str(bg)}},
                }
            }
        ],
        "background": [{"properties": {"show": lit_bool(True), "color": {"solid": {"color": lit_str(BG_LIGHT)}}}}],
        "border": [{"properties": {"show": lit_bool(True), "color": {"solid": {"color": lit_str(PRIMARY_BLUE)}}}}],
        "padding": [
            {
                "properties": {
                    "top": lit_pt(pad),
                    "bottom": lit_pt(pad),
                    "left": lit_pt(12),
                    "right": lit_pt(12),
                }
            }
        ],
    }


def transparent_container() -> dict:
    """Text on top of a shape — no extra box chrome or scrollbars."""
    return {
        "background": [{"properties": {"show": lit_bool(False)}}],
        "border": [{"properties": {"show": lit_bool(False)}}],
        "padding": [
            {
                "properties": {
                    "top": lit_pt(0),
                    "bottom": lit_pt(0),
                    "left": lit_pt(0),
                    "right": lit_pt(0),
                }
            }
        ],
    }


def card_format(*, value_pt: int = 26, label_pt: int = 12) -> dict:
    return {
        "labels": [
            {
                "properties": {
                    "fontSize": lit_pt(value_pt),
                    "color": {"solid": {"color": lit_str(TEXT_BLACK)}},
                }
            }
        ],
        "categoryLabels": [
            {
                "properties": {
                    "fontSize": lit_pt(label_pt),
                    "color": {"solid": {"color": lit_str(PRIMARY_BLUE)}},
                }
            }
        ],
    }


def table_format(*, header_pt: int = 12, value_pt: int = 12) -> dict:
    """Column header row uses light blue + navy text; container title stays dark blue (see container_title)."""
    return {
        "columnHeaders": [
            {
                "properties": {
                    "fontSize": lit_pt(header_pt),
                    "fontColor": {"solid": {"color": lit_str(TABLE_COL_HEADER_FG)}},
                    "backColor": {"solid": {"color": lit_str(TABLE_COL_HEADER_BG)}},
                    "outline": lit_str("Frame"),
                    "bold": lit_bool(True),
                }
            }
        ],
        "values": [
            {
                "properties": {
                    "fontSize": lit_pt(value_pt),
                    "fontColorPrimary": {"solid": {"color": lit_str(TEXT_BLACK)}},
                    "backColorPrimary": {"solid": {"color": lit_str(TEXT_WHITE)}},
                    "backColorSecondary": {"solid": {"color": lit_str(BG_LIGHT)}},
                }
            }
        ],
        "grid": [
            {
                "properties": {
                    "rowPadding": lit_pt(6),
                    "gridHorizontal": lit_bool(True),
                    "gridHorizontalColor": {"solid": {"color": lit_str(TABLE_GRID_LINE)}},
                    "outlineColor": {"solid": {"color": lit_str(TABLE_GRID_LINE)}},
                    "outlineWeight": lit_pt(1),
                }
            }
        ],
    }


def bar_format() -> dict:
    return {
        "categoryAxis": [
            {
                "properties": {
                    "fontSize": lit_pt(12),
                    "color": {"solid": {"color": lit_str(TEXT_BLACK)}},
                }
            }
        ],
        "valueAxis": [
            {
                "properties": {
                    "fontSize": lit_pt(11),
                    "color": {"solid": {"color": lit_str(TEXT_BLACK)}},
                }
            }
        ],
        "labels": [
            {
                "properties": {
                    "show": lit_bool(True),
                    "fontSize": lit_pt(11),
                    "color": {"solid": {"color": lit_str(TEXT_BLACK)}},
                }
            }
        ],
    }


def textbox(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    text: str,
    *,
    bold: bool = False,
    size: str = "14pt",
    color: str = TEXT_BLACK,
    transparent: bool = False,
) -> dict:
    run: dict = {"value": text, "textStyle": {"fontSize": size, "color": color}}
    if bold:
        run["textStyle"]["fontWeight"] = "bold"
    visual: dict = {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [run]}]}}]},
        "drillFilterOtherVisuals": True,
    }
    if transparent:
        visual["visualContainerObjects"] = transparent_container()
    return visual_container(name, x, y, w, h, z, visual)


def shape_rect(name: str, x: float, y: float, w: float, h: float, z: int, color: str) -> dict:
    return visual_container(
        name, x, y, w, h, z,
        {
            "visualType": "shape",
            "objects": {
                "shape": [{"properties": {"tileShape": {"expr": {"Literal": {"Value": "'rectangle'"}}}}}],
                "fill": [{"properties": {"fillColor": {"solid": {"color": lit_str(color)}}}}],
                "outline": [{"properties": {"show": lit_bool(False)}}],
            },
            "drillFilterOtherVisuals": True,
        },
    )


def slicer_dropdown(name: str, x: float, y: float, w: float, h: float, z: int, entity: str, prop: str, default_value: str) -> dict:
    return visual_container(
        name, x, y, w, h, z,
        {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [{**projection(entity, prop), "active": True}]}}},
            "objects": {
                "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
                "header": [{"properties": {"show": lit_bool(False)}}],
                "items": [{"properties": {"fontSize": lit_pt(14), "fontColor": {"solid": {"color": lit_str(TEXT_BLACK)}}}}],
                "selection": [{"properties": {"selectAllCheckboxEnabled": lit_bool(True)}}],
                "general": [{
                    "properties": {
                        "filter": {
                            "filter": {
                                "Version": 2,
                                "From": [{"Name": "c", "Entity": entity, "Type": 0}],
                                "Where": [{
                                    "Condition": {
                                        "In": {
                                            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": prop}}],
                                            "Values": [[{"Literal": {"Value": f"'{default_value}'"}}]],
                                        }
                                    }
                                }],
                            }
                        }
                    }
                }],
            },
            "visualContainerObjects": container_title(
                "Select governed concept (semantic_id)",
                bg=PRIMARY_YELLOW,
                fg=TEXT_BLACK,
                size=14,
                pad=14,
            ),
            "drillFilterOtherVisuals": True,
        },
    )


def card(name: str, x: float, y: float, w: float, h: float, z: int, entity: str, prop: str, *, measure: bool = False, value_pt: int = 26) -> dict:
    return visual_container(
        name, x, y, w, h, z,
        {
            "visualType": "card",
            "query": {"queryState": {"Values": {"projections": [projection(entity, prop, measure=measure)]}}},
            "objects": card_format(value_pt=value_pt),
            "visualContainerObjects": {
                "background": [{"properties": {"show": lit_bool(True), "color": {"solid": {"color": lit_str(TEXT_WHITE)}}}}],
                "border": [{"properties": {"show": lit_bool(True), "color": {"solid": {"color": lit_str(PRIMARY_BLUE)}}}}],
                "padding": [
                    {
                        "properties": {
                            "top": lit_pt(10),
                            "bottom": lit_pt(10),
                            "left": lit_pt(10),
                            "right": lit_pt(10),
                        }
                    }
                ],
            },
            "drillFilterOtherVisuals": True,
        },
    )


def table_ex(name: str, x: float, y: float, w: float, h: float, z: int, entity: str, props: list[str], *, title: str) -> dict:
    return visual_container(
        name, x, y, w, h, z,
        {
            "visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": [projection(entity, p) for p in props]}}},
            "objects": table_format(),
            "visualContainerObjects": container_title(title),
            "drillFilterOtherVisuals": True,
        },
    )


def bar_chart(name: str, x: float, y: float, w: float, h: float, z: int, entity: str, category: str, title: str) -> dict:
    return visual_container(
        name, x, y, w, h, z,
        {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [projection(entity, category)]},
                    "Y": {"projections": [projection(CATALOG, "Total Concepts", measure=True)]},
                }
            },
            "objects": bar_format(),
            "visualContainerObjects": container_title(title),
            "drillFilterOtherVisuals": True,
        },
    )


def write_text_utf8_no_bom(path: Path, content: str) -> None:
    """Power BI PBIP requires UTF-8 without BOM (see excel-workbook-generation-rules / MS PBIP docs)."""
    path.write_bytes(content.encode("utf-8"))


def write_visual(page_dir: Path, container: dict) -> None:
    vdir = page_dir / "visuals" / container["name"]
    vdir.mkdir(parents=True, exist_ok=True)
    write_text_utf8_no_bom(vdir / "visual.json", json.dumps(container, indent=2))


def clear_visuals(page_dir: Path) -> None:
    visuals = page_dir / "visuals"
    if visuals.exists():
        for child in visuals.iterdir():
            if child.is_dir():
                for f in child.iterdir():
                    f.unlink()
                child.rmdir()


def build_concept_profile_page(page_dir: Path) -> None:
    clear_visuals(page_dir)
    w, h = PAGE_PROFILE_W, PAGE_PROFILE_H
    margin = 32
    content_w = w - (margin * 2)
    header_h = 128
    slicer_y = header_h + 12
    slicer_h = 132
    cards_y = slicer_y + slicer_h + 16
    card_h = 156
    tables_y = cards_y + card_h + 20
    biz_h = 318
    dict_y = tables_y + biz_h + 16
    dict_h = 248
    footer_h = 52
    visuals = [
        shape_rect(vid(), 0, 0, w, header_h, 0, PRIMARY_BLUE),
        textbox(
            vid(), margin, 20, 1700, 56, 1,
            "CHI Data Dictionary Catalog",
            bold=True, size="28pt", color=TEXT_WHITE, transparent=True,
        ),
        textbox(
            vid(), margin, 80, 1750, 40, 2,
            "Concept profile — catalog, dictionary, and source availability on one semantic_id",
            size="13pt", color=TEXT_WHITE, transparent=True,
        ),
        slicer_dropdown(vid(), margin, slicer_y, content_w, slicer_h, 3, CATALOG, "semantic_id", "Patient.race"),
        *[
            card(
                vid(),
                margin + (idx * 376),
                cards_y,
                360,
                card_h,
                4 + idx,
                CATALOG,
                measure_name,
                measure=True,
                value_pt=value_pt,
            )
            for idx, (measure_name, value_pt) in enumerate(PROFILE_CARD_MEASURES)
        ],
        table_ex(
            vid(), margin, tables_y, 1184, biz_h, 9, CATALOG,
            ["uscdi_description", "ruleset_category", "uscdi_data_class", "uscdi_data_element", "hipaa_category", "steward_contact"],
            title="Business & USCDI governance",
        ),
        table_ex(
            vid(), margin, dict_y, 1184, dict_h, 10, DICTIONARY,
            [
                "fhir_r4_path",
                "fhir_profile",
                "fhir_data_type",
                "chi_survivorship_logic",
                "data_quality_notes",
                "data_source_rank_reference",
            ],
            title="Implementation & survivorship (FHIR + standards)",
        ),
        table_ex(
            vid(), margin + 1200, tables_y, 656, dict_y + dict_h - tables_y, 11, SOURCES,
            ["source_id", "availability", "completeness_pct", "timeliness_sla_hours", "notes"],
            title="Source availability",
        ),
        shape_rect(vid(), 0, h - footer_h, w, footer_h, 12, PRIMARY_YELLOW),
        textbox(
            vid(), margin, h - footer_h + 10, content_w, 36, 13,
            "Read-only view. Edit chi-steward-workbook.xlsx, run import_steward_workbook_to_parquet.py, then Refresh.",
            size="12pt", color=TEXT_BLACK, transparent=True,
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def build_standards_contexts_page(page_dir: Path) -> None:
    clear_visuals(page_dir)
    w, h = PAGE_PROFILE_W, PAGE_PROFILE_H
    margin = 32
    content_w = w - (margin * 2)
    header_h = 128
    layer_y = header_h + 8
    layer_h = 72
    slicer_y = layer_y + layer_h + 12
    slicer_h = 120
    tables_y = slicer_y + slicer_h + 16
    fhir_h = 170
    codes_y = tables_y + fhir_h + 12
    codes_h = 200
    adt_ccda_y = codes_y + codes_h + 12
    adt_h = 200
    footer_h = 52
    half_w = (content_w - 16) // 2
    visuals = [
        shape_rect(vid(), 0, 0, w, header_h, 0, PRIMARY_BLUE),
        textbox(
            vid(), margin, 20, 1700, 56, 1,
            "Standards & interoperability contexts",
            bold=True, size="28pt", color=TEXT_WHITE, transparent=True,
        ),
        textbox(
            vid(), margin, 80, 1750, 40, 2,
            "Healthcare standards + HL7 ADT + C-CDA + FHIR for one semantic_id",
            size="13pt", color=TEXT_WHITE, transparent=True,
        ),
        textbox(
            vid(), margin, layer_y, content_w, layer_h, 3,
            STANDARDS_LAYER_TEXT,
            size="12pt", color=TEXT_BLACK,
        ),
        slicer_dropdown(vid(), margin, slicer_y, content_w, slicer_h, 4, CATALOG, "semantic_id", "Patient.race"),
        table_ex(
            vid(), margin, tables_y, content_w, fhir_h, 5, DICTIONARY,
            ["semantic_id", "fhir_r4_path", "fhir_profile", "data_quality_notes", "chi_survivorship_logic"],
            title="FHIR R4 + US Core (Dictionary)",
        ),
        table_ex(
            vid(), margin, codes_y, half_w, codes_h, 6, VALUE_MEMBER,
            ["semantic_id", "code_system_oid", "code", "display", "member_type", "binding_strength", "notes"],
            title="Governed value set codes",
        ),
        table_ex(
            vid(), margin + half_w + 16, codes_y, half_w, codes_h, 7, SOURCE_XW,
            [
                "source_id",
                "source_field",
                "source_code",
                "source_display",
                "target_code",
                "target_display",
                "mapping_type",
                "approval_status",
            ],
            title="Source value crosswalk",
        ),
        table_ex(
            vid(), margin, adt_ccda_y, half_w, adt_h, 8, ADT,
            ["semantic_id", "segment_id", "field_id", "field_name", "message_type", "mapping_status", "notes"],
            title="HL7 v2 ADT context",
        ),
        table_ex(
            vid(), margin + half_w + 16, adt_ccda_y, half_w, adt_h, 9, CCDA,
            ["semantic_id", "section_name", "entry_type", "xml_path", "mapping_status", "notes"],
            title="C-CDA / CCD context",
        ),
        shape_rect(vid(), 0, h - footer_h, w, footer_h, 10, PRIMARY_YELLOW),
        textbox(
            vid(), margin, h - footer_h + 10, content_w, 36, 11,
            "Standards: docs/shie-standards-reference.md | Crosswalk model: docs/crosswalk-model.md",
            size="12pt", color=TEXT_BLACK, transparent=True,
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def write_parquet_table_tmdl(table_name: str, parquet_filename: str, columns: list[str]) -> None:
    """Write a minimal import-mode TMDL table from parquet column names."""
    lines = [f"table {table_name}", f"\tlineageTag: {vid()}", ""]
    for col in columns:
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
            f"\tpartition {table_name} = m",
            "\t\tmode: import",
            "\t\tsource =",
            "\t\t\t\tlet",
            f'\t\t\t\t    Source = Parquet.Document(File.Contents("{REPO_PARQUET}\\{parquet_filename}"), [Compression=null, LegacyColumnNameEncoding=false, MaxDepth=null])',
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
    write_text_utf8_no_bom(TABLES_DIR / f"{table_name}.tmdl", "\n".join(lines))


def sync_semantic_model() -> None:
    write_parquet_table_tmdl(
        ADT,
        "ddc-hl7_adt_catalog.parquet",
        [
            "message_format",
            "message_type",
            "segment_id",
            "field_id",
            "field_name",
            "data_type",
            "optionality",
            "cardinality",
            "semantic_id",
            "fhir_r4_path",
            "notes",
            "mapping_status",
        ],
    )
    write_parquet_table_tmdl(
        CCDA,
        "ddc-ccda_catalog.parquet",
        [
            "message_format",
            "section_name",
            "entry_type",
            "xml_path",
            "semantic_id",
            "fhir_r4_path",
            "notes",
            "mapping_status",
        ],
    )
    write_parquet_table_tmdl(
        VALUE_MEMBER,
        "ddc-value_set_member.parquet",
        [
            "semantic_id",
            "code_system_oid",
            "code",
            "display",
            "member_type",
            "binding_role",
            "binding_strength",
            "active",
            "sort_order",
            "notes",
        ],
    )
    write_parquet_table_tmdl(
        SOURCE_XW,
        "ddc-source_value_crosswalk.parquet",
        [
            "source_id",
            "source_field",
            "source_code",
            "source_display",
            "semantic_id",
            "target_code_system_oid",
            "target_code",
            "target_display",
            "mapping_type",
            "approval_status",
            "effective_from",
            "effective_to",
            "notes",
        ],
    )

    rel_path = SEMANTIC_MODEL / "relationships.tmdl"
    rel_body = rel_path.read_text(encoding="utf-8")
    adt_rel = (
        f"\nrelationship {vid()}\n"
        f"\tcrossFilteringBehavior: bothDirections\n"
        f"\tfromColumn: {ADT}.semantic_id\n"
        f"\ttoColumn: {CATALOG}.semantic_id\n"
    )
    ccda_rel = (
        f"\nrelationship {vid()}\n"
        f"\tcrossFilteringBehavior: bothDirections\n"
        f"\tfromColumn: {CCDA}.semantic_id\n"
        f"\ttoColumn: {CATALOG}.semantic_id\n"
    )
    if f"fromColumn: {ADT}.semantic_id" not in rel_body:
        rel_body = rel_body.rstrip() + adt_rel
    if f"fromColumn: {CCDA}.semantic_id" not in rel_body:
        rel_body = rel_body.rstrip() + ccda_rel
    member_rel = (
        f"\nrelationship {vid()}\n"
        f"\tcrossFilteringBehavior: bothDirections\n"
        f"\tfromColumn: {VALUE_MEMBER}.semantic_id\n"
        f"\ttoColumn: {CATALOG}.semantic_id\n"
    )
    xw_rel = (
        f"\nrelationship {vid()}\n"
        f"\tcrossFilteringBehavior: bothDirections\n"
        f"\tfromColumn: {SOURCE_XW}.semantic_id\n"
        f"\ttoColumn: {CATALOG}.semantic_id\n"
    )
    if f"fromColumn: {VALUE_MEMBER}.semantic_id" not in rel_body:
        rel_body = rel_body.rstrip() + member_rel
    if f"fromColumn: {SOURCE_XW}.semantic_id" not in rel_body:
        rel_body = rel_body.rstrip() + xw_rel
    write_text_utf8_no_bom(rel_path, rel_body)

    model_path = SEMANTIC_MODEL / "model.tmdl"
    model_lines = model_path.read_text(encoding="utf-8").splitlines()
    query_order = None
    extra_tables = [ADT, CCDA, VALUE_MEMBER, SOURCE_XW]
    out: list[str] = []
    for line in model_lines:
        if line.startswith("annotation PBI_QueryOrder"):
            tables = [
                "ddc-master_patient_catalog",
                "ddc-master_patient_dictionary",
                "ddc-data_source_availability",
                *extra_tables,
            ]
            out.append(f'annotation PBI_QueryOrder = {json.dumps(tables)}')
            query_order = True
            continue
        out.append(line)
    culture_idx = out.index("ref cultureInfo en-US")
    for ref in extra_tables:
        ref_line = f"ref table {ref}"
        if ref_line not in out:
            out.insert(culture_idx, ref_line)
    if not query_order:
        out.insert(
            8,
            f'annotation PBI_QueryOrder = {json.dumps([CATALOG, DICTIONARY, SOURCES, *extra_tables])}',
        )
    write_text_utf8_no_bom(model_path, "\n".join(out) + "\n")


def build_overview_page(page_dir: Path) -> None:
    clear_visuals(page_dir)
    w, h = PAGE_OVERVIEW_W, PAGE_OVERVIEW_H
    margin = 32
    header_h = 128
    visuals = [
        shape_rect(vid(), 0, 0, w, header_h, 0, PRIMARY_BLUE),
        textbox(
            vid(), margin, 20, 900, 56, 1,
            "Governance overview",
            bold=True, size="28pt", color=TEXT_WHITE, transparent=True,
        ),
        textbox(
            vid(), margin, 80, 1200, 40, 2,
            "Portfolio of governed patient concepts — approval and classification",
            size="13pt", color=TEXT_WHITE, transparent=True,
        ),
        card(vid(), margin, 148, 448, 148, 3, CATALOG, "Total Concepts", measure=True, value_pt=32),
        card(vid(), margin + 464, 148, 448, 148, 4, CATALOG, "Approved Concepts", measure=True, value_pt=32),
        card(vid(), margin + 928, 148, 448, 148, 5, CATALOG, "Pending Approval", measure=True, value_pt=32),
        card(vid(), margin + 1392, 148, 448, 148, 6, CATALOG, "Demographics Pilot", measure=True, value_pt=32),
        bar_chart(vid(), margin, 316, 900, 340, 7, CATALOG, "classification", "Concepts by classification"),
        bar_chart(vid(), margin + 924, 316, 900, 340, 8, CATALOG, "approval_status", "Concepts by approval status"),
        table_ex(
            vid(), margin, 676, w - (margin * 2), 372, 9, CATALOG,
            ["semantic_id", "uscdi_element", "uscdi_description", "classification", "data_steward", "approval_status"],
            title="All governed concepts",
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def write_chi_theme() -> None:
    theme = {
        "name": "CHI High Contrast",
        "dataColors": [PRIMARY_BLUE, PRIMARY_RED, PRIMARY_YELLOW, "#1AAB40", "#6B6B6B", "#0091D5"],
        "foreground": TEXT_BLACK,
        "foregroundNeutralSecondary": "#333333",
        "foregroundNeutralTertiary": "#555555",
        "background": TEXT_WHITE,
        "backgroundLight": BG_LIGHT,
        "backgroundNeutral": "#E8E8E8",
        "tableAccent": PRIMARY_BLUE,
        "good": "#1AAB40",
        "neutral": PRIMARY_YELLOW,
        "bad": PRIMARY_RED,
        "maximum": PRIMARY_BLUE,
        "center": PRIMARY_YELLOW,
        "minimum": BG_LIGHT,
        "null": PRIMARY_RED,
        "hyperlink": PRIMARY_BLUE,
        "visitedHyperlink": PRIMARY_RED,
        "textClasses": {
            "callout": {"fontSize": 32, "fontFace": "Segoe UI Semibold", "color": TEXT_BLACK},
            "title": {"fontSize": 14, "fontFace": "Segoe UI Semibold", "color": TEXT_WHITE},
            "header": {"fontSize": 13, "fontFace": "Segoe UI Semibold", "color": TEXT_WHITE},
            "label": {"fontSize": 12, "fontFace": "Segoe UI", "color": TEXT_BLACK},
            "largeTitle": {"fontSize": 28, "fontFace": "Segoe UI Semibold", "color": TEXT_WHITE},
        },
        "visualStyles": {
            "card": {
                "*": {
                    "labels": [{"fontSize": 26, "color": {"solid": {"color": TEXT_BLACK}}}],
                    "categoryLabels": [{"fontSize": 12, "color": {"solid": {"color": PRIMARY_BLUE}}}],
                }
            },
            "tableEx": {
                "*": {
                    "columnHeaders": [
                        {
                            "fontSize": 12,
                            "fontColor": {"solid": {"color": TABLE_COL_HEADER_FG}},
                            "backColor": {"solid": {"color": TABLE_COL_HEADER_BG}},
                            "outline": "Frame",
                            "bold": True,
                        }
                    ],
                    "values": [
                        {
                            "fontSize": 12,
                            "fontColorPrimary": {"solid": {"color": TEXT_BLACK}},
                            "backColorPrimary": {"solid": {"color": TEXT_WHITE}},
                            "backColorSecondary": {"solid": {"color": BG_LIGHT}},
                        }
                    ],
                    "grid": [
                        {
                            "gridHorizontal": True,
                            "gridHorizontalColor": {"solid": {"color": TABLE_GRID_LINE}},
                            "outlineColor": {"solid": {"color": TABLE_GRID_LINE}},
                            "outlineWeight": 1,
                            "rowPadding": 6,
                        }
                    ],
                }
            },
            "slicer": {
                "*": {
                    "header": [{"fontSize": 13}],
                    "items": [{"fontSize": 13, "fontColor": {"solid": {"color": TEXT_BLACK}}}],
                }
            },
            "clusteredBarChart": {
                "*": {
                    "categoryAxis": [{"fontSize": 12, "color": {"solid": {"color": TEXT_BLACK}}}],
                    "valueAxis": [{"fontSize": 11, "color": {"solid": {"color": TEXT_BLACK}}}],
                    "labels": [{"show": True, "fontSize": 11}],
                }
            },
        },
    }
    write_text_utf8_no_bom(THEME_DIR / "CHI High Contrast.json", json.dumps(theme, indent=2))


def update_report_json() -> None:
    path = REPORT / "report.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["themeCollection"] = {
        "baseTheme": {
            "name": "CHI High Contrast",
            "reportVersionAtImport": {"visual": "2.10.0", "report": "3.4.0", "page": "2.3.1"},
            "type": "SharedResources",
        }
    }
    data["resourcePackages"] = [
        {
            "name": "SharedResources",
            "type": "SharedResources",
            "items": [
                {"name": "CHI High Contrast", "path": "BaseThemes/CHI High Contrast.json", "type": "BaseTheme"},
            ],
        }
    ]
    write_text_utf8_no_bom(path, json.dumps(data, indent=2))


def write_page_json(page_dir: Path, page_id: str, display_name: str, *, width: int, height: int) -> None:
    write_text_utf8_no_bom(
        page_dir / "page.json",
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
                "name": page_id,
                "displayName": display_name,
                "displayOption": "ActualSize",
                "height": height,
                "width": width,
                "objects": {
                    "background": [
                        {
                            "properties": {
                                "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{TEXT_WHITE}'"}}}}},
                                "transparency": {"expr": {"Literal": {"Value": "0D"}}},
                            }
                        }
                    ]
                },
            },
            indent=2,
        ),
    )


def main() -> None:
    profile_id = "abc963c80ac5ed2deeb4"
    standards_id = "d4e5f6a7b8c901234567"
    overview_id = "c8f1a2b3d4e5f6071829"
    profile_page = REPORT / "pages" / profile_id
    standards_page = REPORT / "pages" / standards_id
    overview_page = REPORT / "pages" / overview_id
    profile_page.mkdir(parents=True, exist_ok=True)
    standards_page.mkdir(parents=True, exist_ok=True)
    overview_page.mkdir(parents=True, exist_ok=True)

    write_page_json(profile_page, profile_id, "Concept Profile", width=PAGE_PROFILE_W, height=PAGE_PROFILE_H)
    write_page_json(standards_page, standards_id, "Standards & Contexts", width=PAGE_PROFILE_W, height=PAGE_PROFILE_H)
    write_page_json(overview_page, overview_id, "Governance Overview", width=PAGE_OVERVIEW_W, height=PAGE_OVERVIEW_H)
    write_text_utf8_no_bom(
        REPORT / "pages" / "pages.json",
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
                "pageOrder": [profile_id, standards_id, overview_id],
                "activePageName": profile_id,
            },
            indent=2,
        ),
    )

    THEME_DIR.mkdir(parents=True, exist_ok=True)
    sync_semantic_model()
    write_chi_theme()
    update_report_json()
    build_concept_profile_page(profile_page)
    build_standards_contexts_page(standards_page)
    build_overview_page(overview_page)
    print(f"Regenerated PBIP report and semantic model at {PBIP}")


if __name__ == "__main__":
    main()
