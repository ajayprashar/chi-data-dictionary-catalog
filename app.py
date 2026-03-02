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
import os
from functools import lru_cache
from typing import List

import duckdb
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

    con = duckdb.connect()

    query = f"""
        SELECT
            c.semantic_id,
            c.uscdi_element,
            c.uscdi_description,
            c.classification,
            c.ruleset_category,
            c.privacy_security,
            d.hie_survivorship_logic,
            d.data_source_rank_reference,
            d.coverage_personids,
            d.granularity_level,
            d.innovaccer_survivorship_logic,
            d.data_quality_notes,
            d.fhir_r4_path,
            d.fhir_data_type
        FROM read_parquet('{cat_path}') AS c
        JOIN read_parquet('{dict_path}') AS d
          ON c.semantic_id = d.semantic_id
    """

    df = con.execute(query).df()

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
def load_four_tables_for_review() -> tuple[
    pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None, pd.DataFrame | None
]:
    """
    Load all four ERD tables as separate DataFrames for the Documentation table preview.

    Returns (catalog_df, dictionary_df, adt_catalog_df, ccda_catalog_df); each is None if file missing.
    """
    cat_path = os.path.join(PROJECT_ROOT, "master_patient_catalog.parquet")
    dict_path = os.path.join(PROJECT_ROOT, "master_patient_dictionary.parquet")
    adt_path = os.path.join(PROJECT_ROOT, "hl7_adt_catalog.parquet")
    ccda_path = os.path.join(PROJECT_ROOT, "ccda_catalog.parquet")

    catalog_df = pd.read_parquet(cat_path) if os.path.exists(cat_path) else None
    dictionary_df = pd.read_parquet(dict_path) if os.path.exists(dict_path) else None
    adt_df = pd.read_parquet(adt_path) if os.path.exists(adt_path) else None
    ccda_df = pd.read_parquet(ccda_path) if os.path.exists(ccda_path) else None
    return catalog_df, dictionary_df, adt_df, ccda_df


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
        source_id = base.replace("_feed_segments.csv", "").replace("_feed_segments", "")
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
    @media (min-width: 992px) {
        .field-row {
            display: inline-flex;
            width: calc(50% - 0.5rem);  /* two fields per row on large screens */
            vertical-align: top;
        }
    }
    .field-label {
        min-width: 7.5rem;
        font-weight: 600;
        white-space: nowrap;
        text-align: right;
        color: #4b5563;  /* secondary text */
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
          <div class="field-label">{label}:</div>
          <div class="{value_class}">{format_value(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
        filtered = filtered[mask]

    if fhir_resources:
        filtered = filtered[filtered["fhir_resource"].isin(fhir_resources)]
    if classifications:
        filtered = filtered[filtered["classification"].isin(classifications)]
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
    st.markdown(
        """
        <div class="title-row">
          <h4>Catalog</h4>
          <span class="header-caption">from master_patient_catalog.parquet · What elements exist and how they’re grouped.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_field("Semantic ID", record.semantic_id)
    render_field("USCDI Element", record.uscdi_element)
    render_field("Description", record.uscdi_description)
    render_field("Classification", record.classification)
    render_field("Ruleset Category", record.ruleset_category)
    render_field("Privacy/Security", record.privacy_security)

    st.markdown(
        """
        <div class="title-row">
          <h4>Dictionary – FHIR Mapping</h4>
          <span class="header-caption">from master_patient_dictionary.parquet · Canonical FHIR R4 path &amp; type for this element</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_field("Resource", record.fhir_resource)
    render_field("FHIR Path", record.fhir_r4_path)
    render_field("FHIR Data Type", record.fhir_data_type)

    st.markdown(
        """
        <div class="title-row">
          <h4>Dictionary – Survivorship & Sources</h4>
          <span class="header-caption">Business rules and source logic for this element.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_field("HIE Survivorship Logic", record.hie_survivorship_logic)
    render_field("Innovaccer Survivorship Logic", record.innovaccer_survivorship_logic)
    render_field("Data Source Rank Reference", record.data_source_rank_reference)
    render_field("Coverage (# PersonIDs)", record.coverage_personids)
    render_field("Granularity Level", record.granularity_level)

    st.markdown(
        """
        <div class="title-row">
          <h4>Dictionary – Quality & Governance</h4>
          <span class="header-caption"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_field("Quality & Governance Notes", record.data_quality_notes)

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
            st.markdown("**HL7 ADT (from `hl7_adt_catalog.parquet`)**")
            st.dataframe(
                adt_rows[
                    [
                        "message_type",
                        "segment_id",
                        "field_id",
                        "field_name",
                        "notes",
                    ]
                ].reset_index(drop=True),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "notes": st.column_config.TextColumn("Notes", width="large"),
                },
            )

        if ccda_rows is not None and not ccda_rows.empty:
            st.markdown("**CCD / CCDA (from `ccda_catalog.parquet`)**")
            st.dataframe(
                ccda_rows[
                    [
                        "section_name",
                        "entry_type",
                        "xml_path",
                        "notes",
                    ]
                ].reset_index(drop=True),
                hide_index=True,
                use_container_width=True,
                column_config={
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
        string ruleset_category
        string privacy_security
        string fhir_resource   "derived from fhir_r4_path"
    }

    MASTER_PATIENT_DICTIONARY {
        string semantic_id PK, FK
        string hie_survivorship_logic
        string data_source_rank_reference
        string coverage_personids
        string granularity_level
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
        streamlit_module.components.v1.html(html_content, height=420, scrolling=False)
    except Exception:
        streamlit_module.code(mermaid_src, language="mermaid")
    with streamlit_module.expander("Mermaid source (copy to Mermaid Live to edit)", expanded=False):
        streamlit_module.code(mermaid_src, language="mermaid")
    streamlit_module.caption(
        "Mermaid source: **hl7_ccd_fhir_consideration.md** (Current CHI Metadata Viewer ERD). Copy to [Mermaid Live](https://mermaid.live) to edit. "
        "**FHIR:** Path and type are stored in **MASTER_PATIENT_DICTIONARY** (canonical) and in **HL7_ADT_CATALOG** / **CCDA_CATALOG** (per-format); this POC does not store FHIR resource instance data (that lives in FHIR servers/APIs)."
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
            use_container_width=True,
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
                    st.dataframe(
                        segments_df,
                        hide_index=True,
                        use_container_width=True,
                        column_config={"data_received": st.column_config.TextColumn("Received"),
                                       "notes": st.column_config.TextColumn("Notes")},
                    )
                if events_df is not None and not events_df.empty:
                    st.markdown("**Event types**")
                    st.dataframe(
                        events_df,
                        hide_index=True,
                        use_container_width=True,
                        column_config={"percentage_of_total": st.column_config.TextColumn("%")},
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
    with st.expander("**Documentation**", expanded=False):
        st.markdown(
            "This section documents the current filtered subset and the Parquet tables that back this app."
        )
        st.markdown("#### Summary for current filters")
        st.markdown(
            f"- {total} element(s) · {distinct_resources} FHIR resource type(s)  \n"
            f"- {with_fhir} with FHIR mapping, {missing_fhir} missing  \n"
            f"- {missing_surv} missing HIE survivorship logic  \n"
            f"- {pii_count} with privacy/security flags"
        )
        st.markdown("#### Data model (ERD)")
        _render_erd(st)
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
        catalog_df, dictionary_df, adt_df, ccda_df = load_four_tables_for_review()
        if catalog_df is not None:
            st.markdown("**MASTER_PATIENT_CATALOG** — Catalog data elements (what exists and how they’re grouped).")
            st.dataframe(catalog_df.head(row_limit), use_container_width=True)
        if dictionary_df is not None:
            st.markdown("**MASTER_PATIENT_DICTIONARY** — Per-element rules, survivorship logic, and canonical FHIR path/type.")
            st.dataframe(dictionary_df.head(row_limit), use_container_width=True)
        if adt_df is not None:
            st.markdown("**HL7_ADT_CATALOG** — Where each catalog element lands in HL7 ADT messages (segment/field, data type, optionality).")
            st.dataframe(adt_df.head(row_limit), use_container_width=True)
            st.caption(
                "HL7 ADT columns: **data_type** is the HL7 v2 field data type (e.g., ST, NM, XPN). "
                "**optionality** usually follows HL7 v2 codes (R = required, O = optional, C = conditional, X = not used). "
                "**cardinality** expresses how many repetitions are allowed (e.g., 0..1, 0..*, 1..1, 1..*)."
            )
        if ccda_df is not None:
            st.markdown("**CCDA_CATALOG** — Where each catalog element lands in CCD/CCDA XML (section, entry type, XML path).")
            st.dataframe(ccda_df.head(row_limit), use_container_width=True)
        if catalog_df is None and dictionary_df is None and adt_df is None and ccda_df is None:
            st.caption("No Parquet tables found in project root.")
        st.markdown("---")
        st.caption("Full project docs: **readme-prd.md**, **README.md**, and **docs/** in the project folder.")


if __name__ == "__main__":
    main()

