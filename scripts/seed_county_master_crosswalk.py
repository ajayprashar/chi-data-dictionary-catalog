#!/usr/bin/env python3
"""Seed county master demographics crosswalk from SHIE survivorship SQL mappings.

Loads curated mappings from data/county_survivorship_mappings.py (extracted from
Table 4/5/2 CASE blocks). Does not overwrite value set bindings or members.

Responsible scope:
  - Source strings → standard codes (CDCREC OMB, BCP 47, US Core birth sex)
  - NOT a duplicate of HL7 Value_Set_Members (run build_value_set_members.py separately)
  - NOT county language reporting groups (Asian, European other) - those stay in Dictionary
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.county_survivorship_mappings import (  # noqa: E402
    COUNTY_ETHNICITY_GROUP_TO_CDCREC,
    COUNTY_RACE_GROUP_TO_CDCREC,
    ETHNICITY_AGGREGATE_EXCLUDES,
    ETHNICITY_SOURCE_TO_COUNTY_GROUP,
    LANGUAGE_AGGREGATE_EXCLUDES,
    LANGUAGE_NEEDS_REVIEW,
    LANGUAGE_SOURCE_TO_BCP47,
    RACE_AGGREGATE_EXCLUDES,
    RACE_SOURCE_TO_COUNTY_GROUP,
    SEXID_AGGREGATE_EXCLUDES,
    SEXID_SOURCE_TO_BIRTHSEX,
)

CDCREC_OID = "urn:oid:2.16.840.1.113883.6.238"
BCP47_OID = "urn:ietf:bcp:47"
BIRTHSEX_CS = "http://hl7.org/fhir/us/core/CodeSystem/birthsex"

SOURCE_ID = "county_master"
AUTHORITY = "SHIE master-demographics survivorship workbook; Table 4/5/2 SQL"
APPROVAL = "Approved"

CROSSWALK_COLUMNS = [
    "source_id",
    "source_field",
    "source_code",
    "source_display",
    "semantic_id",
    "target_code_system_oid",
    "target_code",
    "target_display",
    "mapping_type",
    "approval_status",
    "effective_from",
    "effective_to",
    "notes",
]


def _row(
    *,
    source_field: str,
    semantic_id: str,
    source_code: str,
    source_display: str,
    target_oid: str,
    target_code: str,
    target_display: str,
    mapping_type: str,
    notes: str = "",
) -> dict[str, str]:
    return {
        "source_id": SOURCE_ID,
        "source_field": source_field,
        "source_code": source_code,
        "source_display": source_display,
        "semantic_id": semantic_id,
        "target_code_system_oid": target_oid,
        "target_code": target_code,
        "target_display": target_display,
        "mapping_type": mapping_type,
        "approval_status": APPROVAL,
        "effective_from": "",
        "effective_to": "",
        "notes": notes or AUTHORITY,
    }


def _dedupe_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row["semantic_id"], row["source_field"], row["source_code"], row["mapping_type"])


def _append_unique(rows: list[dict[str, str]], seen: set[tuple[str, str, str, str]], row: dict[str, str]) -> None:
    key = _dedupe_key(row)
    if key in seen:
        return
    seen.add(key)
    rows.append(row)


def validate_mappings() -> list[str]:
    """Pre-flight checks before writing parquet."""
    issues: list[str] = []
    for source, group in RACE_SOURCE_TO_COUNTY_GROUP:
        if group not in ("Unknown",) and group not in COUNTY_RACE_GROUP_TO_CDCREC:
            issues.append(f"race: unmapped county group {group!r} for source {source!r}")
    for source, group in ETHNICITY_SOURCE_TO_COUNTY_GROUP:
        if group not in ("Unknown",) and group not in COUNTY_ETHNICITY_GROUP_TO_CDCREC:
            issues.append(f"ethnicity: unmapped county group {group!r} for source {source!r}")
    race_sources = {s for s, _ in RACE_SOURCE_TO_COUNTY_GROUP}
    ethnicity_sources = {s for s, _ in ETHNICITY_SOURCE_TO_COUNTY_GROUP}
    for exc in RACE_AGGREGATE_EXCLUDES:
        if exc not in race_sources:
            issues.append(f"race exclude {exc!r} not in RACE_SOURCE_TO_COUNTY_GROUP")
    for exc in ETHNICITY_AGGREGATE_EXCLUDES:
        if exc not in ethnicity_sources:
            issues.append(f"ethnicity exclude {exc!r} not in ETHNICITY_SOURCE_TO_COUNTY_GROUP")
    return issues


def build_crosswalk_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()

    for source, county_group in RACE_SOURCE_TO_COUNTY_GROUP:
        if source in RACE_AGGREGATE_EXCLUDES or county_group == "Unknown":
            _append_unique(
                rows,
                seen,
                _row(
                    source_field="Race",
                    semantic_id="Patient.race",
                    source_code=source,
                    source_display=source,
                    target_oid=CDCREC_OID,
                    target_code="",
                    target_display="",
                    mapping_type="exclude",
                    notes="Excluded from county aggregates per Table 5 survivorship",
                ),
            )
            continue
        code, display = COUNTY_RACE_GROUP_TO_CDCREC[county_group]
        _append_unique(
            rows,
            seen,
            _row(
                source_field="Race",
                semantic_id="Patient.race",
                source_code=source,
                source_display=source,
                target_oid=CDCREC_OID,
                target_code=code,
                target_display=display,
                mapping_type="rollup",
                notes=f"{AUTHORITY}; Table 5 race groupings → CDCREC OMB",
            ),
        )

    for source, county_group in ETHNICITY_SOURCE_TO_COUNTY_GROUP:
        if source in ETHNICITY_AGGREGATE_EXCLUDES or county_group == "Unknown":
            _append_unique(
                rows,
                seen,
                _row(
                    source_field="Ethnicity",
                    semantic_id="Patient.ethnicity",
                    source_code=source,
                    source_display=source,
                    target_oid=CDCREC_OID,
                    target_code="",
                    target_display="",
                    mapping_type="exclude",
                    notes="Excluded from county aggregates per Table 5 survivorship",
                ),
            )
            continue
        code, display = COUNTY_ETHNICITY_GROUP_TO_CDCREC[county_group]
        _append_unique(
            rows,
            seen,
            _row(
                source_field="Ethnicity",
                semantic_id="Patient.ethnicity",
                source_code=source,
                source_display=source,
                target_oid=CDCREC_OID,
                target_code=code,
                target_display=display,
                mapping_type="rollup",
                notes=f"{AUTHORITY}; Table 5 ethnicity groupings → CDCREC OMB",
            ),
        )

    for source_token, display, bcp47 in LANGUAGE_SOURCE_TO_BCP47:
        if source_token in LANGUAGE_NEEDS_REVIEW:
            continue
        if source_token in LANGUAGE_AGGREGATE_EXCLUDES or bcp47 == "und":
            _append_unique(
                rows,
                seen,
                _row(
                    source_field="Language",
                    semantic_id="Patient.language",
                    source_code=source_token,
                    source_display=display,
                    target_oid=BCP47_OID,
                    target_code="",
                    target_display="",
                    mapping_type="exclude",
                    notes="Excluded from county aggregates per Table 4 survivorship",
                ),
            )
            continue
        _append_unique(
            rows,
            seen,
            _row(
                source_field="Language",
                semantic_id="Patient.language",
                source_code=source_token,
                source_display=display,
                target_oid=BCP47_OID,
                target_code=bcp47,
                target_display=display,
                mapping_type="exact",
                notes=f"{AUTHORITY}; Table 4 language detail → BCP 47",
            ),
        )

    for source in LANGUAGE_AGGREGATE_EXCLUDES:
        if any(source == t[0] for t in LANGUAGE_SOURCE_TO_BCP47):
            continue
        _append_unique(
            rows,
            seen,
            _row(
                source_field="Language",
                semantic_id="Patient.language",
                source_code=source,
                source_display=source,
                target_oid=BCP47_OID,
                target_code="",
                target_display="",
                mapping_type="exclude",
                notes="Excluded from county aggregates per Table 4 survivorship",
            ),
        )

    for source, target_code, target_display, mapping_type in SEXID_SOURCE_TO_BIRTHSEX:
        _append_unique(
            rows,
            seen,
            _row(
                source_field="SexID",
                semantic_id="Patient.birth_sex",
                source_code=source,
                source_display=source,
                target_oid=BIRTHSEX_CS,
                target_code=target_code,
                target_display=target_display,
                mapping_type=mapping_type,
                notes=f"{AUTHORITY}; Table 2 SexID - not Patient.gender_id",
            ),
        )

    for source in SEXID_AGGREGATE_EXCLUDES:
        _append_unique(
            rows,
            seen,
            _row(
                source_field="SexID",
                semantic_id="Patient.birth_sex",
                source_code=source,
                source_display=source,
                target_oid=BIRTHSEX_CS,
                target_code="UNK",
                target_display="Unknown",
                mapping_type="exclude",
                notes="Treated as null at master level per county SexID logic",
            ),
        )

    return rows


def main() -> None:
    issues = validate_mappings()
    if issues:
        print("Mapping validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)

    rows = build_crosswalk_rows()
    crosswalk = pd.DataFrame(rows, columns=CROSSWALK_COLUMNS)
    out_path = ROOT / "ddc-source_value_crosswalk.parquet"
    crosswalk.to_parquet(out_path, index=False)

    print(f"Wrote {out_path} ({len(crosswalk)} rows)")
    for sid in sorted(crosswalk["semantic_id"].unique()):
        sub = crosswalk[crosswalk["semantic_id"] == sid]
        by_type = sub.groupby("mapping_type").size().to_dict()
        print(f"  {sid}: {len(sub)} rows {by_type}")
    review = [t[0] for t in LANGUAGE_SOURCE_TO_BCP47 if t[0] in LANGUAGE_NEEDS_REVIEW]
    if review:
        print(f"  (skipped pending steward BCP 47 review: {', '.join(review)})")


if __name__ == "__main__":
    main()
