#!/usr/bin/env python3
"""Merge starter partner crosswalk template into ddc-source_value_crosswalk.parquet.

Replaces only rows with source_id in partner_crosswalk_template.PARTNER_TEMPLATE_SOURCE_IDS.
Does not touch county_master rows from seed_county_master_crosswalk.py.

After intake: copy partner rows into steward workbook Source_Value_Crosswalk, set real
source_id, set approval_status Approved, then import_steward_workbook_to_parquet.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.partner_crosswalk_template import (  # noqa: E402
    CROSSWALK_COLUMNS,
    PARTNER_TEMPLATE_SOURCE_IDS,
    build_template_rows,
)

CROSSWALK_PATH = ROOT / "ddc-source_value_crosswalk.parquet"
MEMBERS_PATH = ROOT / "ddc-value_set_member.parquet"

# Crosswalk targets allowed even when not in Value_Set_Members (non-answer codes).
ALLOWED_WITHOUT_MEMBER = {
    ("Patient.gender_id", "UNK"),
    ("Patient.gender_id", "asked-declined"),
}


def validate_targets(rows: list[dict[str, str]], members: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    member_keys = set(zip(members["semantic_id"].astype(str), members["code"].astype(str)))
    for row in rows:
        key = (row["semantic_id"], row["target_code"])
        if key in ALLOWED_WITHOUT_MEMBER:
            continue
        if key not in member_keys:
            issues.append(
                f"{row['source_field']}/{row['source_code']!r} → {row['semantic_id']} "
                f"target {row['target_code']!r} not in Value_Set_Members"
            )
    return issues


def merge_template(existing: pd.DataFrame, template: pd.DataFrame) -> pd.DataFrame:
    kept = existing[~existing["source_id"].isin(PARTNER_TEMPLATE_SOURCE_IDS)]
    return pd.concat([kept, template], ignore_index=True)


def main() -> None:
    template_rows = build_template_rows()
    template = pd.DataFrame(template_rows, columns=CROSSWALK_COLUMNS)

    if MEMBERS_PATH.is_file():
        members = pd.read_parquet(MEMBERS_PATH)
        issues = validate_targets(template_rows, members)
        if issues:
            print("Template validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)

    if CROSSWALK_PATH.is_file():
        existing = pd.read_parquet(CROSSWALK_PATH)
        for col in CROSSWALK_COLUMNS:
            if col not in existing.columns:
                existing[col] = ""
        existing = existing[CROSSWALK_COLUMNS]
        crosswalk = merge_template(existing, template)
    else:
        crosswalk = template

    crosswalk.to_parquet(CROSSWALK_PATH, index=False)

    partner = crosswalk[crosswalk["source_id"].isin(PARTNER_TEMPLATE_SOURCE_IDS)]
    print(f"Wrote {CROSSWALK_PATH} ({len(crosswalk)} rows total)")
    print(f"  partner template: {len(partner)} rows (approval_status=draft)")
    for sid in sorted(partner["semantic_id"].unique()):
        sub = partner[partner["semantic_id"] == sid]
        print(f"    {sid}: {len(sub)} row(s)")


if __name__ == "__main__":
    main()
