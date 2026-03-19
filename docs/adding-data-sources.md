# Adding Additional Data Sources

This doc describes how to add more **data source profiles** (like the CMT ADT feed) so the catalog viewer can show segment availability, event types, or other source-specific context for each source.

---

## Current state

- **One source profile in the app**: CMT (PointClickCare) ADT, via `data/cmt_feed_segments.csv` and `data/cmt_feed_event_types.csv`. Shown in the sidebar under "CMT ADT feed profile".
- **Message-format catalogs** (ADT, CCD) are **source-agnostic**: they map semantic_id to HL7/CCD structure. They are not tied to a specific vendor or feed.
- **Master catalog** is also source-agnostic: one set of elements (Patient, Encounter, Coverage, Condition) regardless of which sources populate them.

---

## When you add another data source

### 1. Add a feed profile for that source

Use the **same CSV shape** as CMT so the app can load it without code changes:

- **Segments** (optional): `data/<source_id>_feed_segments.csv`  
  Columns: `segment_id`, `data_received`, `notes`  
  Example: `data/sutter_adt_feed_segments.csv`, `data/whhs_adt_feed_segments.csv`.

- **Event types** (optional): `data/<source_id>_feed_event_types.csv`  
  Columns: `event_type`, `file_count`, `percentage_of_total`, `description`  
  Example: `data/sutter_adt_feed_event_types.csv`.

Choose a short **source_id** (e.g. `sutter_adt`, `whhs_adt`, `welligent_ccd`). The app discovers any file pair matching `*_feed_segments.csv` / `*_feed_event_types.csv` in `data/` and shows one expander per source in the sidebar.

### 2. No change to message-format catalogs

- **ddc-hl7_adt_catalog.parquet** and **ddc-ccda_catalog.parquet** stay source-agnostic. They describe *what* ADT/CCD fields map to which semantic_id, not *which* source sends them.
- If the new source uses the same format (e.g. another ADT feed), the same ADT catalog applies. If you need source-specific notes (e.g. "Sutter sends PID-11, CMT does not"), you can add a **source column** to the mapping later or keep that in the feed profile notes.

### 3. Optional: source-specific mapping or quality

- **Datasource counts**: Add rows to `data/datasource_counts_by_account.csv` for the new source (account_id, enterprise_name, period, count).
- **Quality or fill rates**: For now, keep that in the feed profile CSV (e.g. in `notes`) or in a separate doc. A future step could add a `data/<source_id>_field_quality.csv` and a small UI block if needed.

### 4. Document the source

- Add a line to **data/README.md** listing the new `*_feed_segments.csv` / `*_feed_event_types.csv` and what they represent.
- If the source has a different message format (e.g. FHIR API), define how it maps to semantic_id (e.g. a new mapping CSV and optional catalog parquet) and reference that in the PRD.

---

## Summary

| What you add | Where it lives | App behavior |
|--------------|----------------|--------------|
| New ADT/CCD feed profile (segments, event types) | `data/<source_id>_feed_segments.csv`, `data/<source_id>_feed_event_types.csv` | Sidebar shows one expander per discovered source (e.g. "CMT feed profile", "Sutter ADT feed profile"). |
| New source’s record counts | `data/datasource_counts_by_account.csv` | No UI change yet; use for reference or future summary. |
| New message format (e.g. FHIR API) | New mapping CSV + optional new catalog parquet | Extend app to load and display that catalog when you’re ready. |

The app is set up to **discover** all `*_feed_segments.csv` files in `data/` and show each source’s profile in its own sidebar expander, so adding a second (or third) source is a matter of adding the two CSVs and optionally updating data/README.md.
