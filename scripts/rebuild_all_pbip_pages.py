#!/usr/bin/env python3
"""Rebuild every PBIP report page from scripts (clears visuals first - fixes duplicate layers).

Run after layout or copy changes:
  python scripts/rebuild_all_pbip_pages.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from add_pbip_walkthrough_page import build_walkthrough_page  # noqa: E402
from add_pbip_documentation_page import build_field_guide_page  # noqa: E402
from add_pbip_standards_reference_page import build_standards_reference_page  # noqa: E402
from add_pbip_start_here_page import START_HERE_PAGE_ID, build_start_here_page  # noqa: E402
from enhance_pbip_report import (  # noqa: E402
    PAGE_PROFILE_H,
    PAGE_PROFILE_W,
    REPORT,
    build_concept_profile_page,
    build_overview_page,
    build_standards_contexts_page,
    sync_pages_json,
    sync_page_tab_styles,
    write_page_json,
)
from pbip_layout_constants import (  # noqa: E402
    PAGE_CONCEPT_PROFILE_ID,
    PAGE_FIELD_GUIDE_ID,
    PAGE_GOVERNANCE_ID,
    PAGE_STANDARDS_REF_ID,
    STANDARDS_PAGE_ID,
    TAB_STANDARDS_REF,
    WALKTHROUGH_PAGE_ID,
)


def main() -> None:
    from enhance_pbip_report import sync_semantic_diagram_asset, update_report_json  # noqa: E402

    sync_semantic_diagram_asset()
    update_report_json()
    build_start_here_page(REPORT / "pages" / START_HERE_PAGE_ID)
    build_walkthrough_page(REPORT / "pages" / WALKTHROUGH_PAGE_ID)
    standards_ref_dir = REPORT / "pages" / PAGE_STANDARDS_REF_ID
    standards_ref_dir.mkdir(parents=True, exist_ok=True)
    write_page_json(
        standards_ref_dir,
        PAGE_STANDARDS_REF_ID,
        TAB_STANDARDS_REF,
        width=PAGE_PROFILE_W,
        height=PAGE_PROFILE_H,
        informational=True,
    )
    build_standards_reference_page(standards_ref_dir)
    build_standards_contexts_page(REPORT / "pages" / STANDARDS_PAGE_ID)
    build_concept_profile_page(REPORT / "pages" / PAGE_CONCEPT_PROFILE_ID)
    build_field_guide_page(REPORT / "pages" / PAGE_FIELD_GUIDE_ID)
    build_overview_page(REPORT / "pages" / PAGE_GOVERNANCE_ID)
    sync_pages_json()
    sync_page_tab_styles()
    print("Rebuilt all PBIP pages (visuals cleared per page). Re-open PBIP in Power BI Desktop.")


if __name__ == "__main__":
    main()
