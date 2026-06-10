# FAQ — Catalog, dictionary, and Power BI

Short answers for stewards, reviewers, and demo audiences. Deep detail: `docs/product-vision.md`, `docs/sources-of-truth.md`, `docs/demographics-pilot-plan.md`.

---

## What is the difference between catalog and dictionary?

| Layer | Parquet / Excel | Question it answers |
|-------|-----------------|---------------------|
| **Catalog** | `ddc-master_patient_catalog` / **Catalog** sheet | **WHAT** does CHI govern? (USCDI element, classification, steward, approval, HIPAA/consent) |
| **Dictionary** | `ddc-master_patient_dictionary` / **Dictionary** sheet | **HOW** is it implemented? (FHIR path/profile, survivorship, quality notes, source rank reference) |

One row per `semantic_id` in each table; **1:1** relationship. Join key everywhere: **`semantic_id`**.

```text
USCDI     → WHAT   (Catalog)
US Core   → HOW    (Dictionary)
ADT/CCDA  → WHERE  (message mapping catalogs)
Terminology / crosswalk → WHICH codes; local → standard
```

---

## Do Power BI tabs map to Catalog vs Dictionary tables?

**No.** PBIP pages are **task lenses** on the same `semantic_id` spine, not one tab per parquet table.

| Page | What it is for | Tables used (often mixed on one page) |
|------|----------------|----------------------------------------|
| **Start here** | Orientation | None (static text) |
| **Field guide** | In-report documentation | `ddc-application_guide` — filter by page and visual; column layer and interop role |
| **Standards & Contexts** | Standards + interoperability for one concept | Slicer: catalog. Tables: dictionary (FHIR), value sets, crosswalk, ADT catalog, CCDA catalog |
| **Concept Profile** | Full stewarded profile for one concept | Catalog (governance), dictionary (FHIR + **survivorship**), source availability |
| **Governance Overview** | Portfolio KPIs | Mostly catalog |

A single page can show **catalog columns and dictionary columns side by side**. The split is **per column / per source table**, not per tab.

---

## Why are there multiple tables with "catalog" in the name?

Three different meanings:

| Table | Meaning of "catalog" |
|-------|----------------------|
| `ddc-master_patient_catalog` | **Element catalog** — canonical list of governed concepts (person-centric scope) |
| `ddc-hl7_adt_catalog` | **ADT mapping catalog** — where each `semantic_id` lands in HL7 v2 ADT |
| `ddc-ccda_catalog` | **CCDA mapping catalog** — where each `semantic_id` lands in C-CDA XML |

Only the first pair (master catalog + dictionary) is the core **catalog vs dictionary** split. ADT/CCDA catalogs are **message-placement** artifacts, not duplicates of the master catalog.

---

## Where do I edit vs where do I read?

| Action | Where |
|--------|--------|
| **Author** governance, FHIR, survivorship | `workbooks/chi-steward-workbook.xlsx` (Catalog, Dictionary, Source_Availability, ADT/CCDA sheets) |
| **Publish** machine copy | `python scripts/import_steward_workbook_to_parquet.py` |
| **Read / demo** | `workbooks/pbip/chi-data-dictionary-catalog.pbip` → **Refresh** |

Excel is source of human edits. Power BI is read-only after publish. Do not expect PBIP tabs to mirror Excel sheet names 1:1.

---

## Where does each steward field show up in Power BI?

After import + Refresh (see `docs/demographics-pilot-plan.md` for pilot detail):

| You filled (Excel) | Concept Profile | Standards & Contexts |
|--------------------|-----------------|----------------------|
| Catalog: steward, approval, USCDI, HIPAA | Profile cards + governance table | (via slicer filter) |
| Dictionary: FHIR, quality notes | Implementation table | FHIR table (no survivorship column) |
| Dictionary: `chi_survivorship_logic` | Implementation table | **Not shown** (by design) |
| ADT_Mappings | — | HL7 ADT table |
| CCDA_Mappings | — | C-CDA table |
| Value_Set_Members | — | Governed value set codes |
| Source_Value_Crosswalk | — | Crosswalk table |
| Source_Availability | Source availability table | — |

---

## Does the catalog/dictionary split matter for demos?

| Audience | What matters |
|----------|----------------|
| **Stewards** | **Yes** — put fields in the right Excel sheet; wrong sheet breaks governance intent. |
| **Reviewers** | **Yes** — approval and survivorship live in different tables by design. |
| **Demo viewers** | **Light touch** — explain WHAT / HOW / WHERE layers; they do not need to memorize which tab maps to which table. |

---

## What is `semantic_id`?

Stable spine joining catalog, dictionary, terminology, crosswalk, ADT/CCDA, and source availability. Example: `Patient.race`. Use the **semantic_id** slicer on Concept Profile or Standards & Contexts to drill into one concept.

---

## Where is the in-report field guide?

Open the **Field guide** tab in Power BI. Use slicers to pick a report page and table/visual. **Summary cards** show page purpose, interoperability summary, and primary audience; the detail table explains each column’s layer, role, standards URL, and Excel authoring sheet.

Regenerate after layout changes:

```powershell
python scripts/validate_pbip_manifest.py
python scripts/generate_pbip_model_guide.py
python scripts/add_pbip_documentation_page.py
```

---

## Related docs

- Steward column guide: `docs/demographics-pilot-plan.md` (Catalog vs dictionary table)
- Power BI setup and troubleshooting: `docs/power-bi-concept-profile-setup.md`
- Layered authority (US standards, DAP, CHI publish): `docs/sources-of-truth.md`
- Table naming in architecture: `TECH-SPEC.md` §2.2.1
