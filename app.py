#!/usr/bin/env python
"""
Streamlit viewer for the CHI data catalog & data dictionary.

- Reads two Parquet files: data_catalog.parquet and data_dictionary.parquet.
- Joins them on semantic_id.
- Provides search, filtering (including by FHIR resource), and a detail view.

Run from the project root:

    streamlit run app.py
"""

from __future__ import annotations

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
    cat_path = os.path.join(PROJECT_ROOT, "data_catalog.parquet")
    dict_path = os.path.join(PROJECT_ROOT, "data_dictionary.parquet")

    if not os.path.exists(cat_path) or not os.path.exists(dict_path):
        raise FileNotFoundError(
            "Expected data_catalog.parquet and data_dictionary.parquet in the project root. "
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


def inject_theme(theme: str) -> None:
    """Inject light or dark (terminal) theme CSS."""
    if theme == "Clinical (light)":
        css = """
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-size: 0.95rem;
            background-color: #f3f4f6;
            color: #111827;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff;
        }

        [data-testid="stAppViewContainer"] .block-container {
            padding-top: 1.0rem;
            padding-bottom: 1.0rem;
        }

        .field-row {
            display: flex;
            gap: 0.5rem;
            align-items: flex-start;
            margin-bottom: 0.2rem;
        }
        .field-label {
            min-width: 10rem;
            font-weight: 600;
            white-space: nowrap;
            text-align: right;
            color: #374151;
        }
        .field-value {
            flex: 1;
            background-color: #e5e7eb;  /* darker gray for better contrast */
            padding: 0.2rem 0.55rem;
            border-radius: 4px;
            border: 1px solid #9ca3af;
        }

        .header-caption {
            margin: 0.15rem 0 0.1rem 0;
            color: #4b5563;
        }
        .header-results {
            margin: 0.05rem 0 0.5rem 0;
        }

        h5 {
            margin-top: 0.4rem;
            margin-bottom: 0.15rem;
            color: #2b6cb0;
        }

        /* Summary box under Elements table */
        .summary-box {
            margin-top: 0.4rem;
            padding: 0.4rem 0.6rem;
            border-radius: 4px;
            border: 1px solid #d1d5db;
            background-color: #f9fafb;
            font-size: 0.9rem;
        }
        </style>
        """
    else:
        # Terminal (dark) theme
        css = """
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-size: 0.9rem;
            background-color: #0b0c10;
            color: #e5e5e5;
            font-family: "Consolas", "SF Mono", "Menlo", "Liberation Mono", monospace;
        }

        [data-testid="stSidebar"] {
            background-color: #101218;
            color: #e5e5e5;
        }

        /* Improve readability of inputs and labels in dark sidebar */
        [data-testid="stSidebar"] label {
            color: #e5e5e5;
            font-weight: 500;
        }
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea,
        [data-testid="stSidebar"] select,
        [data-testid="stSidebar"] .stTextInput input,
        [data-testid="stSidebar"] .stMultiSelect div[role="combobox"] {
            background-color: #141821;
            color: #e5e5e5;
            border: 1px solid #2e3440;
        }
        [data-testid="stSidebar"] .stMultiSelect span,
        [data-testid="stSidebar"] .stSelectbox span {
            color: #e5e5e5;
        }

        /* Header strip for toolbar + sidebar toggle */
        [data-testid="stHeader"] {
            background-color: #111827;
            color: #e5e5e5;
        }
        [data-testid="stHeader"] svg,
        [data-testid="stHeader"] button {
            color: #e5e5e5 !important;
            fill: #e5e5e5 !important;
        }
        /* Ensure sidebar collapse/expand control is visible on dark background */
        [data-testid="collapsedControl"] svg,
        [data-testid="collapsedControl"] button,
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stSidebarCollapseButton"] button {
            color: #e5e5e5 !important;
            fill: #e5e5e5 !important;
        }

        [data-testid="stAppViewContainer"] .block-container {
            padding-top: 1.0rem;
            padding-bottom: 1.0rem;
        }

        .field-row {
            display: flex;
            gap: 0.5rem;
            align-items: flex-start;
            margin-bottom: 0.18rem;
        }
        .field-label {
            min-width: 11rem;
            font-weight: 600;
            white-space: nowrap;
            text-align: right;
            color: #88c0d0;
        }
        .field-value {
            flex: 1;
            background-color: #141821;
            padding: 0.18rem 0.5rem;
            border-radius: 3px;
            border: 1px solid #2e3440;
        }

        .header-caption {
            margin: 0.15rem 0 0.1rem 0;
            color: #a0aec0;
        }
        .header-results {
            margin: 0.05rem 0 0.5rem 0;
        }

        h5 {
            margin-top: 0.4rem;
            margin-bottom: 0.15rem;
            color: #a3be8c;
        }

        .summary-box {
            margin-top: 0.4rem;
            padding: 0.4rem 0.6rem;
            border-radius: 4px;
            border: 1px solid #2e3440;
            background-color: #0f1118;
            font-size: 0.9rem;
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
    st.markdown(
        f"""
        <div class="field-row">
          <div class="field-label">{label}:</div>
          <div class="field-value">{format_value(value)}</div>
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


def render_detail(df: pd.DataFrame, selected_id: str) -> None:
    """Render the detail view for a single semantic_id."""
    record = df[df["semantic_id"] == selected_id].iloc[0]

    # Single, vertically stacked layout (no tabs) to minimize clicks and maximize visible context.
    st.markdown("##### Catalog (from `data_catalog.parquet`)")
    render_field("Semantic ID", record.semantic_id)
    render_field("USCDI Element", record.uscdi_element)
    render_field("Description", record.uscdi_description)
    render_field("Classification", record.classification)
    render_field("Ruleset Category", record.ruleset_category)
    render_field("Privacy/Security", record.privacy_security)

    st.markdown("##### Dictionary – FHIR Mapping (from `data_dictionary.parquet`)")
    render_field("Resource", record.fhir_resource)
    render_field("FHIR Path", record.fhir_r4_path)
    render_field("FHIR Data Type", record.fhir_data_type)

    st.markdown("##### Dictionary – Survivorship & Sources")
    render_field("HIE Survivorship Logic", record.hie_survivorship_logic)
    render_field("Innovaccer Survivorship Logic", record.innovaccer_survivorship_logic)
    render_field("Data Source Rank Reference", record.data_source_rank_reference)
    render_field("Coverage (# PersonIDs)", record.coverage_personids)
    render_field("Granularity Level", record.granularity_level)

    st.markdown("##### Dictionary – Quality & Governance")
    render_field("Quality & Governance Notes", record.data_quality_notes)


def main() -> None:
    st.set_page_config(
        page_title="CHI Metadata Catalog Viewer",
        layout="wide",
    )
    # Theme toggle (light vs terminal dark)
    with st.sidebar:
        theme = st.selectbox(
            "Theme",
            options=["Clinical (light)", "Terminal (dark)"],
            index=1,
        )

    inject_theme(theme)

    st.title("Community Health Insights (CHI) Metadata Catalog")
    st.markdown(
        '<p class="header-caption">'
        "Local viewer for the CHI data catalog and data dictionary. "
        "Data is read from Parquet files in this folder; Excel remains the authoring source."
        "</p>",
        unsafe_allow_html=True,
    )

    try:
        df = load_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    filtered = apply_filters(df)

    if filtered.empty:
        st.info("No elements match the current criteria. Relax filters or clear the search term.")
        return

    # Aggregate summary for current filtered set (used under Elements table)
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
        st.markdown("#### Elements")
        st.caption("Use the selection column on the left to choose an element.")
        list_view = list_view.reset_index(drop=True)

        event = st.dataframe(
            list_view,
            hide_index=True,
            use_container_width=True,
            selection_mode="single-row",
            on_select="rerun",
        )

        # Compact summary using the space under the Elements table (line-by-line)
        st.markdown(
            f"""
            <div class="summary-box">
              <strong>Summary for current filters</strong><br/>
              {total} element(s)<br/>
              {distinct_resources} FHIR resource type(s)<br/>
              {with_fhir} with FHIR mapping, {missing_fhir} missing<br/>
              {missing_surv} missing HIE survivorship logic<br/>
              {pii_count} with privacy/security flags
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Determine selected semantic_id from the row selection; default to first row
        selected_rows = getattr(event, "selection", None)
        if selected_rows and selected_rows.rows:
            selected_idx = selected_rows.rows[0]
        else:
            selected_idx = 0

        selected_id = filtered["semantic_id"].iloc[selected_idx]

    with col_detail:
        st.markdown("#### Element detail")
        render_detail(filtered, selected_id or default_id)


if __name__ == "__main__":
    main()

