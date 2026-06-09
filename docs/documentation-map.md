# Documentation Map (Current vs Historical)

Use this page as the index for which documents are actively maintained versus kept for historical context.

---

## Canonical (actively maintained)

- `README.md`
  - Entry point for the 2-layer operating model, pipeline commands, and core files.
- `TECH-SPEC.md`
  - Architecture, data model, and implementation behavior.
- `docs/demographics-pilot-plan.md`
  - Living pilot status, phased plan, definition of done, per-attribute checklist.
- `docs/excel-workbook-guide.md`
  - `workbooks/` living Excel files, governance workflow (Excel → parquet → Power BI), publish ritual, and round-trip pipeline.
- `docs/excel-workbook-generation-rules.md`
  - openpyxl DO/DON'T rules so Excel opens workbooks without repair prompts.
- `docs/power-bi-concept-profile-setup.md`
  - Power BI PBIP viewer — open, refresh, troubleshooting (read surface after Excel import).
- `docs/jupyter-duckdb-parquet-setup.md`
  - Optional ad-hoc DuckDB queries over Parquet (not the primary viewer).

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

Notion pages are treated as planning/reference input. The repo's canonical documents above are the source-controlled implementation contract.
