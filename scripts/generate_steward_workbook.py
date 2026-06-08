#!/usr/bin/env python3
"""
Generate the CHI steward workbook from repo parquet files.

The workbook mirrors ddc-* parquet tables as Excel sheets, documents join
relationships on _Model, and provides lookup-driven validation plus a
Concept_Explorer sheet for cross-table review by semantic_id.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

sys.path.insert(0, str(Path(__file__).resolve().parent))
from excel_workbook_common import (
    MODEL_FILL,
    autosize_columns,
    prepare_data_sheet,
    style_header_row,
    write_readme_sheet,
)


OUT_NAME = "chi-steward-workbook.xlsx"

PARQUET_SHEETS: list[tuple[str, str, str]] = [
    ("ddc-master_patient_catalog.parquet", "Catalog", "Catalog"),
    ("ddc-master_patient_dictionary.parquet", "Dictionary", "Dictionary"),
    ("ddc-data_source_availability.parquet", "Source_Availability", "SourceAvailability"),
    ("ddc-hl7_adt_catalog.parquet", "ADT_Mappings", "AdtMappings"),
    ("ddc-ccda_catalog.parquet", "CCDA_Mappings", "CcdaMappings"),
    ("ddc-fhir_inventory.parquet", "FHIR_Inventory", "FhirInventory"),
    ("ddc-business_rules.parquet", "Business_Rules", "BusinessRules"),
]

MODEL_ROWS = [
    ("rel_id", "parent_sheet", "parent_key", "child_sheet", "child_key", "cardinality", "description"),
    (
        "catalog_dictionary",
        "Catalog",
        "semantic_id",
        "Dictionary",
        "semantic_id",
        "1:1",
        "Each governed concept has one implementation definition row.",
    ),
    (
        "catalog_source_availability",
        "Catalog",
        "semantic_id",
        "Source_Availability",
        "semantic_id",
        "1:N",
        "Links each concept to the data sources that can provide it.",
    ),
    (
        "catalog_adt",
        "Catalog",
        "semantic_id",
        "ADT_Mappings",
        "semantic_id",
        "1:N",
        "HL7 ADT segment/field placements for the same concept.",
    ),
    (
        "catalog_ccda",
        "Catalog",
        "semantic_id",
        "CCDA_Mappings",
        "semantic_id",
        "1:N",
        "C-CDA/CCD XML paths for the same concept.",
    ),
    (
        "catalog_fhir_inventory",
        "Catalog",
        "semantic_id",
        "FHIR_Inventory",
        "semantic_id",
        "1:N",
        "FHIR standards inventory rows tied to the concept.",
    ),
    (
        "catalog_business_rules",
        "Catalog",
        "semantic_id",
        "Business_Rules",
        "semantic_id",
        "1:N",
        "Organization-specific rules for the concept.",
    ),
    (
        "catalog_steward_queue",
        "Catalog",
        "semantic_id",
        "Steward_Queue",
        "semantic_id",
        "1:1",
        "Optional steward workflow overlay keyed by semantic_id.",
    ),
]

STEWARD_QUEUE_HEADERS = [
    "semantic_id",
    "curation_status",
    "steward_assigned_to",
    "steward_action_notes",
    "reviewer_notes",
    "priority",
    "queue_type",
]

EXPLORER_FIELDS = [
    ("Catalog", "uscdi_element"),
    ("Catalog", "uscdi_description"),
    ("Catalog", "classification"),
    ("Catalog", "approval_status"),
    ("Dictionary", "fhir_r4_path"),
    ("Dictionary", "chi_survivorship_logic"),
    ("Dictionary", "data_source_rank_reference"),
]


def load_parquet_frames(repo_root: Path) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for parquet_name, _, _ in PARQUET_SHEETS:
        path = repo_root / parquet_name
        if not path.exists():
            raise FileNotFoundError(f"Missing required parquet file: {path}")
        frames[parquet_name] = pd.read_parquet(path).fillna("")
    return frames


def write_dataframe_sheet(ws: Worksheet, df: pd.DataFrame) -> list[str]:
    headers = [str(col) for col in df.columns]
    ws.append(headers)
    for row in df.itertuples(index=False, name=None):
        ws.append(["" if value is None else str(value) for value in row])
    style_header_row(ws)
    prepare_data_sheet(ws)
    autosize_columns(ws)
    return headers


def add_model_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("_Model")
    for row in MODEL_ROWS:
        ws.append(row)
    style_header_row(ws)
    for cell in ws[1]:
        cell.fill = MODEL_FILL
        cell.font = Font(bold=True)
    ws.freeze_panes = "A2"
    autosize_columns(ws)
    ws.sheet_state = "hidden"


def add_lookup_lists_sheet(wb: Workbook, frames: dict[str, pd.DataFrame]) -> None:
    ws = wb.create_sheet("Lookup_Lists")
    catalog = frames["ddc-master_patient_catalog.parquet"]
    availability = frames["ddc-data_source_availability.parquet"]

    semantic_ids = sorted({str(v).strip() for v in catalog["semantic_id"] if str(v).strip()})
    source_ids = sorted({str(v).strip() for v in availability["source_id"] if str(v).strip()})

    ws["A1"] = "semantic_id"
    ws["B1"] = "source_id"
    ws["D1"] = "mapping_status"
    ws["E1"] = "approval_status"
    ws["F1"] = "availability"
    ws["G1"] = "curation_status"
    style_header_row(ws)

    mapping_status = ["mapped", "needs_new_semantic", "out_of_scope"]
    approval_status = ["Pending", "Ready", "Approved", "Needs Changes"]
    availability_vals = ["full", "partial", "none", "unknown"]
    curation_status = ["Needs Action", "In Progress", "Ready for Review", "Complete"]

    max_len = max(len(semantic_ids), len(source_ids), len(mapping_status), len(approval_status), len(availability_vals), len(curation_status))
    for idx in range(max_len):
        row = idx + 2
        if idx < len(semantic_ids):
            ws.cell(row=row, column=1, value=semantic_ids[idx])
        if idx < len(source_ids):
            ws.cell(row=row, column=2, value=source_ids[idx])
        if idx < len(mapping_status):
            ws.cell(row=row, column=4, value=mapping_status[idx])
        if idx < len(approval_status):
            ws.cell(row=row, column=5, value=approval_status[idx])
        if idx < len(availability_vals):
            ws.cell(row=row, column=6, value=availability_vals[idx])
        if idx < len(curation_status):
            ws.cell(row=row, column=7, value=curation_status[idx])

    autosize_columns(ws)


def add_source_registry_sheet(wb: Workbook, frames: dict[str, pd.DataFrame]) -> None:
    availability = frames["ddc-data_source_availability.parquet"]
    source_ids = sorted({str(v).strip() for v in availability["source_id"] if str(v).strip()})
    ws = wb.create_sheet("Source_Registry")
    headers = ["source_id", "source_name", "organization", "delivery_format", "notes"]
    ws.append(headers)
    for source_id in source_ids:
        ws.append([source_id, "", "", "", "Populate source metadata for steward reference."])
    style_header_row(ws)
    prepare_data_sheet(ws)
    autosize_columns(ws)


def add_steward_queue_sheet(wb: Workbook, frames: dict[str, pd.DataFrame]) -> None:
    catalog = frames["ddc-master_patient_catalog.parquet"]
    ws = wb.create_sheet("Steward_Queue")
    ws.append(STEWARD_QUEUE_HEADERS)
    for semantic_id in catalog["semantic_id"]:
        sid = str(semantic_id).strip()
        if not sid:
            continue
        ws.append([sid, "", "", "", "", "", ""])
    style_header_row(ws)
    prepare_data_sheet(ws)
    autosize_columns(ws)


def column_letter_for_header(ws: Worksheet, header_name: str) -> str:
    for idx, cell in enumerate(ws[1], 1):
        if cell.value == header_name:
            return get_column_letter(idx)
    raise ValueError(f"Header {header_name!r} not found on sheet {ws.title}")


def lookup_formula(sheet_name: str, key_col: str, value_col: str, last_row: int) -> str:
    """INDEX/MATCH works on older Excel builds that do not support XLOOKUP."""
    return (
        f'=IF($B$3="","",IFERROR(INDEX({sheet_name}!${value_col}$2:${value_col}${last_row},'
        f'MATCH($B$3,{sheet_name}!${key_col}$2:${key_col}${last_row},0)),""))'
    )


def add_concept_explorer_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("Concept_Explorer")
    ws["A1"] = "Concept Explorer"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A2"] = "Paste a semantic_id from Lookup_Lists column A into B3."
    ws["A3"] = "semantic_id"
    ws["B3"] = ""
    ws["A4"] = "Field"
    ws["B4"] = "Value"
    ws["A4"].font = Font(bold=True)
    ws["B4"].font = Font(bold=True)

    start_row = 5
    for offset, (sheet_name, column_name) in enumerate(EXPLORER_FIELDS):
        data_ws = wb[sheet_name]
        key_col = column_letter_for_header(data_ws, "semantic_id")
        value_col = column_letter_for_header(data_ws, column_name)
        last_row = max(2, data_ws.max_row)
        row = start_row + offset
        ws.cell(row=row, column=1, value=f"{sheet_name}.{column_name}")
        ws.cell(
            row=row,
            column=2,
            value=lookup_formula(sheet_name, key_col, value_col, last_row),
        )

    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 72
    for row in ws.iter_rows(min_row=5, max_row=start_row + len(EXPLORER_FIELDS) - 1, min_col=2, max_col=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")


def add_readme_sheet(wb: Workbook) -> None:
    ws = wb.active
    ws.title = "README"
    write_readme_sheet(
        ws,
        "CHI Steward Workbook",
        [
            (
                "Purpose",
                "Human-facing steward layer over the governed ddc-* parquet model. Edit data sheets, then import back with import_steward_workbook_to_parquet.py.",
            ),
            ("Join key", "semantic_id links Catalog to Dictionary, Source_Availability, ADT/CCDA mappings, FHIR inventory, business rules, and Steward_Queue."),
            ("Data source links", "Source_Availability links each semantic_id to source_id rows. Source_Registry holds source metadata for stewards."),
            ("Model sheet", "_Model documents parent/child relationships and cardinality."),
            ("Lookup_Lists", "Reference lists for semantic_id, source_id, and status values. Copy/paste into data sheets."),
            ("Concept_Explorer", "Paste a semantic_id into B3 to preview key catalog and dictionary fields."),
            ("Workflow", "Use Steward_Queue for curation_status and assignment. Queue fields are Excel-only until promoted to parquet."),
            ("Round trip", "python scripts/generate_steward_workbook.py exports parquet to this workbook. python scripts/import_steward_workbook_to_parquet.py writes edited data sheets back to parquet."),
            ("Do not edit", "README, _Model, Lookup_Lists, and Concept_Explorer are support sheets, not import sources."),
        ],
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "workbooks"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / OUT_NAME

    frames = load_parquet_frames(repo_root)

    wb = Workbook()
    add_readme_sheet(wb)
    add_model_sheet(wb)
    add_lookup_lists_sheet(wb, frames)

    for parquet_name, sheet_name, _table_name in PARQUET_SHEETS:
        ws = wb.create_sheet(sheet_name)
        write_dataframe_sheet(ws, frames[parquet_name])

    add_source_registry_sheet(wb, frames)
    add_steward_queue_sheet(wb, frames)
    add_concept_explorer_sheet(wb)

    wb.save(out_path)
    print(f"Wrote steward workbook: {out_path}")
    for parquet_name, sheet_name, _ in PARQUET_SHEETS:
        rows = len(frames[parquet_name])
        print(f"  - {sheet_name}: {rows} rows from {parquet_name}")


if __name__ == "__main__":
    main()
