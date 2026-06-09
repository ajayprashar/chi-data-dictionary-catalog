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

# High-contrast primary palette (background vs text)
PRIMARY_BLUE = "#0047AB"
PRIMARY_RED = "#CC0000"
PRIMARY_YELLOW = "#FFC000"
TEXT_BLACK = "#000000"
TEXT_WHITE = "#FFFFFF"
BG_LIGHT = "#FFF9E6"

PAGE_W = 1664
PAGE_H = 1100


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


def container_title(title: str, *, bg: str = PRIMARY_BLUE, fg: str = TEXT_WHITE, size: int = 14) -> dict:
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
        "padding": [{"properties": {"top": lit_pt(8), "bottom": lit_pt(8), "left": lit_pt(10), "right": lit_pt(10)}}],
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


def table_format(*, header_pt: int = 13, value_pt: int = 12) -> dict:
    return {
        "columnHeaders": [
            {
                "properties": {
                    "fontSize": lit_pt(header_pt),
                    "fontColor": {"solid": {"color": lit_str(TEXT_WHITE)}},
                    "backColor": {"solid": {"color": lit_str(PRIMARY_BLUE)}},
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
        "grid": [{"properties": {"rowPadding": lit_pt(6)}}],
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


def textbox(name: str, x: float, y: float, w: float, h: float, z: int, text: str, *, bold: bool = False, size: str = "14pt", color: str = TEXT_BLACK) -> dict:
    run: dict = {"value": text, "textStyle": {"fontSize": size, "color": color}}
    if bold:
        run["textStyle"]["fontWeight"] = "bold"
    return visual_container(
        name, x, y, w, h, z,
        {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [run]}]}}]}, "drillFilterOtherVisuals": True},
    )


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
                "header": [{"properties": {"show": lit_bool(True), "fontSize": lit_pt(13)}}],
                "items": [{"properties": {"fontSize": lit_pt(13), "fontColor": {"solid": {"color": lit_str(TEXT_BLACK)}}}}],
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
            "visualContainerObjects": container_title("Select governed concept", bg=PRIMARY_YELLOW, fg=TEXT_BLACK, size=13),
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


def write_visual(page_dir: Path, container: dict) -> None:
    vdir = page_dir / "visuals" / container["name"]
    vdir.mkdir(parents=True, exist_ok=True)
    (vdir / "visual.json").write_text(json.dumps(container, indent=2), encoding="utf-8")


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
    visuals = [
        shape_rect(vid(), 0, 0, PAGE_W, 96, 0, PRIMARY_BLUE),
        textbox(vid(), 28, 18, 900, 40, 1, "CHI Data Dictionary Catalog", bold=True, size="28pt", color=TEXT_WHITE),
        textbox(
            vid(), 28, 56, 1100, 32, 2,
            "Concept profile — catalog, dictionary, and source availability on one semantic_id",
            size="13pt", color=TEXT_WHITE,
        ),
        slicer_dropdown(vid(), 1120, 20, 520, 72, 3, CATALOG, "semantic_id", "Patient.race"),
        card(vid(), 28, 112, 360, 130, 4, CATALOG, "uscdi_element", value_pt=30),
        card(vid(), 404, 112, 360, 130, 5, CATALOG, "classification", value_pt=22),
        card(vid(), 780, 112, 320, 130, 6, CATALOG, "approval_status", value_pt=22),
        card(vid(), 1116, 112, 260, 130, 7, CATALOG, "data_steward", value_pt=20),
        card(vid(), 1392, 112, 248, 130, 8, CATALOG, "domain", value_pt=20),
        table_ex(
            vid(), 28, 264, 1000, 240, 9, CATALOG,
            ["uscdi_description", "ruleset_category", "uscdi_data_class", "uscdi_data_element", "hipaa_category", "steward_contact"],
            title="Business & USCDI governance",
        ),
        table_ex(
            vid(), 28, 524, 1000, 300, 10, DICTIONARY,
            ["fhir_r4_path", "fhir_data_type", "chi_survivorship_logic", "data_source_rank_reference", "data_quality_notes"],
            title="Implementation & survivorship",
        ),
        table_ex(
            vid(), 1048, 264, 592, 560, 11, SOURCES,
            ["source_id", "availability", "completeness_pct", "timeliness_sla_hours", "notes"],
            title="Source availability",
        ),
        shape_rect(vid(), 0, 1040, PAGE_W, 60, 12, PRIMARY_YELLOW),
        textbox(
            vid(), 28, 1052, 1500, 36, 13,
            "Read-only view. Edit chi-steward-workbook.xlsx, run import_steward_workbook_to_parquet.py, then Refresh.",
            size="12pt", color=TEXT_BLACK,
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def build_overview_page(page_dir: Path) -> None:
    clear_visuals(page_dir)
    visuals = [
        shape_rect(vid(), 0, 0, PAGE_W, 96, 0, PRIMARY_BLUE),
        textbox(vid(), 28, 18, 900, 40, 1, "Governance overview", bold=True, size="28pt", color=TEXT_WHITE),
        textbox(
            vid(), 28, 56, 1100, 32, 2,
            "Portfolio of governed patient concepts — approval and classification",
            size="13pt", color=TEXT_WHITE,
        ),
        card(vid(), 28, 112, 300, 140, 3, CATALOG, "Total Concepts", measure=True, value_pt=32),
        card(vid(), 344, 112, 300, 140, 4, CATALOG, "Approved Concepts", measure=True, value_pt=32),
        card(vid(), 660, 112, 300, 140, 5, CATALOG, "Pending Approval", measure=True, value_pt=32),
        card(vid(), 976, 112, 300, 140, 6, CATALOG, "Demographics Pilot", measure=True, value_pt=32),
        bar_chart(vid(), 28, 276, 780, 360, 7, CATALOG, "classification", "Concepts by classification"),
        bar_chart(vid(), 828, 276, 812, 360, 8, CATALOG, "approval_status", "Concepts by approval status"),
        table_ex(
            vid(), 28, 656, 1612, 420, 9, CATALOG,
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
                            "fontSize": 13,
                            "fontColor": {"solid": {"color": TEXT_WHITE}},
                            "backColor": {"solid": {"color": PRIMARY_BLUE}},
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
    (THEME_DIR / "CHI High Contrast.json").write_text(json.dumps(theme, indent=2), encoding="utf-8")


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
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_page_json(page_dir: Path, page_id: str, display_name: str) -> None:
    (page_dir / "page.json").write_text(
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
                "name": page_id,
                "displayName": display_name,
                "displayOption": "ActualSize",
                "height": PAGE_H,
                "width": PAGE_W,
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
        encoding="utf-8",
    )


def main() -> None:
    profile_id = "abc963c80ac5ed2deeb4"
    overview_id = "c8f1a2b3d4e5f6071829"
    profile_page = REPORT / "pages" / profile_id
    overview_page = REPORT / "pages" / overview_id
    profile_page.mkdir(parents=True, exist_ok=True)
    overview_page.mkdir(parents=True, exist_ok=True)

    write_page_json(profile_page, profile_id, "Concept Profile")
    write_page_json(overview_page, overview_id, "Governance Overview")
    (REPORT / "pages" / "pages.json").write_text(
        json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
                "pageOrder": [profile_id, overview_id],
                "activePageName": profile_id,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    THEME_DIR.mkdir(parents=True, exist_ok=True)
    write_chi_theme()
    update_report_json()
    build_concept_profile_page(profile_page)
    build_overview_page(overview_page)
    print(f"Regenerated PBIP report at {PBIP}")


if __name__ == "__main__":
    main()
