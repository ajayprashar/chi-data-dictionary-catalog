"""Package PBIP, parquet, and Excel workbooks for demo on another Windows PC.

The semantic model uses absolute paths to:
  C:\\AI\\chi-data-dictionary-catalog\\ddc-*.parquet

Extract the zip to that exact folder on the demo machine, then open:
  workbooks\\pbip\\chi-data-dictionary-catalog.pbip
"""

from __future__ import annotations

import argparse
import zipfile
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PBIP_DIR = REPO_ROOT / "workbooks" / "pbip"
DEFAULT_OUT = REPO_ROOT / "workbooks" / f"chi-ddc-demo-{date.today().isoformat()}.zip"

PARQUET_FILES = [
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

Then Home -> Refresh.

If you cannot use C:\\AI\\chi-data-dictionary-catalog on the demo PC:
  Transform data -> Data source settings -> change the folder for all
  seven parquet queries to wherever you extracted the ddc-*.parquet files.

A single-file .pbix is not required for this demo. PBIP is the maintained
report format in git.
"""


def should_skip(path: Path) -> bool:
    parts = "/".join(path.parts).replace("\\", "/")
    return any(parts.endswith(suffix) for suffix in SKIP_SUFFIXES)


def package(out_zip: Path) -> None:
    missing = [name for name in PARQUET_FILES if not (REPO_ROOT / name).exists()]
    missing += [name for name in EXCEL_FILES if not (REPO_ROOT / name).exists()]
    if missing:
        raise SystemExit(f"Missing files: {', '.join(missing)}")

    if not PBIP_DIR.is_dir():
        raise SystemExit(f"PBIP folder not found: {PBIP_DIR}")

    out_zip.parent.mkdir(parents=True, exist_ok=True)
    root_name = "chi-data-dictionary-catalog"

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{root_name}/DEMO-README.txt", README)

        for name in PARQUET_FILES:
            src = REPO_ROOT / name
            zf.write(src, f"{root_name}/{name}")

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
    args = parser.parse_args()
    package(args.output.resolve())


if __name__ == "__main__":
    main()
