## chi-data-dictionary-catalog (POC)

Lightweight, local proof‑of‑concept for viewing a **data catalog** and **data dictionary** that are authored in Excel and stored as Parquet files. Designed to be easy to move between machines.

---

### Interoperability staff quick view

If you just want to **use** the app (not run it locally):

- **Open the catalog**: go to `https://chi-data-dictionary-catalog.streamlit.app/`.
- **Find an element**: use the search box (top left) to type part of the semantic ID, USCDI element name, or FHIR path.
- **Filter**: use the filters on the left (FHIR resource, classification, domain, privacy) to narrow the list.
- **See full details**: click a row in the main table; the right side shows all catalog, dictionary, survivorship, and security fields for that element.
- **See message mappings**: if available, scroll down in the right panel to see how that element maps to HL7 ADT and CCD/CCDA.
- **See architecture docs**: click the **Documentation** button at the bottom of the page to open the diagrams and technical notes.

You can ignore the rest of this README unless you need to install or run the app locally.

---

### Quick start (new machine)

1. **Clone or copy this folder** onto the target machine (e.g. `C:\AI\chi-data-dictionary-catalog`).
2. Open a terminal in this folder and create a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```powershell
   pip install -r requirements.txt
   ```

4. **Open the published app (no install required)**:

   - `https://chi-data-dictionary-catalog.streamlit.app/`

5. **Open the viewer notebook (local dev)**:
   - In Cursor/VS Code: open `chi-data-dictionary-catalog.ipynb` and select the `.venv` interpreter.
   - Run the first cell (`os.chdir(...)`) and the DuckDB query cells to explore `ddc-master_patient_catalog.parquet` and `ddc-master_patient_dictionary.parquet`.

For more detail on Jupyter + DuckDB setup, see `docs/jupyter-duckdb-parquet-setup.md`.

---

### Data pipeline (authoring to Parquet)

1. Author or update metadata in Excel (one sheet with both catalog + dictionary columns).
2. Export the sheet as a CSV (combined export).
3. From this folder, run:

   ```powershell
   .venv\Scripts\activate
   python scripts/split_to_catalog_and_dictionary.py path\to\combined_export.csv
   ```

4. The script regenerates:
   - `ddc-master_patient_catalog.parquet` — catalog view (one row per element).
   - `ddc-master_patient_dictionary.parquet` — dictionary view (definition and rules per element).

Both files use **snake_case** column names (e.g. `semantic_id`, `uscdi_element`, `hie_survivorship_logic`).

**Existing Parquet (no CSV):** To add HIE alignment columns (governance, identity, security, FHIR compliance, survivorship enhancements) to existing Parquet without re-running split on a CSV:
   ```powershell
   python scripts/split_to_catalog_and_dictionary.py --upgrade-schema -d .
   ```

**Optional — rebuild message-format catalogs & source availability:**  
- ADT: `python scripts/build_adt_catalog_from_mapping.py` → `ddc-hl7_adt_catalog.parquet` (from `data/l2_to_semantic_id_mapping.csv`).  
- CCD/CCDA: `python scripts/build_ccda_catalog_from_mapping.py` → `ddc-ccda_catalog.parquet` (from `data/ccd_to_semantic_id_mapping.csv`).  
- Data source availability: `python scripts/build_data_source_availability.py` → `ddc-data_source_availability.parquet` (links sources to semantic IDs).  
See `data/README.md` and `docs/cmt-adt-feed-and-master-patient.md`.

---

### Files of interest

- `readme-prd.md` — 1‑page executive PRD for stakeholders.
- `README.md` — this technical quick‑start guide.
- `TECH-SPEC.md` — Technical specification: architecture strategy, file/table definitions, column schemas, UI layout.
- `EVALUATION.md` — HIE interoperability best practices evaluation (4.1/5 overall score).
- `scripts/split_to_catalog_and_dictionary.py` — CSV → Parquet splitter.
- `ddc-master_patient_catalog.parquet` — catalog table.
- `ddc-master_patient_dictionary.parquet` — dictionary table.
- `ddc-data_source_availability.parquet` — source-to-semantic_id availability matrix.
- `scripts/upload_parquet_to_airtable.py` — re-runnable Airtable uploader (Question #2), with optional Link/Relation fields.
- `docs/airtable-setup.md` — Airtable setup notes (Node + MCP), including troubleshooting.
- `docs/jupyter-duckdb-parquet-setup.md` — full notebook + DuckDB setup instructions.

