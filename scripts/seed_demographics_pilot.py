#!/usr/bin/env python3
"""Seed Phase 1 demographics pilot rows in catalog, dictionary, and source availability parquet."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

PILOT_IDS = [
    "Patient.race",
    "Patient.ethnicity",
    "Patient.language",
    "Patient.gender_id",
    "Patient.birth_sex",
]

STEWARD = "Ajay Prashar"
STEWARD_CONTACT = "Ajay.Prashar@acgov.org"
APPROVAL = "Approved"
CONSENT = "ASCMI"
HIPAA = "Demographics"

CATALOG_UPDATES: dict[str, dict[str, str]] = {
    sid: {
        "data_steward": STEWARD,
        "steward_contact": STEWARD_CONTACT,
        "approval_status": APPROVAL,
        "consent_category": CONSENT,
        "hipaa_category": HIPAA,
        "last_modified_date": date.today().isoformat(),
    }
    for sid in PILOT_IDS
}

DICTIONARY_UPDATES: dict[str, dict[str, str]] = {
    "Patient.race": {
        "chi_survivorship_logic": (
            "County: CDC PHIN Race/Ethnicity v1.3 OMB rollup (R1–R5, R9, Multi-Racial). "
            "Detail trumps rollup (e.g. Japanese > Asian). "
            "Exclude Unknown, DTS, Other Race from aggregates. Self-report first; "
            "else reliability-tiered (FQHC/community > BH > hospital > payer). "
            "Multi-racial when consistent across sources. Alert on unmapped values for curation."
        ),
        "data_quality_notes": (
            "Terminology: CDCREC OID urn:oid:2.16.840.1.113883.6.238; HL7 Race Value Set "
            "(terminology.hl7.org/ValueSet-v3-Race). US Core us-core-race: ombCategory (required), "
            "detailed (optional), text. Example ombCategory codes: 1002-5 AI/AN, 2028-9 Asian, "
            "2054-5 Black, 2076-8 NH/PI, 2106-3 White, 2131-1 Other. "
            "Non-values: HL7 NullFlavor OID urn:oid:2.16.840.1.113883.5.1008 - unknown, declined, "
            "and missing are distinct. Reporting rollup: OMB/CDC PHIN v1.3 + county Table 5. "
            "28+ source race values; granularity varies by source."
        ),
        "data_source_rank_reference": (
            "CMT expanded pop. Reliability tiers 1–3. Highland #1, Alliance #7, Housing #20 (Mark Table 2)."
        ),
    },
    "Patient.ethnicity": {
        "chi_survivorship_logic": (
            "County: CDC OMB ethnicity rollup (Hispanic or Latino / Not Hispanic or Latino). "
            "Detail trumps rollup (e.g. Mexican, Cuban > Hispanic or Latino). "
            "Exclude Unknown, declined, and patient-refused from aggregates. "
            "Self-report first; reliability-tiered fallback."
        ),
        "data_quality_notes": (
            "Terminology: CDCREC OID urn:oid:2.16.840.1.113883.6.238; HL7 Ethnicity Value Set "
            "(terminology.hl7.org/ValueSet-v3-Ethnicity). US Core us-core-ethnicity extension. "
            "Example codes: 2135-2 Hispanic or Latino, 2186-5 Not Hispanic or Latino; "
            "detail (Mexican, Cuban) maps to rollup. "
            "Non-values: HL7 NullFlavor - do not collapse unknown, declined, patient-refused. "
            "Reporting: OMB E1/E2 + county Table 5. 7+ source values; Housing high coverage."
        ),
        "data_source_rank_reference": (
            "CMT expanded pop. Reliability tiers 1–3. Highland #1, Alliance #7, Housing #20 (Mark Table 2)."
        ),
    },
    "Patient.language": {
        "chi_survivorship_logic": (
            "County: ISO 639 detail preferred over macrolanguage rollup (e.g. Japanese > Asian group). "
            "Preferred/self-reported language wins when timestamped. "
            "Exclude undetermined and declined-to-specify from aggregates. "
            "Interpreter/clinical context may override when documented."
        ),
        "data_quality_notes": (
            "Terminology: BCP 47 urn:ietf:bcp:47 is primary FHIR binding for Patient.communication.language "
            "(RFC 5646). ISO 639 lists are stewardship/crosswalk only, not primary exchange binding. "
            "HL7 Languages value set for reference. Exclude undetermined (und) and declined from aggregates. "
            "County Table 4 – Language Groupings. 112+ source values; critical for Mam-speaking outreach."
        ),
        "data_source_rank_reference": "Highland #1 (broad language capture); St Rose #17 per Mark Table 2.",
    },
    "Patient.gender_id": {
        "chi_survivorship_logic": (
            "County: Gender identity is self-reported; patient preference always wins. "
            "Most recent valid value with timestamp. US Core v5+ Observation (LOINC 76691-5). "
            "Rollup for visuals may collapse transition labels per equity policy — detail retained for drill-through. "
            "Do not apply CMT SexID survivorship here; that governs birth sex."
        ),
        "data_quality_notes": (
            "US Core: Observation LOINC 76691-5; answers bind HL7 gender-identity ValueSet (SNOMED minimum set, extensible). "
            "SNOMED CT OID urn:oid:2.16.840.1.113883.6.96. "
            "Distinct from Patient.birth_sex (us-core-birthsex / CMT SexID). "
            "Table 2 – Gender Groupings applies to SBR administrative rollup only, not this identity element."
        ),
        "data_source_rank_reference": "Patient-facing and community sources prioritized over administrative SexID.",
    },
    "Patient.birth_sex": {
        "chi_survivorship_logic": (
            "County: CMT SexID logic — ignore Unknown (U) as null at master level. "
            "Most recently modified among valid values. Reliability-weighted when sources conflict; UMPI matching. "
            "Clinical/legal sources may trump self-report per policy. "
            "SBR rollup: Male to Female → Female, Female to Male → Male (Table 2)."
        ),
        "data_quality_notes": (
            "US Core: us-core-birthsex extension on Patient. Administrative sex codes — not CDCREC race/ethnicity. "
            "NullFlavor: Unknown (U) treated as null at master level. "
            "UMPI matching field; not interchangeable with gender identity (LOINC 76691-5). "
            "County Table 2 – Gender Groupings for SBR rollup (e.g. Male to Female → Female)."
        ),
        "data_source_rank_reference": (
            "Verato UMPI match field; hospital registration over low-reliability EMS sources."
        ),
    },
}

SOURCE_NOTES = {
    "Patient.race": "CMT roster human fields; anonymous list excluded per Verato; POC pilot",
    "Patient.ethnicity": "CMT roster; POC pilot",
    "Patient.language": "CMT roster; POC pilot",
    "Patient.gender_id": "CMT roster; POC pilot",
    "Patient.birth_sex": "CMT roster; POC pilot",
}

PILOT_CCDA_ROWS: list[dict[str, str]] = [
    {
        "message_format": "CCDA",
        "section_name": "Patient Demographics",
        "entry_type": "raceCode",
        "xml_path": "/ClinicalDocument/recordTarget/patientRole/patient/raceCode",
        "semantic_id": "Patient.race",
        "fhir_r4_path": "Patient.extension(us-core-race)",
        "notes": "USCDI Race; CDCREC terminology; POC stewardship row",
        "mapping_status": "mapped",
    },
    {
        "message_format": "CCDA",
        "section_name": "Patient Demographics",
        "entry_type": "ethnicGroupCode",
        "xml_path": "/ClinicalDocument/recordTarget/patientRole/patient/ethnicGroupCode",
        "semantic_id": "Patient.ethnicity",
        "fhir_r4_path": "Patient.extension(us-core-ethnicity)",
        "notes": "USCDI Ethnicity; CDCREC terminology; POC stewardship row",
        "mapping_status": "mapped",
    },
    {
        "message_format": "CCDA",
        "section_name": "Patient Demographics",
        "entry_type": "languageCommunication",
        "xml_path": "/ClinicalDocument/recordTarget/patientRole/patient/languageCommunication/languageCode",
        "semantic_id": "Patient.language",
        "fhir_r4_path": "Patient.communication.language",
        "notes": "BCP 47 binding; POC stewardship row",
        "mapping_status": "mapped",
    },
    {
        "message_format": "CCDA",
        "section_name": "Patient Demographics",
        "entry_type": "administrativeGenderCode",
        "xml_path": "/ClinicalDocument/recordTarget/patientRole/patient/administrativeGenderCode",
        "semantic_id": "Patient.birth_sex",
        "fhir_r4_path": "Patient.extension(us-core-birthsex)",
        "notes": "Administrative sex; not gender identity; POC stewardship row",
        "mapping_status": "mapped",
    },
    {
        "message_format": "CCDA",
        "section_name": "Patient Demographics",
        "entry_type": "note",
        "xml_path": "",
        "semantic_id": "Patient.gender_id",
        "fhir_r4_path": "Observation.valueCodeableConcept (LOINC 76691-5)",
        "notes": "Gender identity rarely in CCDA; govern via FHIR US Core Observation",
        "mapping_status": "partial",
    },
]


def upsert_ccda_pilot_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for row in PILOT_CCDA_ROWS:
        mask = (out["semantic_id"] == row["semantic_id"]) & (out["entry_type"] == row["entry_type"])
        if mask.any():
            for col, val in row.items():
                if col in out.columns:
                    out.loc[mask, col] = val
        else:
            out = pd.concat([out, pd.DataFrame([row])], ignore_index=True)
    return out


def apply_row_updates(df: pd.DataFrame, key_col: str, updates: dict[str, dict[str, str]]) -> pd.DataFrame:
    out = df.copy()
    for semantic_id, fields in updates.items():
        mask = out[key_col] == semantic_id
        if not mask.any():
            continue
        for col, value in fields.items():
            if col in out.columns:
                out.loc[mask, col] = value
    return out


def seed(repo_root: Path) -> None:
    catalog_path = repo_root / "ddc-master_patient_catalog.parquet"
    dictionary_path = repo_root / "ddc-master_patient_dictionary.parquet"
    availability_path = repo_root / "ddc-data_source_availability.parquet"
    ccda_path = repo_root / "ddc-ccda_catalog.parquet"

    catalog = pd.read_parquet(catalog_path)
    dictionary = pd.read_parquet(dictionary_path)
    availability = pd.read_parquet(availability_path)
    ccda = pd.read_parquet(ccda_path)

    catalog = apply_row_updates(catalog, "semantic_id", CATALOG_UPDATES)
    dictionary = apply_row_updates(dictionary, "semantic_id", DICTIONARY_UPDATES)
    ccda = upsert_ccda_pilot_rows(ccda)

    for semantic_id in PILOT_IDS:
        mask = (availability["semantic_id"] == semantic_id) & (availability["source_id"] == "cmt")
        if mask.any():
            availability.loc[mask, "availability"] = "partial"
            availability.loc[mask, "notes"] = SOURCE_NOTES[semantic_id]

    catalog.to_parquet(catalog_path, index=False)
    dictionary.to_parquet(dictionary_path, index=False)
    availability.to_parquet(availability_path, index=False)
    ccda.to_parquet(ccda_path, index=False)

    adt_pilot = pd.read_parquet(repo_root / "ddc-hl7_adt_catalog.parquet")
    adt_count = len(adt_pilot[adt_pilot["semantic_id"].isin(PILOT_IDS)])
    ccda_count = len(ccda[ccda["semantic_id"].isin(PILOT_IDS)])

    print(f"Seeded {len(PILOT_IDS)} pilot concepts in catalog, dictionary, and source availability.")
    print(f"Interop context: {adt_count} ADT rows, {ccda_count} CCDA rows for pilot semantic_ids.")
    for sid in PILOT_IDS:
        row = catalog.loc[catalog["semantic_id"] == sid].iloc[0]
        print(f"  {sid}: approval={row['approval_status']!r}, steward={row['data_steward']!r}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    seed(repo_root)


if __name__ == "__main__":
    main()
