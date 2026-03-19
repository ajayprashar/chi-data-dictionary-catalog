#!/usr/bin/env python3
"""
Build `ddc-ccda_catalog.parquet` from the CCD → semantic_id mapping CSV.

Reads `data/ccd_to_semantic_id_mapping.csv` and writes project-root
`ddc-ccda_catalog.parquet` with columns expected by the Streamlit app:
message_format, section_name, entry_type, xml_path, semantic_id, fhir_r4_path, notes.

Usage:
  python scripts/build_ccda_catalog_from_mapping.py
  python scripts/build_ccda_catalog_from_mapping.py -o path/to/output.parquet

The script overwrites the output file. Default output: ddc-ccda_catalog.parquet
in the project root (parent of scripts/).
"""

import argparse
import csv
from pathlib import Path

import pandas as pd


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    parser = argparse.ArgumentParser(
        description="Build CCD/CCDA catalog Parquet from CCD→semantic_id mapping CSV."
    )
    parser.add_argument(
        "-m",
        "--mapping",
        type=Path,
        default=project_root / "data" / "ccd_to_semantic_id_mapping.csv",
        help="Path to mapping CSV",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=project_root / "ddc-ccda_catalog.parquet",
        help="Output Parquet path",
    )
    args = parser.parse_args()

    mapping_path = args.mapping.resolve()
    if not mapping_path.is_file():
        raise FileNotFoundError(f"Mapping file not found: {mapping_path}")

    rows: list[dict] = []
    with open(mapping_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "message_format": "CCD",
                "section_name": (r.get("section") or "").strip(),
                "entry_type": (r.get("entry_type") or "").strip(),
                "xml_path": (r.get("xml_path") or "").strip(),
                "semantic_id": (r.get("semantic_id") or "").strip(),
                "fhir_r4_path": (r.get("fhir_r4_path") or "").strip(),
                "notes": (r.get("notes") or "").strip(),
            })

    df = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
