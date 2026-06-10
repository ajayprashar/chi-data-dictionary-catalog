# Product Vision — Governed Data Catalog & Data Dictionary

North star for the **chi-data-dictionary-catalog** project.

---

## Vision statement

> A **governed data catalog and data dictionary** for CHI patient concepts (`semantic_id`), **curated against healthcare standards** (USCDI, US Core, terminology), with **dictionary implementation detail** and **interoperability views** for **HL7 ADT**, **C-CDA**, and **FHIR** — so users can discover what CHI governs, how it is implemented, and where it appears in each message context.

---

## Layered model

```text
USCDI              →  WHAT must be collected        (Catalog)
US Core + FHIR R4  →  HOW it is represented         (Dictionary: fhir_r4_path, fhir_profile)
Terminology        →  WHICH coded values are valid  (Value_Set_Bindings / Members; Dictionary notes)
HL7 v2 ADT         →  WHERE in ADT feeds            (ddc-hl7_adt_catalog / ADT_Mappings)
C-CDA              →  WHERE in clinical documents   (ddc-ccda_catalog / CCDA_Mappings)
NullFlavor         →  WHEN there is no value        (survivorship + terminology notes)
County / OMB       →  HOW you roll up for reporting (chi_survivorship_logic)
Governance         →  WHO approved it               (Catalog: steward, approval_status)
```

**Master truth** lives in Catalog + Dictionary. Message-format catalogs **carry** the same `semantic_id` without redefining the concept.

---

## Primary users

| User | Need |
|------|------|
| Data stewards | Author and approve governed concepts in Excel |
| Standards / architecture | See USCDI, US Core, CDCREC, BCP 47 bindings per concept |
| Interface teams | See ADT segment/field and CCDA XPath for the same `semantic_id` |
| Equity / consent / reporting | Review survivorship and approval in one profile |
| Partners | Contribute source inventory via partner workbook (separate from governance) |

---

## Artifacts

| Layer | Artifact | Authoring |
|-------|----------|-----------|
| Catalog | `ddc-master_patient_catalog.parquet` | Catalog sheet |
| Dictionary | `ddc-master_patient_dictionary.parquet` | Dictionary sheet |
| Sources | `ddc-data_source_availability.parquet` | Source_Availability |
| HL7 ADT context | `ddc-hl7_adt_catalog.parquet` | ADT_Mappings |
| C-CDA context | `ddc-ccda_catalog.parquet` | CCDA_Mappings |
| Read surface | Power BI PBIP | Refresh after import |

---

## Sources of truth

National standards (USCDI, US Core, HL7 terminologies) are authoritative **externally**. DAP is authoritative for **enterprise terminology at scale**. CHI steward workbook + published parquet is authoritative for **governed metadata CHI signs**. County and partner source strings are **inputs** mapped via crosswalk — not standards.

Detail: **`docs/sources-of-truth.md`**.

---

## Power BI pages

| Page | Purpose |
|------|---------|
| **Start here** | Purpose, sources-of-truth layers, how to use the report |
| **Concept Profile** | One `semantic_id`: governance + dictionary + survivorship + sources |
| **Standards & Contexts** | Same slicer: FHIR/US Core notes + value sets + crosswalk + ADT + CCDA |
| **Governance Overview** | Portfolio KPIs and full catalog |

---

## POC scope (demographics pilot)

Five attributes: `Patient.race`, `Patient.ethnicity`, `Patient.language`, `Patient.gender_id`, `Patient.birth_sex`.

Operational plan: `docs/demographics-pilot-plan.md`  
SHIE standards detail: `docs/shie-standards-reference.md`  
Architecture depth: `TECH-SPEC.md`

---

## Publish ritual

```text
Edit chi-steward-workbook.xlsx  →  import_steward_workbook_to_parquet.py  →  Refresh Power BI
```

Optional re-seed: `python scripts/seed_demographics_pilot.py` then `python scripts/generate_steward_workbook.py`  
PBIP **Start here** page only: `python scripts/add_pbip_start_here_page.py`  
PBIP full layout (maintainers): `python scripts/enhance_pbip_report.py` then `python scripts/patch_pbip_readability.py`
