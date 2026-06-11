#!/usr/bin/env python3
"""Apply demo usability sprint: enrich catalog, rebuild key pages, demo tab.

Run after pulling usability changes:
  python scripts/apply_pbip_usability.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from add_pbip_demo_page import main as add_demo_page  # noqa: E402
from add_pbip_start_here_page import main as refresh_start_here  # noqa: E402
from enhance_pbip_report import (  # noqa: E402
    REPORT,
    build_concept_profile_page,
    build_standards_contexts_page,
    sync_page_tab_styles,
)
from enrich_parquet_for_pbi import main as enrich_parquet  # noqa: E402
from generate_pbip_model_guide import main as generate_guide  # noqa: E402

PAGE_CONCEPT_PROFILE = "abc963c80ac5ed2deeb4"
PAGE_STANDARDS = "d4e5f6a7b8c901234567"


def main() -> None:
    enrich_parquet()
    generate_guide()
    build_standards_contexts_page(REPORT / "pages" / PAGE_STANDARDS)
    build_concept_profile_page(REPORT / "pages" / PAGE_CONCEPT_PROFILE)
    refresh_start_here()
    add_demo_page()
    sync_page_tab_styles()
    print("Usability sprint applied. Re-open PBIP and Refresh.")


if __name__ == "__main__":
    main()
