#!/usr/bin/env python3
"""
Split a combined metadata CSV into catalog and dictionary Parquet files.

Reads a single CSV (one row per data element with both catalog and dictionary
columns), splits by column set, and writes master_patient_catalog.parquet and
master_patient_dictionary.parquet. Both tables include Semantic ID for joining.

Usage:
  python scripts/split_to_catalog_and_dictionary.py combined_metadata.csv
  python scripts/split_to_catalog_and_dictionary.py combined_metadata.csv -d output_dir
  python scripts/split_to_catalog_and_dictionary.py --upgrade-schema -d project_root

Output (default: same directory as input):
  master_patient_catalog.parquet
  master_patient_dictionary.parquet

Upgrade: Use --upgrade-schema to add HIE alignment columns to existing Parquet
files without a CSV. Adds domain, rollup_relationship, is_rollup, composite_group
to catalog; calculation_grain, historical_freeze, recalc_window_months to dictionary.
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

# Catalog: identity + classification (Semantic ID is primary key)
# HIE Three-Domain Separation (Gap 1): domain enforces governance boundaries
# HIE roll-up vs. detail (Gap 2): rollup_relationship, is_rollup for race/ethnicity etc.
# HIE address coherence (Gap 4): composite_group for survivorship-as-set
CATALOG_COLUMNS = [
    "Semantic ID",
    "USCDI Element",
    "USCDI Description",
    "Classification",
    "Ruleset Category",
    "Privacy/Security",
    "Domain",
    "Rollup Relationship",
    "Is Rollup",
    "Composite Group",
]

# Dictionary: definition + rules (Semantic ID is foreign key)
# HIE temporal/grain (Gap 3): calculation_grain, historical_freeze, recalc_window_months for Domain 2
DICTIONARY_COLUMNS = [
    "Semantic ID",
    "SHIE Survivorship Logic",
    "Data Source Rank Reference",
    "Coverage (# PersonIDs)",
    "Granularity Level",
    "Innovaccer Survivorship Logic",
    "Data Quality Notes",
    "FHIR R4 Path",
    "FHIR Data Type",
    "Calculation Grain",
    "Historical Freeze",
    "Recalc Window (Months)",
]


def normalize_header(s: str) -> str:
    return (s or "").strip()


def to_snake(name: str) -> str:
    """
    Convert a human-friendly column name to lower_snake_case.

    Examples:
      "Semantic ID" -> "semantic_id"
      "Coverage (# PersonIDs)" -> "coverage_personids"
      "FHIR R4 Path" -> "fhir_r4_path"
    """
    # Replace any run of non-alphanumeric characters with underscore
    s = re.sub(r"[^0-9A-Za-z]+", "_", name.strip())
    # Collapse multiple underscores and trim
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lower()


def read_csv(path: Path) -> pd.DataFrame:
    """Read CSV; accept comma or tab, UTF-8."""
    with open(path, "r", encoding="utf-8-sig") as f:
        sample = f.read(8192)
    sep = "\t" if "\t" in sample and sample.count("\t") > sample.count(",") else ","
    return pd.read_csv(path, encoding="utf-8-sig", sep=sep, dtype=str, keep_default_na=False)


def upgrade_parquet_schema(out_dir: Path) -> None:
    """Add HIE alignment columns to existing Parquet files if missing."""
    cat_path = out_dir / "master_patient_catalog.parquet"
    dict_path = out_dir / "master_patient_dictionary.parquet"
    if not cat_path.exists() or not dict_path.exists():
        print("Error: both master_patient_catalog.parquet and master_patient_dictionary.parquet required.", file=sys.stderr)
        sys.exit(1)
    catalog = pd.read_parquet(cat_path)
    dictionary = pd.read_parquet(dict_path)
    catalog_snake = {to_snake(c): c for c in CATALOG_COLUMNS}
    dict_snake = {to_snake(c): c for c in DICTIONARY_COLUMNS}
    added = False
    for col, human in catalog_snake.items():
        if col not in catalog.columns:
            catalog[col] = ""
            added = True
    for col, human in dict_snake.items():
        if col == "semantic_id":
            continue
        if col not in dictionary.columns:
            dictionary[col] = ""
            added = True
    if added:
        catalog.to_parquet(cat_path, index=False)
        dictionary.to_parquet(dict_path, index=False)
        print(f"Upgraded schema in {out_dir}")
    else:
        print("Schema already up to date.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split combined metadata CSV into catalog and dictionary Parquet files."
    )
    parser.add_argument("input", nargs="?", type=Path, help="Combined CSV file path")
    parser.add_argument(
        "-d", "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: same as input file, or project root for --upgrade-schema)",
    )
    parser.add_argument(
        "--upgrade-schema",
        action="store_true",
        help="Add HIE alignment columns to existing Parquet files (no CSV needed)",
    )
    args = parser.parse_args()

    if args.upgrade_schema:
        out_dir = args.output_dir or Path.cwd()
        upgrade_parquet_schema(Path(out_dir))
        return

    if not args.input:
        parser.error("input CSV path required (or use --upgrade-schema)")
    if not args.input.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    df = read_csv(args.input)
    df.columns = [normalize_header(c) for c in df.columns]

    out_dir = args.output_dir or args.input.parent
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build catalog: include all CATALOG_COLUMNS; add missing with empty string for HIE alignment
    for c in CATALOG_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    catalog_cols = [c for c in CATALOG_COLUMNS if c in df.columns]
    if not catalog_cols:
        print("Error: no catalog columns found. Expected at least: Semantic ID, USCDI Element, ...", file=sys.stderr)
        sys.exit(1)
    catalog = df[catalog_cols].copy()
    # Rename columns to snake_case for Parquet/schema friendliness
    catalog = catalog.rename(columns={c: to_snake(c) for c in catalog.columns})
    catalog_path = out_dir / "master_patient_catalog.parquet"
    catalog.to_parquet(catalog_path, index=False)
    print(f"Wrote catalog: {catalog_path} ({len(catalog)} rows)")

    # Build dictionary: include all DICTIONARY_COLUMNS; add missing with empty string
    for c in DICTIONARY_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    dictionary_cols = [c for c in DICTIONARY_COLUMNS if c in df.columns]
    if not dictionary_cols:
        print("Error: no dictionary columns found.", file=sys.stderr)
        sys.exit(1)
    dictionary = df[dictionary_cols].copy()
    dictionary = dictionary.rename(columns={c: to_snake(c) for c in dictionary.columns})
    # Historical name fix: SHIE -> HIE in the Parquet schema
    if "shie_survivorship_logic" in dictionary.columns:
        dictionary = dictionary.rename(columns={"shie_survivorship_logic": "hie_survivorship_logic"})
    dictionary_path = out_dir / "master_patient_dictionary.parquet"
    dictionary.to_parquet(dictionary_path, index=False)
    print(f"Wrote dictionary: {dictionary_path} ({len(dictionary)} rows)")


if __name__ == "__main__":
    main()
