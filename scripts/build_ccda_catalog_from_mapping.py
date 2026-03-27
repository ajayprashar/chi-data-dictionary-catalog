#!/usr/bin/env python3
"""
Build `ddc-ccda_catalog.parquet` from the CCD-to-semantic_id mapping CSV.

Reads mapping CSV (default `data/ccd_to_semantic_id_mapping.csv`; archive fallback supported)
and writes project-root `ddc-ccda_catalog.parquet` with columns expected by the
current steward-workspace pipeline:
message_format, section_name, entry_type, xml_path, semantic_id, fhir_r4_path, notes,
mapping_status.

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


def _resolve_mapping_path(candidate: Path, project_root: Path) -> Path:
    """Resolve mapping path with archive fallback when active data path is archived."""
    if candidate.is_file():
        return candidate
    archive_fallback = project_root / "data" / "archive" / "2026-03-04" / candidate.name
    if archive_fallback.is_file():
        return archive_fallback
    return candidate


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    parser = argparse.ArgumentParser(
        description="Build CCD/CCDA catalog Parquet from CCD-to-semantic_id mapping CSV."
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

    mapping_path = _resolve_mapping_path(args.mapping.resolve(), project_root)
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
                # Governance fields are now promoted into canonical CCDA catalog.
                "mapping_status": "mapped" if (r.get("semantic_id") or "").strip() else "needs_new_semantic",
            })

    df = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
