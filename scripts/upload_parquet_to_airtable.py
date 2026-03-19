import json
import os
import argparse
import re
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd
import requests


BASE_DIR = r"C:\AI\chi-data-dictionary-catalog"

# Airtable base and table names/IDs.
# Note: Airtable REST endpoints use table NAME (not table ID) in the URL path.
AIRTABLE_BASE_ID = "appLZAy0wzE1x3yzU"

TABLES = [
    {
        "name": "ddc-master_patient_catalog",
        "parquet_path": os.path.join(BASE_DIR, "ddc-master_patient_catalog.parquet"),
        "type": "catalog",
    },
    {
        "name": "ddc-master_patient_dictionary",
        "parquet_path": os.path.join(BASE_DIR, "ddc-master_patient_dictionary.parquet"),
        "type": "dictionary",
    },
    {
        "name": "ddc-hl7_adt_catalog",
        "parquet_path": os.path.join(BASE_DIR, "ddc-hl7_adt_catalog.parquet"),
        "type": "adt",
    },
    {
        "name": "ddc-ccda_catalog",
        "parquet_path": os.path.join(BASE_DIR, "ddc-ccda_catalog.parquet"),
        "type": "ccda",
    },
    {
        "name": "ddc-data_source_availability",
        "parquet_path": os.path.join(BASE_DIR, "ddc-data_source_availability.parquet"),
        "type": "availability",
    },
]

CATALOG_COLS = [
    "semantic_id",
    "uscdi_element",
    "uscdi_description",
    "classification",
    "ruleset_category",
    "privacy_security",
    "domain",
    "rollup_relationship",
    "is_rollup",
    "composite_group",
    "data_steward",
    "steward_contact",
    "approval_status",
    "schema_version",
    "last_modified_date",
    "identifier_type",
    "identifier_authority",
    "hipaa_category",
    "fhir_security_label",
    "consent_category",
]

DICTIONARY_COLS = [
    "semantic_id",
    "hie_survivorship_logic",
    "data_source_rank_reference",
    "coverage_personids",
    "granularity_level",
    "innovaccer_survivorship_logic",
    "data_quality_notes",
    "fhir_r4_path",
    "fhir_data_type",
    "shie_survivorship_logic",
    "calculation_grain",
    "historical_freeze",
    "recalc_window_months",
    "fhir_must_support",
    "fhir_profile",
    "fhir_cardinality",
    "identity_resolution_notes",
    "tie_breaker_rule",
    "conflict_detection_enabled",
    "manual_override_allowed",
    "de_identification_method",
]

ADT_COLS = [
    "message_format",
    "message_type",
    "segment_id",
    "field_id",
    "field_name",
    "data_type",
    "optionality",
    "cardinality",
    "semantic_id",
    "fhir_r4_path",
    "notes",
]

CCDA_COLS = ["message_format", "section_name", "entry_type", "xml_path", "semantic_id", "fhir_r4_path", "notes"]

AVAILABILITY_COLS = [
    "source_id",
    "semantic_id",
    "availability",
    "completeness_pct",
    "timeliness_sla_hours",
    "notes",
]

CATALOG_LINK_FIELD_NAME = "catalog_element"

FHIR_QA_READINESS_FIELD = "fhir_r4_mapping_readiness"
FHIR_QA_DETAILS_FIELD = "fhir_r4_mapping_gap_details"
STANDARDS_READINESS_FIELD = "standards_curation_readiness"
STANDARDS_GAP_DETAILS_FIELD = "standards_curation_gap_details"


def load_airtable_token() -> str:
    """
    Loads Airtable API token.

    Prefer the environment variable `AIRTABLE_API_KEY`.
    Otherwise fall back to the Cursor MCP config.
    """
    env_token = os.getenv("AIRTABLE_API_KEY")
    if env_token:
        return env_token

    mcp_path = r"C:\Users\apras\.cursor\mcp.json"
    with open(mcp_path, "r", encoding="utf-8") as f:
        mcp = json.load(f)
    return mcp["mcpServers"]["airtable"]["env"]["AIRTABLE_API_KEY"]


def chunked(items: List[Any], size: int) -> Iterable[List[Any]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def airtable_request(
    session: requests.Session,
    method: str,
    url: str,
    json_body: Dict[str, Any] | None = None,
    params: Dict[str, Any] | None = None,
):
    headers = {"Authorization": f"Bearer {session.headers['AuthorizationToken']}"}
    # We store the token in the session header namespace to keep request helpers concise.
    headers["Content-Type"] = "application/json"
    resp = session.request(method, url, headers=headers, json=json_body, params=params, timeout=60)
    if resp.status_code >= 400:
        try:
            payload = resp.json()
        except Exception:
            payload = {"raw": resp.text}
        raise RuntimeError(f"Airtable API error {resp.status_code}: {payload}")
    return resp


def list_existing_records(
    session: requests.Session,
    table_name: str,
    max_records: int = 500,
) -> List[Dict[str, Any]]:
    """
    Returns Airtable records up to max_records, with pagination (up to Airtable's offset behavior).
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}"
    params: Dict[str, Any] = {"maxRecords": max_records}

    # Airtable supports offset pagination; we loop only if the server returns offset.
    all_records: List[Dict[str, Any]] = []
    offset = None

    while True:
        if offset:
            params["offset"] = offset
        resp = session.get(url, params=params, timeout=60, headers={"Authorization": f"Bearer {session.headers['AuthorizationToken']}"})
        if resp.status_code >= 400:
            try:
                payload = resp.json()
            except Exception:
                payload = {"raw": resp.text}
            raise RuntimeError(f"Airtable list error {resp.status_code}: {payload}")
        data = resp.json()
        records = data.get("records", [])
        all_records.extend(records)
        offset = data.get("offset")
        if not offset or len(all_records) >= max_records:
            break
    return all_records[:max_records]


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure all values are strings; convert NaN/None -> empty string.
    return df.fillna("").astype(str)


def get_expected_cols(table_type: str) -> List[str]:
    if table_type == "catalog":
        return CATALOG_COLS
    if table_type == "dictionary":
        return DICTIONARY_COLS
    if table_type == "adt":
        return ADT_COLS
    if table_type == "ccda":
        return CCDA_COLS
    if table_type == "availability":
        return AVAILABILITY_COLS
    raise ValueError(f"Unknown table_type={table_type}")


def compute_upsert_key(table_type: str, row_fields: Dict[str, str]) -> str:
    if table_type in ("catalog", "dictionary"):
        return row_fields["semantic_id"]
    if table_type == "adt":
        return "|".join(
            [
                row_fields["semantic_id"],
                row_fields["message_type"],
                row_fields["segment_id"],
                row_fields["field_id"],
                row_fields["fhir_r4_path"],
            ]
        )
    if table_type == "ccda":
        return "|".join(
            [
                row_fields["semantic_id"],
                row_fields["section_name"],
                row_fields["entry_type"],
                row_fields["xml_path"],
                row_fields["fhir_r4_path"],
            ]
        )
    if table_type == "availability":
        return "|".join([row_fields["source_id"], row_fields["semantic_id"]])
    raise ValueError(f"Unknown table_type={table_type}")


def build_fields_payload(table_type: str, expected_cols: List[str], row: Dict[str, Any], upsert_key: str) -> Dict[str, str]:
    fields = {c: str(row.get(c, "")) for c in expected_cols}
    if table_type in ("catalog", "dictionary"):
        fields["Name"] = row.get("semantic_id", "") or ""
    else:
        fields["Name"] = upsert_key
    return fields


def compute_fhir_r4_mapping_qa(row_fields: Dict[str, str]) -> tuple[str, str]:
    """
    Compute a steward-friendly FHIR R4 curation readiness summary.
    Uses only the existing dictionary columns as signals.
    """
    reasons: List[str] = []

    fhir_path = (row_fields.get("fhir_r4_path") or "").strip()
    fhir_type = (row_fields.get("fhir_data_type") or "").strip()
    fhir_profile = (row_fields.get("fhir_profile") or "").strip()
    must_support = (row_fields.get("fhir_must_support") or "").strip()
    cardinality = (row_fields.get("fhir_cardinality") or "").strip()

    if not fhir_path:
        reasons.append("Missing FHIR R4 path (fhir_r4_path)")
    else:
        # Basic format sanity: FHIR paths should be compact; whitespace is usually a data issue.
        if re.search(r"\s", fhir_path):
            reasons.append("FHIR R4 path contains whitespace (check format)")

    if not fhir_type:
        reasons.append("Missing FHIR data type (fhir_data_type)")
    if not must_support:
        reasons.append("Missing FHIR Must Support flag (fhir_must_support)")
    if not cardinality:
        reasons.append("Missing FHIR cardinality (fhir_cardinality)")
    if not fhir_profile:
        reasons.append("Missing FHIR profile (fhir_profile)")

    if not reasons:
        return "Complete", "OK: FHIR R4 mapping fields are populated."

    # Keep the top-level value short for quick queue filtering.
    return "Needs FHIR R4 QA", "; ".join(reasons)


def compute_overall_standards_curation_qa(row_fields: Dict[str, str]) -> tuple[str, str]:
    """
    Compute an overall steward queue signal that combines:
    - FHIR R4 mapping readiness (derived from existing FHIR columns)
    - HIE survivorship logic presence
    - Identity/de-identification governance presence (FHIR-adjacent governance)
    """
    fhir_readiness, _ = compute_fhir_r4_mapping_qa(row_fields)

    gaps: List[str] = []

    # Survivorship & sourcing (standards domain for golden value determination)
    hie_logic = (row_fields.get("hie_survivorship_logic") or "").strip()
    data_source_rank_ref = (row_fields.get("data_source_rank_reference") or "").strip()
    granularity = (row_fields.get("granularity_level") or "").strip()

    if not hie_logic:
        gaps.append("Missing HIE survivorship logic (hie_survivorship_logic)")
    if not data_source_rank_ref:
        gaps.append("Missing source rank reference (data_source_rank_reference)")
    if not granularity:
        gaps.append("Missing granularity level (granularity_level)")

    # Identity resolution and de-identification governance
    identity_notes = (row_fields.get("identity_resolution_notes") or "").strip()
    deid_method = (row_fields.get("de_identification_method") or "").strip()
    tie_breaker = (row_fields.get("tie_breaker_rule") or "").strip()

    if not identity_notes:
        gaps.append("Missing identity resolution notes (identity_resolution_notes)")
    if not deid_method:
        gaps.append("Missing de-identification method (de_identification_method)")
    if not tie_breaker:
        gaps.append("Missing tie breaker rule (tie_breaker_rule)")

    if fhir_readiness != "Complete":
        gaps.append(fhir_readiness)

    if not gaps:
        return "Complete", "All standards curation signals are populated."

    return "Needs Standards QA", "; ".join(gaps)


def batch_patch_records(session: requests.Session, table_name: str, records: List[Dict[str, Any]]):
    """
    Batch update up to 10 records with PATCH.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}"
    payload = {"records": records}
    resp = session.patch(
        url,
        headers={"Authorization": f"Bearer {session.headers['AuthorizationToken']}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if resp.status_code >= 400:
        try:
            payload = resp.json()
        except Exception:
            payload = {"raw": resp.text}
        raise RuntimeError(f"Batch PATCH error {resp.status_code}: {payload}")


def batch_post_records(session: requests.Session, table_name: str, records: List[Dict[str, Any]]):
    """
    Batch create up to 10 records with POST.
    """
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}"
    payload = {"records": records}
    resp = session.post(
        url,
        headers={"Authorization": f"Bearer {session.headers['AuthorizationToken']}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if resp.status_code >= 400:
        try:
            payload = resp.json()
        except Exception:
            payload = {"raw": resp.text}
        raise RuntimeError(f"Batch POST error {resp.status_code}: {payload}")


def airtable_meta_tables(session: requests.Session, base_id: str) -> List[Dict[str, Any]]:
    """
    Discover Airtable table IDs by name using the meta API.
    """
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    resp = airtable_request(session, "GET", url)
    data = resp.json()
    return data.get("tables", [])


def airtable_meta_fields(session: requests.Session, base_id: str, table_id: str) -> List[Dict[str, Any]]:
    """
    Discover Airtable field definitions for a table via the meta API.
    """
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields"
    resp = airtable_request(session, "GET", url)
    data = resp.json()
    return data.get("fields", [])


def airtable_meta_create_relation_field(
    session: requests.Session,
    base_id: str,
    table_id: str,
    name: str,
    linked_table_id: str,
) -> None:
    """
    Create a `singleRecordLink` field in a target table.
    """
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields"
    payload = {
        "name": name,
        # Airtable Meta API expects link fields to be created as "multipleRecordLinks".
        # We will populate the field with an array containing exactly one record ID.
        "type": "multipleRecordLinks",
        "options": {"linkedTableId": linked_table_id},
    }
    airtable_request(session, "POST", url, json_body=payload)


def ensure_relation_fields(
    session: requests.Session,
    base_id: str,
    catalog_table_name: str,
    relation_field_name: str,
) -> None:
    """
    Create relation field (if missing) in:
      - ddc-master_patient_dictionary
      - ddc-hl7_adt_catalog
      - ddc-ccda_catalog
      - ddc-data_source_availability

    All relations point to the catalog table row via semantic_id.
    """
    tables_meta = airtable_meta_tables(session, base_id)
    table_id_by_name = {t["name"]: t["id"] for t in tables_meta if "name" in t and "id" in t}
    table_meta_by_name = {t["name"]: t for t in tables_meta if "name" in t}

    if catalog_table_name not in table_id_by_name:
        raise RuntimeError(f"Could not find catalog table '{catalog_table_name}' in Airtable meta.")

    catalog_table_id = table_id_by_name[catalog_table_name]

    target_table_names = [
        "ddc-master_patient_dictionary",
        "ddc-hl7_adt_catalog",
        "ddc-ccda_catalog",
        "ddc-data_source_availability",
    ]

    for table_name in target_table_names:
        if table_name not in table_id_by_name:
            raise RuntimeError(f"Could not find table '{table_name}' in Airtable meta.")
        table_id = table_id_by_name[table_name]

        fields = (table_meta_by_name.get(table_name, {}) or {}).get("fields", []) or []
        if any(f.get("name") == relation_field_name for f in fields):
            print(f"Relation field already exists: {table_name}.{relation_field_name}")
            continue

        print(f"Creating relation field: {table_name}.{relation_field_name} -> {catalog_table_name}")
        airtable_meta_create_relation_field(
            session=session,
            base_id=base_id,
            table_id=table_id,
            name=relation_field_name,
            linked_table_id=catalog_table_id,
        )


def populate_relation_fields(
    session: requests.Session,
    _base_id: str,
    catalog_table_name: str,
    relation_field_name: str,
) -> None:
    """
    Populate relation fields using semantic_id match.
    """
    print("\n== Populating relation fields ==")

    catalog_records = list_existing_records(session, table_name=catalog_table_name, max_records=1000)
    catalog_id_by_semantic: Dict[str, str] = {}
    for rec in catalog_records:
        rec_fields = rec.get("fields", {}) or {}
        sem = str(rec_fields.get("semantic_id", "") or "").strip()
        if not sem:
            continue
        catalog_id_by_semantic[sem] = rec["id"]

    def patch_table(table_name: str) -> None:
        records = list_existing_records(session, table_name=table_name, max_records=1000)
        updates: List[Dict[str, Any]] = []
        for rec in records:
            rec_fields = rec.get("fields", {}) or {}
            sem = str(rec_fields.get("semantic_id", "") or "").strip()
            cat_id = catalog_id_by_semantic.get(sem)
            if not cat_id:
                continue

            updates.append(
                {
                    "id": rec["id"],
                    "fields": {
                        # REST API expects arrays of record IDs for link fields.
                        relation_field_name: [cat_id],
                    },
                }
            )

        if not updates:
            print(f"No relation updates needed: {table_name}")
            return

        print(f"Patching {table_name}: {len(updates)} row(s)")
        for batch in chunked(updates, 10):
            batch_patch_records(session, table_name=table_name, records=batch)

    patch_table("ddc-master_patient_dictionary")
    patch_table("ddc-hl7_adt_catalog")
    patch_table("ddc-ccda_catalog")
    patch_table("ddc-data_source_availability")


def main():
    global AIRTABLE_BASE_ID

    parser = argparse.ArgumentParser(
        description="Upload CHI Parquet tables to Airtable (upsert + optional Link/Relation population)."
    )
    parser.add_argument(
        "--base-id",
        default=AIRTABLE_BASE_ID,
        help="Airtable Base ID (e.g. appXXXXXXXXXXXXXX).",
    )
    parser.add_argument(
        "--add-relations",
        action="store_true",
        help="Create/populate Link/Relation fields using semantic_id joins.",
    )
    parser.add_argument(
        "--relation-field-name",
        default=CATALOG_LINK_FIELD_NAME,
        help="Name of the relation field to create/populate.",
    )
    parser.add_argument(
        "--catalog-table-name",
        default="ddc-master_patient_catalog",
        help="Name of the catalog table used as the relation target.",
    )
    parser.add_argument(
        "--on-duplicate-key",
        choices=["keep_first", "keep_last", "error"],
        default="keep_first",
        help="What to do if Airtable already contains multiple rows with the same upsert key.",
    )
    args = parser.parse_args()

    AIRTABLE_BASE_ID = args.base_id

    token = load_airtable_token()
    session = requests.Session()
    session.headers["AuthorizationToken"] = token  # internal-only

    # Discover which QA fields exist so we don't attempt to write fields that aren't present.
    tables_meta = airtable_meta_tables(session=session, base_id=AIRTABLE_BASE_ID)
    table_meta_by_name = {t.get("name"): t for t in tables_meta if isinstance(t, dict) and t.get("name")}
    dict_meta = table_meta_by_name.get("ddc-master_patient_dictionary") or {}
    dict_fields = dict_meta.get("fields") or []
    dict_has_fhir_qa = any(f.get("name") == FHIR_QA_READINESS_FIELD for f in dict_fields) and any(
        f.get("name") == FHIR_QA_DETAILS_FIELD for f in dict_fields
    )
    dict_has_overall_standards_qa = any(f.get("name") == STANDARDS_READINESS_FIELD for f in dict_fields) and any(
        f.get("name") == STANDARDS_GAP_DETAILS_FIELD for f in dict_fields
    )

    table_results: List[Dict[str, Any]] = []

    for t in TABLES:
        table_name = t["name"]
        parquet_path = t["parquet_path"]
        table_type = t["type"]

        expected_cols = get_expected_cols(table_type)
        print(f"\n== {table_name} ==")
        print(f"Loading parquet: {parquet_path}")

        df = pd.read_parquet(parquet_path)
        df = normalize_df(df)

        missing_cols = [c for c in expected_cols if c not in df.columns]
        if missing_cols:
            raise RuntimeError(f"Missing columns in parquet for {table_name}: {missing_cols}")

        existing = list_existing_records(session, table_name=table_name, max_records=500)
        existing_map: Dict[str, str] = {}

        # Build key map from Airtable records.
        for rec in existing:
            rec_id = rec["id"]
            rec_fields = rec.get("fields", {}) or {}
            # Normalize missing values to empty string for key computation.
            row_fields = {c: str(rec_fields.get(c, "") or "") for c in expected_cols}
            key = compute_upsert_key(table_type, row_fields)
            if key in existing_map:
                if args.on_duplicate_key == "error":
                    raise RuntimeError(f"Duplicate upsert key in Airtable for {table_name}: {key}")
                # Keep first by default; allow overriding with keep_last.
                if args.on_duplicate_key == "keep_last":
                    print(f"Duplicate upsert key (keep_last): {table_name} key={key}")
                    existing_map[key] = rec_id
                else:
                    print(f"Duplicate upsert key (keep_first): {table_name} key={key} -> skipping")
                continue
            existing_map[key] = rec_id

        created = 0
        updated = 0

        # Deduplicate within a single run:
        # - Airtable cannot PATCH the same record twice in a single request.
        # - Parquet exports may contain repeated rows with the same upsert key.
        to_create_by_key: Dict[str, Dict[str, str]] = {}
        to_update_by_rec_id: Dict[str, Dict[str, str]] = {}

        # Compute upsert ops.
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            # Coerce required columns to str for key computation.
            row_fields = {c: str(row_dict.get(c, "") or "") for c in expected_cols}
            upsert_key = compute_upsert_key(table_type, row_fields)
            fields_payload = build_fields_payload(table_type, expected_cols, row_fields, upsert_key)

            if table_type == "dictionary" and dict_has_fhir_qa:
                readiness, details = compute_fhir_r4_mapping_qa(row_fields)
                fields_payload[FHIR_QA_READINESS_FIELD] = readiness
                fields_payload[FHIR_QA_DETAILS_FIELD] = details

                if dict_has_overall_standards_qa:
                    overall_readiness, overall_details = compute_overall_standards_curation_qa(row_fields)
                    fields_payload[STANDARDS_READINESS_FIELD] = overall_readiness
                    fields_payload[STANDARDS_GAP_DETAILS_FIELD] = overall_details

            if upsert_key in existing_map:
                rec_id = existing_map[upsert_key]
                to_update_by_rec_id[rec_id] = fields_payload
            else:
                to_create_by_key[upsert_key] = fields_payload

        to_update: List[Dict[str, Any]] = [{"id": rec_id, "fields": fields} for rec_id, fields in to_update_by_rec_id.items()]
        to_create: List[Dict[str, Any]] = [{"fields": fields} for fields in to_create_by_key.values()]

        # Apply updates first, then creates.
        try:
            for batch in chunked(to_update, 10):
                batch_patch_records(session, table_name=table_name, records=batch)
                updated += len(batch)
            for batch in chunked(to_create, 10):
                batch_post_records(session, table_name=table_name, records=batch)
                created += len(batch)
        except Exception as e:
            # Best-effort: include counts and a generic message; Airtable response is inside exception.
            raise RuntimeError(f"Failed during upsert for table={table_name}. created_so_far={created}, updated_so_far={updated}. Error={e}")

        table_results.append(
            {
                "table": table_name,
                "existing_records_seen": len(existing),
                "created": created,
                "updated": updated,
            }
        )

    print("\n=== Summary ===")
    for r in table_results:
        print(f"{r['table']}: existing={r['existing_records_seen']} created={r['created']} updated={r['updated']}")

    if args.add_relations:
        ensure_relation_fields(
            session=session,
            base_id=AIRTABLE_BASE_ID,
            catalog_table_name=args.catalog_table_name,
            relation_field_name=args.relation_field_name,
        )
        populate_relation_fields(
            session=session,
            _base_id=AIRTABLE_BASE_ID,
            catalog_table_name=args.catalog_table_name,
            relation_field_name=args.relation_field_name,
        )


if __name__ == "__main__":
    main()

