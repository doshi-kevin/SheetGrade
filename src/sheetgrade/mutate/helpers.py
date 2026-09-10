"""Functional updates for the frozen IR.

`frozen=True` on Sheet only stops you reassigning `sheet.cells = ...` -- it
does NOT stop you mutating the dict that `.cells` already points to. Doing
`sheet.cells[addr] = new_cell` would silently corrupt the *original* sheet,
because the mutated copy and the original still share the same dict object.
Every helper here builds a fresh dict first, precisely to avoid that.
"""

from __future__ import annotations

from dataclasses import replace

from sheetgrade.ir import Cell, CellAddress, Sheet, Workbook
from sheetgrade.reader import build_dependency_graph


def set_cell(sheet: Sheet, address: CellAddress, cell: Cell) -> Sheet:
    new_cells = dict(sheet.cells)
    new_cells[address] = cell
    return replace(sheet, cells=new_cells)


def remove_cell(sheet: Sheet, address: CellAddress) -> Sheet:
    new_cells = dict(sheet.cells)
    new_cells.pop(address, None)
    return replace(sheet, cells=new_cells)


def replace_sheet(workbook: Workbook, sheet_name: str, new_sheet: Sheet) -> Workbook:
    new_sheets = tuple(new_sheet if s.name == sheet_name else s for s in workbook.sheets)
    return replace(workbook, sheets=new_sheets, dependency_graph=build_dependency_graph(new_sheets))


def get_sheet(workbook: Workbook, sheet_name: str) -> Sheet:
    for sheet in workbook.sheets:
        if sheet.name == sheet_name:
            return sheet
    raise KeyError(f"no sheet named {sheet_name!r}")
