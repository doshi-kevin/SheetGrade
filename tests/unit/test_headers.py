from pathlib import Path

import pytest

from sheetgrade.detect import ColumnType, Region, detect_header_shape, infer_column_type
from sheetgrade.ir import Cell, CellAddress, CellType, Sheet
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"


@pytest.fixture
def wb():
    return read_xlsx(FIXTURE)


@pytest.fixture
def budget_region(wb):
    sheet = wb.sheets[0]
    return sheet, Region(sheet="Budget", min_row=0, max_row=sheet.n_rows - 1, min_col=0, max_col=sheet.n_cols - 1)


def test_detects_both_header_row_and_header_column(budget_region):
    sheet, region = budget_region
    shape = detect_header_shape(sheet, region)
    assert shape.header_row == 1  # "Category, Q1, Q2, Q3, Q4, Total"
    assert shape.header_col == 0  # "Category, Revenue, Expenses, Profit"


def test_title_row_is_not_mistaken_for_the_header(budget_region):
    """Row 0 (the merged title) is also all-text, but it doesn't sit right
    before the drop into data -- row 1 does."""
    sheet, region = budget_region
    shape = detect_header_shape(sheet, region)
    assert shape.header_row != 0


def test_headerless_region_reports_no_header_row():
    # A block of pure numbers, no label row anywhere.
    cells = {CellAddress(r, c): Cell(CellAddress(r, c), value=r * 10 + c, data_type=CellType.NUMBER) for r in range(3) for c in range(3)}
    sheet = Sheet(name="Numbers", cells=cells, n_rows=3, n_cols=3)
    region = Region(sheet="Numbers", min_row=0, max_row=2, min_col=0, max_col=2)

    shape = detect_header_shape(sheet, region)

    assert not shape.has_header_row
    assert not shape.has_header_col


def test_q1_column_is_currency_from_values_not_format_string(budget_region):
    """Q1's cells carry the '$#,##0' number_format -- but the point of this
    part is that the format string is a hint, not proof. Confirm the type
    still comes out right when values are what's actually being read."""
    sheet, region = budget_region
    column_type = infer_column_type(sheet, region, col=1, header_row=1)
    assert column_type is ColumnType.CURRENCY


def test_total_column_is_formula_despite_being_money_like_q1(budget_region):
    """Total's format string is 'General', unlike Q1's '$#,##0' -- same
    underlying meaning (money), different cosmetic format. It comes out as
    FORMULA rather than CURRENCY because every cell in it is a computed
    formula, which is itself useful signal (a hardcoded Total would not be)."""
    sheet, region = budget_region
    column_type = infer_column_type(sheet, region, col=5, header_row=1)
    assert column_type is ColumnType.FORMULA


def test_category_column_is_categorical():
    """Only 3 distinct labels repeated across 6 rows -- a small repeating
    set, not freeform text."""
    values = ["Revenue", "Expenses", "Profit", "Revenue", "Expenses", "Profit"]
    cells = {CellAddress(r, 0): Cell(CellAddress(r, 0), value=v, data_type=CellType.STRING) for r, v in enumerate(values)}
    sheet = Sheet(name="Sheet1", cells=cells, n_rows=6, n_cols=1)
    region = Region(sheet="Sheet1", min_row=0, max_row=5, min_col=0, max_col=0)

    assert infer_column_type(sheet, region, col=0, header_row=None) is ColumnType.CATEGORICAL


def test_freeform_text_column_is_text_not_categorical():
    values = ["Alpha note", "Bravo comment", "Charlie remark", "Delta observation"]
    cells = {CellAddress(r, 0): Cell(CellAddress(r, 0), value=v, data_type=CellType.STRING) for r, v in enumerate(values)}
    sheet = Sheet(name="Sheet1", cells=cells, n_rows=4, n_cols=1)
    region = Region(sheet="Sheet1", min_row=0, max_row=3, min_col=0, max_col=0)

    assert infer_column_type(sheet, region, col=0, header_row=None) is ColumnType.TEXT
