"""Copy for PBIP Start here page - keep in sync with docs/sources-of-truth.md."""

PAGE_TITLE = "CHI Data Dictionary Catalog"
PAGE_SUBTITLE = "Governed catalog + dictionary aligned to US interoperability standards (SHIE / CHI)"

PURPOSE_LINES = [
    "This application is CHI's read surface for governed patient concepts (semantic_id). "
    "It shows what CHI stewards have approved, how each concept maps to USCDI and US Core, "
    "which terminology bindings apply, and where attributes appear in HL7 v2 ADT, C-CDA R2.1, and FHIR R4.",
    "",
    "Excel is the authoring surface; parquet is the published machine copy; "
    "Power BI is for discovery and review.",
]

SOURCES_LINES = [
    "National standards - USCDI (what), US Core + FHIR R4 (how), HL7 / LOINC / SNOMED / "
    "BCP 47 / CDCREC (codes). Authoritative externally; cited by URL and OID in this catalog.",
    "",
    "DAP (Innovaccer) - enterprise terminology and clinical value sets at scale. "
    "Referenced, not duplicated here (see TECH-SPEC).",
    "",
    "CHI steward workbook - governed metadata CHI signs: approval_status, survivorship, "
    "value set bindings, crosswalk rows. Published via import script + git.",
    "",
    "Operational feeds - CMT, county survivorship SQL, partner source strings. "
    "Mapped to standards in Source_Value_Crosswalk; they are inputs, not national truth.",
    "",
    "semantic_id - stable spine joining catalog, dictionary, terminology, crosswalk, and message context.",
]

HOW_TO_USE_LINES = [
    "1. Guide · Start here - purpose and sources of truth (this page).",
    "2. Guide · Demo walkthrough - 5-minute tour (default landing for demos).",
    "3. Guide · Field guide - column purpose, steward workflow, and curation gaps (slicers).",
    "4. Standards & Contexts - terminology, crosswalk, ADT/CCDA per semantic_id.",
    "5. Concept Profile - governance, FHIR R4 implementation, survivorship, source availability.",
    "6. Governance Overview - portfolio KPIs and full concept list.",
    "",
    "Tip: On Standards & Contexts, set Show concepts = yes and pick Patient.race or Patient.language.",
]

PILOT_CALLOUT = (
    "Demographics pilot (Approved): Patient.race, Patient.ethnicity, Patient.language, "
    "Patient.gender_id, Patient.birth_sex"
)

PUBLISH_LINES = [
    "Edit workbooks/chi-steward-workbook.xlsx",
    "-> python scripts/import_steward_workbook_to_parquet.py",
    "-> Refresh Power BI -> git commit",
    "",
    "Docs: docs/operational-runbook.md, docs/sources-of-truth.md",
]
