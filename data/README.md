# Data artifacts for CMT ADT and Master Patient

- **ccd_to_semantic_id_mapping.csv** — Maps CCD section, INV column (optional), entry type, and representative XML path to `semantic_id` and FHIR path. Used by `scripts/build_ccda_catalog_from_mapping.py` to build **ccda_catalog.parquet**. Aligns with **ccd_interface_mapping.md** (INV focus).
- **datasource_counts_by_account.csv** — Reference: record counts by AccountID and enterprise name for a given period (e.g. 2/2026). Add new rows or new period columns when refreshing counts; use for source-volume context and reporting.
- **l2_to_semantic_id_mapping.csv** — Maps CMT ADT L2 column names (and Segment/HL7 Field) to master patient `semantic_id` and FHIR path. Used by `scripts/build_adt_catalog_from_mapping.py` to build or extend `hl7_adt_catalog.parquet`. Includes PID, PV1, PV2, PD1, IN1, DG1. Rows that use `Encounter.*`, `Coverage.*`, or `Condition.*` will only appear in the Streamlit element-detail “Message-format mappings” when those elements exist in the master catalog.
- **cmt_feed_segments.csv** — CMT feed segment availability (data received Y/N). Shown in the Streamlit sidebar when present. Source-specific; not part of the source-agnostic ADT catalog.
- **cmt_feed_event_types.csv** — CMT ADT event type distribution (A01, A02, A03, A08) and percentages. Shown in the Streamlit sidebar when present. A08 (update) ~93% of volume.

See **docs/cmt-adt-feed-and-master-patient.md** for how these support the Master Patient effort.
