#!/usr/bin/env python3
"""Enrich parquet for Power BI readability (run after ADT / value-set builds).

1. ADT: merge HL7 CE component pairs (e.g. PID-22.1 code + PID-22.2 text) into one row.
2. Value set members: add pbi_default_show (hide HL7 detailed expansion in PBIP import).

Excel / steward workbook keep full parquet; PBIP semantic model filters members at load.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

ADT_PATH = ROOT / "ddc-hl7_adt_catalog.parquet"
MEMBER_PATH = ROOT / "ddc-value_set_member.parquet"

CE_CODE_RE = re.compile(r"\bcode\b", re.IGNORECASE)
CE_TEXT_RE = re.compile(r"name|description", re.IGNORECASE)


def _is_ce_code_row(field_name: str) -> bool:
    return bool(CE_CODE_RE.search(field_name)) and "coding system" not in field_name.lower()


def _is_ce_text_row(field_name: str) -> bool:
    return bool(CE_TEXT_RE.search(field_name))


def collapse_adt_ce_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    if "hl7_ce_encoding" not in df.columns:
        df = df.copy()
        df["hl7_ce_encoding"] = ""

    drop_indices: list[int] = []
    new_rows: list[pd.Series] = []

    group_cols = ["semantic_id", "segment_id", "field_id", "message_format", "message_type"]
    for _, grp in df.groupby(group_cols, dropna=False):
        if len(grp) != 2:
            continue
        names = grp["field_name"].astype(str).tolist()
        code_rows = grp[grp["field_name"].apply(_is_ce_code_row)]
        text_rows = grp[grp["field_name"].apply(_is_ce_text_row)]
        if len(code_rows) != 1 or len(text_rows) != 1:
            continue

        code_row = code_rows.iloc[0].copy()
        field_id = str(code_row["field_id"])
        base = str(code_row["field_name"])
        if base.lower().endswith(" code"):
            base = base[: -len(" code")]
        code_row["field_name"] = f"{base} (CE: {field_id}.1 code ^ {field_id}.2 text)"
        code_row["hl7_ce_encoding"] = f"{field_id}.1^{field_id}.2"
        if str(code_row.get("data_type", "")).strip() == "":
            code_row["data_type"] = "CE"

        note_parts = [str(code_row.get("notes", "")).strip(), f"HL7 CE components {field_id}.1^{field_id}.2"]
        code_row["notes"] = "; ".join(p for p in note_parts if p)

        new_rows.append(code_row)
        drop_indices.extend(grp.index.tolist())

    if not new_rows:
        return df

    out = df.drop(index=drop_indices)
    out = pd.concat([out, pd.DataFrame(new_rows)], ignore_index=True)
    return out


def add_pbi_default_show(members: pd.DataFrame) -> pd.DataFrame:
    out = members.copy()
    out["pbi_default_show"] = out["member_type"].apply(
        lambda t: "false" if str(t).strip().lower() == "detailed" else "true"
    )
    return out


def enrich_adt(path: Path = ADT_PATH) -> int:
    if not path.is_file():
        print(f"Skip ADT (missing): {path}")
        return 0
    before = len(pd.read_parquet(path))
    df = pd.read_parquet(path)
    df = collapse_adt_ce_rows(df)
    df.to_parquet(path, index=False)
    print(f"ADT {path.name}: {before} -> {len(df)} rows (CE pairs merged)")
    return len(df)


def enrich_members(path: Path = MEMBER_PATH) -> int:
    if not path.is_file():
        print(f"Skip members (missing): {path}")
        return 0
    df = pd.read_parquet(path)
    df = add_pbi_default_show(df)
    df.to_parquet(path, index=False)
    hidden = (df["pbi_default_show"] == "false").sum()
    print(f"Members {path.name}: {len(df)} rows ({hidden} detailed hidden in PBIP)")
    return len(df)


def main() -> None:
    enrich_adt()
    enrich_members()


if __name__ == "__main__":
    main()
    sys.exit(0)
