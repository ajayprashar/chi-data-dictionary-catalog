# Excel Workbook Generation Rules

Lessons learned building `chi-steward-workbook.xlsx` and `chi-partner-intake-workbook.xlsx` with **openpyxl**. Follow these rules when changing generators so Excel opens files without the *"problem with some content"* repair prompt.

**Generators:** `scripts/generate_steward_workbook.py`, `scripts/generate_intake_workbook.py`  
**Shared helpers:** `scripts/excel_workbook_common.py`

---

## What triggers Excel repair prompts

Excel is validating **workbook XML**, not your catalog data. Common openpyxl issues:

| Symptom | Typical cause |
|---------|----------------|
| Repair prompt on open | Invalid or duplicate Table / AutoFilter XML |
| `#NAME?` in formulas | `XLOOKUP` on Excel versions that lack it |
| `#REF!` in Concept_Explorer | Formulas reference Table names that Excel removed during repair |
| Dropdowns disappear after repair | openpyxl `DataValidation` XML stripped or corrupted |

**Not causes:** parquet files, missing live links to parquet, or steward data values.

---

## Required practices (DO)

### 1. Use real Excel Tables with consistent names

- **Steward pattern:** `chi_{artifact}` — e.g. `chi_catalog`, `chi_dictionary`
- **Intake pattern:** `chi_intake_{artifact}` — e.g. `chi_intake_field_inventory`
- Names: snake_case, unique across the workbook, start with a letter
- Create tables only via `add_excel_table()` in `excel_workbook_common.py`

### 2. One AutoFilter per sheet — inside the Table only

`add_excel_table()` registers AutoFilter on the Table definition. **Do not** also set `ws.auto_filter.ref` on the worksheet. Duplicate filters triggered repair prompts.

### 3. Use INDEX/MATCH for cross-sheet lookups

`Concept_Explorer` uses structured references with INDEX/MATCH:

```excel
=IF($B$3="","",IFERROR(INDEX(chi_catalog[uscdi_element],MATCH($B$3,chi_catalog[semantic_id],0)),""))
```

Do **not** use `XLOOKUP` in generated workbooks (unsupported on many enterprise Excel builds).

### 4. Keep headers valid

- Every column header must be a **non-empty string**
- Column names must be **unique** on each sheet (no duplicates, even different case)
- No blank header cells between columns (breaks Table XML)

### 5. Put allowed values in Lookup_Lists

Use a `Lookup_Lists` sheet and **Table_Index** for reference. Partners and stewards copy/paste values. Do not generate dropdown validations in POC workbooks.

### 6. Regenerate workbooks from scripts

After parquet or schema changes:

```powershell
python scripts/generate_steward_workbook.py
python scripts/generate_intake_workbook.py
```

Do not hand-edit Table definitions in XML-prone ways and expect them to round-trip through openpyxl.

---

## Forbidden practices (DO NOT)

| Do not | Why |
|--------|-----|
| `ws.auto_filter.ref = ...` after `add_excel_table()` | Duplicate AutoFilter → repair prompt |
| `DataValidation` / dropdown lists via openpyxl | Corrupt or stripped XML → repair prompt |
| `XLOOKUP` in generated formulas | `#NAME?` on older Excel |
| Table structured refs without a real Table object | `#REF!` after repair |
| Mix `docs/templates/` path (legacy) | Working files live in `workbooks/` |
| Assume Excel ↔ parquet is live-linked | Sync is manual via import/generate scripts |

---

## Architecture reminders

```text
workbooks/*.xlsx  ←edit→  import_steward_workbook_to_parquet.py  →  ddc-*.parquet
ddc-*.parquet  →  generate_steward_workbook.py  →  workbooks/*.xlsx
```

- Excel tables are the **human editing surface**
- Parquet is the **machine layer** in the repo
- Import reads **sheet tab names** (`Catalog`, `Dictionary`, …), not Excel Table display names

---

## Checklist before committing generator changes

1. Regenerate both workbooks
2. Open `chi-steward-workbook.xlsx` in Excel — **no repair prompt**
3. Confirm **Table Design** shows expected name (e.g. `chi_catalog`)
4. Test **Concept_Explorer** with `Patient.race` in B3 — values appear, no `#NAME?` / `#REF!`
5. Run `python scripts/import_steward_workbook_to_parquet.py` — row counts unchanged
6. Zip check (optional): worksheet XML has **0** `dataValidation`, **0** worksheet-level `<autoFilter` when Tables are used

---

## Related documents

- `docs/excel-workbook-guide.md` — operational POC guide
- `README.md` — quick start
