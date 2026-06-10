#!/usr/bin/env python3
"""Generate ddc-application_guide.parquet from data/pbip_report_manifest.py."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "data"))

from pbip_report_manifest import (  # noqa: E402
    DEFAULT_FIELD,
    FIELD_GUIDE,
    GUIDE_COLUMNS,
    GUIDE_PARQUET,
    LAYER_QUESTIONS,
    PAGES,
    VISUALS,
)


def build_guide_rows() -> list[dict]:
    page_by_id = {p["page_id"]: p for p in PAGES}
    rows: list[dict] = []
    sort_order = 0
    for visual in VISUALS:
        page = page_by_id[visual["page_id"]]
        layer = visual["layer"]
        for column_name in visual["columns"]:
            sort_order += 1
            key = (visual["semantic_model_table"], column_name)
            meta = {**DEFAULT_FIELD, **FIELD_GUIDE.get(key, {})}
            guide_id = f"{visual['page_id']}.{visual['semantic_model_table']}.{column_name}".replace(" ", "_")
            rows.append(
                {
                    "guide_id": guide_id,
                    "page_id": page["page_id"],
                    "page_display_name": page["page_display_name"],
                    "page_purpose": page["page_purpose"],
                    "page_interop_summary": page["page_interop_summary"],
                    "visual_title": visual["visual_title"],
                    "sort_order": str(sort_order),
                    "semantic_model_table": visual["semantic_model_table"],
                    "column_name": column_name,
                    "layer": layer,
                    "layer_question": LAYER_QUESTIONS.get(layer, ""),
                    "purpose_short": meta["purpose_short"],
                    "interop_role": meta["interop_role"],
                    "standards_touchpoint": meta["standards_touchpoint"],
                    "exchange_formats": meta["exchange_formats"],
                    "excel_sheet": meta["excel_sheet"],
                    "editable_in_excel": meta["editable_in_excel"],
                    "pilot_example": meta["pilot_example"],
                    "doc_ref": meta["doc_ref"],
                }
            )
    return rows


def generate(out_path: Path | None = None) -> Path:
    out = out_path or (REPO / GUIDE_PARQUET)
    rows = build_guide_rows()
    df = pd.DataFrame(rows, columns=GUIDE_COLUMNS)
    df.to_parquet(out, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO / GUIDE_PARQUET,
        help="Output parquet path",
    )
    args = parser.parse_args()
    rows = build_guide_rows()
    out = generate(args.output.resolve())
    print(f"Wrote {len(rows)} guide rows to {out}")


if __name__ == "__main__":
    main()
