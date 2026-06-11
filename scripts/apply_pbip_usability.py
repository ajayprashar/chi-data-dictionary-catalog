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

from enrich_parquet_for_pbi import main as enrich_parquet  # noqa: E402
from generate_pbip_model_guide import main as generate_guide  # noqa: E402
from rebuild_all_pbip_pages import main as rebuild_all_pages  # noqa: E402


def main() -> None:
    enrich_parquet()
    generate_guide()
    rebuild_all_pages()
    print("Usability sprint applied. Re-open PBIP and Refresh.")


if __name__ == "__main__":
    main()
