# FAQ - Catalog, dictionary, and Power BI

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

## Is a "Concept" the same as an "Element"?

**Usually yes** — in this project, both words mean **one governed piece of patient information**, identified by a single `semantic_id`.

| Term | Typical use here | Example |
|------|------------------|---------|
| **Concept** | Steward and demo language; Power BI **Concept Profile** | "Review the **concept** `Patient.race`" |
| **Element** | Catalog/dictionary and USCDI-aligned language | "The catalog lists one **element** per `semantic_id`" |
| **`semantic_id`** | Stable ID both terms point to | `Patient.name_first` |

**Definitions**

- **Concept** — A patient attribute CHI officially governs (name, race, address, etc.). One concept = one row in the catalog and one row in the dictionary, joined by `semantic_id`.
- **Element** — The same governed attribute when described as a **catalog row** or a **field on a standards checklist**. "Data element" in the PRD and "governed concept" in the vision statement refer to the same grain.

They are **not** interchangeable when **USCDI** uses "Element" for its own labels (see below).

### Plain example (high school level)

Imagine a **school registration form** online:

| Blank on the form | What it is in CHI terms |
|-------------------|-------------------------|
| **First name** | One **concept** and one **element** — CHI ID: `Patient.name_first` |
| **Last name** | A different **concept** / **element** — CHI ID: `Patient.name_last` |

Both blanks are about "name," but CHI tracks them as **two separate concepts** (two `semantic_id`s), not one.

The **government checklist** (USCDI) groups them differently:

| USCDI label type | Example | Think of it as… |
|------------------|---------|-----------------|
| **USCDI Data Element** (official category) | "Patient Name" | The **section heading** on the government form |
| **USCDI Element** (friendly label) | "First Name", "Last Name" | The **specific blanks** under that heading |

So:

- **CHI concept** ≈ **CHI element** ≈ one governed `semantic_id` (e.g. first name).
- **USCDI Element** = a standards display name (often matches the friendly blank, e.g. "First Name").
- **USCDI Data Element** = the broader official USCDI category (e.g. "Patient Name") that may cover **several** CHI concepts.

**Rule of thumb:** If someone says "pick a concept" or "pick an element" and means one row in the catalog → they mean the same thing. If someone says "USCDI Element" or "USCDI Data Element" → they mean **standards column labels**, not a substitute for `semantic_id`.

See also `TECH-SPEC.md` §2.2.1 (table naming) and §3.1 (catalog grain).

---

## Do Power BI tabs map to Catalog vs Dictionary tables?

**No.** PBIP pages are **task lenses** on the same `semantic_id` spine, not one tab per parquet table.

| Page | What it is for | Tables used (often mixed on one page) |
|------|----------------|----------------------------------------|
| **Guide · Start here** | Orientation | None (static text) |
| **Guide · Demo tour** | 5-minute walkthrough (demo landing) | None (static text) |
| **Guide · National standards** | External standards lookup | None (static text) |
| **Standards & Contexts** | Standards + interoperability for one concept | Slicer: catalog. Tables: dictionary (FHIR), value sets, crosswalk, ADT catalog, CCDA catalog |
| **Concept Profile** | Full stewarded profile for one concept | Catalog (governance), dictionary (FHIR + **survivorship**), source availability |
| **Guide · Field guide** | In-report documentation | `ddc-application_guide`, `ddc-application_guide_gaps` |
| **Governance Overview** | Portfolio KPIs | Mostly catalog |

A single page can show **catalog columns and dictionary columns side by side**. The split is **per column / per source table**, not per tab.

---

## Why are there multiple tables with "catalog" in the name?

Three different meanings:

| Table | Meaning of "catalog" |
|-------|----------------------|
| `ddc-master_patient_catalog` | **Element catalog** - canonical list of governed concepts (person-centric scope) |
| `ddc-hl7_adt_catalog` | **ADT mapping catalog** - where each `semantic_id` lands in HL7 v2 ADT |
| `ddc-ccda_catalog` | **CCDA mapping catalog** - where each `semantic_id` lands in C-CDA XML |

Only the first pair (master catalog + dictionary) is the core **catalog vs dictionary** split. ADT/CCDA catalogs are **message-placement** artifacts, not duplicates of the master catalog.

---

## Where do I edit vs where do I read?

| Action | Where |
|--------|--------|
| **Author** governance, FHIR, survivorship | `workbooks/chi-steward-workbook.xlsx` (Catalog, Dictionary, Source_Availability, ADT/CCDA sheets) |
| **Publish** machine copy | `python scripts/import_steward_workbook_to_parquet.py` |
| **Read / demo** | `workbooks/pbip/chiddc.pbip` → **Refresh** |

Excel is source of human edits. Power BI is read-only after publish. Do not expect PBIP tabs to mirror Excel sheet names 1:1.

---

## Where does each steward field show up in Power BI?

After import + Refresh (see `docs/demographics-pilot-plan.md` for pilot detail):

| You filled (Excel) | Concept Profile | Standards & Contexts |
|--------------------|-----------------|----------------------|
| Catalog: steward, approval, USCDI, HIPAA | Profile cards + governance table | (via slicer filter) |
| Dictionary: FHIR, quality notes | Implementation table | FHIR table (no survivorship column) |
| Dictionary: `chi_survivorship_logic` | Implementation table | **Not shown** (by design) |
| ADT_Mappings | - | HL7 ADT table |
| CCDA_Mappings | - | C-CDA table |
| Value_Set_Members | - | Governed value set codes |
| Source_Value_Crosswalk | - | Crosswalk table |
| Source_Availability | Source availability table | - |

---

## Does the catalog/dictionary split matter for demos?

| Audience | What matters |
|----------|----------------|
| **Stewards** | **Yes** - put fields in the right Excel sheet; wrong sheet breaks governance intent. |
| **Reviewers** | **Yes** - approval and survivorship live in different tables by design. |
| **Demo viewers** | **Light touch** - explain WHAT / HOW / WHERE layers; they do not need to memorize which tab maps to which table. |

---

## What is `semantic_id`?

Stable spine joining catalog, dictionary, terminology, crosswalk, ADT/CCDA, and source availability. Example: `Patient.race`. Use the **semantic_id** slicer on Concept Profile or Standards & Contexts to drill into one concept.

---

## Why does the PBIP semantic model have nine tables?

The model has **seven governed data tables** (from steward Excel → import) plus **two guide tables** (generated for the Field guide tab). They serve different purposes.

### Seven data tables (governed catalog spine)

Published by `python scripts/import_steward_workbook_to_parquet.py`. Joined on **`semantic_id`** for concept drill-down.

| Table | Source | Role |
|-------|--------|------|
| `ddc-master_patient_catalog` | Steward workbook **Catalog** | WHAT CHI governs |
| `ddc-master_patient_dictionary` | Steward workbook **Dictionary** | HOW it is implemented (FHIR, survivorship) |
| `ddc-data_source_availability` | Steward workbook **Source_Availability** | Where source data exists |
| `ddc-hl7_adt_catalog` | Steward workbook **ADT_Mappings** | HL7 v2 ADT placement |
| `ddc-ccda_catalog` | Steward workbook **CCDA_Mappings** | C-CDA placement |
| `ddc-value_set_member` | Steward workbook **Value_Set_Members** | Governed codes |
| `ddc-source_value_crosswalk` | Steward workbook **Source_Value_Crosswalk** | Local source strings → standards |

### Two guide tables (in-report documentation)

**Not** from the steward workbook. Regenerated from repo metadata and live parquet checks.

| Table | Source | Role |
|-------|--------|------|
| `ddc-application_guide` | `data/pbip_report_manifest.py` via `scripts/generate_pbip_model_guide.py` | Column dictionary: purpose, Excel sheet, steward action, interoperability role |
| `ddc-application_guide_gaps` | `data/pilot_curation_checks.py` via same script | Missing Concept Profile fields per `semantic_id` (pilots + backlog) |

**Why add them to the model?** Power BI needs queryable tables for the **Guide · Field guide** slicers and tables. Keeping the guide as data (not hard-coded text in visuals) means:

- Layout or column changes update from `pbip_report_manifest.py` after validation.
- Curation gaps refresh from catalog/dictionary parquet after each steward publish.
- Stewards see **what each column means** and **what is still empty** without leaving the report.

Guide tables are **not** joined to the `semantic_id` spine; they document the report itself.

```text
Steward Excel  →  import  →  7 ddc-* data parquets  →  Concept Profile / Standards & Contexts / …
Repo manifest  →  generate  →  2 ddc-application_* parquets  →  Guide · Field guide only
```

See also: `docs/operational-runbook.md` (publish checklist), `docs/power-bi-concept-profile-setup.md` (regen commands).

---

## Where is the in-report field guide?

Open the **Guide · Field guide** tab in Power BI. Use slicers to pick a report page, table/visual, and whether the column is **editable in Excel**. **Summary cards** show page purpose, interoperability summary, and primary audience. The detail table links each column to **steward_action** (workbook sheet → import → Refresh) and **review_on_page** (usually Concept Profile). The **curation gaps** table lists missing Concept Profile fields for demographics pilots and non-Approved concepts (from live parquet).

Regenerate after layout or steward publish:

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
