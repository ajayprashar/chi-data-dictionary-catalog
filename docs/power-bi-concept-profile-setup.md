# Power BI Concept Profile

Read-only **governed catalog and dictionary viewer** (see `docs/product-vision.md`). Excel authors data; Power BI presents governance, standards, and ADT/CDA/FHIR contexts.

**Recommended:** open the PBIP project in Power BI Desktop:

```text
workbooks/pbip/chi-data-dictionary-catalog.pbip
```

The report includes seven tabs (left-to-right):

| Page | Purpose |
|------|---------|
| **Guide · Start here** | Purpose, sources-of-truth layers, how to navigate the report (static text; cream canvas) |
| **Guide · Demo tour** | 5-minute guided tour (default landing in demo package; cream canvas) |
| **Guide · National standards** | Static lookup of external authorities (FHIR R4, USCDI, terminology; cream canvas) |
| **Standards & Contexts** | Per `semantic_id` - FHIR/terminology, value sets, crosswalk, **HL7 ADT**, **C-CDA** (no survivorship column on FHIR table) |
| **Concept Profile** | One `semantic_id` - governance, FHIR/US Core, **survivorship**, sources |
| **Guide · Field guide** | In-report column reference + curation gaps (slicers; cream canvas) |
| **Governance Overview** | Portfolio KPIs, classification/approval charts, full concept table |

Add or refresh **Start here** only: `python scripts/add_pbip_start_here_page.py` (does not rebuild other pages).

Regenerate **Field guide** (parquet + page):

```powershell
python scripts/validate_pbip_manifest.py
python scripts/generate_pbip_model_guide.py
python scripts/add_pbip_documentation_page.py
```

The Field guide tab includes **page summary cards**, **steward workflow** (Excel sheet → import → Refresh), an **editable in Excel** slicer, column detail with `steward_action` / `review_on_page`, and a **curation gaps** table (`ddc-application_guide_gaps.parquet`) built from live catalog/dictionary parquet. Regenerate gaps after each steward publish. After changing PBIP table columns, update `data/pbip_report_manifest.py` so validation stays green.

**Default landing page:** **Guide · Demo tour** in the demo package; **Standards & Contexts** in maintainer full regen unless overridden. Guide tabs use a cream canvas and `Guide ·` prefix; functional tabs use a white canvas.

### Semantic model: nine tables

| Group | Tables | Source |
|-------|--------|--------|
| **Governed data (7)** | `ddc-master_patient_catalog`, `ddc-master_patient_dictionary`, `ddc-data_source_availability`, `ddc-hl7_adt_catalog`, `ddc-ccda_catalog`, `ddc-value_set_member`, `ddc-source_value_crosswalk` | Steward workbook → `import_steward_workbook_to_parquet.py`; joined on `semantic_id` |
| **Field guide (2)** | `ddc-application_guide`, `ddc-application_guide_gaps` | **Not** from steward import; `generate_pbip_model_guide.py` from manifest + curation checks |

The two guide tables exist so **Guide · Field guide** can use slicers and tables instead of hard-coded text. They document the report and flag missing steward fields; they are not part of the catalog spine. Full rationale: **`docs/faq.md`** → *Why does the PBIP semantic model have nine tables?*

**Pages are task lenses, not catalog-vs-dictionary tabs.** The catalog/dictionary split is per column and per source table; pages mix both by design.

After steward Excel edits: `python scripts/import_steward_workbook_to_parquet.py` → **Refresh** in Power BI.

**Maintainers only** (regenerate report layout): `python scripts/enhance_pbip_report.py`

**Readability layout** (slicer width, FHIR table word wrap, multiline-friendly tables) without a full regen:

```powershell
python scripts/patch_pbip_readability.py
```

Layout constants live in `scripts/pbip_layout_constants.py` - keep in sync with `enhance_pbip_report.py`. After a full `enhance_pbip_report.py` run, re-run `patch_pbip_readability.py` if needed.

Pilot dictionary notes use `\n` line breaks in `scripts/seed_demographics_pilot.py`; re-seed with `python scripts/seed_demographics_pilot.py` and publish import when notes change.

### Readability (zoom and page size)

The report uses **Actual size** (not Fit to page) and a **high-contrast** theme (blue / yellow / black on white).

**Table readability:** each table has three visual layers - **dark blue title band** (visual title), **light blue column header row** (field names), **white/zebra data rows**. If column headers look like the title after manual edits, select the visual → **Format** → **Reset to default** (theme + `enhance_pbip_report.py` set the header row separately).

In Power BI Desktop:

1. **View → Zoom → 100%** (avoid 79% or lower - text looks much smaller).
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
| **Unable to save document** / invalid path when saving `.pbix` | Not caused by repo cleanup. This project uses **PBIP + TMDL + PBIR**; **Save a copy → PBIX** is unreliable on some Desktop builds (especially Microsoft Store, June 2026). Use the **demo package** below instead of fighting PBIX export. |
| Report opens but has no data | Parquet must be at `C:\AI\chi-data-dictionary-catalog\ddc-*.parquet` (hardcoded in the model). Refresh after parquets are in place. |
| **Transform data** → query preview: `Container exited unexpectedly` **0x80131623** | **Not corrupt parquet.** Known Power BI Mashup crash when previewing parquet queries inside PBIP (common on **Microsoft Store** app, **US Gov cloud**, June 2026). **Close Power Query** without Apply if broken; use **Home → Refresh** on the report canvas instead. Do not use Transform data for routine demos. Try **EXE installer**, clear `%LocalAppData%\Microsoft\Power BI Desktop\Cache`, or re-run `python scripts/package_pbi_demo.py` (rewrites parquets to Parquet 1.0). |
| **Unable to save auto recovery file** / invalid path in `...\Power BI Desktop Store App\TempSaves\` | **Not corrupt PBIP.** Store-app auto-recovery cannot write its temp `.pbix`. Click **Close** and demo anyway - switch to **Report** view → **Home → Refresh**. On demo PC: **File → Options → Global → Auto recovery** → uncheck; or use the **EXE** installer. Repo sets `"enableAutoRecovery": false` in `chi-data-dictionary-catalog.pbip`. |

---

## Demonstrating on another computer

**Recommended:** do **not** depend on exporting a `.pbix`. Ship PBIP + parquet instead.

### Create a demo zip (on your machine)

```powershell
python scripts/package_pbi_demo.py
```

Writes `workbooks/chi-ddc-demo-YYYY-MM-DD.zip` containing:

- 9 `ddc-*.parquet` files (7 governed data + 2 field guide; rewritten to Parquet 1.0 for Desktop compatibility)
- `workbooks/chi-steward-workbook.xlsx` and `workbooks/chi-partner-intake-workbook.xlsx`
- `workbooks/pbip/` (report + semantic model; excludes local `.pbi` cache)

### On the demo PC

1. Extract the zip to **`C:\AI\chi-data-dictionary-catalog\`** (same path the model expects).
2. Install [Power BI Desktop](https://www.microsoft.com/en-us/download/details.aspx?id=58494) (EXE installer preferred over Store for PBIP work).
3. Open `workbooks\pbip\chi-data-dictionary-catalog.pbip`.
4. **Home → Refresh**.
5. **View → Zoom → 100%**.

If you cannot use `C:\AI\chi-data-dictionary-catalog`: **Transform data → Data source settings** → point all nine parquet queries at the folder where you placed `ddc-*.parquet`.

### Optional: single-file `.pbix` (often fails)

Only if you need one portable file:

1. Open the **repo** PBIP (`workbooks/pbip/...`), not a copy under `C:\AI\Incoming\`.
2. **Home → Refresh** (all queries must succeed).
3. **File → Save a copy** → `C:\Temp\chi-demo.pbix` (short path; use file picker).
4. Disable **OneDrive save** preview feature if the dialog misbehaves.

If export still fails, use the demo zip or **Publish** to a Power BI workspace and download `.pbix` from the service.

**Excel workbooks** are included in the demo zip for stewardship walkthroughs. They are not required to *view* the report; running `import_steward_workbook_to_parquet.py` on the demo PC still requires a full repo clone with Python.

---

## Legacy: manual `.pbix` (deprecated)

Before PBIP, stewards could build a one-off `.pbix` by connecting to parquet manually. That path is **deprecated**:

- Use **`workbooks/pbip/chi-data-dictionary-catalog.pbip`** (seven tabs, nine-table semantic model).
- Do not commit `workbooks/*.pbix` (gitignored).
- Regenerate layout with `enhance_pbip_report.py` / `patch_pbip_readability.py` instead of hand-building visuals.

If you must connect parquet manually for debugging: **Get data → Parquet** → select root `ddc-master_patient_catalog.parquet`, `ddc-master_patient_dictionary.parquet`, and `ddc-data_source_availability.parquet`; relate on `semantic_id`. You will not get ADT/CCDA/value set/crosswalk pages without adding those parquets yourself.

---

## Appendix: old manual build steps (historical)

The steps below described a minimal three-table `.pbix`. Kept for reference only.

### What you need running

Only the steward round-trip you already have:

1. Edit `workbooks/chi-steward-workbook.xlsx`
2. `python scripts/import_steward_workbook_to_parquet.py`
3. Open or refresh your `.pbix` in Power BI Desktop

---

## One-time setup in Power BI Desktop

### 1. Load three tables

Power BI’s **Parquet** dialog often says “URL” even for local files. That field accepts a **full Windows path** - you are not required to use a web address.

**Option A - paste a local path (simplest)**

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

**Option B - pick from a folder**

1. **Get data → Folder** → browse to `C:\AI\chi-data-dictionary-catalog`.
2. **Transform data** → filter **Extension** = `.parquet` → keep the three `ddc-*` files above → **Combine** (or load each file as its own query).

**Option C - if Parquet still won’t take a local path**

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

### 3. Build the page - tables first, slicer last

Stay in **Report** view. You should see a blank white canvas.

Until you add the slicer (step 4), each table shows **all 46 rows**. That is normal - you are checking that fields load correctly.

#### Table 1 - Catalog (business context)

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

#### Table 2 - Dictionary (FHIR and survivorship)

1. Click empty space below Table 1 (so you do not replace it).
2. **Visualizations** → **Table** again.
3. Expand `ddc-master_patient_dictionary` → check:

   - `semantic_id`
   - `fhir_r4_path`
   - `chi_survivorship_logic`
   - `data_source_rank_reference`

#### Table 3 - Sources (where data comes from)

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
