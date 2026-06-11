#!/usr/bin/env python3
"""Generate ddc-application_guide.parquet from data/pbip_report_manifest.py."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "data"))

from pilot_curation_checks import (  # noqa: E402
    CONCEPT_PROFILE_CHECKS,
    GUIDE_GAPS_COLUMNS,
    GUIDE_GAPS_PARQUET,
    PILOT_SEMANTIC_IDS,
)
from pbip_report_manifest import (  # noqa: E402
    DEFAULT_FIELD,
    FIELD_GUIDE,
    GUIDE_COLUMNS,
    GUIDE_PARQUET,
    LAYER_QUESTIONS,
    PAGE_CONCEPT_PROFILE,
    PAGES,
    VISUALS,
    excel_table_for_sheet,
    resolve_standards_url,
    steward_action_for,
)

CONCEPT_PROFILE_PAGE = next(p for p in PAGES if p["page_id"] == PAGE_CONCEPT_PROFILE)


def _is_empty(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    text = str(value).strip()
    return text in ("", "-", "unknown", "nan", "None")


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
                    "primary_audience": page.get("primary_audience", ""),
                    "visual_title": visual["visual_title"],
                    "sort_order": str(sort_order),
                    "semantic_model_table": visual["semantic_model_table"],
                    "column_name": column_name,
                    "layer": layer,
                    "layer_question": LAYER_QUESTIONS.get(layer, ""),
                    "purpose_short": meta["purpose_short"],
                    "interop_role": meta["interop_role"],
                    "standards_touchpoint": meta["standards_touchpoint"],
                    "standards_url": resolve_standards_url(meta["standards_touchpoint"], meta),
                    "exchange_formats": meta["exchange_formats"],
                    "excel_sheet": meta["excel_sheet"],
                    "excel_table": excel_table_for_sheet(meta["excel_sheet"]),
                    "editable_in_excel": meta["editable_in_excel"],
                    "steward_action": steward_action_for(meta),
                    "review_on_page": page["page_display_name"],
                    "pilot_example": meta["pilot_example"],
                    "doc_ref": meta["doc_ref"],
                }
            )
    return rows


def _load_parquet(stem: str) -> pd.DataFrame:
    path = REPO / f"{stem}.parquet"
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_parquet(path)


def _gap_reason(check: dict, value: object, approval_status: str) -> str | None:
    mode = check["gap_if"]
    if mode == "empty_or_not_approved":
        if _is_empty(value):
            return "Missing value - Concept Profile will show blank"
        if str(value).strip().lower() != "approved":
            return f"Not Approved (current: {value})"
        return None
    if mode == "empty" and _is_empty(value):
        return "Missing value - Concept Profile will show blank"
    return None


def _source_availability_gap(semantic_id: str, src_df: pd.DataFrame) -> str | None:
    rows = src_df[src_df["semantic_id"] == semantic_id] if not src_df.empty and "semantic_id" in src_df.columns else pd.DataFrame()
    if rows.empty:
        return "No Source_Availability row - add link in workbook"
    if "availability" not in rows.columns:
        return None
    values = [str(v).strip().lower() for v in rows["availability"].tolist()]
    if not values or all(v in ("", "unknown") for v in values):
        return "All sources unknown - set availability in Source_Availability sheet"
    return None


def build_curation_gap_rows() -> list[dict]:
    catalog = _load_parquet("ddc-master_patient_catalog")
    dictionary = _load_parquet("ddc-master_patient_dictionary")
    source_availability = _load_parquet("ddc-data_source_availability")
    if catalog.empty or "semantic_id" not in catalog.columns:
        return []

    frames = {
        "ddc-master_patient_catalog": catalog,
        "ddc-master_patient_dictionary": dictionary,
    }
    pilot_set = set(PILOT_SEMANTIC_IDS)
    scope_ids: list[str] = []
    for sid in PILOT_SEMANTIC_IDS:
        if sid not in scope_ids:
            scope_ids.append(sid)
    if "approval_status" in catalog.columns:
        backlog = catalog[catalog["approval_status"].astype(str).str.strip().str.lower() != "approved"]
        for sid in backlog["semantic_id"].astype(str).tolist():
            if sid not in scope_ids:
                scope_ids.append(sid)

    rows: list[dict] = []
    sort_order = 0
    for semantic_id in scope_ids:
        cat_row = catalog[catalog["semantic_id"] == semantic_id]
        approval = ""
        if not cat_row.empty and "approval_status" in cat_row.columns:
            approval = str(cat_row.iloc[0]["approval_status"]).strip()

        for check in CONCEPT_PROFILE_CHECKS:
            frame = frames.get(check["parquet"], pd.DataFrame())
            if frame.empty or "semantic_id" not in frame.columns:
                continue
            match = frame[frame["semantic_id"] == semantic_id]
            value = match.iloc[0][check["column"]] if not match.empty and check["column"] in match.columns else ""
            reason = _gap_reason(check, value, approval)
            if not reason:
                continue
            sort_order += 1
            sheet = check["excel_sheet"]
            rows.append(
                {
                    "gap_id": f"{semantic_id}.{check['column']}".replace(" ", "_"),
                    "semantic_id": semantic_id,
                    "pilot_scope": "yes" if semantic_id in pilot_set else "no",
                    "approval_status": approval,
                    "report_page": CONCEPT_PROFILE_PAGE["page_display_name"],
                    "report_column": check["report_column"],
                    "excel_sheet": sheet,
                    "source_column": check["column"],
                    "gap_reason": reason,
                    "steward_action": (
                        f"Edit {sheet} ({excel_table_for_sheet(sheet)}) for {semantic_id} → "
                        f"import → Refresh Concept Profile"
                    ),
                    "sort_order": str(sort_order),
                }
            )

        src_reason = _source_availability_gap(semantic_id, source_availability)
        if src_reason:
            sort_order += 1
            sheet = "Source_Availability"
            rows.append(
                {
                    "gap_id": f"{semantic_id}.source_availability",
                    "semantic_id": semantic_id,
                    "pilot_scope": "yes" if semantic_id in pilot_set else "no",
                    "approval_status": approval,
                    "report_page": CONCEPT_PROFILE_PAGE["page_display_name"],
                    "report_column": "Source availability",
                    "excel_sheet": sheet,
                    "source_column": "availability",
                    "gap_reason": src_reason,
                    "steward_action": (
                        f"Edit {sheet} ({excel_table_for_sheet(sheet)}) for {semantic_id} → "
                        f"import → Refresh Concept Profile"
                    ),
                    "sort_order": str(sort_order),
                }
            )
    return rows


def generate(out_path: Path | None = None) -> Path:
    out = out_path or (REPO / GUIDE_PARQUET)
    rows = build_guide_rows()
    df = pd.DataFrame(rows, columns=GUIDE_COLUMNS)
    df.to_parquet(out, index=False)
    return out


def generate_gaps(out_path: Path | None = None) -> Path:
    out = out_path or (REPO / GUIDE_GAPS_PARQUET)
    rows = build_curation_gap_rows()
    df = pd.DataFrame(rows, columns=GUIDE_GAPS_COLUMNS)
    df.to_parquet(out, index=False)
    return out


def default_field_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["purpose_short"] == DEFAULT_FIELD["purpose_short"]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO / GUIDE_PARQUET,
        help="Output parquet path",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Do not compare manifest to live PBIP visual.json projections",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if manifest/PBIP validation fails",
    )
    args = parser.parse_args()
    if not args.skip_validate:
        from validate_pbip_manifest import validate_manifest  # noqa: E402

        errors = validate_manifest()
        if errors:
            print("Manifest vs PBIP validation issues:")
            for err in errors:
                print(f"  - {err}")
            if args.strict:
                raise SystemExit(1)
        else:
            print("Manifest vs PBIP validation: OK")
    rows = build_guide_rows()
    out = generate(args.output.resolve())
    gap_rows = build_curation_gap_rows()
    gaps_out = generate_gaps()
    defaults = default_field_rows(rows)
    pilot_gaps = [r for r in gap_rows if r["pilot_scope"] == "yes"]
    print(f"Wrote {len(rows)} guide rows to {out}")
    print(f"Wrote {len(gap_rows)} curation gap rows to {gaps_out} ({len(pilot_gaps)} pilot)")
    if defaults:
        print(f"  {len(defaults)} row(s) still use DEFAULT_FIELD prose - extend FIELD_GUIDE in pbip_report_manifest.py")


if __name__ == "__main__":
    main()
