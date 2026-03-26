#!/usr/bin/env python3
"""
Build `ddc-hl7_adt_catalog.parquet` from the L2-to-semantic_id mapping CSV.

Reads mapping CSV (default `data/l2_to_semantic_id_mapping.csv`; archive fallback supported)
and writes project-root `ddc-hl7_adt_catalog.parquet` with columns expected by the
current steward-workspace pipeline:
message_format, message_type, segment_id, field_id, field_name, data_type,
optionality, cardinality, semantic_id, fhir_r4_path, notes, mapping_status,
business_rule_required, business_rule_notes.

Usage:
  python scripts/build_adt_catalog_from_mapping.py
  python scripts/build_adt_catalog_from_mapping.py -o path/to/output.parquet

The script overwrites the output file. Default output: ddc-hl7_adt_catalog.parquet
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
        description="Build ADT catalog Parquet from L2-to-semantic_id mapping CSV."
    )
    parser.add_argument(
        "-m",
        "--mapping",
        type=Path,
        default=project_root / "data" / "l2_to_semantic_id_mapping.csv",
        help="Path to mapping CSV",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=project_root / "ddc-hl7_adt_catalog.parquet",
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
            # Optionality: R if Mandatory, else O
            rec = r.get("recommended", "")
            optionality = "R" if rec and rec.strip().lower() == "mandatory" else "O"
            cardinality = (r.get("cardinality") or "1").strip()
            rows.append({
                "message_format": "ADT",
                "message_type": "A08",  # Update dominates CMT volume; field applies across event types
                "segment_id": (r.get("segment") or "").strip(),
                "field_id": (r.get("field_id") or "").strip(),
                "field_name": (r.get("display_name") or r.get("l2_column") or "").strip(),
                "data_type": (r.get("data_type") or "").strip(),
                "optionality": optionality,
                "cardinality": cardinality,
                "semantic_id": (r.get("semantic_id") or "").strip(),
                "fhir_r4_path": (r.get("fhir_r4_path") or "").strip(),
                "notes": (r.get("notes") or "").strip(),
                # Governance fields are now promoted into canonical ADT catalog.
                "mapping_status": "mapped" if (r.get("semantic_id") or "").strip() else "needs_new_semantic",
                "business_rule_required": "",
                "business_rule_notes": (r.get("notes") or "").strip(),
            })

    df = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
