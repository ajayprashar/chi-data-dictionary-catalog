#!/usr/bin/env python3
"""Add or refresh the PBIP Start here page without regenerating other report pages.

Safe to re-run. Updates pages.json (Start here first; default landing = Standards & Contexts).
Full report regen: enhance_pbip_report.py (includes this page).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enhance_pbip_report import (  # noqa: E402
    PAGE_PROFILE_H,
    PAGE_PROFILE_W,
    PRIMARY_BLUE,
    PRIMARY_YELLOW,
    REPORT,
    TEXT_BLACK,
    TEXT_WHITE,
    clear_visuals,
    container_title,
    lit_bool,
    lit_pt,
    lit_str,
    shape_rect,
    text_run_style,
    textbox,
    vid,
    visual_container,
    write_page_json,
    write_text_utf8_no_bom,
    write_visual,
)
from pbip_layout_constants import GUIDE_BODY_PT, GUIDE_FOOTER_PT, TAB_START_HERE  # noqa: E402
from pbip_start_here_content import (  # noqa: E402
    HOW_TO_USE_LINES,
    PAGE_SUBTITLE,
    PAGE_TITLE,
    PILOT_CALLOUT,
    PURPOSE_LINES,
    SOURCES_LINES,
)

START_HERE_PAGE_ID = "e1f2a3b4c5d607182934"
START_HERE_DISPLAY_NAME = TAB_START_HERE


def _body_paragraphs(lines: list[str], *, size: str = GUIDE_BODY_PT) -> list[dict]:
    paragraphs: list[dict] = []
    for line in lines:
        if not line:
            paragraphs.append({"textRuns": [{"value": "", "textStyle": text_run_style("6pt", TEXT_BLACK)}]})
            continue
        style = text_run_style(size, TEXT_BLACK)
        if " - " in line and not line[0].isdigit() and not line.strip().startswith(("1.", "2.", "3.", "4.")):
            label, rest = line.split(" - ", 1)
            paragraphs.append(
                {
                    "textRuns": [
                        {"value": f"{label} - ", "textStyle": text_run_style(size, TEXT_BLACK, bold=True)},
                        {"value": rest, "textStyle": style},
                    ]
                }
            )
        else:
            paragraphs.append({"textRuns": [{"value": line, "textStyle": style}]})
    return paragraphs


def section_panel(
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    title: str,
    body_lines: list[str],
    *,
    body_size: str = GUIDE_BODY_PT,
) -> dict:
    """Card-style panel: blue title band + cream body (matches table visuals)."""
    return visual_container(
        vid(), x, y, w, h, z,
        {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": _body_paragraphs(body_lines, size=body_size)}}]},
            "visualContainerObjects": container_title(title, bg=PRIMARY_BLUE, fg=TEXT_WHITE, size=14, pad=10),
            "drillFilterOtherVisuals": True,
        },
    )


def callout_banner(x: float, y: float, w: float, h: float, z: int, text: str) -> dict:
    """Yellow accent strip for pilot / key message."""
    return visual_container(
        vid(), x, y, w, h, z,
        {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": text,
                                            "textStyle": text_run_style(GUIDE_BODY_PT, TEXT_BLACK, bold=True),
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "background": [
                    {
                        "properties": {
                            "show": lit_bool(True),
                            "color": {"solid": {"color": lit_str(PRIMARY_YELLOW)}},
                        }
                    }
                ],
                "border": [
                    {
                        "properties": {
                            "show": lit_bool(True),
                            "color": {"solid": {"color": lit_str(PRIMARY_BLUE)}},
                        }
                    }
                ],
                "padding": [
                    {
                        "properties": {
                            "top": lit_pt(10),
                            "bottom": lit_pt(10),
                            "left": lit_pt(14),
                            "right": lit_pt(14),
                        }
                    }
                ],
            },
            "drillFilterOtherVisuals": True,
        },
    )


def build_start_here_page(page_dir: Path) -> None:
    clear_visuals(page_dir)
    w, h = PAGE_PROFILE_W, PAGE_PROFILE_H
    margin = 32
    content_w = w - (margin * 2)
    header_h = 128
    col_w = (content_w - 16) // 2
    row1_y = header_h + 12
    panel_h = 360
    callout_y = row1_y + panel_h + 12
    callout_h = 48
    row2_y = callout_y + callout_h + 12
    how_to_h = 300  # 9+ body lines + title band; short panels caused stacked text in PBI
    footer_h = 52

    visuals = [
        shape_rect(vid(), 0, 0, w, header_h, 0, PRIMARY_BLUE),
        textbox(
            vid(), margin, 20, 1200, 56, 1,
            PAGE_TITLE,
            bold=True, size="28pt", color=TEXT_WHITE, transparent=True,
        ),
        textbox(
            vid(), margin, 80, 1750, 44, 2,
            PAGE_SUBTITLE,
            size="13pt", color=TEXT_WHITE, transparent=True,
        ),
        section_panel(margin, row1_y, col_w, panel_h, 3, "Purpose", PURPOSE_LINES),
        section_panel(margin + col_w + 16, row1_y, col_w, panel_h, 4, "Sources of truth", SOURCES_LINES),
        callout_banner(margin, callout_y, content_w, callout_h, 5, PILOT_CALLOUT),
        section_panel(margin, row2_y, content_w, how_to_h, 6, "How to use this report", HOW_TO_USE_LINES),
        shape_rect(vid(), 0, h - footer_h, w, footer_h, 8, PRIMARY_YELLOW),
        textbox(
            vid(), margin, h - footer_h + 10, content_w, 36, 9,
            "Read-only | docs/product-vision.md | docs/sources-of-truth.md | docs/shie-standards-reference.md",
            size=GUIDE_FOOTER_PT, color=TEXT_BLACK, transparent=True,
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def main() -> None:
    page_dir = REPORT / "pages" / START_HERE_PAGE_ID
    page_dir.mkdir(parents=True, exist_ok=True)
    write_page_json(
        page_dir,
        START_HERE_PAGE_ID,
        START_HERE_DISPLAY_NAME,
        width=PAGE_PROFILE_W,
        height=PAGE_PROFILE_H,
        informational=True,
    )
    build_start_here_page(page_dir)
    from enhance_pbip_report import sync_pages_json, sync_page_tab_styles  # noqa: E402

    sync_pages_json()
    sync_page_tab_styles()
    print(f"Wrote PBIP page: {START_HERE_DISPLAY_NAME} ({START_HERE_PAGE_ID})")
    print("  Landing page unchanged (use add_pbip_demo_page.py to set Demo tab landing).")
    from pbip_paths import PBIP_FILE  # noqa: E402

    print(f"  Re-open {PBIP_FILE} in Power BI Desktop.")


if __name__ == "__main__":
    main()
