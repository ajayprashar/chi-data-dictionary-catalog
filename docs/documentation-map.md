# Documentation Map (Current vs Historical)

Use this page as the index for which documents are actively maintained versus kept for historical context.

---

## Canonical (actively maintained)

- `README.md`
  - Entry point for Airtable-first setup, pipeline commands, and core files.
- `TECH-SPEC.md`
  - Architecture, data model, and implementation behavior.
- `docs/airtable-setup.md`
  - Airtable setup, workflow, interface specification, standards inventories, and verification guidance.
- `docs/jupyter-duckdb-parquet-setup.md`
  - Notebook and DuckDB execution guidance.

## Reference (domain/source-specific)

- `docs/cmt-adt-feed-and-master-patient.md`
  - CMT ADT profile and how it maps into the catalog model.
- `docs/adding-data-sources.md`
  - Pattern for onboarding additional source systems.
- `data/README.md`
  - Mapping CSV artifact definitions in `data/`.
- `ccd_interface_mapping.md`
  - CCD field mapping reference for expansion work.

## Historical snapshots (not source of truth)

- `docs/archive/EVALUATION.md`
  - Point-in-time interoperability evaluation and recommendations.
- `docs/archive/hl7_ccd_fhir_consideration.md`
  - Strategy draft and historical architecture analysis.
- `docs/archive/GAPS-CLOSED.md`
  - Point-in-time implementation summary of resolved gaps.
- `docs/archive/CLEANUP-SUMMARY.md`
  - Point-in-time cleanup event summary.

When content conflicts, prefer the canonical set first.
