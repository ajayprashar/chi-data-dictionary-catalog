#!/usr/bin/env python3
"""
Split a combined metadata CSV into catalog and dictionary Parquet files.

Reads a single CSV (one row per data element with both catalog and dictionary
columns), splits by column set, and writes master_patient_catalog.parquet and
master_patient_dictionary.parquet. Both tables include Semantic ID for joining.

Usage:
  python scripts/split_to_catalog_and_dictionary.py combined_metadata.csv
  python scripts/split_to_catalog_and_dictionary.py combined_metadata.csv -d output_dir

Output (default: same directory as input):
  master_patient_catalog.parquet
  master_patient_dictionary.parquet
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

# Catalog: identity + classification (Semantic ID is primary key)
CATALOG_COLUMNS = [
    "Semantic ID",
    "USCDI Element",
    "USCDI Description",
    "Classification",
    "Ruleset Category",
    "Privacy/Security",
]

# Dictionary: definition + rules (Semantic ID is foreign key)
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split combined metadata CSV into catalog and dictionary Parquet files."
    )
    parser.add_argument("input", type=Path, help="Combined CSV file path")
    parser.add_argument(
        "-d", "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: same as input file)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    df = read_csv(args.input)
    df.columns = [normalize_header(c) for c in df.columns]

    out_dir = args.output_dir or args.input.parent
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build catalog: only columns that exist
    catalog_cols = [c for c in CATALOG_COLUMNS if c in df.columns]
    if "Semantic ID" not in catalog_cols and "Semantic ID" in df.columns:
        catalog_cols.insert(0, "Semantic ID")
    if not catalog_cols:
        print("Error: no catalog columns found. Expected at least: Semantic ID, USCDI Element, ...", file=sys.stderr)
        sys.exit(1)
    catalog = df[catalog_cols].copy()
    # Rename columns to snake_case for Parquet/schema friendliness
    catalog = catalog.rename(columns={c: to_snake(c) for c in catalog.columns})
    catalog_path = out_dir / "master_patient_catalog.parquet"
    catalog.to_parquet(catalog_path, index=False)
    print(f"Wrote catalog: {catalog_path} ({len(catalog)} rows)")

    # Build dictionary: only columns that exist
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
