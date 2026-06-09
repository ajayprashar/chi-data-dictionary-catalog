# Crosswalk and Value Set Model

How CHI documents **which standards apply**, **which codes are governed**, and **how source values map** — without duplicating full terminology catalogs (DAP remains system of record per `TECH-SPEC.md` §1.7).

**Related:** `docs/shie-standards-reference.md`, `docs/operational-runbook.md`, `docs/demographics-pilot-plan.md`

---

## Three companion tables (not one mega-table)

| Parquet | Sheet | Grain | Purpose |
|---------|-------|-------|---------|
| `ddc-value_set_binding.parquet` | `Value_Set_Bindings` | 1 row per (`semantic_id`, `binding_role`) | Which value set / code system applies |
| `ddc-value_set_member.parquet` | `Value_Set_Members` | 1 row per (`semantic_id`, `code`) | CHI-governed codes (subset, not full CDCREC) |
| `ddc-source_value_crosswalk.parquet` | `Source_Value_Crosswalk` | 1 row per source value → target | **Crosswalk:** CMT (etc.) → standard code |

All join to **`semantic_id`** on the master catalog.

```mermaid
flowchart LR
    Catalog["ddc-master_patient_catalog"]
    Binding["ddc-value_set_binding"]
    Member["ddc-value_set_member"]
    XWalk["ddc-source_value_crosswalk"]

    Catalog --> Binding
    Catalog --> Member
    Catalog --> XWalk
```

---

## What this repo does **not** host

| Do not duplicate locally | Use instead |
|--------------------------|-------------|
| Full CDCREC / SNOMED / LOINC / ICD-10 | HL7 terminology URLs + **DAP** at runtime |
| Every BCP 47 language tag | Binding + pilot **examples**; expand as needed |
| ICD-10 / ICD-9 (not in demographics pilot) | Add when curating clinical `semantic_id`s |

**Demographics pilot:** no ICD download required. Seed from `docs/shie-standards-reference.md` via `scripts/seed_value_sets_pilot.py`.

---

## Column reference

### Value set binding

| Column | Example (`Patient.race`) |
|--------|--------------------------|
| `semantic_id` | `Patient.race` |
| `binding_role` | `primary` |
| `value_set_url` | `http://terminology.hl7.org/ValueSet/v3-Race` |
| `code_system_oid` | `urn:oid:2.16.840.1.113883.6.238` |
| `binding_strength` | `required` |
| `fhir_element` | `Patient.extension(us-core-race).ombCategory` |

### Value set member

| Column | Example |
|--------|---------|
| `code` | `2054-5` |
| `display` | Black or African American |
| `member_type` | `omb_rollup` / `nullflavor` / `language_tag` / `administrative` |
| `active` | `true` |

### Source value crosswalk

| Column | Example |
|--------|---------|
| `source_id` | `cmt` |
| `source_field` | `PID-10` |
| `source_code` | *(validated CMT code)* |
| `target_code` | `2054-5` |
| `mapping_type` | `exact` / `rollup` / `exclude` |
| `approval_status` | `draft` until steward validates |

---

## Publish ritual

```powershell
# Expand Race / Ethnicity from HL7 (optional; preserves nullflavor rows):
python scripts/build_value_set_members.py --write-cache

# Re-seed pilot bindings from script (maintainers only — overwrites binding/crosswalk seed):
python scripts/seed_value_sets_pilot.py

# Or edit Value_Set_* / Source_Value_Crosswalk sheets in Excel, then:
python scripts/import_steward_workbook_to_parquet.py
python scripts/generate_steward_workbook.py      # optional reverse sync
```

Refresh Power BI → **Standards & Contexts** shows **Governed value set** and **Source crosswalk** tables.

---

## When you **will** need external datasets

| Domain | Typical source | When |
|--------|----------------|------|
| Race / ethnicity | [HL7 Race/Ethnicity ValueSet](https://terminology.hl7.org/) | Expanding beyond OMB pilot subset |
| Language | BCP 47 / IANA | Large language crosswalk from partner intake |
| Gender identity | US Core + LOINC 76691-5 answer codes | After partner code inventory |
| **ICD-10-CM / ICD-9** | CMS / NLM / **DAP** | Clinical concepts (problems, diagnoses) — **not demographics pilot** |
| SNOMED / LOINC clinical | **DAP** | Clinical attributes |

For production clinical expansion, reference DAP by ID in `authority_reference` or a future `dap_value_set_id` column — do not import full ICD tables into this repo unless CHI explicitly chooses a local overlay.

---

## CMT crosswalk next step

Starter rows in `ddc-source_value_crosswalk.parquet` are **draft placeholders**. Replace `EXAMPLE_*` `source_code` values with the validated CMT code list from:

- Partner intake workbook `Code_Values` sheet, or
- County survivorship Table 4/5 mappings

Set `approval_status` to `Approved` when mappings are steward-signed.
