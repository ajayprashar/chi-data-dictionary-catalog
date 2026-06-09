# Power BI Concept Profile

Read-only **governed catalog and dictionary viewer** (see `docs/product-vision.md`). Excel authors data; Power BI presents governance, standards, and ADT/CDA/FHIR contexts.

**Recommended:** open the PBIP project in Power BI Desktop:

```text
workbooks/pbip/chi-data-dictionary-catalog.pbip
```

The report includes three pages:

| Page | Purpose |
|------|---------|
| **Concept Profile** | One `semantic_id` — governance, FHIR/US Core, survivorship, sources |
| **Standards & Contexts** | Same slicer — terminology notes, **HL7 ADT** fields, **C-CDA** paths, layered standards banner |
| **Governance Overview** | Portfolio KPIs, classification/approval charts, full concept table |

Semantic model tables: catalog, dictionary, source availability, **ADT catalog**, **CCDA catalog**, **value set members**, **source crosswalk** (joined on `semantic_id`).

After steward Excel edits: `python scripts/import_steward_workbook_to_parquet.py` → **Refresh** in Power BI.

**Maintainers only** (regenerate report layout): `python scripts/enhance_pbip_report.py`

### Readability (zoom and page size)

The report uses **Actual size** (not Fit to page) and a **high-contrast** theme (blue / yellow / black on white).

**Table readability:** each table has three visual layers — **dark blue title band** (visual title), **light blue column header row** (field names), **white/zebra data rows**. If column headers look like the title after manual edits, select the visual → **Format** → **Reset to default** (theme + `enhance_pbip_report.py` set the header row separately).

In Power BI Desktop:

1. **View → Zoom → 100%** (avoid 79% or lower — text looks much smaller).
2. **View → Page view → Actual size** (if available).
3. Use **Fit to page** only when presenting on a small screen.

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| Text too small / hard to read | Set zoom to **100%**; pages are laid out at Actual size with 12–13pt table text. |
| UTF-8 BOM error on open | PBIP JSON must be UTF-8 **without** BOM. Do not edit with PowerShell `Set-Content -Encoding utf8`; use Python or VS Code “UTF-8” (not “UTF-8 with BOM”). |
| Yellow banner: *"Some tables have incomplete or no data"* | Click **Refresh now** (or **Home → Refresh**). Parquet must exist at `C:\AI\chi-data-dictionary-catalog\ddc-*.parquet`. |
| Red error icons on measures | Close the report, reopen `chi-data-dictionary-catalog.pbip`. KPI measures live under `ddc-master_patient_catalog` → **Governance KPIs** (not a separate metrics table). |
| Source shows wrong `source_id` | Run `import_steward_workbook_to_parquet.py`, then Refresh. |

---

## Manual setup (if not using PBIP)

Connect Power BI Desktop directly to the parquet files the Excel workflow already produces.

---

## What you need running

Only the steward round-trip you already have:

1. Edit `workbooks/chi-steward-workbook.xlsx`
2. `python scripts/import_steward_workbook_to_parquet.py`
3. Open or refresh your `.pbix` in Power BI Desktop

---

## One-time setup in Power BI Desktop

### 1. Load three tables

Power BI’s **Parquet** dialog often says “URL” even for local files. That field accepts a **full Windows path** — you are not required to use a web address.

**Option A — paste a local path (simplest)**

1. **Home → Get data → Parquet** (under *Database* or search “Parquet”).
2. In the path/URL box, paste the full path to one file, for example:

   ```text
   C:\AI\chi-data-dictionary-catalog\ddc-master_patient_catalog.parquet
   ```

3. **OK** → preview loads → **Load** (or **Transform data** if you want to rename the query).
4. Repeat for the other two files.

| File | Role |
|------|------|
| `ddc-master_patient_catalog.parquet` | Business context |
| `ddc-master_patient_dictionary.parquet` | FHIR, survivorship |
| `ddc-data_source_availability.parquet` | Source links |

Rename queries in Power Query if helpful: `Catalog`, `Dictionary`, `Sources`.

**Option B — pick from a folder**

1. **Get data → Folder** → browse to `C:\AI\chi-data-dictionary-catalog`.
2. **Transform data** → filter **Extension** = `.parquet` → keep the three `ddc-*` files above → **Combine** (or load each file as its own query).

**Option C — if Parquet still won’t take a local path**

1. **Get data → Blank query**.
2. **Advanced editor** and paste (adjust path):

   ```powerquery
   let
       Source = Parquet.Document(File.Contents("C:\AI\chi-data-dictionary-catalog\ddc-master_patient_catalog.parquet"))
   in
       Source
   ```

3. Repeat for each file.

**Close & apply** when all three queries are loaded.

### 2. Relationships (Model view)

Left sidebar → **Model** (diagram icon). Connect all three tables on `semantic_id`:

| From | To | Cardinality |
|------|-----|-------------|
| `ddc-master_patient_catalog` | `ddc-master_patient_dictionary` | one-to-one |
| `ddc-master_patient_catalog` | `ddc-data_source_availability` | one-to-one (or one-to-many later) |

If lines already exist from auto-detect, you are done. Return to **Report** view (chart icon).

---

### 3. Build the page — tables first, slicer last

Stay in **Report** view. You should see a blank white canvas.

Until you add the slicer (step 4), each table shows **all 46 rows**. That is normal — you are checking that fields load correctly.

#### Table 1 — Catalog (business context)

1. Click empty space on the canvas.
2. **Visualizations** pane (right) → click the **Table** icon (grid).
3. **Data** pane (far right) → expand `ddc-master_patient_catalog`.
4. Check these fields (click each checkbox):

   - `semantic_id`
   - `uscdi_element`
   - `uscdi_description`
   - `classification`
   - `data_steward`
   - `approval_status`

5. Drag the visual wider. You should see 46 rows.

#### Table 2 — Dictionary (FHIR and survivorship)

1. Click empty space below Table 1 (so you do not replace it).
2. **Visualizations** → **Table** again.
3. Expand `ddc-master_patient_dictionary` → check:

   - `semantic_id`
   - `fhir_r4_path`
   - `chi_survivorship_logic`
   - `data_source_rank_reference`

#### Table 3 — Sources (where data comes from)

1. Click empty space below Table 2.
2. **Visualizations** → **Table** again.
3. Expand `ddc-data_source_availability` → check:

   - `semantic_id`
   - `source_id`
   - `availability`
   - `completeness_pct`
   - `notes`

**Checkpoint:** Three tables on the page, each with data. Scroll Table 1 and confirm `Patient.race` appears in the `semantic_id` column.

---

### 4. Add the slicer (last)

1. Click empty space on the canvas (e.g. top-left above Table 1).
2. **Visualizations** → **Slicer** icon (funnel).
3. **Data** → `ddc-master_patient_catalog` → check **`semantic_id`** only.
4. In the slicer visual, click the dropdown and choose **`Patient.race`**.

**Checkpoint:** All three tables should collapse to **one row** each (for `Patient.race`).

Optional: with the slicer selected → **Format** (paint roller) → **Slicer settings** → **Options** → Style → **Dropdown** (easier than a long list).

---

### 5. Save

**File → Save as** → `workbooks/chi-steward-catalog.pbix` (next to `chi-steward-workbook.xlsx`).

---

## After Excel edits

```powershell
python scripts/import_steward_workbook_to_parquet.py
```

Then **Refresh** in Power BI Desktop. No other scripts.

---

## Optional later

Add more parquets (ADT, CCDA, FHIR, Business Rules) with the same `semantic_id` key when you need mapping drill-down. Not required for the demographics POC.
