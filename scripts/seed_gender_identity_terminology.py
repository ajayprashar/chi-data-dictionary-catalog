#!/usr/bin/env python3
"""Patch Patient.gender_id binding and HL7 minimum gender-identity members.

Updates ddc-value_set_binding.parquet and merges ddc-value_set_member.parquet
without overwriting race/ethnicity HL7 expansions or other semantic_ids.

Source of truth for row content: scripts/seed_value_sets_pilot.py (BINDINGS + MEMBERS).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SEMANTIC_ID = "Patient.gender_id"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seed_value_sets_pilot import (  # noqa: E402
    BINDING_COLUMNS,
    BINDINGS,
    MEMBER_COLUMNS,
    MEMBERS,
)


def patch_binding(bindings: pd.DataFrame) -> pd.DataFrame:
    row = next(b for b in BINDINGS if b["semantic_id"] == SEMANTIC_ID)
    mask = bindings["semantic_id"] == SEMANTIC_ID
    if not mask.any():
        return pd.concat([bindings, pd.DataFrame([row], columns=BINDING_COLUMNS)], ignore_index=True)
    for col, val in row.items():
        bindings.loc[mask, col] = val
    return bindings


def merge_members(existing: pd.DataFrame) -> pd.DataFrame:
    new_rows = [m for m in MEMBERS if m["semantic_id"] == SEMANTIC_ID]
    other = existing[existing["semantic_id"] != SEMANTIC_ID]
    return pd.concat([other, pd.DataFrame(new_rows, columns=MEMBER_COLUMNS)], ignore_index=True)


def main() -> None:
    bindings_path = ROOT / "ddc-value_set_binding.parquet"
    members_path = ROOT / "ddc-value_set_member.parquet"

    bindings = pd.read_parquet(bindings_path)
    members = pd.read_parquet(members_path)

    bindings = patch_binding(bindings)
    members = merge_members(members)

    bindings.to_parquet(bindings_path, index=False)
    members.to_parquet(members_path, index=False)

    from enrich_parquet_for_pbi import enrich_members

    enrich_members(members_path)

    n = len(members[members["semantic_id"] == SEMANTIC_ID])
    row = bindings[bindings["semantic_id"] == SEMANTIC_ID].iloc[0]
    print(f"Patched binding: {row['value_set_url']}")
    print(f"  binding_strength={row['binding_strength']!r}, fhir_element={row['fhir_element']!r}")
    print(f"Wrote {n} governed member row(s) for {SEMANTIC_ID}")


if __name__ == "__main__":
    main()
