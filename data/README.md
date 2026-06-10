# Data artifacts for CMT ADT and Master Patient

**Active mapping CSVs** were archived on 2026-03-04 under `data/archive/2026-03-04/`. Build scripts resolve paths with archive fallback unless you pass `--mapping` or copy files back to `data/`.

## Archived CSV inputs (`data/archive/2026-03-04/`)

| File | Used by |
|------|---------|
| `ccd_to_semantic_id_mapping.csv` | `scripts/build_ccda_catalog_from_mapping.py` -> `ddc-ccda_catalog.parquet` |
| `l2_to_semantic_id_mapping.csv` | `scripts/build_adt_catalog_from_mapping.py` -> `ddc-hl7_adt_catalog.parquet` |
| `cmt_feed_segments.csv`, `cmt_feed_event_types.csv` | `scripts/build_data_source_availability.py` |
| `datasource_counts_by_account.csv` | Reference counts (not loaded by PBIP) |

Aligns with `ccd_interface_mapping.md` for CCD paths.

## Python modules (curated, not CSV)

| Module | Role |
|--------|------|
| `county_survivorship_mappings.py` | County SQL -> crosswalk seed (`scripts/seed_county_master_crosswalk.py`) |
| `partner_crosswalk_template.py` | Partner intake example rows (`scripts/seed_partner_crosswalk_template.py`) |

## Terminology cache (`data/terminology/`)

HL7 `$expand` offline cache for `build_value_set_members.py --offline`. See `data/terminology/README.md`.

## Adding a new source

See **`docs/adding-data-sources.md`** - add `*_feed_segments.csv` / `*_feed_event_types.csv`, rebuild source availability, update steward workbook.

See **`docs/cmt-adt-feed-and-master-patient.md`** for CMT ADT context.
