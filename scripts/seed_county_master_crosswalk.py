#!/usr/bin/env python3
"""Seed county master demographics crosswalk from SHIE survivorship Table 4/5/2 logic.

Source: master-demographics survivorship workbook (Mark B / county SQL CASE blocks).
Maps local source strings (Race, Ethnicity, Language, SexID) to governed standard codes.

Does not overwrite value set bindings or members — run seed_value_sets_pilot.py separately.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

CDCREC_OID = "urn:oid:2.16.840.1.113883.6.238"
BCP47_OID = "urn:ietf:bcp:47"
BIRTHSEX_CS = "http://hl7.org/fhir/us/core/CodeSystem/birthsex"

SOURCE_ID = "county_master"
AUTHORITY = "SHIE master-demographics survivorship workbook; Table 4/5/2 SQL"
APPROVAL = "draft"

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

# OMB / county rollup label → CDCREC (Table 5 race groupings)
RACE_ROLLUP_CDCREC: dict[str, tuple[str, str]] = {
    "Black or African American": ("2054-5", "Black or African American"),
    "American Indian or Alaska Native": ("1002-5", "American Indian or Alaska Native"),
    "Asian": ("2028-9", "Asian"),
    "Native Hawaiian or Other Pacific Islander": ("2076-8", "Native Hawaiian or Other Pacific Islander"),
    "Native Hawaiian/ Pacific Islander": ("2076-8", "Native Hawaiian or Other Pacific Islander"),
    "White": ("2106-3", "White"),
    "Other Race": ("2131-1", "Other Race"),
    "More than one race": ("2131-1", "Other Race"),
}

# source display → county rollup (from race_expanded_population RaceGroup CASE)
RACE_SOURCE_TO_ROLLUP: list[tuple[str, str]] = [
    ("African American", "Black or African American"),
    ("American Indian", "American Indian or Alaska Native"),
    ("American Indian or Alaska Native", "American Indian or Alaska Native"),
    ("Asian", "Asian"),
    ("Asian /White", "More than one race"),
    ("Asian Indian", "Asian"),
    ("Black", "Black or African American"),
    ("Black or African American", "Black or African American"),
    ("Black Or African American /White", "More than one race"),
    ("Cambodian", "Asian"),
    ("CAUCASIAN", "White"),
    ("Chinese", "Asian"),
    ("Eskimo", "American Indian or Alaska Native"),
    ("Filipino", "Asian"),
    ("Guamanian or Chamorro", "Native Hawaiian/ Pacific Islander"),
    ("Japanese", "Asian"),
    ("Korean", "Asian"),
    ("Laotian", "Asian"),
    ("More than one race", "More than one race"),
    ("NAT AMER/ESK/ALEUT", "American Indian or Alaska Native"),
    ("Native American/Alaskan / White", "More than one race"),
    ("Native American/Alaskan /Black", "More than one race"),
    ("Native Hawaiian", "Native Hawaiian/ Pacific Islander"),
    ("Native Hawaiian or Other Pacific Islander", "Native Hawaiian/ Pacific Islander"),
    ("Other Pacific Islander", "Native Hawaiian/ Pacific Islander"),
    ("Samoan", "Native Hawaiian/ Pacific Islander"),
    ("Vietnamese", "Asian"),
    ("White", "White"),
]

RACE_EXCLUDES = ("U", "Unknown", "Unknown/Not Reported", "DTS", "Other Race")

ETHNICITY_ROLLUP_CDCREC: dict[str, tuple[str, str]] = {
    "Hispanic or Latino": ("2135-2", "Hispanic or Latino"),
    "Not Hispanic or Latino": ("2186-5", "Not Hispanic or Latino"),
}

ETHNICITY_SOURCE_TO_ROLLUP: list[tuple[str, str]] = [
    ("Cuban", "Hispanic or Latino"),
    ("Hispanic or Latino", "Hispanic or Latino"),
    ("Mexican", "Hispanic or Latino"),
    ("Mexicano", "Hispanic or Latino"),
    ("NOT HISPANIC", "Not Hispanic or Latino"),
    ("Not Hispanic or Latino", "Not Hispanic or Latino"),
    ("Puerto Rican", "Hispanic or Latino"),
]

ETHNICITY_EXCLUDES = (
    "Declined To Specify",
    "MU Unknown Do Not Use",
    "Patient Refused",
    "Unk/Decline",
    "Unknown",
)

# source → BCP 47 (Table 4 detail normalization; codes and display names)
LANGUAGE_TO_BCP47: list[tuple[str, str, str]] = [
    # (source_code, source_display, bcp47)
    ("eng", "English", "en"),
    ("English", "English", "en"),
    ("spa", "Spanish", "es"),
    ("Spanish", "Spanish", "es"),
    ("vie", "Vietnamese", "vi"),
    ("Vietnamese", "Vietnamese", "vi"),
    ("jpn", "Japanese", "ja"),
    ("Japanese", "Japanese", "ja"),
    ("zho", "Chinese", "zh"),
    ("Chinese", "Chinese", "zh"),
    ("ara", "Arabic", "ar"),
    ("Arabic", "Arabic", "ar"),
    ("hin", "Hindi", "hi"),
    ("Hindi", "Hindi", "hi"),
    ("rus", "Russian", "ru"),
    ("Russian", "Russian", "ru"),
    ("nld", "Dutch", "nl"),
    ("mya", "Burmese", "my"),
    ("Burmese", "Burmese", "my"),
    ("tir", "Tigrigna", "ti"),
    ("Tigrigna", "Tigrigna", "ti"),
    ("Tigrinya", "Tigrigna", "ti"),
    ("tgl", "Tagalog", "tl"),
    ("Tagalog", "Tagalog", "tl"),
    ("Mam", "Mam", "mam"),
    ("Cantonese", "Cantonese", "yue"),
    ("Mandarin", "Mandarin", "cmn"),
    ("Korean", "Korean", "ko"),
    ("Thai", "Thai", "th"),
    ("French", "French", "fr"),
    ("German", "German", "de"),
    ("Portuguese", "Portuguese", "pt"),
    ("Persian", "Persian", "fa"),
    ("Farsi", "Farsi", "fa"),
    ("Hebrew", "Hebrew", "he"),
    ("Polish", "Polish", "pl"),
    ("Somali", "Somali", "so"),
    ("Swahili", "Swahili", "sw"),
    ("Amharic", "Amharic", "am"),
    ("Bengali", "Bengali", "bn"),
    ("Gujarati", "Gujarati", "gu"),
    ("Urdu", "Urdu", "ur"),
    ("Lao", "Lao", "lo"),
    ("Laotian", "Laotian", "lo"),
    ("Cambodian", "Cambodian", "km"),
    ("Armenian", "Armenian", "hy"),
    ("ASL", "Sign language", "sgn"),
    ("Sign Language", "Sign language", "sgn"),
    ("sgn", "Sign Language", "sgn"),
]

LANGUAGE_EXCLUDES = ("und", "Declined to specify", "Declined to spec", "SPE", "OTHER", "Other")

# SexID / Table 2 → US Core birth sex (administrative; not gender identity)
SEXID_TO_BIRTHSEX: list[tuple[str, str, str, str]] = [
    # (source, target_code, target_display, mapping_type)
    ("M", "M", "Male", "exact"),
    ("F", "F", "Female", "exact"),
    ("Male", "M", "Male", "rollup"),
    ("Female", "F", "Female", "rollup"),
    ("Male to Female", "F", "Female", "rollup"),
    ("Female to Male", "M", "Male", "rollup"),
]

SEXID_EXCLUDES = ("U", "Unknown", "Any", "Unknown/ Other")


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


def build_crosswalk_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for source, rollup in RACE_SOURCE_TO_ROLLUP:
        code, display = RACE_ROLLUP_CDCREC[rollup]
        rows.append(
            _row(
                source_field="Race",
                semantic_id="Patient.race",
                source_code=source,
                source_display=source,
                target_oid=CDCREC_OID,
                target_code=code,
                target_display=display,
                mapping_type="rollup",
                notes=f"{AUTHORITY}; Table 5 race groupings",
            )
        )

    for source in RACE_EXCLUDES:
        rows.append(
            _row(
                source_field="Race",
                semantic_id="Patient.race",
                source_code=source,
                source_display=source,
                target_oid=CDCREC_OID,
                target_code="",
                target_display="",
                mapping_type="exclude",
                notes="Excluded from county aggregates per survivorship",
            )
        )

    for source, rollup in ETHNICITY_SOURCE_TO_ROLLUP:
        code, display = ETHNICITY_ROLLUP_CDCREC[rollup]
        rows.append(
            _row(
                source_field="Ethnicity",
                semantic_id="Patient.ethnicity",
                source_code=source,
                source_display=source,
                target_oid=CDCREC_OID,
                target_code=code,
                target_display=display,
                mapping_type="rollup",
                notes=f"{AUTHORITY}; Table 5 ethnicity groupings",
            )
        )

    for source in ETHNICITY_EXCLUDES:
        rows.append(
            _row(
                source_field="Ethnicity",
                semantic_id="Patient.ethnicity",
                source_code=source,
                source_display=source,
                target_oid=CDCREC_OID,
                target_code="",
                target_display="",
                mapping_type="exclude",
                notes="Excluded from county aggregates per survivorship",
            )
        )

    seen_lang: set[tuple[str, str]] = set()
    for source_code, source_display, bcp47 in LANGUAGE_TO_BCP47:
        key = (source_code, source_display)
        if key in seen_lang:
            continue
        seen_lang.add(key)
        rows.append(
            _row(
                source_field="Language",
                semantic_id="Patient.language",
                source_code=source_code,
                source_display=source_display,
                target_oid=BCP47_OID,
                target_code=bcp47,
                target_display=source_display,
                mapping_type="exact",
                notes=f"{AUTHORITY}; Table 4 language groupings",
            )
        )

    for source in LANGUAGE_EXCLUDES:
        rows.append(
            _row(
                source_field="Language",
                semantic_id="Patient.language",
                source_code=source,
                source_display=source,
                target_oid=BCP47_OID,
                target_code="",
                target_display="",
                mapping_type="exclude",
                notes="Excluded from county aggregates; und excluded per survivorship",
            )
        )

    for source, target_code, target_display, mapping_type in SEXID_TO_BIRTHSEX:
        rows.append(
            _row(
                source_field="SexID",
                semantic_id="Patient.birth_sex",
                source_code=source,
                source_display=source,
                target_oid=BIRTHSEX_CS,
                target_code=target_code,
                target_display=target_display,
                mapping_type=mapping_type,
                notes=f"{AUTHORITY}; Table 2 gender groupings — not Patient.gender_id",
            )
        )

    for source in SEXID_EXCLUDES:
        rows.append(
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
            )
        )

    return rows


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    rows = build_crosswalk_rows()
    crosswalk = pd.DataFrame(rows, columns=CROSSWALK_COLUMNS)
    out_path = root / "ddc-source_value_crosswalk.parquet"
    crosswalk.to_parquet(out_path, index=False)

    print(f"Wrote {out_path} ({len(crosswalk)} rows)")
    for sid in sorted(crosswalk["semantic_id"].unique()):
        sub = crosswalk[crosswalk["semantic_id"] == sid]
        by_type = sub.groupby("mapping_type").size().to_dict()
        print(f"  {sid}: {len(sub)} rows {by_type}")


if __name__ == "__main__":
    main()
