# Repository cleanup methodology

How to keep **chi-data-dictionary-catalog** aligned with what is actually running today (Level A demographics pilot + PBIP viewer).

**Index:** `docs/documentation-map.md` lists canonical vs historical docs.

---

## Principles

1. **Canonical docs win** - If `docs/archive/*` or `TECH-SPEC.md` disagrees with `README.md`, `docs/operational-runbook.md`, and parquet/PBIP reality, update the canonical doc or add a dated note; do not treat archive snapshots as roadmap.
2. **One role per artifact** - Steward Excel authors; import publishes parquet; PBIP reads; scripts are either **publish pipeline**, **maintainer rebuild**, or **optional expansion** - not all three.
3. **Delete only with evidence** - Remove files that are untracked in docs/runbook, unreferenced in code, and superseded by another path. When unsure, gitignore or move to `docs/archive/` instead of delete.
4. **Historical stays labeled** - `docs/archive/` is read-only context; never merge archive prose into runbooks without rewriting for current state.

---

## What is active (do not remove)

| Layer | Artifacts |
|-------|-----------|
| Authoring | `workbooks/chi-steward-workbook.xlsx`, optional `chi-partner-intake-workbook.xlsx` |
| Published data | Root `ddc-*.parquet` (commit after steward publish) |
| Viewer | `workbooks/pbip/chi-data-dictionary-catalog.pbip` |
| Publish | `import_steward_workbook_to_parquet.py`, `generate_steward_workbook.py` |
| Demographics pilot | `seed_demographics_pilot.py`, value set / crosswalk seed scripts (see runbook maintainer section) |
| PBIP layout | `add_pbip_start_here_page.py`, `patch_pbip_readability.py`, `enhance_pbip_report.py` (full regen) |
| Mapping inputs | `data/archive/2026-03-04/*.csv` (scripts use archive fallback) |
| Terminology cache | `data/terminology/*.expansion.json` (offline HL7 expand) |

---

## Script tiers

| Tier | Scripts | When to run |
|------|---------|-------------|
| **Publish** | `import_steward_workbook_to_parquet.py` | Every steward session (publisher) |
| **Regenerate Excel** | `generate_steward_workbook.py` | After parquet rebuild from scripts |
| **Maintainer terminology** | `build_value_set_members.py`, `seed_county_master_crosswalk.py`, `seed_gender_identity_terminology.py`, `seed_partner_crosswalk_template.py`, `enrich_parquet_for_pbi.py` | Rare; see `docs/operational-runbook.md` |
| **PBIP** | `add_pbip_start_here_page.py`, `patch_pbip_readability.py`, `enhance_pbip_report.py` | Layout/copy changes only |
| **Optional expansion** | `build_adt_catalog_from_mapping.py`, `build_ccda_catalog_from_mapping.py`, `build_data_source_availability.py`, `build_standards_inventories.py`, `split_to_catalog_and_dictionary.py`, `generate_intake_workbook.py` | New sources or greenfield catalog build |
| **Pilot seed** | `seed_demographics_pilot.py`, `seed_value_sets_pilot.py` | Reset pilot rows (careful: `seed_value_sets_pilot` overwrites all members) |

Remove scripts only when: zero references in repo, not in this table, and superseded.

---

## Documentation tiers

| Tier | Paths |
|------|--------|
| **Canonical** | `README.md`, `TECH-SPEC.md`, `docs/product-vision.md`, `docs/sources-of-truth.md`, `docs/operational-runbook.md`, `docs/demographics-pilot-plan.md`, excel + power-bi guides |
| **Reference** | `docs/shie-standards-reference.md`, `docs/crosswalk-model.md`, `docs/partner-crosswalk-template.md`, `data/README.md`, `ccd_interface_mapping.md` |
| **Historical** | `docs/archive/*` - do not delete; keep status banner |

Quarterly review: search for "defer", "future", "app", "sidebar", "Streamlit", "Airtable", `.pbix` - fix or mark legacy.

---

## Generated / local (gitignore, do not commit)

- `.tmp/` - debug JSON exports
- `workbooks/*.pbix` - superseded by PBIP
- `workbooks/pbip/**/.pbi/cache.abf`, `localSettings.json`, `editorSettings.json`
- `.venv/`, `__pycache__/`

---

## Cleanup checklist (repeatable)

1. `git status` - confirm user committed before cleanup.
2. Remove gitignored junk; delete orphaned scripts (grep repo for imports/refs).
3. Align `TECH-SPEC.md` POC/deferred language with `docs/crosswalk-model.md` and parquet list.
4. Fix docs that describe a removed UI (old Streamlit/sidebar viewer).
5. Update `docs/documentation-map.md` if adding/removing canonical docs.
6. Run publish smoke test: `import_steward_workbook_to_parquet.py` + open PBIP Refresh.
7. Commit with message: `chore: repo cleanup - <what changed>`.

---

## Last cleanup (2026-06)

- Removed: legacy `chi-data-dictionary-catalog.pbix`, `.tmp/` JSON exports, orphaned `enrich_dictionary_fhir_profiles.py`
- Updated: `docs/adding-data-sources.md`, `data/README.md`, `TECH-SPEC.md` POC scope, power-bi legacy manual section
- Added: this methodology doc
