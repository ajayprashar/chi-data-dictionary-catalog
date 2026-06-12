"""Shared PBIP layout constants - used by enhance_pbip_report.py and patch_pbip_readability.py."""

from __future__ import annotations

PAGE_W = 1920
PAGE_MARGIN = 32
CONTENT_W = PAGE_W - (PAGE_MARGIN * 2)  # 1856

# ~50% of full-width slicer; aligns with half-width tables on Standards & Contexts.
SLICER_W = 920
SLICER_H_PROFILE = 120
SLICER_H_STANDARDS = 108

# Standards page: taller canvas (1920x1200) so middle tables meet TABLE_STANDARD_H without overlap.
STANDARDS_PAGE_H = 1200

# Table height tiers (visible-row budget at 12pt + 8px row padding; ~32px per row, ~68px chrome).
TABLE_STANDARD_H = 300  # ~8-10 rows - value sets, crosswalk, source lists
TABLE_COMPACT_H = 160  # ~4-5 rows - ADT/CCDA per concept

# Standards page: FHIR terminology table (survivorship stays on Concept Profile only).
FHIR_STANDARDS_TABLE_H = 220
FHIR_STANDARDS_COLUMNS = [
    "semantic_id",
    "fhir_r4_path",
    "fhir_profile",
    "data_quality_notes",
]

STANDARDS_PAGE_ID = "d4e5f6a7b8c901234567"
PAGE_CONCEPT_PROFILE_ID = "abc963c80ac5ed2deeb4"
PAGE_GOVERNANCE_ID = "c8f1a2b3d4e5f6071829"
DEFAULT_LANDING_PAGE_ID = STANDARDS_PAGE_ID

SLICER_TITLE = "Choose a concept - try Patient.race (full example)"
PILOT_SLICER_TITLE = "Show concepts"
PAGE_START_HERE_ID = "e1f2a3b4c5d607182934"
PAGE_FIELD_GUIDE_ID = "f7a8b9c0d1e2f304152637"
DEMO_PAGE_ID = "a9b8c7d6e5f403120918"
DEMO_LANDING_PAGE_ID = DEMO_PAGE_ID

# Informational (guide) vs functional (data) tabs - tab label prefix; both use white canvas for readability.
GUIDE_TAB_PREFIX = "Guide · "
PAGE_BG_INFORMATIONAL = "#FFFFFF"
PAGE_BG_FUNCTIONAL = "#FFFFFF"

# Guide textbox typography (match tableEx theme: Segoe UI, 13pt body).
TEXT_FONT_FACE = "Segoe UI"
TEXT_FONT_FACE_SEMIBOLD = "Segoe UI Semibold"
GUIDE_BODY_PT = "13pt"
GUIDE_FOOTER_PT = "12pt"
PAGE_STANDARDS_REF_ID = "b1c2d3e4f5061728394a"
INFORMATIONAL_PAGE_IDS = frozenset(
    {PAGE_START_HERE_ID, DEMO_PAGE_ID, PAGE_STANDARDS_REF_ID, PAGE_FIELD_GUIDE_ID}
)

TAB_START_HERE = f"{GUIDE_TAB_PREFIX}Start here"
TAB_DEMO = f"{GUIDE_TAB_PREFIX}Demo tour"
TAB_STANDARDS_REF = f"{GUIDE_TAB_PREFIX}National standards"
TAB_FIELD_GUIDE = f"{GUIDE_TAB_PREFIX}Field guide"
TAB_STANDARDS_CONTEXTS = "Standards & Contexts"
TAB_CONCEPT_PROFILE = "Concept Profile"
TAB_GOVERNANCE_OVERVIEW = "Governance Overview"

# Left-to-right tab order: orient → tour → lookup → explore by concept → steward docs → portfolio.
PAGE_TAB_ORDER: tuple[str, ...] = (
    PAGE_START_HERE_ID,
    DEMO_PAGE_ID,
    PAGE_STANDARDS_REF_ID,
    STANDARDS_PAGE_ID,
    PAGE_CONCEPT_PROFILE_ID,
    PAGE_FIELD_GUIDE_ID,
    PAGE_GOVERNANCE_ID,
)


def guide_tab_name(short_name: str) -> str:
    return f"{GUIDE_TAB_PREFIX}{short_name}"


def is_informational_page(page_id: str) -> bool:
    return page_id in INFORMATIONAL_PAGE_IDS


PROFILE_PAGE_H = 1080
CONCEPT_HEADER_H = 128
CONCEPT_FOOTER_H = 52
CONCEPT_CALLOUT_H = 56
CONCEPT_CARD_H = 148
CONCEPT_CARD_GAP = 16
CONCEPT_PROFILE_CARD_COUNT = 5
ADT_CALLOUT_TEXT = (
    "ADT: field_id = HL7 position (e.g. PID-15 for language). "
    "hl7_ce_encoding = code^text CE pair when both components are mapped (race, ethnicity)."
)
CONCEPT_BLANK_CALLOUT = (
    "Empty fields are normal for concepts not yet curated in Excel. "
    "Use the five demographics pilots (filter Show concepts = yes) for a complete example."
)
FHIR_STANDARDS_TITLE = "FHIR R4 + US Core (Dictionary)"
DICT_PROFILE_TITLE = "Implementation & survivorship (FHIR R4 + standards)"
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
STANDARDS_HALF_TABLE_H = TABLE_STANDARD_H  # alias: half-width pair on Standards page
STANDARDS_ADT_TABLE_H = TABLE_COMPACT_H
STANDARDS_ADT_CALLOUT_H = 64


def concept_profile_layout() -> dict[str, int]:
    """Vertical layout for Concept Profile (1920x1080) - keeps tables above the footer band."""
    content_bottom = PROFILE_PAGE_H - CONCEPT_FOOTER_H - 12
    slicer_y = CONCEPT_HEADER_H + 12
    callout_y = slicer_y + SLICER_H_PROFILE + 8
    cards_y = callout_y + CONCEPT_CALLOUT_H + 12
    tables_y = cards_y + CONCEPT_CARD_H + 20
    biz_h = 268
    dict_y = tables_y + biz_h + 12
    dict_h = content_bottom - dict_y
    card_w = (CONTENT_W - CONCEPT_CARD_GAP * (CONCEPT_PROFILE_CARD_COUNT - 1)) // CONCEPT_PROFILE_CARD_COUNT
    return {
        "header_h": CONCEPT_HEADER_H,
        "footer_h": CONCEPT_FOOTER_H,
        "footer_y": PROFILE_PAGE_H - CONCEPT_FOOTER_H,
        "slicer_y": slicer_y,
        "callout_y": callout_y,
        "callout_h": CONCEPT_CALLOUT_H,
        "cards_y": cards_y,
        "card_h": CONCEPT_CARD_H,
        "card_w": card_w,
        "tables_y": tables_y,
        "biz_h": biz_h,
        "dict_y": dict_y,
        "dict_h": dict_h,
        "source_h": content_bottom - tables_y,
        "content_bottom": content_bottom,
    }


def standards_page_y_positions(*, page_h: int = STANDARDS_PAGE_H) -> dict[str, int]:
    """Vertical layout for Standards & Contexts (1920x1200) - bottom-up with overlap check."""
    content_bottom = page_h - CONCEPT_FOOTER_H - 12
    layer_y = STANDARDS_HEADER_H + 8
    slicer_y = layer_y + STANDARDS_LAYER_H + STANDARDS_TABLE_GAP
    fhir_y = slicer_y + SLICER_H_STANDARDS + 16
    fhir_h = FHIR_STANDARDS_TABLE_H
    codes_y = fhir_y + fhir_h + STANDARDS_TABLE_GAP
    adt_h = STANDARDS_ADT_TABLE_H
    adt_callout_h = STANDARDS_ADT_CALLOUT_H
    adt_y = content_bottom - adt_h
    adt_callout_y = adt_y - adt_callout_h - 4
    codes_h = adt_callout_y - codes_y - STANDARDS_TABLE_GAP
    if codes_h < TABLE_STANDARD_H:
        raise ValueError(
            f"Standards page layout: codes_h={codes_h}px < TABLE_STANDARD_H={TABLE_STANDARD_H}. "
            f"Increase STANDARDS_PAGE_H or shrink bands above the codes row."
        )
    codes_end = codes_y + codes_h
    callout_end = codes_end + STANDARDS_TABLE_GAP + adt_callout_h
    if callout_end + 4 > adt_y:
        raise ValueError(
            f"Standards page layout overlap: codes/callout end at {callout_end + 4}px "
            f"but ADT row starts at {adt_y}px."
        )
    return {
        "page_h": page_h,
        "layer_y": layer_y,
        "layer_h": STANDARDS_LAYER_H,
        "slicer_y": slicer_y,
        "fhir_y": fhir_y,
        "fhir_h": fhir_h,
        "codes_y": codes_y,
        "codes_h": codes_h,
        "adt_callout_y": adt_callout_y,
        "adt_callout_h": adt_callout_h,
        "adt_y": adt_y,
        "adt_h": adt_h,
        "footer_y": page_h - CONCEPT_FOOTER_H,
        "content_bottom": content_bottom,
    }
