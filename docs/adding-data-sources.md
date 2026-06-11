# Adding additional data sources

How to register another **data source** so CHI can document feed coverage and (optionally) rebuild the source availability matrix.

**Viewer today:** Power BI PBIP (`workbooks/pbip/chiddc.pbip`) - not a separate Streamlit or sidebar app.

---

## Current state

- **CMT ADT** feed profile CSVs live under `data/archive/2026-03-04/` (`cmt_feed_segments.csv`, `cmt_feed_event_types.csv`).
- **`scripts/build_data_source_availability.py`** discovers `*_feed_segments.csv` under `data/` and archive fallback, then writes `ddc-data_source_availability.parquet`.
- **Message-format catalogs** (`ddc-hl7_adt_catalog`, `ddc-ccda_catalog`) are **source-agnostic** - they map `semantic_id` to HL7/CCDA structure, not to one vendor feed.
- **Steward workbook** `Source_Availability` sheet is the human edit surface after import.

---

## When you add another source

### 1. Add feed profile CSVs

Use the same shape as CMT:

| File | Columns |
|------|---------|
| `data/<source_id>_feed_segments.csv` | `segment_id`, `data_received`, `notes` |
| `data/<source_id>_feed_event_types.csv` | `event_type`, `file_count`, `percentage_of_total`, `description` |

Choose a short **source_id** (e.g. `sutter_adt`, `local_jail`). Place files in `data/` or keep under `data/archive/YYYY-MM-DD/` and rely on script fallback (see `data/README.md`).

### 2. Rebuild source availability

```powershell
python scripts/build_data_source_availability.py
python scripts/generate_steward_workbook.py
```

Stewards refine rows in Excel `Source_Availability`, then normal publish: import -> Refresh.

### 3. Optional reference counts

Add rows to `data/archive/2026-03-04/datasource_counts_by_account.csv` (or a new period file) for volume context.

### 4. Partner intake (separate track)

For new partners supplying field/code inventories, use `workbooks/chi-partner-intake-workbook.xlsx` and `docs/partner-crosswalk-template.md` - not the feed segment CSVs alone.

### 5. Document

- Add a line to `data/README.md` for the new CSV pair.
- If ADT/CCD mappings change, update mapping CSVs and run `build_adt_catalog_from_mapping.py` / `build_ccda_catalog_from_mapping.py`.

---

## Summary

| What you add | Where | Effect |
|--------------|-------|--------|
| Feed segments / event types | `data/<source_id>_feed_*.csv` | Included in source availability build |
| Steward edits | `Source_Availability` sheet | Published parquet + Power BI Concept Profile |
| Record counts | `datasource_counts_by_account.csv` | Reference only (no PBIP page yet) |
| New message format | New mapping CSV + catalog build script | New `ddc-*_catalog.parquet` rows |

---

## Related

- `docs/cmt-adt-feed-and-master-patient.md`
- `docs/operational-runbook.md`
- `data/README.md`
