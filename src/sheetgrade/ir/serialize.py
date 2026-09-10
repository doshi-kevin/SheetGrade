"""Workbook -> plain JSON-serializable dict, for golden snapshot tests.

Dataclasses.asdict() doesn't work directly here: Sheet.cells is a dict keyed
by CellAddress, and CellAddress isn't a valid JSON key. This flattens it to a
sorted list instead, which also makes snapshot diffs stable and readable.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from sheetgrade.ir import Workbook


def workbook_to_dict(workbook: Workbook) -> dict[str, Any]:
    return {
        "sheets": [_sheet_to_dict(sheet) for sheet in workbook.sheets],
        "defined_names": [asdict(dn) for dn in workbook.defined_names],
        "dependency_graph": {
            key: sorted(refs) for key, refs in sorted(workbook.dependency_graph.items())
        },
    }


def _sheet_to_dict(sheet: Any) -> dict[str, Any]:
    cells = []
    for address in sorted(sheet.cells, key=lambda a: (a.row, a.col)):
        cell = sheet.cells[address]
        cell_dict = asdict(cell)
        cell_dict["data_type"] = cell.data_type.name  # asdict() leaves Enums as-is, not JSON-safe
        cells.append(cell_dict)
    return {
        "name": sheet.name,
        "n_rows": sheet.n_rows,
        "n_cols": sheet.n_cols,
        "cells": cells,
    }
