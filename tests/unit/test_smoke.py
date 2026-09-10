"""Every module must import cleanly. Catches broken imports before anything else does."""

import importlib
import pkgutil

import sheetgrade


def test_all_submodules_import() -> None:
    package = sheetgrade
    for module_info in pkgutil.walk_packages(package.__path__, prefix=f"{package.__name__}."):
        importlib.import_module(module_info.name)


def test_ir_dataclasses_construct() -> None:
    from sheetgrade.ir import Cell, CellAddress, CellType, Sheet, Workbook

    cell = Cell(address=CellAddress(0, 0), value=1.0, data_type=CellType.NUMBER)
    sheet = Sheet(name="Sheet1", cells={cell.address: cell}, n_rows=1, n_cols=1)
    workbook = Workbook(sheets=(sheet,))

    assert workbook.sheets[0].cells[CellAddress(0, 0)].value == 1.0
