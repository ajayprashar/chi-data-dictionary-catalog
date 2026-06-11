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

SLICER_TITLE = "Choose a concept — try Patient.race (full example)"
PILOT_SLICER_TITLE = "Show concepts"
PAGE_START_HERE_ID = "e1f2a3b4c5d607182934"
PAGE_FIELD_GUIDE_ID = "f7a8b9c0d1e2f304152637"
DEMO_PAGE_ID = "a9b8c7d6e5f403120918"
DEMO_LANDING_PAGE_ID = DEMO_PAGE_ID

# Informational (guide) vs functional (data) tabs — canvas background + tab label prefix.
GUIDE_TAB_PREFIX = "Guide · "
PAGE_BG_INFORMATIONAL = "#FFF9E6"
PAGE_BG_FUNCTIONAL = "#FFFFFF"
INFORMATIONAL_PAGE_IDS = frozenset({PAGE_START_HERE_ID, DEMO_PAGE_ID, PAGE_FIELD_GUIDE_ID})

TAB_START_HERE = f"{GUIDE_TAB_PREFIX}Start here"
TAB_DEMO = f"{GUIDE_TAB_PREFIX}Demo walkthrough"
TAB_FIELD_GUIDE = f"{GUIDE_TAB_PREFIX}Field guide"


def guide_tab_name(short_name: str) -> str:
    return f"{GUIDE_TAB_PREFIX}{short_name}"


def is_informational_page(page_id: str) -> bool:
    return page_id in INFORMATIONAL_PAGE_IDS
STANDARDS_ADT_CALLOUT_H = 44
ADT_CALLOUT_TEXT = (
    "ADT: field_id = HL7 position (e.g. PID-15 for language). "
    "hl7_ce_encoding = code^text CE pair when both components are mapped (race, ethnicity)."
)
CONCEPT_BLANK_CALLOUT = (
    "Empty fields are normal for concepts not yet curated in Excel. "
    "Use the five demographics pilots (filter Show concepts = yes) for a complete example."
)
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
    adt_callout_y = codes_y + STANDARDS_HALF_TABLE_H + STANDARDS_TABLE_GAP
    adt_y = adt_callout_y + STANDARDS_ADT_CALLOUT_H + 4
    adt_h = STANDARDS_HALF_TABLE_H - STANDARDS_ADT_CALLOUT_H - 4
    return {
        "slicer_y": slicer_y,
        "fhir_y": fhir_y,
        "codes_y": codes_y,
        "adt_callout_y": adt_callout_y,
        "adt_y": adt_y,
        "adt_h": adt_h,
    }
