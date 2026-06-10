"""Shared PBIP layout constants — used by enhance_pbip_report.py and patch_pbip_readability.py."""

from __future__ import annotations

PAGE_W = 1920
PAGE_MARGIN = 32
CONTENT_W = PAGE_W - (PAGE_MARGIN * 2)  # 1856

# ~50% of full-width slicer; aligns with half-width tables on Standards & Contexts.
SLICER_W = 920
SLICER_H_PROFILE = 120
SLICER_H_STANDARDS = 108

# Standards page: FHIR terminology table (survivorship stays on Concept Profile only).
FHIR_STANDARDS_TABLE_H = 248
FHIR_STANDARDS_COLUMNS = [
    "semantic_id",
    "fhir_r4_path",
    "fhir_profile",
    "data_quality_notes",
]

STANDARDS_PAGE_ID = "d4e5f6a7b8c901234567"
DEFAULT_LANDING_PAGE_ID = STANDARDS_PAGE_ID

SLICER_TITLE = "Select governed concept (semantic_id)"
FHIR_STANDARDS_TITLE = "FHIR R4 + US Core (Dictionary)"
DICT_PROFILE_TITLE = "Implementation & survivorship (FHIR + standards)"
ADT_CONTEXT_TITLE = "HL7 v2 ADT context (CE fields merged: .1 code ^ .2 text)"
ADT_CONTEXT_COLUMNS = [
    "semantic_id",
    "segment_id",
    "field_id",
    "hl7_ce_encoding",
    "field_name",
    "message_type",
    "mapping_status",
    "notes",
]

STANDARDS_HEADER_H = 128
STANDARDS_LAYER_H = 72
STANDARDS_TABLE_GAP = 12
STANDARDS_HALF_TABLE_H = 200


def standards_page_y_positions() -> dict[str, int]:
    """Vertical layout for Standards & Contexts (1920x1080 canvas)."""
    layer_y = STANDARDS_HEADER_H + 8
    slicer_y = layer_y + STANDARDS_LAYER_H + STANDARDS_TABLE_GAP
    fhir_y = slicer_y + SLICER_H_STANDARDS + 16
    codes_y = fhir_y + FHIR_STANDARDS_TABLE_H + STANDARDS_TABLE_GAP
    adt_y = codes_y + STANDARDS_HALF_TABLE_H + STANDARDS_TABLE_GAP
    return {
        "slicer_y": slicer_y,
        "fhir_y": fhir_y,
        "codes_y": codes_y,
        "adt_y": adt_y,
    }
