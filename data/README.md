# Data artifacts for CMT ADT and Master Patient

Archived on 2026-03-04:
- Active CSV inputs were moved to `data/archive/2026-03-04/`.
- Build scripts include fallback support to this archive location.
- To reactivate, copy needed files back into `data/` or pass explicit `--mapping` paths.

- **ccd_to_semantic_id_mapping.csv** — Maps CCD section, INV column (optional), entry type, and representative XML path to `semantic_id` and FHIR path. Used by `scripts/build_ccda_catalog_from_mapping.py` to build **ddc-ccda_catalog.parquet**. Aligns with **ccd_interface_mapping.md** (INV focus).
- **datasource_counts_by_account.csv** — Reference: record counts by AccountID and enterprise name for a given period (e.g. 2/2026). Add new rows or new period columns when refreshing counts; use for source-volume context and reporting.
- **l2_to_semantic_id_mapping.csv** — Maps CMT ADT L2 column names (and Segment/HL7 Field) to master patient `semantic_id` and FHIR path. Used by `scripts/build_adt_catalog_from_mapping.py` to build or extend `ddc-hl7_adt_catalog.parquet`. Includes PID, PV1, PV2, PD1, IN1, DG1. Rows that use `Encounter.*`, `Coverage.*`, or `Condition.*` appear in ADT catalog/inventory outputs when those elements exist in the master catalog.
- **`<source_id>_feed_segments.csv`** and **`<source_id>_feed_event_types.csv`** — Feed profile per data source (e.g. **cmt_feed_segments.csv** / **cmt_feed_event_types.csv** for CMT ADT). The app discovers all `*_feed_segments.csv` in `data/` and shows one sidebar expander per source. Same column shape for every source. See **docs/adding-data-sources.md** when adding new sources.

See **docs/cmt-adt-feed-and-master-patient.md** for how these support the Master Patient effort.
