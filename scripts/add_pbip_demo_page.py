#!/usr/bin/env python3
"""Add or refresh PBIP Demo walkthrough page (5-minute tour).

Safe to re-run. Sets default landing to Demo tab.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from add_pbip_start_here_page import (  # noqa: E402
    START_HERE_PAGE_ID,
    callout_banner,
    section_panel,
)
from enhance_pbip_report import (  # noqa: E402
    PAGE_PROFILE_H,
    PAGE_PROFILE_W,
    PRIMARY_BLUE,
    PRIMARY_YELLOW,
    REPORT,
    TEXT_BLACK,
    TEXT_WHITE,
    shape_rect,
    textbox,
    vid,
    write_page_json,
    write_text_utf8_no_bom,
    write_visual,
    clear_visuals,
)
from pbip_demo_walkthrough_content import (  # noqa: E402
    INTRO_LINES,
    PAGE_SUBTITLE,
    PAGE_TITLE,
    PERSONA_LINES,
    PILOT_CALLOUT,
    STEPS_LINES,
    TIPS_LINES,
)
from pbip_layout_constants import DEMO_LANDING_PAGE_ID, DEMO_PAGE_ID, TAB_DEMO  # noqa: E402

DEMO_DISPLAY_NAME = TAB_DEMO


def build_demo_page(page_dir: Path) -> None:
    clear_visuals(page_dir)
    w, h = PAGE_PROFILE_W, PAGE_PROFILE_H
    margin = 32
    content_w = w - (margin * 2)
    header_h = 128
    row1_y = header_h + 12
    panel_h = 300
    callout_y = row1_y + panel_h + 12
    callout_h = 48
    row2_y = callout_y + callout_h + 12
    row3_y = row2_y + 200
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
        section_panel(margin, row1_y, content_w, panel_h, 3, "Follow these steps", STEPS_LINES, body_size="12pt"),
        callout_banner(margin, callout_y, content_w, callout_h, 4, PILOT_CALLOUT),
        section_panel(margin, row2_y, (content_w - 16) // 2, 184, 5, "Who uses which tab", PERSONA_LINES),
        section_panel(
            margin + (content_w - 16) // 2 + 16,
            row2_y,
            (content_w - 16) // 2,
            184,
            6,
            "Tips",
            TIPS_LINES,
            body_size="11pt",
        ),
        section_panel(margin, row3_y, content_w, 88, 7, "About this report", INTRO_LINES, body_size="11pt"),
        shape_rect(vid(), 0, h - footer_h, w, footer_h, 8, PRIMARY_YELLOW),
        textbox(
            vid(), margin, h - footer_h + 10, content_w, 36, 9,
            "Next: Standards & Contexts tab | OPEN-DEMO.bat and DEMO-WALKTHROUGH.txt in demo zip",
            size="11pt", color=TEXT_BLACK, transparent=True,
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def update_pages_json(*, landing_page_id: str = DEMO_LANDING_PAGE_ID) -> None:
    pages_json = REPORT / "pages" / "pages.json"
    data = json.loads(pages_json.read_text(encoding="utf-8"))
    order = [p for p in data.get("pageOrder", []) if p not in (START_HERE_PAGE_ID, DEMO_PAGE_ID)]
    if START_HERE_PAGE_ID in data.get("pageOrder", []):
        order.insert(0, START_HERE_PAGE_ID)
    else:
        order.insert(0, START_HERE_PAGE_ID)
    order.insert(1, DEMO_PAGE_ID)
    data["pageOrder"] = order
    data["activePageName"] = landing_page_id
    if "landingPageName" in data:
        data["landingPageName"] = landing_page_id
    write_text_utf8_no_bom(pages_json, json.dumps(data, indent=2))


def main() -> None:
    page_dir = REPORT / "pages" / DEMO_PAGE_ID
    page_dir.mkdir(parents=True, exist_ok=True)
    write_page_json(
        page_dir,
        DEMO_PAGE_ID,
        DEMO_DISPLAY_NAME,
        width=PAGE_PROFILE_W,
        height=PAGE_PROFILE_H,
        informational=True,
    )
    build_demo_page(page_dir)
    update_pages_json()
    print(f"Wrote PBIP page: {DEMO_DISPLAY_NAME} ({DEMO_PAGE_ID})")
    print(f"  Default landing page: {DEMO_DISPLAY_NAME} ({DEMO_LANDING_PAGE_ID})")
    print("  Re-open chi-data-dictionary-catalog.pbip in Power BI Desktop and Refresh.")


if __name__ == "__main__":
    main()
