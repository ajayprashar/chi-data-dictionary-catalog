#!/usr/bin/env python3
"""Seed demographics pilot value set bindings, members, and starter source crosswalk rows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PILOT_IDS = [
    "Patient.race",
    "Patient.ethnicity",
    "Patient.language",
    "Patient.gender_id",
    "Patient.birth_sex",
]

CDCREC_OID = "urn:oid:2.16.840.1.113883.6.238"
NULLFLAVOR_OID = "urn:oid:2.16.840.1.113883.5.1008"
BCP47_OID = "urn:ietf:bcp:47"
SNOMED_OID = "urn:oid:2.16.840.1.113883.6.96"
LOINC_OID = "urn:oid:2.16.840.1.113883.6.1"

BINDING_COLUMNS = [
    "semantic_id",
    "binding_role",
    "value_set_name",
    "value_set_url",
    "code_system_oid",
    "code_system_name",
    "binding_strength",
    "fhir_element",
    "authority_reference",
    "approval_status",
    "notes",
]

MEMBER_COLUMNS = [
    "semantic_id",
    "code_system_oid",
    "code",
    "display",
    "member_type",
    "binding_role",
    "binding_strength",
    "active",
    "sort_order",
    "notes",
]

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

BINDINGS: list[dict[str, str]] = [
    {
        "semantic_id": "Patient.race",
        "binding_role": "primary",
        "value_set_name": "HL7 Race",
        "value_set_url": "http://terminology.hl7.org/ValueSet/v3-Race",
        "code_system_oid": CDCREC_OID,
        "code_system_name": "CDCREC",
        "binding_strength": "required",
        "fhir_element": "Patient.extension(us-core-race).ombCategory",
        "authority_reference": "docs/shie-standards-reference.md#cdcrec-race-codes-omb-rollup-examples",
        "approval_status": "Approved",
        "notes": "US Core us-core-race: ombCategory required; detailed optional.",
    },
    {
        "semantic_id": "Patient.ethnicity",
        "binding_role": "primary",
        "value_set_name": "HL7 Ethnicity",
        "value_set_url": "http://terminology.hl7.org/ValueSet/v3-Ethnicity",
        "code_system_oid": CDCREC_OID,
        "code_system_name": "CDCREC",
        "binding_strength": "required",
        "fhir_element": "Patient.extension(us-core-ethnicity).ombCategory",
        "authority_reference": "docs/shie-standards-reference.md#cdcrec-ethnicity-codes-examples",
        "approval_status": "Approved",
        "notes": "US Core us-core-ethnicity extension.",
    },
    {
        "semantic_id": "Patient.language",
        "binding_role": "primary",
        "value_set_name": "FHIR Languages (BCP 47)",
        "value_set_url": "http://hl7.org/fhir/ValueSet/languages",
        "code_system_oid": BCP47_OID,
        "code_system_name": "BCP 47",
        "binding_strength": "required",
        "fhir_element": "Patient.communication.language",
        "authority_reference": "docs/shie-standards-reference.md",
        "approval_status": "Approved",
        "notes": "Primary FHIR binding; ISO 639 for stewardship crosswalk only.",
    },
    {
        "semantic_id": "Patient.gender_id",
        "binding_role": "primary",
        "value_set_name": "US Core Gender Identity Observation",
        "value_set_url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-social-history",
        "code_system_oid": LOINC_OID,
        "code_system_name": "LOINC",
        "binding_strength": "required",
        "fhir_element": "Observation.code (LOINC 76691-5)",
        "authority_reference": "docs/shie-standards-reference.md",
        "approval_status": "Approved",
        "notes": "Answer values often SNOMED-coded; expand members from US Core / partner intake.",
    },
    {
        "semantic_id": "Patient.birth_sex",
        "binding_role": "primary",
        "value_set_name": "US Core Birth Sex",
        "value_set_url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
        "code_system_oid": "http://hl7.org/fhir/us/core/CodeSystem/birthsex",
        "code_system_name": "US Core birth sex",
        "binding_strength": "required",
        "fhir_element": "Patient.extension(us-core-birthsex)",
        "authority_reference": "docs/shie-standards-reference.md",
        "approval_status": "Approved",
        "notes": "Administrative sex — not CDCREC; distinct from gender identity.",
    },
]

MEMBERS: list[dict[str, str]] = [
    # Patient.race — OMB rollup (CDCREC)
    *[
        {
            "semantic_id": "Patient.race",
            "code_system_oid": CDCREC_OID,
            "code": code,
            "display": display,
            "member_type": "omb_rollup",
            "binding_role": "primary",
            "binding_strength": "required",
            "active": "true",
            "sort_order": str(i),
            "notes": "HL7 Race Value Set / CDC PHIN reporting rollup",
        }
        for i, (code, display) in enumerate(
            [
                ("1002-5", "American Indian or Alaska Native"),
                ("2028-9", "Asian"),
                ("2054-5", "Black or African American"),
                ("2076-8", "Native Hawaiian or Other Pacific Islander"),
                ("2106-3", "White"),
                ("2131-1", "Other Race"),
            ],
            start=1,
        )
    ],
    # Patient.race — NullFlavor (non-answers)
    *[
        {
            "semantic_id": "Patient.race",
            "code_system_oid": NULLFLAVOR_OID,
            "code": code,
            "display": display,
            "member_type": "nullflavor",
            "binding_role": "nullflavor",
            "binding_strength": "example",
            "active": "true",
            "sort_order": str(10 + i),
            "notes": "Do not collapse with valid race codes in reporting",
        }
        for i, (code, display) in enumerate(
            [
                ("UNK", "Unknown"),
                ("ASKU", "Asked but not known"),
                ("NASK", "Not asked"),
            ],
            start=0,
        )
    ],
    # Patient.ethnicity
    {
        "semantic_id": "Patient.ethnicity",
        "code_system_oid": CDCREC_OID,
        "code": "2135-2",
        "display": "Hispanic or Latino",
        "member_type": "omb_rollup",
        "binding_role": "primary",
        "binding_strength": "required",
        "active": "true",
        "sort_order": "1",
        "notes": "",
    },
    {
        "semantic_id": "Patient.ethnicity",
        "code_system_oid": CDCREC_OID,
        "code": "2186-5",
        "display": "Not Hispanic or Latino",
        "member_type": "omb_rollup",
        "binding_role": "primary",
        "binding_strength": "required",
        "active": "true",
        "sort_order": "2",
        "notes": "",
    },
    {
        "semantic_id": "Patient.ethnicity",
        "code_system_oid": NULLFLAVOR_OID,
        "code": "UNK",
        "display": "Unknown",
        "member_type": "nullflavor",
        "binding_role": "nullflavor",
        "binding_strength": "example",
        "active": "true",
        "sort_order": "10",
        "notes": "Distinct from patient-refused / declined in survivorship",
    },
    # Patient.language — pilot examples (BCP 47)
    *[
        {
            "semantic_id": "Patient.language",
            "code_system_oid": BCP47_OID,
            "code": code,
            "display": display,
            "member_type": "language_tag",
            "binding_role": "primary",
            "binding_strength": "example",
            "active": "true",
            "sort_order": str(i),
            "notes": "Pilot examples; full list from IANA/BCP 47 — not duplicated locally",
        }
        for i, (code, display) in enumerate(
            [
                ("en", "English"),
                ("es", "Spanish"),
                ("zh", "Chinese"),
                ("vi", "Vietnamese"),
                ("ar", "Arabic"),
            ],
            start=1,
        )
    ],
    {
        "semantic_id": "Patient.language",
        "code_system_oid": BCP47_OID,
        "code": "und",
        "display": "Undetermined",
        "member_type": "exclude",
        "binding_role": "primary",
        "binding_strength": "example",
        "active": "true",
        "sort_order": "90",
        "notes": "Excluded from county aggregates per survivorship",
    },
    # Patient.birth_sex — US Core birth sex
    *[
        {
            "semantic_id": "Patient.birth_sex",
            "code_system_oid": "http://hl7.org/fhir/us/core/CodeSystem/birthsex",
            "code": code,
            "display": display,
            "member_type": "administrative",
            "binding_role": "primary",
            "binding_strength": "required",
            "active": "true",
            "sort_order": str(i),
            "notes": "Not interchangeable with Patient.gender_id",
        }
        for i, (code, display) in enumerate(
            [("M", "Male"), ("F", "Female"), ("UNK", "Unknown")],
            start=1,
        )
    ],
]

# Starter crosswalk — replace source_code values with validated CMT code list from partner intake.
CROSSWALK_STARTER: list[dict[str, str]] = [
    {
        "source_id": "cmt",
        "source_field": "PID-10",
        "source_code": "EXAMPLE_B",
        "source_display": "CMT race code (replace with validated list)",
        "semantic_id": "Patient.race",
        "target_code_system_oid": CDCREC_OID,
        "target_code": "2054-5",
        "target_display": "Black or African American",
        "mapping_type": "rollup",
        "approval_status": "draft",
        "effective_from": "",
        "effective_to": "",
        "notes": "POC placeholder — populate from CMT race code inventory / county Table 5",
    },
    {
        "source_id": "cmt",
        "source_field": "PID-22",
        "source_code": "EXAMPLE_H",
        "source_display": "CMT ethnicity code (replace with validated list)",
        "semantic_id": "Patient.ethnicity",
        "target_code_system_oid": CDCREC_OID,
        "target_code": "2135-2",
        "target_display": "Hispanic or Latino",
        "mapping_type": "rollup",
        "approval_status": "draft",
        "effective_from": "",
        "effective_to": "",
        "notes": "POC placeholder — populate from CMT ethnicity code inventory",
    },
    {
        "source_id": "cmt",
        "source_field": "PID-15",
        "source_code": "en",
        "source_display": "English",
        "semantic_id": "Patient.language",
        "target_code_system_oid": BCP47_OID,
        "target_code": "en",
        "target_display": "English",
        "mapping_type": "exact",
        "approval_status": "draft",
        "effective_from": "",
        "effective_to": "",
        "notes": "Example exact map when CMT sends BCP 47 or ISO-aligned language code",
    },
    {
        "source_id": "cmt",
        "source_field": "PID-8",
        "source_code": "M",
        "source_display": "Male",
        "semantic_id": "Patient.birth_sex",
        "target_code_system_oid": "http://hl7.org/fhir/us/core/CodeSystem/birthsex",
        "target_code": "M",
        "target_display": "Male",
        "mapping_type": "exact",
        "approval_status": "draft",
        "effective_from": "",
        "effective_to": "",
        "notes": "Administrative sex / SexID — not gender identity",
    },
]


def main() -> None:
    root = Path(__file__).resolve().parent.parent

    bindings = pd.DataFrame(BINDINGS, columns=BINDING_COLUMNS)
    members = pd.DataFrame(MEMBERS, columns=MEMBER_COLUMNS)
    crosswalk = pd.DataFrame(CROSSWALK_STARTER, columns=CROSSWALK_COLUMNS)

    bindings_path = root / "ddc-value_set_binding.parquet"
    members_path = root / "ddc-value_set_member.parquet"
    crosswalk_path = root / "ddc-source_value_crosswalk.parquet"

    bindings.to_parquet(bindings_path, index=False)
    members.to_parquet(members_path, index=False)
    crosswalk.to_parquet(crosswalk_path, index=False)

    print(f"Wrote {bindings_path} ({len(bindings)} rows)")
    print(f"Wrote {members_path} ({len(members)} rows)")
    print(f"Wrote {crosswalk_path} ({len(crosswalk)} rows)")
    for sid in PILOT_IDS:
        n = len(members[members["semantic_id"] == sid])
        print(f"  {sid}: {n} governed member row(s)")


if __name__ == "__main__":
    main()
