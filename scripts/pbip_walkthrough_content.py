"""Walkthrough copy - shared by Guide Walkthrough tab, WALKTHROUGH.txt, and release zip."""

from __future__ import annotations

PAGE_TITLE = "5-minute walkthrough"
PAGE_SUBTITLE = "Follow these steps in order - then explore on your own"
# Header band uses tab label only; subtitle is the first section panel title below.

INTRO_LINES = [
    "This report is CHI's read surface for governed patient concepts (semantic_id) across USCDI, "
    "US Core on FHIR R4, terminology, crosswalk, and HL7 v2 ADT / C-CDA R2.1 message placement.",
    "",
    "Start with the five Approved demographics pilot concepts - they are fully curated examples.",
]

STEPS_LINES = [
    "1. Standards & Contexts - choose Patient.race in the concept slicer (pilots filter = yes).",
    "   Middle tables: left = CHI-approved standard codes; right = how partner values map to those codes.",
    "   Then read FHIR R4 path above, and ADT (field_id + CE encoding) and C-CDA XPath below.",
    "2. Repeat with Patient.language - ADT field_id should show PID-15 (hl7_ce_encoding may be blank).",
    "3. Concept Profile - governance cards, survivorship, and source availability for the same concept.",
    "4. Guide · Field guide - filter by page or visual; steward_action shows which Excel sheet to edit.",
    "5. Governance Overview - portfolio KPIs and full concept list (most rows are not yet curated).",
]

PERSONA_LINES = [
    "Program / governance - Concept Profile + Governance Overview",
    "Interface / standards engineering - Standards & Contexts + Guide · Field guide",
    "New to CHI metadata - Guide · Start here, then this Walkthrough tab",
]

TIPS_LINES = [
    "Tip: On Standards & Contexts, set Demographics pilot only = yes, pick Patient.race - "
    "left table = allowed standard codes; right table = partner value -> standard code.",
    "Standards & Contexts = codes and message placement; Concept Profile = steward approval and survivorship.",
    "Empty Concept Profile fields = not yet stewarded in Excel (expected for 41 backlog concepts).",
    "ADT table: field_id is the HL7 position (e.g. PID-15). hl7_ce_encoding appears only for code+text CE pairs.",
    "Home -> Refresh from Report view after opening (do not use Transform data preview).",
]

PILOT_CALLOUT = (
    "Demographics pilots (Approved): Patient.race | Patient.ethnicity | Patient.language | "
    "Patient.gender_id | Patient.birth_sex"
)

PILOT_QUICK_REF_TITLE = "Pilot quick reference (ADT + FHIR R4)"

PILOT_QUICK_REF_LINES = [
    "Five Approved demographics pilots - open Standards & Contexts, set Demographics pilot only = yes, then pick any row below.",
    "",
    "Patient.race - ADT field_id PID-10 | hl7_ce_encoding PID-10.1^PID-10.2 | US Core race extension",
    "Patient.ethnicity - ADT PID-22 | hl7_ce_encoding PID-22.1^PID-22.2 | US Core ethnicity extension",
    "Patient.language - ADT PID-15 | hl7_ce_encoding blank (single component, not a CE pair)",
    "Patient.birth_sex - ADT PID-8 | US Core birthSex extension",
    "Patient.gender_id - FHIR R4 Observation LOINC 76691-5 | ADT row not yet in catalog",
    "",
    "hl7_ce_encoding appears only when both code and text components are mapped (race, ethnicity).",
]


def render_walkthrough_txt() -> str:
    sections = [
        "CHI Data Dictionary Catalog - 5-minute walkthrough",
        "=" * 55,
        "",
        *INTRO_LINES,
        "",
        "Steps",
        "-" * 5,
        *STEPS_LINES,
        "",
        "Who should use which tab",
        "-" * 28,
        *PERSONA_LINES,
        "",
        "Tips",
        "-" * 4,
        *TIPS_LINES,
        "",
        PILOT_QUICK_REF_TITLE,
        "-" * len(PILOT_QUICK_REF_TITLE),
        *PILOT_QUICK_REF_LINES,
        "",
        "Open: workbooks\\pbip\\chiddc.pbip",
        "Or double-click OPEN-CATALOG.bat in the extracted folder.",
    ]
    return "\n".join(sections) + "\n"
