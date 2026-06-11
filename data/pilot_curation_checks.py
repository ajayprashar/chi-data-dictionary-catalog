"""Concept Profile curation checks - used by generate_pbip_model_guide.py (Phase 3)."""

from __future__ import annotations

PILOT_SEMANTIC_IDS: tuple[str, ...] = (
    "Patient.race",
    "Patient.ethnicity",
    "Patient.language",
    "Patient.gender_id",
    "Patient.birth_sex",
)

# Each check: parquet stem, source column, steward sheet, Concept Profile column label.
CONCEPT_PROFILE_CHECKS: list[dict] = [
    {
        "parquet": "ddc-master_patient_catalog",
        "column": "approval_status",
        "excel_sheet": "Catalog",
        "report_column": "Profile Approval Status",
        "gap_if": "empty_or_not_approved",
    },
    {
        "parquet": "ddc-master_patient_catalog",
        "column": "data_steward",
        "excel_sheet": "Catalog",
        "report_column": "Profile Data Steward",
        "gap_if": "empty",
    },
    {
        "parquet": "ddc-master_patient_catalog",
        "column": "classification",
        "excel_sheet": "Catalog",
        "report_column": "Profile Classification",
        "gap_if": "empty",
    },
    {
        "parquet": "ddc-master_patient_dictionary",
        "column": "fhir_r4_path",
        "excel_sheet": "Dictionary",
        "report_column": "fhir_r4_path",
        "gap_if": "empty",
    },
    {
        "parquet": "ddc-master_patient_dictionary",
        "column": "chi_survivorship_logic",
        "excel_sheet": "Dictionary",
        "report_column": "chi_survivorship_logic",
        "gap_if": "empty",
    },
    {
        "parquet": "ddc-master_patient_dictionary",
        "column": "data_quality_notes",
        "excel_sheet": "Dictionary",
        "report_column": "data_quality_notes",
        "gap_if": "empty",
    },
]

GUIDE_GAPS_TABLE = "ddc-application_guide_gaps"
GUIDE_GAPS_PARQUET = "ddc-application_guide_gaps.parquet"

GUIDE_GAPS_COLUMNS = [
    "gap_id",
    "semantic_id",
    "pilot_scope",
    "approval_status",
    "report_page",
    "report_column",
    "excel_sheet",
    "source_column",
    "gap_reason",
    "steward_action",
    "sort_order",
]
