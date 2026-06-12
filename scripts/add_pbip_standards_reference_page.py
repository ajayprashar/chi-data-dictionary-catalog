#!/usr/bin/env python3
"""Add or refresh Guide · Standards reference page (authoritative standards table as readable panels)."""

from __future__ import annotations

import json
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
    TEXT_WHITE,
    clear_visuals,
    page_header_title,
    shape_rect,
    textbox,
    vid,
    write_page_json,
    write_text_utf8_no_bom,
    write_visual,
)
from pbip_layout_constants import (  # noqa: E402
    GUIDE_FOOTER_PT,
    PAGE_HEADER_H,
    PAGE_STANDARDS_REF_ID,
    TAB_STANDARDS_REF,
)
from pbip_standards_reference_content import (  # noqa: E402
    EXCHANGE_STANDARDS_LINES,
    LAYER_LINES,
    PAGE_SUBTITLE,
    PAGE_TITLE,
    SUPPORTING_LINES,
    TERMINOLOGY_LINES,
)

STANDARDS_REF_DISPLAY_NAME = TAB_STANDARDS_REF


def build_standards_reference_page(page_dir: Path) -> None:
    clear_visuals(page_dir)
    w, h = PAGE_PROFILE_W, PAGE_PROFILE_H
    margin = 32
    content_w = w - (margin * 2)
    header_h = PAGE_HEADER_H
    footer_h = 52
    content_bottom = h - footer_h - 12
    row1_y = header_h + 12
    col_w = (content_w - 16) // 2
    layer_h = 128  # 3 body lines at 13pt + title band
    cols_gap = 12
    cols_h = 300
    cols_y = row1_y + layer_h + cols_gap
    row2_y = cols_y + cols_h + cols_gap
    row2_h = content_bottom - row2_y

    visuals = [
        shape_rect(vid(), 0, 0, w, header_h, 0, PRIMARY_BLUE),
        page_header_title(vid(), content_w, 1, TAB_STANDARDS_REF),
        section_panel(
            margin, row1_y, content_w, layer_h, 2,
            f"How standards layer together - {PAGE_SUBTITLE.lower()}",
            LAYER_LINES,
        ),
        section_panel(
            margin, cols_y, col_w, cols_h, 4,
            "Exchange & content standards", EXCHANGE_STANDARDS_LINES,
        ),
        section_panel(
            margin + col_w + 16, cols_y, col_w, cols_h, 5,
            "Terminology authorities", TERMINOLOGY_LINES,
        ),
        section_panel(
            margin, row2_y, content_w, row2_h, 6,
            "Supporting references", SUPPORTING_LINES,
        ),
        shape_rect(vid(), 0, h - footer_h, w, footer_h, 7, PRIMARY_YELLOW),
        textbox(
            vid(), margin, h - footer_h + 10, content_w, 36, 8,
            "Mirror: docs/shie-standards-reference.md | Notion Authoritative Standards / Sources of Truth",
            size=GUIDE_FOOTER_PT, color=TEXT_BLACK, transparent=True,
        ),
    ]
    for v in visuals:
        write_visual(page_dir, v)


def main() -> None:
    page_dir = REPORT / "pages" / PAGE_STANDARDS_REF_ID
    page_dir.mkdir(parents=True, exist_ok=True)
    write_page_json(
        page_dir,
        PAGE_STANDARDS_REF_ID,
        STANDARDS_REF_DISPLAY_NAME,
        width=PAGE_PROFILE_W,
        height=PAGE_PROFILE_H,
        informational=True,
    )
    build_standards_reference_page(page_dir)
    from enhance_pbip_report import sync_pages_json, sync_page_tab_styles  # noqa: E402

    sync_pages_json()
    sync_page_tab_styles()
    print(f"Wrote PBIP page: {STANDARDS_REF_DISPLAY_NAME} ({PAGE_STANDARDS_REF_ID})")


if __name__ == "__main__":
    main()
