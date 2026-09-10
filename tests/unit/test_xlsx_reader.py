from pathlib import Path

from sheetgrade.ir import CellAddress, CellType
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"


def test_reads_all_non_empty_cells() -> None:
    wb = read_xlsx(FIXTURE)
    sheet = wb.sheets[0]
    assert sheet.name == "Budget"
    assert len(sheet.cells) == 25  # 1 title + 6 headers + 2*5 data + 5 profit row


def test_formula_cell_has_no_cached_value_from_a_never_opened_file() -> None:
    """openpyxl writes formulas but never computes them -- only Excel does.
    A cached value only exists once Excel has actually opened and saved the file."""
    wb = read_xlsx(FIXTURE)
    f3 = wb.sheets[0].cells[CellAddress(2, 5)]
    assert f3.data_type is CellType.FORMULA
    assert f3.formula == "=SUM(B3:E3)"
    assert f3.computed_value is None


def test_merged_title_cell() -> None:
    wb = read_xlsx(FIXTURE)
    a1 = wb.sheets[0].cells[CellAddress(0, 0)]
    assert a1.value == "Quarterly Budget"
    assert a1.merge_range == "A1:E1"


def test_comment_is_read() -> None:
    wb = read_xlsx(FIXTURE)
    a3 = wb.sheets[0].cells[CellAddress(2, 0)]
    assert a3.comment == "Confirmed against last year's actuals."


def test_dependency_graph_extracts_formula_references() -> None:
    wb = read_xlsx(FIXTURE)
    assert wb.dependency_graph["Budget!F3"] == frozenset({"B3:E3"})
    assert wb.dependency_graph["Budget!B5"] == frozenset({"B3", "B4"})
