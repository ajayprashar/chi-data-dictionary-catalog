#!/usr/bin/env python3
"""Add or refresh Guide · Walkthrough page (5-minute tour).

Safe to re-run. Default landing page is Guide · Start here (see pbip_layout_constants).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from add_pbip_start_here_page import section_panel  # noqa: E402
from enhance_pbip_report import (  # noqa: E402
    PAGE_PROFILE_H,
    PAGE_PROFILE_W,
    PRIMARY_BLUE,
    PRIMARY_YELLOW,
    REPORT,
    TEXT_BLACK,
    clear_visuals,
    page_header_title,
    shape_rect,
    textbox,
    vid,
    write_page_json,
    write_visual,
)
from pbip_layout_constants import (  # noqa: E402
    DEFAULT_LANDING_PAGE_ID,
    GUIDE_FOOTER_PT,
    PAGE_HEADER_H,
    TAB_WALKTHROUGH,
    WALKTHROUGH_PAGE_ID,
)
from pbip_walkthrough_content import (  # noqa: E402
    INTRO_LINES,
    PAGE_SUBTITLE,
    PERSONA_LINES,
    PILOT_QUICK_REF_LINES,
    PILOT_QUICK_REF_TITLE,
    STEPS_LINES,
    TIPS_LINES,
)

WALKTHROUGH_DISPLAY_NAME = TAB_WALKTHROUGH


def build_walkthrough_page(page_dir: Path) -> None:
    clear_visuals(page_dir)
    w, h = PAGE_PROFILE_W, PAGE_PROFILE_H
    margin = 32
    content_w = w - (margin * 2)
    header_h = PAGE_HEADER_H
    footer_h = 52
    content_bottom = h - footer_h - 12
    row1_y = header_h + 12
    steps_h = 248
    quick_ref_h = 300
    row2_h = 156
    quick_ref_y = row1_y + steps_h + 12
    row2_y = quick_ref_y + quick_ref_h + 12
    row3_y = row2_y + row2_h + 12
    about_h = content_bottom - row3_y

    visuals = [
        shape_rect(vid(), 0, 0, w, header_h, 0, PRIMARY_BLUE),
        page_header_title(vid(), content_w, 1, TAB_WALKTHROUGH),
        section_panel(
            margin, row1_y, content_w, steps_h, 2,
            f"Follow these steps - {PAGE_SUBTITLE.lower()}",
            STEPS_LINES,
        ),
        section_panel(
            margin,
            quick_ref_y,
            content_w,
            quick_ref_h,
            4,
            PILOT_QUICK_REF_TITLE,
            PILOT_QUICK_REF_LINES,
        ),
        section_panel(margin, row2_y, (content_w - 16) // 2, row2_h, 5, "Who uses which tab", PERSONA_LINES),
        section_panel(
            margin + (content_w - 16) // 2 + 16,
            row2_y,
            (content_w - 16) // 2,
            row2_h,
            6,
            "Tips",
            TIPS_LINES,
        ),
        section_panel(margin, row3_y, content_w, about_h, 7, "About this report", INTRO_LINES),
        shape_rect(vid(), 0, h - footer_h, w, footer_h, 8, PRIMARY_YELLOW),
        textbox(
            vid(), margin, h - footer_h + 10, content_w, 36, 9,
            "Next: Standards & Contexts tab | OPEN-CATALOG.bat and WALKTHROUGH.txt in release package",
            size=GUIDE_FOOTER_PT, color=TEXT_BLACK, transparent=True,
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def main() -> None:
    page_dir = REPORT / "pages" / WALKTHROUGH_PAGE_ID
    page_dir.mkdir(parents=True, exist_ok=True)
    write_page_json(
        page_dir,
        WALKTHROUGH_PAGE_ID,
        WALKTHROUGH_DISPLAY_NAME,
        width=PAGE_PROFILE_W,
        height=PAGE_PROFILE_H,
        informational=True,
    )
    build_walkthrough_page(page_dir)
    from enhance_pbip_report import sync_pages_json, sync_page_tab_styles  # noqa: E402

    sync_pages_json(landing_page_id=DEFAULT_LANDING_PAGE_ID)
    sync_page_tab_styles()
    print(f"Wrote PBIP page: {WALKTHROUGH_DISPLAY_NAME} ({WALKTHROUGH_PAGE_ID})")
    print(f"  Default landing page: Guide · Start here ({DEFAULT_LANDING_PAGE_ID})")
    from pbip_paths import PBIP_FILE  # noqa: E402

    print(f"  Re-open {PBIP_FILE} in Power BI Desktop and Refresh.")


if __name__ == "__main__":
    main()
