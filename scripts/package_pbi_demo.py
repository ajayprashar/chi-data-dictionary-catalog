"""Package PBIP, parquet, and Excel workbooks for demo on another Windows PC.

The semantic model uses absolute paths to:
  C:\\AI\\chi-data-dictionary-catalog\\ddc-*.parquet

Extract the zip to that exact folder on the demo machine, then open:
  workbooks\\pbip\\chi-data-dictionary-catalog.pbip
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parent.parent
PBIP_DIR = REPO_ROOT / "workbooks" / "pbip"
DEFAULT_OUT = REPO_ROOT / "workbooks" / f"chi-ddc-demo-{date.today().isoformat()}.zip"

PARQUET_FILES = [
    "ddc-application_guide.parquet",
    "ddc-application_guide_gaps.parquet",
    "ddc-master_patient_catalog.parquet",
    "ddc-master_patient_dictionary.parquet",
    "ddc-data_source_availability.parquet",
    "ddc-hl7_adt_catalog.parquet",
    "ddc-ccda_catalog.parquet",
    "ddc-value_set_member.parquet",
    "ddc-source_value_crosswalk.parquet",
]

EXCEL_FILES = [
    "workbooks/chi-steward-workbook.xlsx",
    "workbooks/chi-partner-intake-workbook.xlsx",
]

SKIP_SUFFIXES = {
    ".pbi/cache.abf",
    ".pbi/localSettings.json",
    ".pbi/editorSettings.json",
}

README = """CHI Data Dictionary Catalog - Power BI demo package
=====================================================

Extract this zip so the folder exists at:

  C:\\AI\\chi-data-dictionary-catalog\\

Required layout after extract:

  C:\\AI\\chi-data-dictionary-catalog\\
    ddc-master_patient_catalog.parquet
    ddc-master_patient_dictionary.parquet
    ddc-data_source_availability.parquet
    ddc-hl7_adt_catalog.parquet
    ddc-ccda_catalog.parquet
    ddc-value_set_member.parquet
    ddc-source_value_crosswalk.parquet
    ddc-application_guide.parquet
    ddc-application_guide_gaps.parquet
    workbooks\\chi-steward-workbook.xlsx
    workbooks\\chi-partner-intake-workbook.xlsx
    workbooks\\pbip\\chi-data-dictionary-catalog.pbip
    workbooks\\pbip\\chi-data-dictionary-catalog.Report\\
    workbooks\\pbip\\chi-data-dictionary-catalog.SemanticModel\\

Steward authoring (optional demo of edit -> publish):
  workbooks\\chi-steward-workbook.xlsx
  After edits: python scripts/import_steward_workbook_to_parquet.py (requires repo clone)
  Then Refresh in Power BI.

Open in Power BI Desktop:

  workbooks\\pbip\\chi-data-dictionary-catalog.pbip

Then Home -> Refresh from the REPORT view (do not open Transform data unless you must).

Power Query preview crash (0x80131623 on ddc-ccda_catalog, etc.):
  This is a known Power BI Desktop Mashup bug with PBIP + parquet preview,
  not corrupt data. The report can still work: close Power Query, use Home -> Refresh.
  Parquets in this zip are rewritten to Parquet 1.0 for broader Desktop compatibility.
  Prefer the EXE installer over Microsoft Store. US Gov cloud tenants: use EXE build.

If you cannot use C:\\AI\\chi-data-dictionary-catalog on the demo PC:
  Transform data -> Data source settings -> change the folder for all
  seven parquet queries to wherever you extracted the ddc-*.parquet files.

A single-file .pbix is not required for this demo. PBIP is the maintained
report format in git.
"""


def should_skip(path: Path) -> bool:
    parts = "/".join(path.parts).replace("\\", "/")
    return any(parts.endswith(suffix) for suffix in SKIP_SUFFIXES)


def write_pbi_compatible_parquet(src: Path, dest: Path) -> None:
    """Rewrite parquet as version 1.0 without pandas metadata (better PBI compatibility)."""
    df = pd.read_parquet(src)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].where(df[col].notna(), None)
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, dest, version="1.0", compression="snappy")


def package(out_zip: Path, *, native_parquet: bool = False) -> None:
    guide_script = REPO_ROOT / "scripts" / "generate_pbip_model_guide.py"
    if not (REPO_ROOT / "ddc-application_guide.parquet").exists() and guide_script.is_file():
        subprocess.run([sys.executable, str(guide_script)], check=True, cwd=REPO_ROOT)
    missing = [name for name in PARQUET_FILES if not (REPO_ROOT / name).exists()]
    missing += [name for name in EXCEL_FILES if not (REPO_ROOT / name).exists()]
    if missing:
        raise SystemExit(f"Missing files: {', '.join(missing)}")

    if not PBIP_DIR.is_dir():
        raise SystemExit(f"PBIP folder not found: {PBIP_DIR}")

    out_zip.parent.mkdir(parents=True, exist_ok=True)
    root_name = "chi-data-dictionary-catalog"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{root_name}/DEMO-README.txt", README)

            for name in PARQUET_FILES:
                src = REPO_ROOT / name
                if native_parquet:
                    zf.write(src, f"{root_name}/{name}")
                else:
                    compat = tmp_path / name
                    write_pbi_compatible_parquet(src, compat)
                    zf.write(compat, f"{root_name}/{name}")

            for rel in EXCEL_FILES:
                src = REPO_ROOT / rel
                zf.write(src, f"{root_name}/{Path(rel).as_posix()}")

            for src in PBIP_DIR.rglob("*"):
                if src.is_dir() or should_skip(src.relative_to(PBIP_DIR)):
                    continue
                rel = src.relative_to(REPO_ROOT)
                zf.write(src, f"{root_name}/{rel.as_posix()}")

    print(f"Wrote {out_zip}")
    print("On demo PC: extract to C:\\AI\\ then open workbooks\\pbip\\chi-data-dictionary-catalog.pbip")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output zip path (default: {DEFAULT_OUT.name})",
    )
    parser.add_argument(
        "--native-parquet",
        action="store_true",
        help="Copy repo parquets as-is (default: rewrite to Parquet 1.0 for Power BI)",
    )
    args = parser.parse_args()
    package(args.output.resolve(), native_parquet=args.native_parquet)


if __name__ == "__main__":
    main()
