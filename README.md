## chi-data-dictionary-catalog (POC)

Lightweight, local proof‑of‑concept for viewing a **data catalog** and **data dictionary** that are authored in Excel and stored as Parquet files. Designed to be easy to move between machines.

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
   - Run the first cell (`os.chdir(...)`) and the DuckDB query cells to explore `master_patient_catalog.parquet` and `master_patient_dictionary.parquet`.

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
   - `master_patient_catalog.parquet` — catalog view (one row per element).
   - `master_patient_dictionary.parquet` — dictionary view (definition and rules per element).

Both files use **snake_case** column names (e.g. `semantic_id`, `uscdi_element`, `hie_survivorship_logic`).

**Optional — rebuild message-format catalogs:**  
- ADT: `python scripts/build_adt_catalog_from_mapping.py` → `hl7_adt_catalog.parquet` (from `data/l2_to_semantic_id_mapping.csv`).  
- CCD/CCDA: `python scripts/build_ccda_catalog_from_mapping.py` → `ccda_catalog.parquet` (from `data/ccd_to_semantic_id_mapping.csv`).  
See `data/README.md` and `docs/cmt-adt-feed-and-master-patient.md`.

---

### Files of interest

- `readme-prd.md` — 1‑page executive PRD for stakeholders.
- `README.md` — this technical quick‑start guide.
- `scripts/split_to_catalog_and_dictionary.py` — CSV → Parquet splitter.
- `master_patient_catalog.parquet` — catalog table.
- `master_patient_dictionary.parquet` — dictionary table.
- `docs/jupyter-duckdb-parquet-setup.md` — full notebook + DuckDB setup instructions.

