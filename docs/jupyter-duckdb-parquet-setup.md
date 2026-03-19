# Jupyter Notebooks with DuckDB and Parquet (Python)

This document describes how to run Jupyter notebooks that query Parquet files using DuckDB, and how to reproduce the environment.

---

## Minimal environment (recommended)

The approach that works reliably uses the **DuckDB Python API** only (no `%%sql` magic).

### 1. Python and virtual environment

- **Python**: 3.10+ (tested with 3.13).
- Create and use a virtual environment so dependencies are reproducible:

  ```powershell
  cd C:\AI\chi-data-dictionary-catalog
  python -m venv .venv
  .venv\Scripts\activate
  ```

### 2. Install dependencies

From the project root with `.venv` activated:

```powershell
pip install -r requirements.txt
```

The **minimal** packages needed for DuckDB + Parquet in Jupyter are:

| Package   | Purpose |
|----------|---------|
| `duckdb` | Query Parquet (and CSV) in-process; `.df()` returns a pandas DataFrame. |
| `pandas` | Required by DuckDB’s `.df()` for DataFrame output. |

The project `requirements.txt` also includes `pandas` and `pyarrow` for the **split script** (`scripts/split_to_catalog_and_dictionary.py`). For notebooks alone, `duckdb` and `pandas` are enough.

### 3. Notebook setup

**Working directory**

The notebook kernel’s current working directory must be the project folder so that relative paths like `'ddc-master_patient_catalog.parquet'` resolve. Run this in the **first cell**:

```python
import os
os.chdir(r'C:\AI\chi-data-dictionary-catalog')  # or your project path
```

**Query pattern**

Use DuckDB’s Python API so results display as a normal pandas DataFrame in Jupyter:

```python
import duckdb

# Option A: relative path (only valid after os.chdir to project folder)
df = duckdb.query("SELECT * FROM read_parquet('ddc-master_patient_catalog.parquet') LIMIT 10").df()

# Option B: absolute path (works regardless of kernel cwd)
path = os.path.join(os.getcwd(), 'ddc-master_patient_catalog.parquet')
df = duckdb.query(f"SELECT * FROM read_parquet('{path}') LIMIT 10").df()

df   # display in notebook
```

- `duckdb.query(...)` returns a DuckDB relation; `.df()` converts it to a pandas DataFrame.
- Jupyter will render the DataFrame as a table.

### 4. Reproducing the environment from scratch

1. Clone or copy the project; `cd` into the project root.
2. Create and activate a venv: `python -m venv .venv` then `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux).
3. Install: `pip install -r requirements.txt`.
4. In Jupyter (VS Code, Cursor, or `jupyter notebook`), select the `.venv` kernel.
5. In the notebook, run the `os.chdir(...)` cell first, then the DuckDB query cell(s) above.

No database server or config files are required; DuckDB runs in-process.

---

## Optional: `%%sql` magic (ipython-sql)

You can use the `%sql` / `%%sql` magics with DuckDB, but in this project that path had display and compatibility issues and is **not** required for the working setup.

If you want to use it anyway:

1. Install: `pip install ipython-sql duckdb-engine`.
2. In a cell: `%load_ext sql`, then `%sql duckdb:///:memory:`.
3. **Caveats:**
   - With **PrettyTable 3.x**, ipython-sql can raise `KeyError: 'DEFAULT'` when rendering results. A patch was applied under `.venv/Lib/site-packages/sql/run.py` to avoid the broken style lookup; that patch is not in `requirements.txt` and would need to be reapplied if you recreate the venv.
   - `%%sql` often does not display result tables in the notebook (only “Done.”); the DuckDB API + `.df()` pattern above avoids that.

The project’s **minimal** `requirements.txt` does not include `ipython-sql` or `duckdb-engine`; add them only if you choose to use the SQL magic.

---

## Summary

| What you need | Purpose |
|----------------|---------|
| Python 3.10+   | Runtime. |
| `.venv`        | Isolated, reproducible environment. |
| `duckdb`       | Query Parquet in the notebook. |
| `pandas`       | For `.df()` and DataFrame display. |
| `os.chdir(...)` or absolute path | So `read_parquet('...')` finds the file. |
| `duckdb.query("SELECT * FROM read_parquet('...')").df()` | Reliable query + display in Jupyter. |

No server, no `%%sql`, and no extra SQL drivers are required for this workflow.
