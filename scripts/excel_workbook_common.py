"""Shared helpers for CHI Excel workbook generators."""

from __future__ import annotations

from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet


HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
MODEL_FILL = PatternFill("solid", fgColor="E2EFDA")
README_TITLE_FILL = PatternFill("solid", fgColor="D9EAF7")


def style_header_row(ws: Worksheet, row: int = 1) -> None:
    for cell in ws[row]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(vertical="top", wrap_text=True)


def autosize_columns(ws: Worksheet, max_width: int = 38, min_width: int = 12) -> None:
    for idx, col in enumerate(ws.columns, 1):
        width = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[get_column_letter(idx)].width = min(max(width + 2, min_width), max_width)


def add_excel_table(ws: Worksheet, table_name: str) -> None:
    if ws.max_row < 2 or ws.max_column < 1:
        return
    end_col = get_column_letter(ws.max_column)
    ref = f"A1:{end_col}{ws.max_row}"
    table = Table(displayName=table_name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    ws.add_table(table)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ref


def add_list_validation(
    ws: Worksheet,
    column_name: str,
    list_range: str,
    headers: list[str],
    max_row: int = 500,
) -> None:
    if column_name not in headers:
        return
    col_idx = headers.index(column_name) + 1
    col_letter = get_column_letter(col_idx)
    dv = DataValidation(type="list", formula1=list_range, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{col_letter}2:{col_letter}{max_row}")


def write_readme_sheet(ws: Worksheet, title: str, rows: list[tuple[str, str]]) -> None:
    ws.append((title,))
    ws.append(())
    for left, right in rows:
        ws.append((left, right))
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].fill = README_TITLE_FILL
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 110
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
