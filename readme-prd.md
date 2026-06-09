Below is a **1‑page executive PRD** distilled from the longer PRD and our discussion. It’s written for **leaders and decision‑makers**—clear, non‑technical, and focused on *why this matters*, not how it’s built.

***

# Executive PRD — Local Metadata Catalog & Data Dictionary (POC)

## Product Name

**Metadata Catalog Viewer (POC)**

***

## Executive Summary

This proof‑of‑concept (POC) demonstrates how existing Excel‑based metadata (data catalog and data dictionary) can be presented as a **clean, application‑style experience**—without Power Apps, Dataverse, VBA, or enterprise platform dependencies.

The goal is to validate **usability, data model clarity, and stakeholder value** before committing to any production technology or licensing decisions.

***

## Problem Statement

Excel is effective for **authoring** metadata but is a poor **presentation and discovery interface**. Reviewing metadata record‑by‑record, understanding governance context, and linking catalog entries to detailed dictionary definitions is cumbersome and error‑prone in spreadsheets.

Stakeholders need a clearer way to **view and understand metadata**, not edit it.

***

## Objectives

*   Present metadata in a **record‑centric, readable UI**
*   Clearly link **data catalog entries** to their **data dictionary definitions**
*   Operate under **strict local PC constraints**
*   Avoid premature platform decisions (Power Apps, Dataverse, etc.)

***

## Scope (POC Only)

### In Scope

*   Read‑only viewing of metadata
*   Data catalog and data dictionary displayed together
*   Manual data refresh from Excel
*   Local execution

### Out of Scope

*   Editing or write‑back
*   Authentication / authorization
*   Automation, lineage, or workflows
*   Multi‑user access
*   Production deployment

***

## Target Users

*   Data governance stakeholders
*   Data stewards
*   Architects and technical leadership

Primary use case: **review, validation, and discussion of metadata**.

***

## Solution Overview

*   Metadata **authored** in **Excel** (`chi-steward-workbook.xlsx`)
*   Saved to **open, portable Parquet files** in the project folder
*   **Presented** in **Power BI Desktop** (read-only PBIP report) as:
    *   A **Concept Profile** — one `semantic_id` at a time (catalog + dictionary + sources)
    *   A **Governance Overview** — portfolio KPIs and full concept table

Excel remains the **authoring surface**; Power BI is the **review and discovery surface**. A Jupyter notebook is available only for optional ad-hoc DuckDB queries over Parquet.

***

## Data Model (Conceptual)

Metadata is split into **two files** joined by a **Semantic ID**:

| File | Grain | Purpose |
|------|--------|---------|
| **Data Catalog** | One row per data element (e.g., USCDI element) | Discoverability: identity, name, description, classification, and high‑level governance. Answers *what elements we have*. |
| **Data Dictionary** | One row per element (expandable to multiple rows later) | Definition and rules: FHIR mapping, survivorship logic, data sources, quality notes, business rules. Answers *what the element means and how it is implemented*. |

*   **Join key**: **Semantic ID** is the primary key in the catalog and the foreign key in the dictionary. The viewer uses it to link a catalog record to its dictionary details.
*   **Catalog** holds minimal, stable identity and classification; **dictionary** holds technical and rule‑oriented attributes (including business rules).

This mirrors enterprise metadata patterns while remaining simple.

### Artifacts

*   **ddc-master_patient_catalog.parquet** — Master patient catalog (Semantic ID, element name, description, classification, ruleset category, HIPAA/FHIR/consent governance tags).
*   **ddc-master_patient_dictionary.parquet** — Master patient dictionary (Semantic ID plus FHIR paths, survivorship logic, data quality notes, and other definition/rule columns).
*   Source data is authored in the steward Excel workbook and imported to these Parquet files (see *Data pipeline* below).
*   Optional **message-format catalogs** for interoperability demonstrations:
    *   `ddc-hl7_adt_catalog.parquet` — Example HL7 ADT field mappings (PID segment for a few core demographics).
    *   `ddc-ccda_catalog.parquet` — Example CCD/CCDA XML paths for the same master patient elements.

### Data pipeline

1. Author or edit metadata in **`workbooks/chi-steward-workbook.xlsx`** (`Catalog`, `Dictionary`, `Source_Availability` sheets).
2. Import workbook changes to Parquet:
   `python scripts/import_steward_workbook_to_parquet.py`
3. Open **`workbooks/pbip/chi-data-dictionary-catalog.pbip`** in Power BI Desktop and **Refresh** to load the latest catalog and dictionary (joined on Semantic ID).
4. Optional — regenerate the workbook from Parquet after script rebuilds:
   `python scripts/generate_steward_workbook.py`
5. Optional — legacy CSV split or ad-hoc queries: `scripts/split_to_catalog_and_dictionary.py`, or Jupyter + DuckDB (**docs/jupyter-duckdb-parquet-setup.md**).

***

## Portability & Deployment

*   **Single‑folder app**: All artifacts live under one project folder (this directory). Copying or zipping this folder copies the entire POC.
*   **No machine‑specific paths**: Scripts and the Power BI model use Parquet files in the project folder. The same folder layout works on any Windows PC.
*   **Local runtime**: Parquet files are the portable data layer. Power BI Desktop reads them directly; no external database or web server is required.
*   **Reproducible setup**:
    *   Create a local virtual environment in the project folder.
    *   Install dependencies from `requirements.txt`.
    *   Edit the steward workbook, run `import_steward_workbook_to_parquet.py`, then open or refresh the PBIP report (**docs/power-bi-concept-profile-setup.md**).
*   **Mobility requirement**: A user can move the POC to a new machine by copying the folder, recreating the virtual environment, and reinstalling from `requirements.txt`—no additional configuration files, registries, or services.

***

## Viewer UX (Excel authors, Power BI presents)

**Authoring:** stewards edit `chi-steward-workbook.xlsx` (and optionally the partner intake workbook when onboarding a source).

**Presentation:** stakeholders open the PBIP report in Power BI Desktop (**docs/power-bi-concept-profile-setup.md**). After Excel edits, run the import script and **Refresh** in Power BI.

### Report pages

| Page | Purpose |
|------|---------|
| **Concept Profile** | Select one `semantic_id` — USCDI identity, FHIR mapping, survivorship, and source availability on one screen |
| **Governance Overview** | Portfolio KPIs (total, approved, pending, demographics pilot), classification/approval charts, full catalog table |

### Key user workflows

*   **Review one element in depth**: Use the Concept Profile slicer to pick a `semantic_id` and see catalog + dictionary + sources together.
*   **Scan portfolio health**: Use Governance Overview KPIs and charts to spot pending approvals and demographics pilot progress.
*   **Browse the full catalog**: Scroll or filter the catalog table on Governance Overview.
*   **Author changes**: Return to Excel, edit Catalog/Dictionary/Source_Availability, import to Parquet, refresh Power BI.

### Optional: Jupyter notebook

`chi-data-dictionary-catalog.ipynb` supports ad-hoc DuckDB queries over Parquet for developers and stewards who need custom SQL. It is not the primary stakeholder viewer.

***

## Success Criteria

*   Stakeholders can intuitively review a single data element and all its metadata
*   The relationship between catalog and dictionary is immediately clear
*   The POC runs locally with no special permissions
*   The solution is understandable without training

***

## Why This Matters

This POC answers a critical question *before* platform investment:

> “Does this metadata structure and user experience actually work for our users?”

It provides evidence to guide future decisions—whether that’s Power Pages, a commercial catalog, or a custom solution—without locking the organization into any one path.

***

## Future Path (Not a Commitment)

If validated, this model can later be:

*   Migrated to Dataverse / Power Pages
*   Ingested into an enterprise data catalog
*   Extended with search, governance workflows, or automation

The POC is **platform‑agnostic by design**.

***

## Bottom Line

This POC delivers **high signal at low cost**: it improves clarity, reduces friction, and informs strategy—without triggering licensing, governance, or architectural overhead.

