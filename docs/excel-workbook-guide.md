# Excel Workbook Guide (POC)

Local proof-of-concept: **one steward workbook** is the primary surface; parquet is the portable machine copy in this repo folder.

---

## POC scope (what matters now)

| In scope | Deferred |
|----------|----------|
| `chi-steward-workbook.xlsx` — edit Catalog + Dictionary | SharePoint / team portals |
| 5 demographics pilot (`Patient.race`, `.ethnicity`, `.language`, `.gender_id`, `.birth_sex`) | All 28 data sources |
| `semantic_id` as join key | Power BI search UI |
| Round-trip: Excel → parquet in this folder | Partner intake (until onboarding a source) |
| Optional: notebook browse of parquet | Full FHIR inventory curation |

**POC success** = a steward can open the workbook, review one concept in `Concept_Explorer`, and see catalog + dictionary + source link on one `semantic_id`.

---

## Operating model (simplified)

```mermaid
flowchart LR
    Steward["chi-steward-workbook.xlsx"]
    Parquet["ddc-*.parquet in repo folder"]
    Notebook["notebook optional"]

    Steward --> Parquet
    Parquet --> Steward
    Parquet --> Notebook
```

1. **Edit** the steward workbook locally.
2. **Import** changes to parquet when ready.
3. **Regenerate** the workbook from parquet if parquet was rebuilt by scripts.

`semantic_id` is the stable join key.

---

## Primary workbook: CHI steward

**Path:** `workbooks/chi-steward-workbook.xlsx`

```powershell
python scripts/generate_steward_workbook.py
python scripts/import_steward_workbook_to_parquet.py
```

### Sheets to use in the POC

| Sheet | Use in POC? | Purpose |
|-------|-------------|---------|
| `Concept_Explorer` | **Yes** | Pick `semantic_id` in B3; preview linked fields |
| `Catalog` | **Yes** | Business context, steward, approval |
| `Dictionary` | **Yes** | FHIR, survivorship, implementation |
| `Source_Availability` | **Yes** | Link concepts to `source_id` |
| `Steward_Queue` | Optional | Workflow notes |
| `ADT_Mappings` | Optional | HL7 demo / CMT work |
| `CCDA_Mappings` | Optional | CCD demo |
| `FHIR_Inventory` | Defer | Large reference inventory |
| `Business_Rules` | Defer | Until rule authoring needed |
| `_Model`, `Lookup_Lists` | Auto | Hidden support sheets |

### Data source linking

`Source_Availability` columns:

- `semantic_id` — governed concept
- `source_id` — data source (e.g. `cmt`)
- `availability` — `full`, `partial`, `none`, `unknown`

---

## Secondary workbook: partner intake (defer until needed)

**Path:** `workbooks/chi-partner-intake-workbook.xlsx`

Use when onboarding an external source (jail, HMIS, etc.). Not required for the demographics POC.

```powershell
python scripts/generate_intake_workbook.py
```

---

## POC commands (minimal)

```powershell
.venv\Scripts\activate

# Refresh workbook from parquet
python scripts/generate_steward_workbook.py

# Save Excel edits back to parquet
python scripts/import_steward_workbook_to_parquet.py
```

### Optional (interoperability demos only)

```powershell
python scripts/build_adt_catalog_from_mapping.py
python scripts/build_ccda_catalog_from_mapping.py
python scripts/build_data_source_availability.py
python scripts/build_standards_inventories.py -d .
python scripts/split_to_catalog_and_dictionary.py path\to\combined_export.csv
```

---

## Related documents

- `README.md` — quick start
- `TECH-SPEC.md` — full column schemas (reference, not required for daily POC use)
- `docs/cmt-adt-feed-and-master-patient.md` — ADT mapping context
