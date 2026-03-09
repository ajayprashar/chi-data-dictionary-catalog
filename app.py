#!/usr/bin/env python
"""
Streamlit viewer for the CHI master patient catalog & data dictionary.

- Reads two Parquet files: master_patient_catalog.parquet and master_patient_dictionary.parquet.
- Joins them on semantic_id.
- Provides search, filtering (including by FHIR resource and format scope), and a detail view.

Run from the project root:

    streamlit run app.py
"""

from __future__ import annotations

import glob
import html
import os
import re
from functools import lru_cache
from typing import List

import pandas as pd
import streamlit as st


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """Load and join catalog + dictionary into a single DataFrame."""
    cat_path = os.path.join(PROJECT_ROOT, "master_patient_catalog.parquet")
    dict_path = os.path.join(PROJECT_ROOT, "master_patient_dictionary.parquet")

    if not os.path.exists(cat_path) or not os.path.exists(dict_path):
        raise FileNotFoundError(
            "Expected master_patient_catalog.parquet and master_patient_dictionary.parquet in the project root. "
            "Run scripts/split_to_catalog_and_dictionary.py first."
        )

    # Use pandas for schema-tolerant merge (handles old Parquet without HIE columns)
    catalog = pd.read_parquet(cat_path)
    dictionary = pd.read_parquet(dict_path)

    # Basic sanity check: ensure catalog and dictionary agree on semantic_id coverage.
    # Inner joins will silently drop elements that do not exist in both tables.
    # Use dropna().tolist() to avoid relying on pandas Series directly in set().
    if "semantic_id" in catalog.columns:
        cat_ids = set(catalog["semantic_id"].dropna().tolist())
    else:
        cat_ids = set()
    if "semantic_id" in dictionary.columns:
        dict_ids = set(dictionary["semantic_id"].dropna().tolist())
    else:
        dict_ids = set()
    only_in_catalog = sorted(cat_ids - dict_ids)
    only_in_dictionary = sorted(dict_ids - cat_ids)
    # Attach mismatch info to the function for use in the Streamlit UI.
    load_data.join_mismatches = {
        "only_in_catalog": only_in_catalog,
        "only_in_dictionary": only_in_dictionary,
    }
    hie_catalog_cols = [
        "domain", "rollup_relationship", "is_rollup", "composite_group",
        "data_steward", "steward_contact", "approval_status", "schema_version", "last_modified_date",
        "identifier_type", "identifier_authority", "hipaa_category", "fhir_security_label", "consent_category"
    ]
    hie_dict_cols = [
        "calculation_grain", "historical_freeze", "recalc_window_months",
        "fhir_must_support", "fhir_profile", "fhir_cardinality",
        "identity_resolution_notes", "tie_breaker_rule", "conflict_detection_enabled",
        "manual_override_allowed", "de_identification_method"
    ]
    for col in hie_catalog_cols:
        if col not in catalog.columns:
            catalog[col] = ""
    for col in hie_dict_cols:
        if col not in dictionary.columns:
            dictionary[col] = ""
    df = catalog.merge(dictionary, on="semantic_id", how="inner")

    # Derive a FHIR resource name from fhir_r4_path (e.g. "Patient.name.given" -> "Patient")
    df["fhir_resource"] = df["fhir_r4_path"].fillna("").str.split(".", n=1).str[0]
    return df


@lru_cache(maxsize=1)
def load_message_catalogs() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """
    Load optional HL7 ADT and CCD/CCDA catalogs.

    These are small POC files that map master patient elements (semantic_id)
    into message-specific fields/paths.
    """
    adt_path = os.path.join(PROJECT_ROOT, "hl7_adt_catalog.parquet")
    ccda_path = os.path.join(PROJECT_ROOT, "ccda_catalog.parquet")

    adt_df = pd.read_parquet(adt_path) if os.path.exists(adt_path) else None
    ccda_df = pd.read_parquet(ccda_path) if os.path.exists(ccda_path) else None
    return adt_df, ccda_df


@lru_cache(maxsize=1)
def load_five_tables_for_review() -> tuple[
    pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None
]:
    """
    Load all ERD tables as separate DataFrames for the Documentation table preview.

    Returns (catalog_df, dictionary_df, adt_catalog_df, ccda_catalog_df, availability_df); each is None if file missing.
    """
    cat_path = os.path.join(PROJECT_ROOT, "master_patient_catalog.parquet")
    dict_path = os.path.join(PROJECT_ROOT, "master_patient_dictionary.parquet")
    adt_path = os.path.join(PROJECT_ROOT, "hl7_adt_catalog.parquet")
    ccda_path = os.path.join(PROJECT_ROOT, "ccda_catalog.parquet")
    avail_path = os.path.join(PROJECT_ROOT, "data_source_availability.parquet")

    catalog_df = pd.read_parquet(cat_path) if os.path.exists(cat_path) else None
    dictionary_df = pd.read_parquet(dict_path) if os.path.exists(dict_path) else None
    adt_df = pd.read_parquet(adt_path) if os.path.exists(adt_path) else None
    ccda_df = pd.read_parquet(ccda_path) if os.path.exists(ccda_path) else None
    avail_df = pd.read_parquet(avail_path) if os.path.exists(avail_path) else None
    return catalog_df, dictionary_df, adt_df, ccda_df, avail_df


def _discover_feed_profiles() -> List[tuple[str, pd.DataFrame | None, pd.DataFrame | None]]:
    """
    Discover all data source feed profiles in data/ by convention.

    Looks for data/*_feed_segments.csv; for each, derives source_id (e.g. cmt_feed_segments -> cmt)
    and loads the matching *_feed_event_types.csv if present.
    Returns list of (source_id, segments_df, events_df). segments_df/events_df may be None if file missing.
    """
    data_dir = os.path.join(PROJECT_ROOT, "data")
    if not os.path.isdir(data_dir):
        return []
    pattern = os.path.join(data_dir, "*_feed_segments.csv")
    out: List[tuple[str, pd.DataFrame | None, pd.DataFrame | None]] = []
    for path in sorted(glob.glob(pattern)):
        base = os.path.basename(path)
        # e.g. cmt_feed_segments.csv -> source_id = cmt
        source_id = base.replace("_feed_segments.csv", "")
        if not source_id:
            continue
        segments_df = pd.read_csv(path) if os.path.exists(path) else None
        events_path = os.path.join(data_dir, f"{source_id}_feed_event_types.csv")
        events_df = pd.read_csv(events_path) if os.path.exists(events_path) else None
        out.append((source_id, segments_df, events_df))
    return out


@lru_cache(maxsize=1)
def load_all_feed_profiles() -> tuple[tuple[str, pd.DataFrame | None, pd.DataFrame | None], ...]:
    """Load all discovered feed profiles (cached). Returns tuple of (source_id, segments_df, events_df)."""
    return tuple(_discover_feed_profiles())


def inject_theme() -> None:
    """Inject medical-app style theme: light, clinical neutrals with green accents and good label/value contrast."""
    css = """
    <style>
    /* Main content: soft grey background, dark readable text */
    html, body, [data-testid="stAppViewContainer"] {
        font-size: 0.95rem;
        background-color: #f3f4f6;  /* app backdrop */
        color: #111827;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    [data-testid="stAppViewContainer"] .block-container {
        padding-top: 1.0rem;
        padding-bottom: 0.5rem;
    }

    /* Sidebar: slightly darker than main for separation */
    [data-testid="stSidebar"] {
        background-color: #e5e7eb;
        color: #111827;
    }
    [data-testid="stSidebar"] label {
        color: #374151;
        font-weight: 500;
    }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stMultiSelect div[role="combobox"],
    [data-testid="stSidebar"] .stSelectbox > div {
        background-color: #ffffff;
        color: #111827;
        border: 1px solid #d1d5db;
    }
    [data-testid="stSidebar"] .stMultiSelect span,
    [data-testid="stSidebar"] .stSelectbox span {
        color: #111827;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #111827;
    }

    /* Primary accent: medical green (buttons, subheadings, links) */
    h1, h2, h3 {
        color: #111827;
        margin-bottom: 0.15rem;
        font-weight: 600;
    }
    /* Make the main app title compact (override Streamlit defaults) */
    .title-row h1 { font-size: 1.1rem; }
    h1 { font-size: 1.1rem; }
    h2 { font-size: 1.0rem; }
    h3 { font-size: 0.95rem; }
    h4, h5 {
        margin-top: 0.4rem;
        margin-bottom: 0.15rem;
        color: #047857;
    }
    [data-testid="stAppViewContainer"] a {
        color: #047857;
    }
    [data-testid="baseButton-primary"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        border-color: #059669 !important;
    }
    [data-testid="baseButton-primary"]:hover {
        background-color: #047857 !important;
        border-color: #047857 !important;
    }

    /* Alerts / important: red */
    [data-testid="stAlert"] [data-baseweb="notification"] {
        border-left-color: #c62828;
    }
    .stException .message { color: #b71c1c; }

    .field-row {
        display: flex;
        gap: 0.5rem;
        align-items: flex-start;
        margin-bottom: 0.2rem;
        width: 100%;
    }
    /* Keep one field per row so label colons and value boxes align consistently. */
    .field-label {
        width: 10rem;
        min-width: 10rem;
        font-weight: 600;
        white-space: nowrap;
        text-align: right;
        color: #4b5563;  /* secondary text */
    }
    .field-label::after {
        content: ":";
        margin-left: 0.15rem;
    }
    .field-value {
        flex: 1;
        background-color: #ffffff;
        padding: 0.2rem 0.55rem;
        border-radius: 4px;
        border: 1px solid #d1d5db;
        color: #111827;
    }
    .field-value-multiline {
        flex: 1;
        background-color: #ffffff;
        padding: 0.2rem 0.55rem;
        border-radius: 4px;
        border: 1px solid #d1d5db;
        color: #111827;
        white-space: pre-wrap;
        min-height: 3.2em;  /* ~3 lines */
        max-height: 6.4em;  /* ~6 lines */
        overflow-y: auto;
    }

    .header-caption {
        font-size: 0.8rem;
        font-weight: 400;
        color: #5f6368;
        margin-left: 0.5rem;
    }
    .title-row {
        display: flex;
        align-items: baseline;
        gap: 0.25rem;
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
    }

    .summary-box {
        margin-top: 0.4rem;
        padding: 0.4rem 0.6rem;
        border-radius: 4px;
        border: 1px solid #d1d5db;
        background-color: #ffffff;
        font-size: 0.9rem;
    }
    /* Tighter spacing around horizontal rules */
    hr {
        margin-top: 0.6rem;
        margin-bottom: 0.6rem;
    }
    /* Standards-domain background tints (subtle, for visual anchoring) */
    .section-block {
        padding: 0.5rem 0.6rem;
        border-radius: 4px;
        margin-bottom: 0.4rem;
    }
    .section-catalog { background-color: #f9fafb; }
    .section-fhir { background-color: #ecfdf5; }
    .section-survivorship { background-color: #fffbeb; }
    .section-quality { background-color: #f5f3ff; }
    .section-adt { background-color: #eff6ff; }
    .section-ccda { background-color: #f0fdf4; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def format_value(value: object) -> str:
    """Return a user-friendly string for a field value."""
    if value is None:
        return "—"
    text = str(value).strip()
    return text if text else "—"


def render_field(label: str, value: object) -> None:
    """Render a single label/value pair with aligned layout and subtle value background."""
    multiline_labels = {
        "Description",
        "HIE Survivorship Logic",
        "Innovaccer Survivorship Logic",
        "Data Source Rank Reference",
        "Quality & Governance Notes",
    }
    value_class = "field-value-multiline" if label in multiline_labels else "field-value"
    st.markdown(
        f"""
        <div class="field-row">
          <div class="field-label">{label}</div>
          <div class="{value_class}">{format_value(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_section_block(
    section_class: str,
    title: str,
    caption: str,
    fields: list[tuple[str, object]],
) -> None:
    """Render a full section (title + fields) in one colored block."""
    multiline_labels = {
        "Description",
        "HIE Survivorship Logic",
        "Innovaccer Survivorship Logic",
        "Data Source Rank Reference",
        "Quality & Governance Notes",
    }
    rows = []
    for label, value in fields:
        val_class = "field-value-multiline" if label in multiline_labels else "field-value"
        rows.append(
            f'<div class="field-row"><div class="field-label">{label}</div>'
            f'<div class="{val_class}">{html.escape(format_value(value))}</div></div>'
        )
    html_content = f"""
    <div class="section-block {section_class}">
      <div class="title-row"><h4>{html.escape(title)}</h4><span class="header-caption">{html.escape(caption)}</span></div>
      {"".join(rows)}
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply search and filter controls from the sidebar."""
    st.sidebar.header("Search & Filters")

    # Global search across common fields
    search = st.sidebar.text_input(
        "Quick search",
        placeholder="semantic_id, element name, description, FHIR path…",
    ).strip()

    # Build filter options from data
    def options(col: str) -> List[str]:
        vals = sorted(v for v in df[col].dropna().unique() if str(v).strip() != "")
        return vals

    fhir_resources = st.sidebar.multiselect("FHIR resource", options("fhir_resource"))
    classifications = st.sidebar.multiselect("Classification", options("classification"))
    domains = st.sidebar.multiselect("Domain", options("domain")) if "domain" in df.columns else []
    rulesets = st.sidebar.multiselect("Ruleset category", options("ruleset_category"))
    privacy_flags = st.sidebar.multiselect("Privacy / security", options("privacy_security"))

    filtered = df.copy()

    # Text search (case-insensitive) across key fields
    if search:
        mask = (
            filtered["semantic_id"].str.contains(search, case=False, na=False)
            | filtered["uscdi_element"].str.contains(search, case=False, na=False)
            | filtered["uscdi_description"].str.contains(search, case=False, na=False)
            | filtered["fhir_r4_path"].str.contains(search, case=False, na=False)
        )
        if "domain" in filtered.columns:
            mask = mask | filtered["domain"].str.contains(search, case=False, na=False)
        if "composite_group" in filtered.columns:
            mask = mask | filtered["composite_group"].str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    if fhir_resources:
        filtered = filtered[filtered["fhir_resource"].isin(fhir_resources)]
    if classifications:
        filtered = filtered[filtered["classification"].isin(classifications)]
    if domains and "domain" in filtered.columns:
        filtered = filtered[filtered["domain"].isin(domains)]
    if rulesets:
        filtered = filtered[filtered["ruleset_category"].isin(rulesets)]
    if privacy_flags:
        filtered = filtered[filtered["privacy_security"].isin(privacy_flags)]

    return filtered


def render_detail(
    df: pd.DataFrame,
    selected_id: str,
    adt_df: pd.DataFrame | None = None,
    ccda_df: pd.DataFrame | None = None,
) -> None:
    """Render the detail view for a single semantic_id."""
    record = df[df["semantic_id"] == selected_id].iloc[0]

    # Single, vertically stacked layout (no tabs) to minimize clicks and maximize visible context.
    # Each section uses a subtle background tint to distinguish standards domains.
    _render_section_block(
        "section-catalog",
        "Catalog",
        "from master_patient_catalog.parquet · What elements exist and how they're grouped.",
        [
            # Order is chosen so that USCDI fields appear in the right-hand column
            # (positions 2, 4, and 6) in the two-column layout.
            ("Semantic ID", record.semantic_id),  # left, row 1
            ("USCDI Data Class", getattr(record, "uscdi_data_class", "")),  # right, row 1
            ("Classification", record.classification),  # left, row 2
            ("USCDI Data Element", getattr(record, "uscdi_data_element", "")),  # right, row 2
            ("Domain", getattr(record, "domain", "")),  # left, row 3
            ("USCDI Element", record.uscdi_element),  # right, row 3
            ("Description", record.uscdi_description),
            ("Ruleset Category", record.ruleset_category),
            ("Privacy/Security", record.privacy_security),
            ("HIPAA Category", getattr(record, "hipaa_category", "")),
            ("FHIR Security Label", getattr(record, "fhir_security_label", "")),
            ("Consent Category", getattr(record, "consent_category", "")),
            ("Rollup Relationship", getattr(record, "rollup_relationship", "")),
            ("Is Rollup", getattr(record, "is_rollup", "")),
            ("Composite Group", getattr(record, "composite_group", "")),
            ("Identifier Type", getattr(record, "identifier_type", "")),
            ("Identifier Authority", getattr(record, "identifier_authority", "")),
            ("Data Steward", getattr(record, "data_steward", "")),
            ("Steward Contact", getattr(record, "steward_contact", "")),
            ("Approval Status", getattr(record, "approval_status", "")),
            ("Schema Version", getattr(record, "schema_version", "")),
            ("Last Modified Date", getattr(record, "last_modified_date", "")),
        ],
    )

    _render_section_block(
        "section-fhir",
        "Dictionary – FHIR Mapping",
        "from master_patient_dictionary.parquet · Canonical FHIR R4 path & type for this element",
        [
            ("Resource", record.fhir_resource),
            ("FHIR Path", record.fhir_r4_path),
            ("FHIR Data Type", record.fhir_data_type),
            ("FHIR Profile", getattr(record, "fhir_profile", "")),
            ("FHIR Cardinality", getattr(record, "fhir_cardinality", "")),
            ("FHIR Must Support", getattr(record, "fhir_must_support", "")),
        ],
    )

    _render_section_block(
        "section-survivorship",
        "Dictionary – Survivorship & Sources",
        "Business rules and source logic for this element.",
        [
            ("HIE Survivorship Logic", record.hie_survivorship_logic),
            ("Tie Breaker Rule", getattr(record, "tie_breaker_rule", "")),
            ("Conflict Detection Enabled", getattr(record, "conflict_detection_enabled", "")),
            ("Manual Override Allowed", getattr(record, "manual_override_allowed", "")),
            ("Innovaccer Survivorship Logic", record.innovaccer_survivorship_logic),
            ("Data Source Rank Reference", record.data_source_rank_reference),
            ("Identity Resolution Notes", getattr(record, "identity_resolution_notes", "")),
            ("Coverage (# PersonIDs)", record.coverage_personids),
            ("Granularity Level", record.granularity_level),
            ("Calculation Grain", getattr(record, "calculation_grain", "")),
            ("Historical Freeze", getattr(record, "historical_freeze", "")),
            ("Recalc Window (Months)", getattr(record, "recalc_window_months", "")),
        ],
    )

    _render_section_block(
        "section-quality",
        "Dictionary – Quality & Governance",
        "",
        [
            ("Quality & Governance Notes", record.data_quality_notes),
            ("De-identification Method", getattr(record, "de_identification_method", "")),
        ],
    )

    # Optional HL7 ADT / CCD mappings for this element, shown side by side
    adt_rows = None
    if adt_df is not None:
        adt_rows = adt_df[adt_df["semantic_id"] == selected_id]

    ccda_rows = None
    if ccda_df is not None:
        ccda_rows = ccda_df[ccda_df["semantic_id"] == selected_id]

    if (adt_rows is not None and not adt_rows.empty) or (
        ccda_rows is not None and not ccda_rows.empty
    ):
        st.markdown("---")
        st.markdown(
            """
            <div class="title-row">
              <h4>Message-format mappings</h4>
              <span class="header-caption">Where this element lands in HL7 ADT and CCD/CCDA messages.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if adt_rows is not None and not adt_rows.empty:
            st.markdown('<div class="section-block section-adt"><strong>HL7 ADT</strong> (from <code>hl7_adt_catalog.parquet</code>)</div>', unsafe_allow_html=True)
            st.dataframe(
                adt_rows[
                    [
                        "semantic_id",
                        "message_type",
                        "segment_id",
                        "field_id",
                        "field_name",
                        "notes",
                    ]
                ].reset_index(drop=True),
                hide_index=True,
                width="stretch",
                column_config={
                    "semantic_id": st.column_config.TextColumn("Semantic ID", width="medium"),
                    "notes": st.column_config.TextColumn("Notes", width="large"),
                },
            )

        if ccda_rows is not None and not ccda_rows.empty:
            st.markdown('<div class="section-block section-ccda"><strong>CCD / CCDA</strong> (from <code>ccda_catalog.parquet</code>)</div>', unsafe_allow_html=True)
            st.dataframe(
                ccda_rows[
                    [
                        "semantic_id",
                        "section_name",
                        "entry_type",
                        "xml_path",
                        "notes",
                    ]
                ].reset_index(drop=True),
                hide_index=True,
                width="stretch",
                column_config={
                    "semantic_id": st.column_config.TextColumn("Semantic ID", width="medium"),
                    "section_name": st.column_config.TextColumn("Section", width="small"),
                    "entry_type": st.column_config.TextColumn("Entry type", width="small"),
                    "xml_path": st.column_config.TextColumn("XML path", width="medium"),
                    "notes": st.column_config.TextColumn("Notes", width="large"),
                },
            )


# Current POC ERD (aligned with master_patient_*.parquet, hl7_adt_catalog.parquet, ccda_catalog.parquet)
# FHIR: canonical path/type in MASTER_PATIENT_DICTIONARY; per-format path in ADT/CCDA catalogs. No FHIR resource instance data stored here.
#
# Mermaid erDiagram syntax (keep in sync with hl7_ccd_fhir_consideration.md):
# - Attribute keys: only PK, FK, UK are valid. For an attribute that is both PK and FK use "PK, FK"
#   (comma-separated). Writing "PK_FK" causes "Syntax error in graph" in Mermaid 9.x.
# - Relationship cardinality: use single braces, e.g. ||--o{ (one-to-many). Double braces ||--o{{
#   are invalid and cause syntax errors.
_ERD_MERMAID = """
erDiagram
    MASTER_PATIENT_CATALOG {
        string semantic_id PK
        string uscdi_element
        string uscdi_description
        string classification
        string domain
        string ruleset_category
        string privacy_security
        string rollup_relationship
        string is_rollup
        string composite_group
        string data_steward
        string steward_contact
        string approval_status
        string schema_version
        string last_modified_date
        string identifier_type
        string identifier_authority
        string hipaa_category
        string fhir_security_label
        string consent_category
        string fhir_resource   "derived from fhir_r4_path"
    }

    MASTER_PATIENT_DICTIONARY {
        string semantic_id PK, FK
        string hie_survivorship_logic
        string data_source_rank_reference
        string coverage_personids
        string granularity_level
        string calculation_grain
        string historical_freeze
        string recalc_window_months
        string fhir_must_support
        string fhir_profile
        string fhir_cardinality
        string identity_resolution_notes
        string tie_breaker_rule
        string conflict_detection_enabled
        string manual_override_allowed
        string de_identification_method
        string innovaccer_survivorship_logic
        string data_quality_notes
        string fhir_r4_path
        string fhir_data_type
    }

    HL7_ADT_CATALOG {
        string message_format   "ADT"
        string message_type
        string segment_id
        string field_id
        string field_name
        string data_type
        string optionality
        string cardinality
        string semantic_id FK
        string fhir_r4_path
        string notes
    }

    CCDA_CATALOG {
        string message_format   "CCD"
        string section_name
        string entry_type
        string xml_path
        string semantic_id FK
        string fhir_r4_path
        string notes
    }

    MASTER_PATIENT_CATALOG ||--|| MASTER_PATIENT_DICTIONARY : "has dictionary row"
    MASTER_PATIENT_CATALOG ||--o{ HL7_ADT_CATALOG         : "maps to ADT fields"
    MASTER_PATIENT_CATALOG ||--o{ CCDA_CATALOG            : "maps to CCD/CCDA paths"
"""

# Extended ERD for FUTURE / POST POC: value-set/code-system tables and crosswalks (strategically left out of POC)
# See hl7_ccd_fhir_consideration.md "Value set / code system support (future extension)" and "Key Relationships"
_ERD_FUTURE_MERMAID = """
erDiagram
    MASTER_PATIENT_CATALOG {
        string semantic_id PK
        string uscdi_element
        string uscdi_description
        string classification
        string ruleset_category
        string privacy_security
        string fhir_resource
    }

    MASTER_PATIENT_DICTIONARY {
        string semantic_id PK, FK
        string hie_survivorship_logic
        string data_source_rank_reference
        string fhir_r4_path
        string fhir_data_type
    }

    HL7_ADT_CATALOG {
        string segment_id
        string field_id
        string semantic_id FK
        string fhir_r4_path
    }

    CCDA_CATALOG {
        string section_name
        string entry_type
        string xml_path
        string semantic_id FK
        string fhir_r4_path
    }

    FHIR_CATALOG {
        string catalog_id PK
        string resource_type
        string element_path
        string master_attribute_mapping FK
        string profile_url
        string cardinality
    }

    INTEROPERABILITY_CROSSWALK {
        string crosswalk_id PK
        string partner_id
        string message_format
        string l3_attribute FK
        string target_field
        string transformation_rule
        string value_mapping
        string effective_date
    }

    VALUE_SET_DEFINITION {
        string value_set_id PK
        string name
        string description
        string code_system
        string version
    }

    VALUE_SET_MEMBER {
        string value_set_id FK
        string code
        string display
        string definition
        string inactive_flag
    }

    SEMANTIC_ID_VALUE_SET {
        string semantic_id FK
        string value_set_id FK
        string binding_strength
        string binding_notes
    }

    MASTER_PATIENT_CATALOG ||--|| MASTER_PATIENT_DICTIONARY : "has dictionary row"
    MASTER_PATIENT_CATALOG ||--o{ HL7_ADT_CATALOG         : "maps to ADT"
    MASTER_PATIENT_CATALOG ||--o{ CCDA_CATALOG            : "maps to CCD/CCDA"
    MASTER_PATIENT_CATALOG ||--o{ FHIR_CATALOG            : "maps to FHIR"
    MASTER_PATIENT_CATALOG ||--o{ SEMANTIC_ID_VALUE_SET   : "bound to value sets"
    VALUE_SET_DEFINITION ||--o{ VALUE_SET_MEMBER         : "contains codes"
    VALUE_SET_DEFINITION ||--o{ SEMANTIC_ID_VALUE_SET   : "bound to elements"
    HL7_ADT_CATALOG ||--o{ INTEROPERABILITY_CROSSWALK    : "uses crosswalk"
    CCDA_CATALOG ||--o{ INTEROPERABILITY_CROSSWALK       : "uses crosswalk"
    FHIR_CATALOG ||--o{ INTEROPERABILITY_CROSSWALK       : "uses crosswalk"
"""


def _render_tech_spec(st_module: "st", content: str) -> None:
    """
    Render TECH-SPEC markdown, with ```mermaid blocks rendered as diagrams instead of code.
    """
    parts = re.split(r"```mermaid\s*\n(.*?)```", content, flags=re.DOTALL)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                st_module.markdown(part)
        else:
            _render_mermaid(st_module, part, height=900, scrolling=False)


def _render_mermaid(st_module: "st", mermaid_src: str, height: int = 450, scrolling: bool = True) -> None:
    """Render arbitrary Mermaid diagram in-browser via mermaid.js. Uses same config as _render_erd."""
    src = mermaid_src.strip()
    # Prevent </script> in mermaid from closing the script tag
    safe_src = src.replace("</", "<\\/")
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js?v=9"></script>
  <style>body {{ margin: 0; font-family: sans-serif; }} .mermaid {{ margin: 0.5rem 0; }}</style>
</head>
<body>
  <div class="mermaid">{safe_src}</div>
  <script>
    mermaid.initialize({{ startOnLoad: true, theme: "neutral" }});
  </script>
</body>
</html>
"""
    try:
        st_module.components.v1.html(html_content, height=height, scrolling=scrolling)
    except Exception:
        st_module.code(src, language="mermaid")


def _render_erd(streamlit_module: "st") -> None:
    """Render the POC ERD in-browser with Mermaid 9 (single-brace diagram; no mermaid.ink)."""
    mermaid_src = _ERD_MERMAID.strip()
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js?v=9"></script>
  <style>body {{ margin: 0; font-family: sans-serif; }} .mermaid {{ margin: 0.5rem 0; }}</style>
</head>
<body>
  <div class="mermaid">{mermaid_src}</div>
  <script>
    mermaid.initialize({{ startOnLoad: true, theme: "neutral" }});
  </script>
</body>
</html>
"""
    try:
        streamlit_module.components.v1.html(html_content, height=600, scrolling=True)
    except Exception:
        streamlit_module.code(mermaid_src, language="mermaid")
    with streamlit_module.expander("Mermaid source (copy to Mermaid Live to edit)", expanded=False):
        streamlit_module.code(mermaid_src, language="mermaid")
    streamlit_module.caption(
        "Mermaid source: **hl7_ccd_fhir_consideration.md** (Current CHI Metadata Viewer ERD). Copy to [Mermaid Live](https://mermaid.live) to edit. "
        "**FHIR:** Path and type are stored in **MASTER_PATIENT_DICTIONARY** (canonical) and in **HL7_ADT_CATALOG** / **CCDA_CATALOG** (per-format); this POC does not store FHIR resource instance data (that lives in FHIR servers/APIs)."
    )


def _render_erd_future(streamlit_module: "st") -> None:
    """Render the FUTURE / POST POC ERD (value-set tables, FHIR catalog, crosswalks)."""
    mermaid_src = _ERD_FUTURE_MERMAID.strip()
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js?v=9"></script>
  <style>body {{ margin: 0; font-family: sans-serif; }} .mermaid {{ margin: 0.5rem 0; }}</style>
</head>
<body>
  <div class="mermaid">{mermaid_src}</div>
  <script>
    mermaid.initialize({{ startOnLoad: true, theme: "neutral" }});
  </script>
</body>
</html>
"""
    try:
        streamlit_module.components.v1.html(html_content, height=700, scrolling=True)
    except Exception:
        streamlit_module.code(mermaid_src, language="mermaid")
    with streamlit_module.expander("Mermaid source (copy to Mermaid Live to edit)", expanded=False):
        streamlit_module.code(mermaid_src, language="mermaid")
    streamlit_module.caption(
        "**FUTURE / POST POC:** Value-set/code-system tables (VALUE_SET_DEFINITION, VALUE_SET_MEMBER, SEMANTIC_ID_VALUE_SET), "
        "FHIR_CATALOG, and INTEROPERABILITY_CROSSWALK were strategically left out of the current POC. "
        "See **hl7_ccd_fhir_consideration.md** → \"Value set / code system support (future extension)\" and \"Key Relationships\"."
    )


def main() -> None:
    st.set_page_config(
        page_title="CHI Metadata Catalog Viewer",
        layout="wide",
    )
    inject_theme()

    st.markdown(
        """
        <div class="title-row">
          <h1>Community Health Insights (CHI) Metadata Catalog</h1>
          <span class="header-caption">
            Local viewer for the CHI data catalog and data dictionary, backed by Parquet files in this folder.
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = load_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    # Surface any join mismatches between catalog and dictionary so they are not silent.
    mismatches = getattr(load_data, "join_mismatches", None)
    if mismatches:
        only_in_cat = mismatches.get("only_in_catalog") or []
        only_in_dict = mismatches.get("only_in_dictionary") or []
        if only_in_cat or only_in_dict:
            st.warning(
                "Catalog and dictionary have mismatched semantic_id values. "
                f"{len(only_in_cat)} id(s) exist only in the catalog and "
                f"{len(only_in_dict)} id(s) exist only in the dictionary. "
                "Only elements present in both tables will appear in the viewer."
            )

    # Optional message catalogs (ADT / CCD)
    adt_df, ccda_df = load_message_catalogs()

    # Apply search/attribute filters from sidebar (no format gating; all formats always visible)
    filtered = apply_filters(df)

    if filtered.empty:
        st.info("No elements match the current criteria. Relax filters or clear the search term.")
        return

    # Aggregate summary for current filtered set (for Documentation expander)
    total = len(filtered)
    distinct_resources = (
        filtered["fhir_resource"].fillna("").str.strip().replace("", pd.NA).dropna().nunique()
    )
    has_fhir = filtered["fhir_r4_path"].fillna("").str.strip() != ""
    with_fhir = int(has_fhir.sum())
    missing_fhir = total - with_fhir
    has_surv = filtered["hie_survivorship_logic"].fillna("").str.strip() != ""
    missing_surv = total - int(has_surv.sum())
    pii_count = int(filtered["privacy_security"].fillna("").str.strip().ne("").sum())

    # Left: list of matching elements; Right: detail view
    col_list, col_detail = st.columns([1.0, 2.2])

    with col_list:
        st.caption(f"{len(filtered)} element(s) match the current filters.")
        list_cols = ["semantic_id", "uscdi_element", "fhir_resource"]
        list_view = filtered[list_cols].rename(
            columns={
                "semantic_id": "Semantic ID",
                "uscdi_element": "Element",
                "fhir_resource": "Resource",
            }
        )
        st.markdown(
            """
            <div class="title-row">
              <h4>Catalog elements</h4>
              <span class="header-caption">Catalog data elements from master_patient_catalog.parquet. Use the selection column on the left to choose an element.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        list_view = list_view.reset_index(drop=True)

        event = st.dataframe(
            list_view,
            hide_index=True,
            width="stretch",
            selection_mode="single-row",
            on_select="rerun",
        )

        # Data source feed profiles: dropdown to pick source, then show that source's tables
        feed_profiles = load_all_feed_profiles()
        if feed_profiles:
            st.markdown("---")
            # Only list sources that have at least one table
            valid_sources = [
                (sid, seg, evt) for sid, seg, evt in feed_profiles
                if (seg is not None and not seg.empty) or (evt is not None and not evt.empty)
            ]
            if valid_sources:
                options = [f"{sid.upper()} feed profile" for sid, _, _ in valid_sources]
                selected_label = st.selectbox(
                    "Feed profile",
                    options=options,
                    index=0,
                    label_visibility="collapsed",
                )
                idx = options.index(selected_label)
                source_id, segments_df, events_df = valid_sources[idx]
                st.markdown(
                    f"""
                    <div class="title-row">
                      <h4>Data source profiles</h4>
                      <span class="header-caption">Source: data/{source_id}_feed_*.csv</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if segments_df is not None and not segments_df.empty:
                    st.markdown("**Segments**")
                    segments_view = segments_df.copy()
                    if "segment_id" in segments_view.columns:
                        # Explicitly show the linkage key as the trailing column for readability.
                        segments_view["link_segment_id"] = segments_view["segment_id"]
                    st.dataframe(
                        segments_view,
                        hide_index=True,
                        width="stretch",
                        column_config={
                            "data_received": st.column_config.TextColumn("Received"),
                            "notes": st.column_config.TextColumn("Notes"),
                            "link_segment_id": st.column_config.TextColumn("Link Segment ID"),
                        },
                    )
                if events_df is not None and not events_df.empty:
                    st.markdown("**Event types**")
                    events_view = events_df.copy()
                    # Event types are event-level and do not map to a single segment_id.
                    events_view["link_segment_id"] = "event-level (no single segment)"
                    st.dataframe(
                        events_view,
                        hide_index=True,
                        width="stretch",
                        column_config={
                            "percentage_of_total": st.column_config.TextColumn("%"),
                            "link_segment_id": st.column_config.TextColumn("Link Segment ID"),
                        },
                    )

        # Determine selected semantic_id from the row selection; default to first row
        selected_rows = getattr(event, "selection", None)
        if selected_rows and selected_rows.rows:
            selected_idx = selected_rows.rows[0]
        else:
            selected_idx = 0

        selected_id = filtered["semantic_id"].iloc[selected_idx]

    with col_detail:
        st.markdown(
            """
            <div class="title-row">
              <h4>Element detail</h4>
              <span class="header-caption"></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_detail(filtered, selected_id, adt_df=adt_df, ccda_df=ccda_df)

    # Documentation at bottom of page: summary + doc link + ERD (collapsed by default)
    st.markdown("---")

    def _return_to_catalog():
        st.session_state.show_documentation = False

    if st.session_state.get("show_documentation", False):
        if st.button("↑ Return to catalog", key="doc_return_top", help="Minimize documentation and return to the main catalog view"):
            _return_to_catalog()
            st.rerun()
        st.markdown(
            "This section documents the current filtered subset and the Parquet tables that back this app."
        )
        st.markdown("#### Technical Specification")
        tech_spec_path = os.path.join(PROJECT_ROOT, "TECH-SPEC.md")
        if os.path.exists(tech_spec_path):
            try:
                with open(tech_spec_path, encoding="utf-8") as f:
                    tech_spec_md = f.read()
                _render_tech_spec(st, tech_spec_md)
            except Exception as e:
                st.caption(f"Could not load TECH-SPEC.md: {e}")
        else:
            st.caption("TECH-SPEC.md not found in project folder. See README.md for setup.")
        if st.button("↑ Return to catalog", key="doc_return_after_spec", help="Minimize documentation and return to the main catalog view"):
            _return_to_catalog()
            st.rerun()
        st.markdown("#### Summary for current filters")
        st.markdown(
            f"- {total} element(s) · {distinct_resources} FHIR resource type(s)  \n"
            f"- {with_fhir} with FHIR mapping, {missing_fhir} missing  \n"
            f"- {missing_surv} missing HIE survivorship logic  \n"
            f"- {pii_count} with privacy/security flags"
        )
        st.markdown("#### Data model (ERD)")
        _render_erd(st)
        if st.button("↑ Return to catalog", key="doc_return_after_erd", help="Minimize documentation and return to the main catalog view"):
            _return_to_catalog()
            st.rerun()
        st.markdown("#### Table preview (for review)")
        _row_options = [50, 500, 5_000_000_000_000]
        col_rows, _ = st.columns([1, 5])
        with col_rows:
            row_limit = st.selectbox(
                "Rows to show per table",
                options=_row_options,
                index=0,
                format_func=lambda x: "5 trillion" if x == 5_000_000_000_000 else str(x),
                key="doc_erd_table_rows",
            )
        catalog_df, dictionary_df, adt_df, ccda_df, avail_df = load_five_tables_for_review()
        if catalog_df is not None:
            st.markdown('<div class="section-block section-catalog"><strong>MASTER_PATIENT_CATALOG</strong> — Catalog data elements (what exists and how they\'re grouped).</div>', unsafe_allow_html=True)
            st.dataframe(catalog_df.head(row_limit), width="stretch")
        if dictionary_df is not None:
            st.markdown('<div class="section-block section-fhir"><strong>MASTER_PATIENT_DICTIONARY</strong> — Per-element rules, survivorship logic, and canonical FHIR path/type.</div>', unsafe_allow_html=True)
            st.dataframe(dictionary_df.head(row_limit), width="stretch")
        if adt_df is not None:
            st.markdown('<div class="section-block section-adt"><strong>HL7_ADT_CATALOG</strong> — Where each catalog element lands in HL7 ADT messages (segment/field, data type, optionality).</div>', unsafe_allow_html=True)
            st.dataframe(adt_df.head(row_limit), width="stretch")
            st.caption(
                "HL7 ADT columns: **data_type** is the HL7 v2 field data type (e.g., ST, NM, XPN). "
                "**optionality** usually follows HL7 v2 codes (R = required, O = optional, C = conditional, X = not used). "
                "**cardinality** expresses how many repetitions are allowed (e.g., 0..1, 0..*, 1..1, 1..*)."
            )
        if ccda_df is not None:
            st.markdown('<div class="section-block section-ccda"><strong>CCDA_CATALOG</strong> — Where each catalog element lands in CCD/CCDA XML (section, entry type, XML path).</div>', unsafe_allow_html=True)
            st.dataframe(ccda_df.head(row_limit), width="stretch")
        if avail_df is not None:
            st.markdown('<div class="section-block section-survivorship"><strong>DATA_SOURCE_AVAILABILITY</strong> — Links data sources (feed profiles) to catalog semantic IDs for source selection and quality tracking.</div>', unsafe_allow_html=True)
            st.dataframe(avail_df.head(row_limit), width="stretch")
            st.caption(
                "Source availability columns: **availability** (full/partial/none/unknown), "
                "**completeness_pct** (0.0-100.0), **timeliness_sla_hours**. "
                "POC uses placeholder 'unknown'; production would profile actual feed data."
            )
        if catalog_df is None and dictionary_df is None and adt_df is None and ccda_df is None and avail_df is None:
            st.caption("No Parquet tables found in project root.")
        st.markdown("---")
        st.markdown("#### FUTURE / POST POC")
        st.markdown(
            "Extended ERD including value-set/code-system tables, FHIR catalog, and interoperability crosswalks "
            "(strategically left out of the current POC)."
        )
        _render_erd_future(st)
        st.markdown("---")
        st.caption("Full project docs: **readme-prd.md**, **README.md**, **TECH-SPEC.md** (technical spec), and **docs/** in the project folder.")

        st.markdown("---")
        if st.button("↑ Return to catalog", key="doc_return_bottom", help="Minimize documentation and return to the main catalog view"):
            _return_to_catalog()
            st.rerun()
    else:
        if st.button(
            "**Documentation** — Summary, ERD, table preview, TECH-SPEC",
            key="doc_open",
            help="Open documentation section",
        ):
            st.session_state.show_documentation = True
            st.rerun()


if __name__ == "__main__":
    main()

