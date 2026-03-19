#!/usr/bin/env python3
"""
Build `ddc-data_source_availability.parquet` from feed profiles and catalog.

Links data sources (feed profiles) to catalog semantic IDs, documenting which
sources can provide which attributes. This supports intelligent source selection
for survivorship and enables data quality tracking per source per attribute.

Usage:
  python scripts/build_data_source_availability.py

Inputs:
  - ddc-master_patient_catalog.parquet (required)
  - data/*_feed_segments.csv (feed profiles)

Output:
  - ddc-data_source_availability.parquet

Schema:
  - source_id: Data source identifier (e.g., "cmt", "sutter")
  - semantic_id: FK to master_patient_catalog
  - availability: "full" | "partial" | "none" | "unknown"
  - completeness_pct: Estimated completeness (0.0-100.0)
  - timeliness_sla_hours: Expected freshness SLA in hours
  - notes: Source-specific notes

This is a starter implementation that creates placeholder rows for demonstration.
Production implementation would analyze actual feed data to compute real metrics.
"""

import sys
from pathlib import Path
import glob
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent


def discover_sources() -> list[str]:
    """Discover source IDs from data/*_feed_segments.csv files."""
    data_dir = PROJECT_ROOT / "data"
    if not data_dir.is_dir():
        return []
    pattern = str(data_dir / "*_feed_segments.csv")
    sources = []
    for path in sorted(glob.glob(pattern)):
        base = Path(path).name
        source_id = base.replace("_feed_segments.csv", "")
        if source_id:
            sources.append(source_id)
    return sources


def build_availability_table() -> pd.DataFrame:
    """
    Build data source availability table.

    For POC: creates starter rows linking discovered sources to all catalog semantic IDs
    with placeholder availability="unknown". Production would analyze actual feed data.
    """
    cat_path = PROJECT_ROOT / "ddc-master_patient_catalog.parquet"
    if not cat_path.exists():
        print(f"Error: expected {cat_path.name} not found.", file=sys.stderr)
        sys.exit(1)

    catalog = pd.read_parquet(cat_path)
    sources = discover_sources()

    if not sources:
        print("Warning: no feed profiles found in data/. Creating empty table.", file=sys.stderr)

    rows = []
    for source_id in sources:
        for semantic_id in catalog["semantic_id"]:
            rows.append({
                "source_id": source_id,
                "semantic_id": semantic_id,
                "availability": "unknown",
                "completeness_pct": "",
                "timeliness_sla_hours": "",
                "notes": ""
            })

    if not rows:
        df = pd.DataFrame(columns=[
            "source_id", "semantic_id", "availability",
            "completeness_pct", "timeliness_sla_hours", "notes"
        ])
    else:
        df = pd.DataFrame(rows)

    return df


def main() -> None:
    df = build_availability_table()
    out_pref_path = PROJECT_ROOT / "ddc-data_source_availability.parquet"
    out_path = out_pref_path
    df.to_parquet(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
    if not df.empty:
        sources = df["source_id"].unique()
        semantic_ids = df["semantic_id"].nunique()
        print(f"  {len(sources)} source(s) × {semantic_ids} semantic ID(s)")
        print(f"  Sources: {', '.join(sources)}")
    print("\nNote: availability='unknown' is placeholder. Update manually or implement")
    print("      data profiling to compute real completeness and timeliness metrics.")


if __name__ == "__main__":
    main()
