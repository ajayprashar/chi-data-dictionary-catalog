#!/usr/bin/env python3
"""
Generate a single CHI partner intake workbook with an internal curation bridge
that supports later contribution into the governed catalog and dictionary.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


OUT_NAME = "chi-partner-intake-workbook.xlsx"


def style_header(ws) -> None:
    fill = PatternFill("solid", fgColor="1F4E78")
    for cell in ws[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = fill
        cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def autosize(ws) -> None:
    for idx, col in enumerate(ws.columns, 1):
        width = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[get_column_letter(idx)].width = min(max(width + 2, 12), 38)


def write_sheet(ws, headers: list[str], rows: list[list[str]]) -> None:
    ws.append(headers)
    for row in rows:
        ws.append(row)
    style_header(ws)
    autosize(ws)


def add_readme_sheet(wb: Workbook) -> None:
    ws = wb.active
    ws.title = "README"
    rows = [
        ("CHI Partner Intake and Curation Workbook",),
        ("",),
        (
            "Purpose",
            "Use this workbook with a data partner such as a local jail to gather source information in a simple way, then let CHI map that intake into the governed Data Catalog and Data Dictionary.",
        ),
        ("",),
        (
            "Who fills what",
            "The partner mainly fills Source_Summary, Field_Inventory, Code_Values, Keys_and_Relationships, and Open_Questions.",
        ),
        ("", "CHI fills CHI_Curation_Bridge and Governance_Load_Plan after intake review."),
        ("",),
        ("Recommended workflow", "1) Meet with the partner and complete the partner-facing sheets."),
        ("", "2) Review the intake internally and map each field to CHI concepts."),
        ("", "3) Use CHI_Curation_Bridge to decide whether each source field maps to an existing semantic concept or requires a new one."),
        ("", "4) Use Governance_Load_Plan to determine which governed table or sheet should receive the curated result."),
        ("",),
        (
            "Important boundary",
            "Partners do not need to assign semantic_id values, FHIR paths, USCDI mappings, survivorship logic, or governance columns.",
        ),
    ]
    for row in rows:
        ws.append(row)
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].fill = PatternFill("solid", fgColor="D9EAF7")
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 110
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)


def add_validations(ws) -> None:
    headers = {cell.value: idx + 1 for idx, cell in enumerate(ws[1])}
    dv_bool = DataValidation(type="list", formula1='"true,false"', allow_blank=True)
    dv_status = DataValidation(
        type="list",
        formula1='"open,in_progress,resolved"',
        allow_blank=True,
    )
    dv_disposition = DataValidation(
        type="list",
        formula1='"map_existing,needs_new_semantic,out_of_scope,needs_review"',
        allow_blank=True,
    )
    dv_target = DataValidation(
        type="list",
        formula1='"ddc-master_patient_catalog,ddc-master_patient_dictionary,ddc-hl7_adt_catalog,ddc-ccda_catalog,ddc-data_source_availability,ddc-fhir_inventory,ddc-business_rules"',
        allow_blank=True,
    )
    dv_domain = DataValidation(
        type="list",
        formula1='"Domain 1: Master Demographics,Domain 2: Master Patient Attributes,Domain 3: Clinical Governance"',
        allow_blank=True,
    )
    for dv in [dv_bool, dv_status, dv_disposition, dv_target, dv_domain]:
        ws.add_data_validation(dv)

    if "contains_identifier" in headers:
        col = get_column_letter(headers["contains_identifier"])
        dv_bool.add(f"{col}2:{col}500")
    if "contains_sensitive_data" in headers:
        col = get_column_letter(headers["contains_sensitive_data"])
        dv_bool.add(f"{col}2:{col}500")
    if "needs_business_rule_review" in headers:
        col = get_column_letter(headers["needs_business_rule_review"])
        dv_bool.add(f"{col}2:{col}500")
    if "status" in headers:
        col = get_column_letter(headers["status"])
        dv_status.add(f"{col}2:{col}500")
    if "curation_disposition" in headers:
        col = get_column_letter(headers["curation_disposition"])
        dv_disposition.add(f"{col}2:{col}500")
    if "proposed_domain" in headers:
        col = get_column_letter(headers["proposed_domain"])
        dv_domain.add(f"{col}2:{col}500")
    if "target_governance_table" in headers:
        col = get_column_letter(headers["target_governance_table"])
        dv_target.add(f"{col}2:{col}500")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "workbooks"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / OUT_NAME

    wb = Workbook()
    add_readme_sheet(wb)

    write_sheet(
        wb.create_sheet("Source_Summary"),
        [
            "source_id",
            "source_name",
            "organization_name",
            "business_owner",
            "technical_contact",
            "delivery_format",
            "refresh_cadence",
            "primary_record_grain",
            "primary_identifiers",
            "notes",
        ],
        [[
            "local_jail",
            "Jail Scheduling Export",
            "Local Jail",
            "Jail Operations",
            "integration.contact@example.org",
            "CSV export",
            "Daily",
            "booking",
            "BookingNumber; PersonID",
            "Replace this example row with real source details.",
        ]],
    )

    write_sheet(
        wb.create_sheet("Field_Inventory"),
        [
            "source_field_name",
            "source_table_or_file",
            "business_label",
            "description",
            "data_type",
            "required_optional",
            "example_value",
            "allowed_values_or_code_set",
            "contains_identifier",
            "contains_sensitive_data",
            "updated_when",
            "notes",
        ],
        [
            [
                "BookingNumber",
                "bookings.csv",
                "Booking Number",
                "Unique booking identifier for the incarceration event",
                "string",
                "Required",
                "BK-2026-000145",
                "",
                "true",
                "false",
                "At booking creation",
                "Primary booking-level key.",
            ],
            [
                "BookingDate",
                "bookings.csv",
                "Booking Date",
                "Date and time the person was booked into custody",
                "datetime",
                "Required",
                "2026-03-24 21:17:00",
                "",
                "false",
                "false",
                "At booking creation",
                "Useful for event or encounter mapping.",
            ],
        ],
    )

    write_sheet(
        wb.create_sheet("Code_Values"),
        [
            "field_name",
            "code_system_name",
            "local_code",
            "meaning",
            "active_inactive",
            "notes",
        ],
        [[
            "FacilityCode",
            "Jail Facility Codes",
            "SANTA_RITA",
            "Santa Rita Jail",
            "active",
            "Example code row.",
        ]],
    )

    write_sheet(
        wb.create_sheet("Keys_and_Relationships"),
        [
            "record_type",
            "primary_key",
            "foreign_key",
            "joins_to_record_type",
            "one_to_many_or_one_to_one",
            "history_or_audit_field",
            "notes",
        ],
        [[
            "Booking",
            "BookingNumber",
            "PersonID",
            "Person",
            "many_to_one",
            "LastUpdatedDateTime",
            "A person may have multiple bookings over time.",
        ]],
    )

    write_sheet(
        wb.create_sheet("Open_Questions"),
        [
            "topic",
            "question",
            "owner",
            "status",
            "resolution_notes",
        ],
        [[
            "Identifiers",
            "Is PersonID stable across re-bookings and historical extracts?",
            "Local Jail + CHI",
            "open",
            "",
        ]],
    )

    write_sheet(
        wb.create_sheet("CHI_Curation_Bridge"),
        [
            "source_field_name",
            "proposed_semantic_id",
            "proposed_uscdi_data_class",
            "proposed_uscdi_data_element",
            "proposed_uscdi_element",
            "proposed_fhir_r4_path",
            "proposed_domain",
            "proposed_ruleset_category",
            "proposed_target_artifact",
            "curation_disposition",
            "needs_business_rule_review",
            "chi_notes",
        ],
        [[
            "BookingDate",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "needs_review",
            "true",
            "CHI completes this after intake review.",
        ]],
    )

    write_sheet(
        wb.create_sheet("Governance_Load_Plan"),
        [
            "source_field_name",
            "approved_semantic_id",
            "target_governance_table",
            "target_column_or_purpose",
            "load_action",
            "dependencies_or_prereqs",
            "notes",
        ],
        [[
            "BookingDate",
            "",
            "",
            "",
            "create_or_update",
            "Needs approved semantic mapping first.",
            "Internal CHI planning sheet for governance load steps.",
        ]],
    )

    for sheet_name in [
        "Field_Inventory",
        "Open_Questions",
        "CHI_Curation_Bridge",
        "Governance_Load_Plan",
    ]:
        add_validations(wb[sheet_name])

    wb.save(out_path)
    print(f"Wrote workbook: {out_path}")


if __name__ == "__main__":
    main()
