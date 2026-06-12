"""Shared PBIP layout constants - used by enhance_pbip_report.py and patch_pbip_readability.py."""

from __future__ import annotations

PAGE_W = 1920
PAGE_MARGIN = 32
CONTENT_W = PAGE_W - (PAGE_MARGIN * 2)  # 1856

# ~50% of full-width slicer; aligns with half-width tables on Standards & Contexts.
SLICER_W = 920
SLICER_H_PROFILE = 120
SLICER_H_STANDARDS = 108

# Standards page: same 1080 canvas as other tabs so content fits above PBI's bottom tab bar.
STANDARDS_PAGE_H = 1080

# Table height tiers (visible-row budget at 12pt + 8px row padding; ~32px per row, ~68px chrome).
TABLE_STANDARD_H = 300  # ~8-10 rows - value sets, crosswalk, source lists
TABLE_COMPACT_H = 160  # ~4-5 rows - ADT/CCDA per concept

# Standards page: FHIR terminology table (survivorship stays on Concept Profile only).
FHIR_STANDARDS_TABLE_H = 175
FHIR_STANDARDS_COLUMNS = [
    "fhir_r4_path",
    "fhir_profile",
]
FHIR_STANDARDS_SUBTITLE = "HOW in FHIR (path, profile) - full notes in Guide Field guide"

GOVERNED_CODES_COLUMNS = [
    "code_system_oid",
    "code",
    "display",
    "member_type",
    "binding_strength",
]

CCDA_STANDARDS_COLUMNS = [
    "section_name",
    "entry_type",
    "xml_path",
    "mapping_status",
]

STANDARDS_PAGE_ID = "d4e5f6a7b8c901234567"
PAGE_CONCEPT_PROFILE_ID = "abc963c80ac5ed2deeb4"
PAGE_GOVERNANCE_ID = "c8f1a2b3d4e5f6071829"

SLICER_TITLE = "Concept - pick semantic_id (e.g. Patient.race)"
SLICER_SUBTITLE = None
PILOT_SLICER_TITLE = "Demographics pilot only - yes = five Approved concepts"
PILOT_SLICER_SUBTITLE = None
PAGE_START_HERE_ID = "e1f2a3b4c5d607182934"
PAGE_FIELD_GUIDE_ID = "f7a8b9c0d1e2f304152637"
WALKTHROUGH_PAGE_ID = "a9b8c7d6e5f403120918"
# Stable page id; legacy alias for scripts that still import DEMO_PAGE_ID.
DEMO_PAGE_ID = WALKTHROUGH_PAGE_ID
DEFAULT_LANDING_PAGE_ID = PAGE_START_HERE_ID
DEMO_LANDING_PAGE_ID = DEFAULT_LANDING_PAGE_ID

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
    {PAGE_START_HERE_ID, WALKTHROUGH_PAGE_ID, PAGE_STANDARDS_REF_ID, PAGE_FIELD_GUIDE_ID}
)

TAB_START_HERE = f"{GUIDE_TAB_PREFIX}Start here"
TAB_WALKTHROUGH = f"{GUIDE_TAB_PREFIX}Walkthrough"
TAB_DEMO = TAB_WALKTHROUGH  # legacy alias
TAB_STANDARDS_REF = f"{GUIDE_TAB_PREFIX}National standards"
TAB_FIELD_GUIDE = f"{GUIDE_TAB_PREFIX}Field guide"
TAB_STANDARDS_CONTEXTS = "Standards & Contexts"
TAB_CONCEPT_PROFILE = "Concept Profile"
TAB_GOVERNANCE_OVERVIEW = "Governance Overview"

# Left-to-right tab order: orient → tour → lookup → explore by concept → steward docs → portfolio.
PAGE_TAB_ORDER: tuple[str, ...] = (
    PAGE_START_HERE_ID,
    WALKTHROUGH_PAGE_ID,
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
PAGE_HEADER_H = 96
# Title box must fit 26pt Semibold line (~40px); 44px caused PBI textbox scrollbars.
PAGE_HEADER_TITLE_Y = 28
PAGE_HEADER_TITLE_H = 56
PAGE_HEADER_TITLE_SIZE = "26pt"

CONCEPT_HEADER_H = PAGE_HEADER_H
CONCEPT_FOOTER_H = 52
CONCEPT_CALLOUT_H = 72
CONCEPT_CARD_H = 148
CONCEPT_CARD_GAP = 16
CONCEPT_PROFILE_CARD_COUNT = 5
ADT_CALLOUT_TEXT = (
    "ADT = hospital event messages. field_id is the HL7 location (e.g. PID-10 for race). "
    "hl7_ce_encoding = code^text when both components are mapped (race, ethnicity)."
)
CONCEPT_PROFILE_CALLOUT = (
    "Empty fields = not yet curated (filter demographics pilot on Standards). "
    "Survivorship on this tab only; codes and ADT/CCDA on Standards & Contexts."
)
FHIR_STANDARDS_TITLE = "FHIR R4 + US Core (Dictionary)"

# Standards page: terminology tables (side by side).
GOVERNED_CODES_TITLE = "Governed value set codes"
GOVERNED_CODES_SUBTITLE = "member_type = code role (omb_rollup, detailed, language_tag, nullflavor, exclude)"
SOURCE_XW_TITLE = "Source value crosswalk"
SOURCE_XW_SUBTITLE = "How each partner's values map to those codes"

STANDARDS_LAYER_TEXT = (
    "WHAT = USCDI | HOW = FHIR R4 | WHICH = governed codes (left) + crosswalk (right) | "
    "WHERE = ADT + C-CDA below | member_type = code role in set | "
    "Authority definitions: Guide National standards tab"
)
# Page header band: tab title only (hints live in yellow banners / callouts below).
STANDARDS_PAGE_TITLE = TAB_STANDARDS_CONTEXTS
STANDARDS_PAGE_HEADER = STANDARDS_PAGE_TITLE  # alias

# Concept Profile tables.
CONCEPT_GOV_TITLE = "Business & USCDI governance"
CONCEPT_GOV_SUBTITLE = "WHAT we govern (catalog): USCDI, steward, approval"
CONCEPT_DICT_TITLE = "Implementation & survivorship (FHIR R4 + standards)"
CONCEPT_DICT_SUBTITLE = "HOW we implement and resolve conflicts (dictionary + survivorship)"
CONCEPT_SOURCE_TITLE = "Source availability"
CONCEPT_SOURCE_SUBTITLE = "Which partners can supply this concept"
CONCEPT_PAGE_TITLE = TAB_CONCEPT_PROFILE
CONCEPT_PROFILE_HEADER = CONCEPT_PAGE_TITLE  # alias
DICT_PROFILE_TITLE = CONCEPT_DICT_TITLE

# Message-context tables (Standards page).
ADT_CONTEXT_TITLE = "HL7 v2 ADT context"
ADT_CONTEXT_SUBTITLE = "WHERE in ADT; hl7_ce_encoding = code^text when mapped"
CCDA_TITLE = "C-CDA / CCD context"
CCDA_SUBTITLE = "WHERE in clinical documents - segment/notes in Guide Field guide"

# Governance Overview.
GOVERNANCE_PAGE_TITLE = TAB_GOVERNANCE_OVERVIEW
GOVERNANCE_HEADER = GOVERNANCE_PAGE_TITLE  # alias
GOVERNANCE_PORTFOLIO_CALLOUT = (
    "46 governed concepts, 5 Approved pilots, 41 need steward review (demographics POC)"
)
GOVERNANCE_PORTFOLIO_CALLOUT_H = 44
GOVERNANCE_PORTFOLIO_SUBTITLE = GOVERNANCE_PORTFOLIO_CALLOUT  # alias
GOVERNANCE_TABLE_TITLE = "All governed concepts"
GOVERNANCE_TABLE_SUBTITLE = "Searchable portfolio - most rows are not yet fully curated"

# Field guide.
FIELD_GUIDE_PAGE_TITLE = TAB_FIELD_GUIDE
FIELD_GUIDE_HEADER = FIELD_GUIDE_PAGE_TITLE  # alias
FIELD_GUIDE_SUBTITLE = FIELD_GUIDE_PAGE_TITLE  # alias
ADT_CONTEXT_COLUMNS = [
    "field_id",
    "field_name",
    "hl7_ce_encoding",
    "mapping_status",
]

STANDARDS_HEADER_H = PAGE_HEADER_H
STANDARDS_LAYER_H = 88
STANDARDS_TABLE_GAP = 12
STANDARDS_VISUAL_GAP = 28  # extra space between stacked table visuals (avoids title-band overlap)
STANDARDS_HALF_TABLE_H = TABLE_STANDARD_H  # alias: half-width pair on Standards page
STANDARDS_ADT_TABLE_H = TABLE_COMPACT_H
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
    """Vertical layout for Standards & Contexts (1920x1080) - bottom-up with overlap check."""
    content_bottom = page_h - CONCEPT_FOOTER_H - 12
    layer_y = STANDARDS_HEADER_H + 8
    slicer_y = layer_y + STANDARDS_LAYER_H + STANDARDS_TABLE_GAP
    fhir_y = slicer_y + SLICER_H_STANDARDS + 12
    fhir_h = FHIR_STANDARDS_TABLE_H
    codes_y = fhir_y + fhir_h + STANDARDS_VISUAL_GAP
    adt_h = STANDARDS_ADT_TABLE_H
    adt_y = content_bottom - adt_h
    codes_h = adt_y - codes_y - STANDARDS_TABLE_GAP
    if codes_h < TABLE_STANDARD_H:
        raise ValueError(
            f"Standards page layout: codes_h={codes_h}px < TABLE_STANDARD_H={TABLE_STANDARD_H}. "
            f"Shrink bands above the codes row or lower TABLE_STANDARD_H."
        )
    codes_end = codes_y + codes_h
    if codes_end + STANDARDS_TABLE_GAP > adt_y:
        raise ValueError(
            f"Standards page layout overlap: codes end at {codes_end}px "
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
        "adt_y": adt_y,
        "adt_h": adt_h,
        "footer_y": page_h - CONCEPT_FOOTER_H,
        "content_bottom": content_bottom,
    }
