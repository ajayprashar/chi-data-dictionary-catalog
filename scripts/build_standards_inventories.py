"""
Build standards parquet files for FHIR and business rules.

This script keeps the current five-table model intact and adds companion
inventory artifacts that can be iterated safely before promoting schema
changes into core tables.

Outputs (project root by default):
  - ddc-fhir_inventory.parquet
  - ddc-business_rules.parquet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List

import pandas as pd


FHIR_ADMIN_RESOURCES = {
    "Patient",
    "Practitioner",
    "CareTeam",
    "Device",
    "Organization",
    "Location",
    "HealthcareService",
}


def _clean_str(v: object) -> str:
    if pd.isna(v):
        return ""
    return str(v).strip()


def _resource_from_fhir_path(path: str) -> str:
    if not path:
        return ""
    return path.split(".", 1)[0].strip()


def _build_fhir_inventory(df_dict: pd.DataFrame, include_all_resources: bool) -> pd.DataFrame:
    rows: List[dict] = []

    for _, row in df_dict.iterrows():
        semantic_id = _clean_str(row.get("semantic_id", ""))
        fhir_path = _clean_str(row.get("fhir_r4_path", ""))
        resource = _resource_from_fhir_path(fhir_path)

        if not include_all_resources and resource and resource not in FHIR_ADMIN_RESOURCES:
            continue

        if not fhir_path:
            # Keep only mapped FHIR rows for inventory quality.
            continue

        rows.append(
            {
                "inventory_scope": "admin_core" if resource in FHIR_ADMIN_RESOURCES else "other",
                "fhir_version": "R4",
                "fhir_resource": resource,
                "fhir_path": fhir_path,
                "fhir_data_type": _clean_str(row.get("fhir_data_type", "")),
                "fhir_cardinality": _clean_str(row.get("fhir_cardinality", "")),
                "fhir_must_support": _clean_str(row.get("fhir_must_support", "")),
                "fhir_profile": _clean_str(row.get("fhir_profile", "")),
                "fhir_definition": "",
                "standard_reference_url": f"https://hl7.org/fhir/R4/{resource.lower()}.html" if resource else "",
                "semantic_id": semantic_id,
                "mapping_status": "mapped" if semantic_id else "needs_new_semantic",
                "business_rule_required": "",
                "business_rule_notes": "",
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out = out.drop_duplicates(subset=["fhir_path", "semantic_id"]).sort_values(["fhir_resource", "fhir_path", "semantic_id"])
    return out.reset_index(drop=True)


def _build_fhir_inventory_from_r5_spec(
    df_dict: pd.DataFrame,
    profiles_resources_path: Path,
    include_all_resources: bool,
) -> pd.DataFrame:
    """
    Build inventory from FHIR R5 StructureDefinition snapshot elements and
    merge semantic mappings from existing dictionary fhir_r4_path values.
    """
    bundle = json.loads(profiles_resources_path.read_text(encoding="utf-8"))
    entries = bundle.get("entry", [])

    dict_by_path: dict[str, dict] = {}
    for _, row in df_dict.iterrows():
        fhir_path = _clean_str(row.get("fhir_r4_path", ""))
        if not fhir_path:
            continue
        dict_by_path[fhir_path] = {
            "semantic_id": _clean_str(row.get("semantic_id", "")),
            "fhir_data_type": _clean_str(row.get("fhir_data_type", "")),
            "fhir_cardinality": _clean_str(row.get("fhir_cardinality", "")),
            "fhir_must_support": _clean_str(row.get("fhir_must_support", "")),
            "fhir_profile": _clean_str(row.get("fhir_profile", "")),
        }

    rows: List[dict] = []
    for entry in entries:
        sd = entry.get("resource", {})
        if sd.get("resourceType") != "StructureDefinition":
            continue
        if sd.get("kind") != "resource":
            continue

        resource = _clean_str(sd.get("type", ""))
        if not include_all_resources and resource not in FHIR_ADMIN_RESOURCES:
            continue

        elements = sd.get("snapshot", {}).get("element", []) or []
        for element in elements:
            fhir_path = _clean_str(element.get("path", ""))
            if not fhir_path or "." not in fhir_path:
                # Skip root resource row (e.g., "Patient"), keep child elements.
                continue

            mapped = dict_by_path.get(fhir_path, {})
            types = element.get("type", []) or []
            inferred_type = ""
            if types and isinstance(types, list):
                inferred_type = _clean_str(types[0].get("code", ""))

            min_v = _clean_str(element.get("min", ""))
            max_v = _clean_str(element.get("max", ""))
            cardinality = f"{min_v}..{max_v}" if (min_v or max_v) else ""

            fhir_data_type = mapped.get("fhir_data_type", "") or inferred_type
            fhir_cardinality = mapped.get("fhir_cardinality", "") or cardinality
            semantic_id = mapped.get("semantic_id", "")
            mapping_status = "mapped" if semantic_id else "needs_new_semantic"

            rows.append(
                {
                    "inventory_scope": "admin_core" if resource in FHIR_ADMIN_RESOURCES else "other",
                    "fhir_version": "R5",
                    "fhir_resource": resource,
                    "fhir_path": fhir_path,
                    "fhir_data_type": fhir_data_type,
                    "fhir_cardinality": fhir_cardinality,
                    "fhir_must_support": mapped.get("fhir_must_support", _clean_str(element.get("mustSupport", ""))),
                    "fhir_profile": mapped.get("fhir_profile", _clean_str(sd.get("url", ""))),
                    "fhir_definition": _clean_str(element.get("definition", "")),
                    "standard_reference_url": _clean_str(sd.get("url", "")),
                    "semantic_id": semantic_id,
                    "mapping_status": mapping_status,
                    "business_rule_required": "",
                    "business_rule_notes": "",
                }
            )

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out = out.drop_duplicates(subset=["fhir_path", "semantic_id"]).sort_values(["fhir_resource", "fhir_path", "semantic_id"])
    return out.reset_index(drop=True)


def _build_business_rules_stub(semantic_ids: Iterable[str]) -> pd.DataFrame:
    rows = []
    for semantic_id in sorted({s for s in semantic_ids if s}):
        rows.append(
            {
                "rule_id": "",
                "semantic_id": semantic_id,
                "standard_scope": "",  # fhir | adt | ccda | cross-standard
                "rule_name": "",
                "rule_type": "",  # constraint | transformation | survivorship | privacy | quality
                "rule_expression": "",
                "severity": "",  # info | warning | error
                "active": "true",
                "owner": "",
                "approval_status": "",  # draft | review | approved | deprecated
                "notes": "",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build FHIR inventory and business rules parquet files.")
    parser.add_argument(
        "-d",
        "--directory",
        default=".",
        help="Project root containing the ddc-*.parquet files.",
    )
    parser.add_argument(
        "--include-all-fhir-resources",
        action="store_true",
        help="Include all dictionary rows with fhir_r4_path, not just Administration resources.",
    )
    parser.add_argument(
        "--fhir-spec-dir",
        default="fhir_release_5",
        help="Directory containing FHIR R5 bundles (e.g., profiles-resources.json).",
    )
    args = parser.parse_args()

    root = Path(args.directory).resolve()
    dict_path = root / "ddc-master_patient_dictionary.parquet"
    df_dict = pd.read_parquet(dict_path).fillna("")

    profiles_resources_path = (root / args.fhir_spec_dir / "profiles-resources.json").resolve()
    if profiles_resources_path.exists():
        fhir_inventory = _build_fhir_inventory_from_r5_spec(
            df_dict=df_dict,
            profiles_resources_path=profiles_resources_path,
            include_all_resources=args.include_all_fhir_resources,
        )
    else:
        # Fallback to existing dictionary-only inventory if R5 bundle is missing.
        fhir_inventory = _build_fhir_inventory(df_dict, include_all_resources=args.include_all_fhir_resources)
    business_rules = _build_business_rules_stub(
        list(fhir_inventory.get("semantic_id", []))
    )

    fhir_inventory.to_parquet(root / "ddc-fhir_inventory.parquet", index=False)
    business_rules.to_parquet(root / "ddc-business_rules.parquet", index=False)

    print("Wrote:")
    print(f"- {root / 'ddc-fhir_inventory.parquet'} ({len(fhir_inventory)} rows)")
    print(f"- {root / 'ddc-business_rules.parquet'} ({len(business_rules)} rows)")


if __name__ == "__main__":
    main()
