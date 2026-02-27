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

*   Metadata authored in **Excel**
*   Manually exported to **open, portable files**
*   Lightweight local application renders metadata as:
    *   A **catalog record view** (one element at a time)
    *   A linked **data dictionary table** (field‑level details)

This approach keeps Excel as the **source of truth** while eliminating Excel as the **user interface**.

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

*   **data_catalog.parquet** — Catalog table (Semantic ID, element name, description, classification, ruleset category, privacy/security).
*   **data_dictionary.parquet** — Dictionary table (Semantic ID plus FHIR paths, survivorship logic, data quality notes, and other definition/rule columns).
*   Source data is authored in Excel; a single combined export is split into these two Parquet files by the project script (see *Data pipeline* below).

### Data pipeline

1. Author or edit metadata in Excel (one sheet or linked sheets).
2. Export a single combined CSV (e.g., one row per USCDI element with all catalog and dictionary columns).
3. Run the project script to split the CSV into **data_catalog.parquet** and **data_dictionary.parquet**:
   `python scripts/split_to_catalog_and_dictionary.py <combined_export.csv>`
4. The local viewer reads both Parquet files and joins on Semantic ID to present a record‑centric view.
5. For querying the Parquet files in Jupyter with DuckDB (Python), see **docs/jupyter-duckdb-parquet-setup.md**.

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

***

If you want next, I can:

*   Reformat this as a **1‑slide executive brief**
*   Add a **“current state vs future state” visual**
*   Turn this into a **decision memo** explaining why Power Pages was deferred

Just tell me what artifact you want.

