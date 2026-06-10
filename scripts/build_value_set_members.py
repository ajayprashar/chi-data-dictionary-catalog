#!/usr/bin/env python3
"""Expand HL7 ValueSets into ddc-value_set_member.parquet for stewarded bindings.

Default targets: Patient.race and Patient.ethnicity (CDCREC via HL7 Race/Ethnicity
ValueSets). Preserves nullflavor / exclude rows and members for other semantic_ids.

Online: FHIR $expand via tx.fhir.org (paginated).
Offline: read cached expansion JSON from data/terminology/ (write cache with --write-cache).

Example:
  python scripts/build_value_set_members.py
  python scripts/build_value_set_members.py --write-cache
  python scripts/build_value_set_members.py --offline
  python scripts/build_value_set_members.py --dry-run
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests

MEMBER_COLUMNS = [
    "semantic_id",
    "code_system_oid",
    "code",
    "display",
    "member_type",
    "binding_role",
    "binding_strength",
    "active",
    "sort_order",
    "notes",
]

DEFAULT_SEMANTIC_IDS = ("Patient.race", "Patient.ethnicity")

OMB_ROLLUP_CODES: dict[str, set[str]] = {
    "Patient.race": {
        "1002-5",
        "2028-9",
        "2054-5",
        "2076-8",
        "2106-3",
        "2131-1",
    },
    "Patient.ethnicity": {"2135-2", "2186-5"},
}

PRESERVE_MEMBER_TYPES = frozenset({"nullflavor", "exclude"})

TX_EXPAND_URL = "https://tx.fhir.org/r4/ValueSet/$expand"
REQUEST_TIMEOUT = 120
PAGE_SIZE = 500


def _cache_path(repo_root: Path, value_set_url: str) -> Path:
    slug = value_set_url.rstrip("/").split("/")[-1]
    return repo_root / "data" / "terminology" / f"{slug}.expansion.json"


def _slug_from_url(value_set_url: str) -> str:
    return value_set_url.rstrip("/").split("/")[-1]


def expand_valueset_online(value_set_url: str) -> list[dict[str, str]]:
    """Fetch full ValueSet expansion from the public HL7 FHIR terminology server."""
    all_contains: list[dict] = []
    offset = 0
    total: int | None = None

    while True:
        response = requests.get(
            TX_EXPAND_URL,
            params={"url": value_set_url, "count": PAGE_SIZE, "offset": offset},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        expansion = response.json().get("expansion", {})
        batch = expansion.get("contains", [])
        if total is None:
            total = expansion.get("total")
        if not batch:
            break
        all_contains.extend(batch)
        offset += len(batch)
        if total is not None and offset >= total:
            break
        if len(batch) < PAGE_SIZE:
            break

    return [
        {
            "code": str(item.get("code", "")).strip(),
            "display": str(item.get("display", "")).strip(),
            "system": str(item.get("system", "")).strip(),
        }
        for item in all_contains
        if str(item.get("code", "")).strip()
    ]


def load_expansion_cache(cache_path: Path) -> list[dict[str, str]]:
    if not cache_path.is_file():
        raise FileNotFoundError(
            f"Offline cache not found: {cache_path}\n"
            "Run online once with --write-cache to create it."
        )
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    return payload.get("contains", [])


def write_expansion_cache(cache_path: Path, value_set_url: str, contains: list[dict[str, str]]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "value_set_url": value_set_url,
        "cached_date": date.today().isoformat(),
        "contains": contains,
    }
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _member_type(semantic_id: str, code: str) -> str:
    if code in OMB_ROLLUP_CODES.get(semantic_id, set()):
        return "omb_rollup"
    return "detailed"


def _sort_key(semantic_id: str, code: str, member_type: str) -> int:
    if member_type == "omb_rollup":
        order = sorted(OMB_ROLLUP_CODES.get(semantic_id, set()))
        try:
            return order.index(code) + 1
        except ValueError:
            return 100
    return 200


def expansion_to_member_rows(
    semantic_id: str,
    binding: pd.Series,
    contains: list[dict[str, str]],
    expand_note: str,
) -> list[dict[str, str]]:
    code_system_oid = str(binding.get("code_system_oid", "")).strip()
    binding_role = str(binding.get("binding_role", "primary")).strip() or "primary"
    binding_strength = str(binding.get("binding_strength", "")).strip()

    rows: list[dict[str, str]] = []
    for item in contains:
        code = item["code"]
        member_type = _member_type(semantic_id, code)
        rows.append(
            {
                "semantic_id": semantic_id,
                "code_system_oid": code_system_oid,
                "code": code,
                "display": item.get("display", ""),
                "member_type": member_type,
                "binding_role": binding_role,
                "binding_strength": binding_strength,
                "active": "true",
                "sort_order": str(_sort_key(semantic_id, code, member_type)),
                "notes": expand_note,
            }
        )

    rows.sort(key=lambda r: (int(r["sort_order"]), r["code"]))
    for i, row in enumerate(rows, start=1):
        if row["member_type"] == "detailed":
            row["sort_order"] = str(100 + i)
    return rows


def _apply_steward_overrides(
    new_rows: list[dict[str, str]],
    existing_sid: pd.DataFrame,
) -> list[dict[str, str]]:
    if existing_sid.empty:
        return new_rows

    for row in new_rows:
        match = existing_sid[
            (existing_sid["code"] == row["code"])
            & (~existing_sid["member_type"].isin(PRESERVE_MEMBER_TYPES))
        ]
        if match.empty:
            continue
        prior = match.iloc[0]
        for col in ("notes", "active", "sort_order"):
            val = str(prior.get(col, "")).strip()
            if val and col == "notes" and row["notes"] not in val:
                row["notes"] = f"{val} | {row['notes']}" if row["notes"] else val
            elif val and col != "notes":
                row[col] = val
    return new_rows


def merge_members(
    existing: pd.DataFrame,
    semantic_id: str,
    new_rows: list[dict[str, str]],
) -> pd.DataFrame:
    if existing.empty:
        return pd.DataFrame(new_rows, columns=MEMBER_COLUMNS)

    other = existing[existing["semantic_id"] != semantic_id]
    existing_sid = existing[existing["semantic_id"] == semantic_id]
    preserved = existing_sid[existing_sid["member_type"].isin(PRESERVE_MEMBER_TYPES)]

    new_rows = _apply_steward_overrides(new_rows, existing_sid)
    expanded = pd.DataFrame(new_rows, columns=MEMBER_COLUMNS)

    return pd.concat([other, preserved, expanded], ignore_index=True)


def load_bindings(repo_root: Path) -> pd.DataFrame:
    path = repo_root / "ddc-value_set_binding.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"Missing bindings parquet: {path}")
    return pd.read_parquet(path)


def load_members(repo_root: Path) -> pd.DataFrame:
    path = repo_root / "ddc-value_set_member.parquet"
    if path.is_file():
        df = pd.read_parquet(path)
        for col in MEMBER_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[MEMBER_COLUMNS]
    return pd.DataFrame(columns=MEMBER_COLUMNS)


def is_expandable_binding(row: pd.Series) -> bool:
    url = str(row.get("value_set_url", "")).strip()
    return "/ValueSet/" in url or url.endswith("-Race") or url.endswith("-Ethnicity")


def build_members(
    repo_root: Path,
    semantic_ids: tuple[str, ...],
    *,
    offline: bool,
    write_cache: bool,
    dry_run: bool,
) -> pd.DataFrame:
    bindings = load_bindings(repo_root)
    members = load_members(repo_root)
    expand_note = f"HL7 ValueSet expand ({date.today().isoformat()})"

    for semantic_id in semantic_ids:
        binding_rows = bindings[bindings["semantic_id"] == semantic_id]
        if binding_rows.empty:
            print(f"  skip {semantic_id}: no binding row")
            continue
        binding = binding_rows.iloc[0]
        if not is_expandable_binding(binding):
            print(f"  skip {semantic_id}: value_set_url is not a ValueSet ({binding.get('value_set_url')})")
            continue

        value_set_url = str(binding["value_set_url"]).strip()
        cache_path = _cache_path(repo_root, value_set_url)

        if offline:
            contains = load_expansion_cache(cache_path)
            source = f"cache {_slug_from_url(value_set_url)}"
        else:
            contains = expand_valueset_online(value_set_url)
            source = "tx.fhir.org $expand"
            if write_cache:
                write_expansion_cache(cache_path, value_set_url, contains)
                print(f"  wrote cache {cache_path}")

        new_rows = expansion_to_member_rows(semantic_id, binding, contains, expand_note)
        members = merge_members(members, semantic_id, new_rows)
        print(f"  {semantic_id}: {len(new_rows)} codes from {source}")

    if not dry_run:
        out_path = repo_root / "ddc-value_set_member.parquet"
        members.to_parquet(out_path, index=False)
        print(f"Wrote {out_path} ({len(members)} rows total)")
        import sys

        scripts_dir = Path(__file__).resolve().parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from enrich_parquet_for_pbi import enrich_members

        enrich_members(out_path)

    return members


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--semantic-id",
        nargs="+",
        default=list(DEFAULT_SEMANTIC_IDS),
        help="semantic_id values to expand (default: Patient.race Patient.ethnicity)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Load expansion from data/terminology/*.expansion.json cache",
    )
    parser.add_argument(
        "--write-cache",
        action="store_true",
        help="When online, save expansion JSON under data/terminology/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print counts without writing parquet",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    semantic_ids = tuple(args.semantic_id)

    print(f"Expanding value set members for: {', '.join(semantic_ids)}")
    build_members(
        repo_root,
        semantic_ids,
        offline=args.offline,
        write_cache=args.write_cache,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
