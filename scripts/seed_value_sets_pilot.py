#!/usr/bin/env python3
"""Seed demographics pilot value set bindings and members.

Source crosswalk: scripts/seed_county_master_crosswalk.py
"""

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
DAR_CS = "http://terminology.hl7.org/CodeSystem/data-absent-reason"
GENDER_IDENTITY_VS = "http://terminology.hl7.org/ValueSet/gender-identity"

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
        "value_set_name": "HL7 Gender Identity (minimum set)",
        "value_set_url": GENDER_IDENTITY_VS,
        "code_system_oid": SNOMED_OID,
        "code_system_name": "SNOMED CT",
        "binding_strength": "extensible",
        "fhir_element": "Observation.valueCodeableConcept (LOINC 76691-5)",
        "authority_reference": "docs/shie-standards-reference.md#gender-identity-minimum-set",
        "approval_status": "Approved",
        "notes": "LOINC 76691-5 identifies the observation; answers bind HL7 gender-identity ValueSet (SNOMED + DAR/nullflavor). Not CMT SexID.",
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
        "notes": "Administrative sex - not CDCREC; distinct from gender identity.",
    },
]

MEMBERS: list[dict[str, str]] = [
    # Patient.race - OMB rollup (CDCREC)
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
    # Patient.race - NullFlavor (non-answers)
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
    # Patient.language - pilot examples (BCP 47)
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
            "notes": "Pilot examples; full list from IANA/BCP 47 - not duplicated locally",
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
    # Patient.gender_id - HL7 minimum gender identity (SNOMED + non-answers)
    {
        "semantic_id": "Patient.gender_id",
        "code_system_oid": SNOMED_OID,
        "code": "446141000124107",
        "display": "Female gender identity",
        "member_type": "standard",
        "binding_role": "primary",
        "binding_strength": "extensible",
        "active": "true",
        "sort_order": "1",
        "notes": "HL7 gender-identity minimum set; US Core extensible binding",
    },
    {
        "semantic_id": "Patient.gender_id",
        "code_system_oid": SNOMED_OID,
        "code": "446151000124109",
        "display": "Male gender identity",
        "member_type": "standard",
        "binding_role": "primary",
        "binding_strength": "extensible",
        "active": "true",
        "sort_order": "2",
        "notes": "HL7 gender-identity minimum set",
    },
    {
        "semantic_id": "Patient.gender_id",
        "code_system_oid": SNOMED_OID,
        "code": "33791000087105",
        "display": "Non-binary gender identity",
        "member_type": "standard",
        "binding_role": "primary",
        "binding_strength": "extensible",
        "active": "true",
        "sort_order": "3",
        "notes": "HL7 gender-identity minimum set; county equity rollup may map to Other",
    },
    {
        "semantic_id": "Patient.gender_id",
        "code_system_oid": NULLFLAVOR_OID,
        "code": "UNK",
        "display": "Unknown",
        "member_type": "nullflavor",
        "binding_role": "nullflavor",
        "binding_strength": "example",
        "active": "true",
        "sort_order": "10",
        "notes": "HL7 v3 NullFlavor; not a gender identity answer",
    },
    {
        "semantic_id": "Patient.gender_id",
        "code_system_oid": DAR_CS,
        "code": "asked-declined",
        "display": "Asked but declined",
        "member_type": "exclude",
        "binding_role": "primary",
        "binding_strength": "example",
        "active": "true",
        "sort_order": "20",
        "notes": "FHIR Data Absent Reason; exclude from equity aggregates",
    },
    # Patient.birth_sex - US Core birth sex
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

def main() -> None:
    root = Path(__file__).resolve().parent.parent

    bindings = pd.DataFrame(BINDINGS, columns=BINDING_COLUMNS)
    members = pd.DataFrame(MEMBERS, columns=MEMBER_COLUMNS)

    bindings_path = root / "ddc-value_set_binding.parquet"
    members_path = root / "ddc-value_set_member.parquet"

    bindings.to_parquet(bindings_path, index=False)
    members.to_parquet(members_path, index=False)

    print(f"Wrote {bindings_path} ({len(bindings)} rows)")
    print(f"Wrote {members_path} ({len(members)} rows)")
    print("Crosswalk: run scripts/seed_county_master_crosswalk.py (not overwritten here)")
    for sid in PILOT_IDS:
        n = len(members[members["semantic_id"] == sid])
        print(f"  {sid}: {n} governed member row(s)")


if __name__ == "__main__":
    main()
