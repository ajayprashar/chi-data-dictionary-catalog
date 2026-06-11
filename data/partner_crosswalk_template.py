"""Starter partner source → standard crosswalk rows (intake examples).

Partners copy these patterns in chi-partner-intake-workbook.xlsx (Crosswalk_Template
sheet) or stewards edit this file after intake review. Rows use source_id
``partner_intake`` and approval_status ``draft`` until signed.

Not county_master survivorship - that stays in county_survivorship_mappings.py.
"""

from __future__ import annotations

SNOMED_OID = "urn:oid:2.16.840.1.113883.6.96"
NULLFLAVOR_OID = "urn:oid:2.16.840.1.113883.5.1008"
DAR_CS = "http://terminology.hl7.org/CodeSystem/data-absent-reason"
CDCREC_OID = "urn:oid:2.16.840.1.113883.6.238"

# Re-seeding replaces rows with these source_id values only.
PARTNER_TEMPLATE_SOURCE_IDS = ("partner_intake",)

SOURCE_ID = "partner_intake"
AUTHORITY = "CHI partner crosswalk template; replace source_id with assigned source_id after intake"

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

# (source_field, source_code, source_display, semantic_id, target_oid, target_code,
#  target_display, mapping_type, notes)
PARTNER_CROSSWALK_TEMPLATE: list[tuple[str, ...]] = [
    (
        "GenderIdentity",
        "FEMALE",
        "Female (self-reported)",
        "Patient.gender_id",
        SNOMED_OID,
        "446141000124107",
        "Female gender identity",
        "exact",
        "Example: local export code → HL7 gender-identity minimum set. Not SexID / birth sex.",
    ),
    (
        "GenderIdentity",
        "MALE",
        "Male (self-reported)",
        "Patient.gender_id",
        SNOMED_OID,
        "446151000124109",
        "Male gender identity",
        "exact",
        "Distinct from administrative SexID on Patient.birth_sex.",
    ),
    (
        "GenderIdentity",
        "NONBINARY",
        "Non-binary",
        "Patient.gender_id",
        SNOMED_OID,
        "33791000087105",
        "Non-binary gender identity",
        "exact",
        "",
    ),
    (
        "GenderIdentity",
        "TWO_SPIRIT",
        "Two-Spirit",
        "Patient.gender_id",
        SNOMED_OID,
        "33791000087105",
        "Non-binary gender identity",
        "rollup",
        "Jurisdiction-specific label rolled to SNOMED minimum set; steward may refine after clinical review.",
    ),
    (
        "GenderIdentity",
        "DECLINE",
        "Declined to answer",
        "Patient.gender_id",
        DAR_CS,
        "asked-declined",
        "Asked but declined",
        "exclude",
        "Exclude from equity aggregates per survivorship.",
    ),
    (
        "GenderIdentity",
        "UNKNOWN",
        "Unknown",
        "Patient.gender_id",
        NULLFLAVOR_OID,
        "UNK",
        "Unknown",
        "exclude",
        "Treated as null at master level when source sends non-answer.",
    ),
    (
        "RaceCode",
        "A",
        "Asian",
        "Patient.race",
        CDCREC_OID,
        "2028-9",
        "Asian",
        "rollup",
        "Pattern example only - replace with your local race code list; target must be governed CDCREC OMB rollup.",
    ),
]


def template_row(
    source_field: str,
    source_code: str,
    source_display: str,
    semantic_id: str,
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
        "approval_status": "draft",
        "effective_from": "",
        "effective_to": "",
        "notes": notes or AUTHORITY,
    }


def build_template_rows() -> list[dict[str, str]]:
    return [
        template_row(
            source_field=t[0],
            source_code=t[1],
            source_display=t[2],
            semantic_id=t[3],
            target_oid=t[4],
            target_code=t[5],
            target_display=t[6],
            mapping_type=t[7],
            notes=t[8] if len(t) > 8 else "",
        )
        for t in PARTNER_CROSSWALK_TEMPLATE
    ]
