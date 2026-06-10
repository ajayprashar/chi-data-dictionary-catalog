# Operational Runbook (Level A — No SharePoint)

How to run the **governed catalog + dictionary** as an **operational POC** until SharePoint or Power BI Service is available.

**North star:** `docs/product-vision.md`  
**Curation detail:** `docs/demographics-pilot-plan.md`  
**Excel how-to:** `docs/excel-workbook-guide.md`  
**Power BI setup:** `docs/power-bi-concept-profile-setup.md`

---

## What “Level A production” means here

| In scope | Out of scope (for now) |
|----------|-------------------------|
| Trusted, steward-signed content | SharePoint co-authoring |
| Repeatable publish ritual | Power BI Service scheduled refresh |
| Git as source of truth | Multi-user concurrent Excel editing |
| Power BI Desktop for reviewers | Enterprise metadata platform |
| One named **publisher** per publish cycle | Full 28-source coverage |

Level A is **repeatable process + accountable content**, not a new platform.

---

## Architecture (unchanged)

```text
Excel (author)  →  import script  →  parquet  →  Power BI Refresh (read)
```

| Artifact | Path | Role |
|----------|------|------|
| Steward workbook | `workbooks/chi-steward-workbook.xlsx` | Authoring |
| Parquet | `ddc-*.parquet` (repo root) | Published machine copy (7 clinical tables from steward import) |
| Field guide parquet | `ddc-application_guide.parquet` | In-report column reference — **not** from steward import; regenerate from `data/pbip_report_manifest.py` |
| Read surface | `workbooks/pbip/chi-data-dictionary-catalog.pbip` | Review / discovery |

---

## Roles

| Role | Responsibility |
|------|----------------|
| **Steward** | Edits Catalog, Dictionary, Source_Availability (and Steward_Queue notes) in Excel |
| **Publisher** | Runs import script, spot-checks Power BI, commits workbook + parquet to git |
| **Reviewer** | `git pull` → opens PBIP → **Refresh** → validates Concept Profile |
| **Maintainer** (optional) | Regenerates workbook from parquet, PBIP layout (`enhance_pbip_report.py`) — rare |

**Rule:** One published snapshot at a time. Whoever runs import and commits is the publisher for that cycle. Everyone else pulls before reviewing.

### Assigned roles (Level A)

| Role | Name | Notes |
|------|------|-------|
| **Publisher** | **Ajay Prashar** (`Ajay.Prashar@acgov.org`) | Runs import, spot-checks Power BI, commits publish cycles |
| **Steward** (demographics pilot) | **Ajay Prashar** (`Ajay.Prashar@acgov.org`) | `data_steward` / `steward_contact` on five pilot `semantic_id`s until additional stewards are named |
| **Reviewer** | *TBD* | Pulls repo and Refresh after each publish notification |

---

## Machine setup (one-time per person)

### 1. Clone to a standard path

Use the **same folder name** on every machine so PBIP parquet paths work without edits:

```text
C:\AI\chi-data-dictionary-catalog
```

If you must use a different drive, either:

- Clone to that path via subst/junction, or  
- Re-point parquet paths in the semantic model (maintainer task; see `docs/power-bi-concept-profile-setup.md`)

### 2. Python environment

```powershell
cd C:\AI\chi-data-dictionary-catalog
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Power BI Desktop

Install Power BI Desktop. Open:

```text
workbooks\pbip\chi-data-dictionary-catalog.pbip
```

Set **View → Zoom → 100%** for readable text.

---

## Publish ritual (every curation session)

### Steward

1. Open `workbooks/chi-steward-workbook.xlsx`.
2. Curate via **Steward_Queue** or **Concept_Explorer** (see `docs/demographics-pilot-plan.md`).
3. Update **Catalog**, **Dictionary**, **Source_Availability** (and ADT/CCDA sheets when relevant).
4. Save the workbook.
5. Hand off to **Publisher** (or become Publisher if you wear both hats).

### Publisher

```powershell
cd C:\AI\chi-data-dictionary-catalog
.venv\Scripts\activate
python scripts/import_steward_workbook_to_parquet.py
```

6. Open PBIP → **Home → Refresh**.
7. Spot-check **Concept Profile**, **Field guide** (slicers + detail table), and **Standards & Contexts** for at least one changed `semantic_id`. On **Standards & Contexts**, confirm:
   - **Governed value set codes** shows ~26 rows (OMB rollup + pilot codes incl. gender identity), not 900+ HL7 detailed race codes.
   - **HL7 ADT context** shows one row per CE field (`PID-10`, `PID-22`, `PID-16`) with `hl7_ce_encoding` like `PID-22.1^PID-22.2`.
8. Commit (see [Git commit policy](#git-commit-policy)).
9. Notify reviewers: “Published — please `git pull` and Refresh.”

### Reviewer

```powershell
cd C:\AI\chi-data-dictionary-catalog
git pull
```

Open PBIP → **Refresh** → verify the concept(s) under review.

---

## Git commit policy

**Commit when:** A publish cycle is complete and Power BI spot-check passed.

**Typical files:**

| File | Commit? | Notes |
|------|---------|-------|
| `workbooks/chi-steward-workbook.xlsx` | Yes | Source of human edits |
| `ddc-master_patient_catalog.parquet` | Yes | Published catalog |
| `ddc-master_patient_dictionary.parquet` | Yes | Published dictionary |
| `ddc-data_source_availability.parquet` | Yes | Source links |
| `ddc-hl7_adt_catalog.parquet` | Yes, if ADT_Mappings changed | |
| `ddc-ccda_catalog.parquet` | Yes, if CCDA_Mappings changed | |
| `ddc-value_set_binding.parquet` | Yes, if Value_Set_Bindings changed | |
| `ddc-value_set_member.parquet` | Yes, if Value_Set_Members changed | |
| `ddc-source_value_crosswalk.parquet` | Yes, if Source_Value_Crosswalk changed | |
| `docs/demographics-pilot-plan.md` | Yes, if status counts changed | Update “Where we are” |

**Commit message pattern:**

```text
Steward publish: Patient.race, Patient.ethnicity — approval + survivorship review
```

**Do not commit:** `.venv/`, `node_modules/`, local PBIP cache, secrets.

### Maintainer terminology rebuild (rare)

When HL7 expansions or county survivorship mappings change in repo scripts:

```powershell
python scripts/build_value_set_members.py --write-cache
python scripts/seed_county_master_crosswalk.py
python scripts/seed_gender_identity_terminology.py
python scripts/seed_partner_crosswalk_template.py
python scripts/enrich_parquet_for_pbi.py
python scripts/generate_steward_workbook.py
```

Steward reviews `Source_Value_Crosswalk` in Excel (`approval_status` starts as `draft`), then normal publish: import → Refresh → commit.

---

## Production checklist — close Phase 1 (five demographics)

Complete before calling the demographics pilot **operationally done**:

### Content

- [x] Replace placeholder `SHIE Data Governance` with **named stewards** on all five pilot rows (`Ajay Prashar`)
- [ ] All five `approval_status` = `Approved` (or documented exception in **Steward_Queue**)
- [x] `Patient.gender_id` CCDA path filled or explicitly documented as N/A (`partial`; note: govern via FHIR US Core Observation — rarely in CCDA)
- [ ] `data_quality_notes` reviewed against `docs/shie-standards-reference.md`
- [ ] Source_Availability: honest `availability` per `source_id` (not `unknown` without reason)

### Review

- [ ] Power BI **Concept Profile** verified for each of the five after publish
- [ ] Power BI **Standards & Contexts** shows ADT/CCDA where expected
- [ ] Checkboxes updated in `docs/demographics-pilot-plan.md` (per-attribute section)

### Process

- [ ] This runbook shared with stewards and reviewers
- [x] Publisher role assigned (**Ajay Prashar**)
- [ ] Standard clone path agreed (`C:\AI\chi-data-dictionary-catalog`)

---

## Production checklist — ongoing publish (each batch)

Use for every curation batch after Phase 1:

| Step | Done |
|------|------|
| Steward edits saved in workbook | ☐ |
| `import_steward_workbook_to_parquet.py` completed without error | ☐ |
| Power BI Refresh succeeded | ☐ |
| At least one `semantic_id` spot-checked on Concept Profile | ☐ |
| Git commit pushed (publisher) | ☐ |
| Reviewers notified | ☐ |
| `demographics-pilot-plan.md` “Where we are” updated if counts changed | ☐ |

---

## 90-day path (Level A, no SharePoint)

| Weeks | Focus | Exit signal |
|-------|--------|-------------|
| **1–2** | Close Phase 1 sign-off (five demographics) | All production checklist items above checked |
| **3** | Runbook in practice; first git-based publish cycle with a second reviewer | Reviewer can pull + Refresh without help |
| **4–6** | **Batch 2:** next 10–15 catalog rows (remaining demographics) | Each row Approved or excepted in Steward_Queue |
| **7–8** | Add **one** second source (`docs/adding-data-sources.md`) | Source_Availability pattern proven |
| **9–12** | **Batch 3:** next domain (per team priority) | Same publish ritual; no new tooling |

---

## Collaboration without SharePoint

| Need | Substitute |
|------|------------|
| Version history | Git commits + descriptive messages |
| “Who has the workbook?” | One steward edits at a time; coordinate in email/Teams |
| Passing drafts | Email `.xlsx` copy; publisher merges into repo workbook |
| Leadership review | Power BI screenshots or screen-share; optional PDF export |
| Approval audit | `approval_status`, `data_steward`, `last_modified_date`, Steward_Queue notes |

When SharePoint becomes available, move the workbook and published parquet to a shared library and add this runbook’s **Publisher** step as “save to shared folder” before import.

---

## When to run other scripts

| Script | When | Who |
|--------|------|-----|
| `import_steward_workbook_to_parquet.py` | **Every publish** | Publisher |
| `generate_steward_workbook.py` | After parquet rebuilt by other scripts | Maintainer |
| `seed_demographics_pilot.py` | Re-seed pilot content from plan text | Maintainer only |
| `enhance_pbip_report.py` | PBIP full layout regen (includes Field guide) | Maintainer only |
| `generate_pbip_model_guide.py` | Regenerate `ddc-application_guide.parquet` from manifest | Maintainer; after manifest or column changes |
| `add_pbip_documentation_page.py` | Field guide PBIP tab + semantic model table | Maintainer; after guide parquet regen |
| `add_pbip_start_here_page.py` | Start here tab (purpose + sources of truth) | Maintainer; safe to re-run |
| `patch_pbip_readability.py` | Slicer width, table word wrap, FHIR columns, vertical layout | Maintainer; safe to re-run |
| `seed_demographics_pilot.py` | Multiline `data_quality_notes` / survivorship for five pilots | After note edits |
| `build_*` / `split_*` / `build_standards_inventories.py` | Mapping CSV or schema rebuilds | Maintainer only |

Stewards should only need **import** for daily work.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Power BI shows stale data | Publisher ran import? Reviewer ran `git pull` + **Refresh**? |
| Parquet path error on open | Clone path must match `C:\AI\chi-data-dictionary-catalog` or re-point TMDL |
| Import script fails | Workbook open in Excel? Close file and retry |
| Excel repair prompt on open | See `docs/excel-workbook-generation-rules.md`; regenerate with `generate_steward_workbook.py` |
| UTF-8 BOM error on PBIP | PBIP JSON must be UTF-8 without BOM — see `docs/power-bi-concept-profile-setup.md` |
| Merge conflict on `.xlsx` | Avoid concurrent edits; publisher resolves with steward |

---

## Deferred until SharePoint or Power BI Service

| Capability | Trigger to add |
|------------|----------------|
| Shared workbook co-authoring | SharePoint library available |
| Scheduled dataset refresh | Power BI Service + gateway or shared parquet path |
| Web-only reviewers (no Desktop) | PBI Service publish |
| Automated import on save | CI pipeline or scheduled task on shared folder |

Do not block Level A on these.

---

## Related documents

| Doc | Use |
|-----|-----|
| `docs/demographics-pilot-plan.md` | What to curate; Phase 1–4 roadmap |
| `docs/excel-workbook-guide.md` | Sheet names, columns, publish ritual detail |
| `docs/power-bi-concept-profile-setup.md` | Open PBIP, zoom, refresh, path fixes |
| `docs/shie-standards-reference.md` | Terminology bindings for pilot attributes |
| `docs/adding-data-sources.md` | Second source onboarding (Phase 3) |
| `TECH-SPEC.md` | Schema and architecture depth |
