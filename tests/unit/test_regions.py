from pathlib import Path

import pytest

from sheetgrade.detect import detect_regions
from sheetgrade.ir import Cell, CellAddress, CellType, Sheet
from sheetgrade.mutate import MutationSpec, apply_mutations
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"


@pytest.fixture
def wb():
    return read_xlsx(FIXTURE)


def test_single_table_is_one_region(wb):
    sheet = wb.sheets[0]
    regions = detect_regions(sheet, gap_tolerance=1)
    assert len(regions) == 1
    assert regions[0].min_row == 0
    assert regions[0].max_row == sheet.n_rows - 1


def test_empty_sheet_has_no_regions():
    empty = Sheet(name="Empty", cells={}, n_rows=0, n_cols=0)
    assert detect_regions(empty) == []


def test_split_table_creates_two_regions_under_strict_tolerance(wb):
    """split_table (Part 3) inserts a 3-row gap starting at row 2. A gap
    tolerance smaller than the gap should see two separate tables."""
    new_wb, _ = apply_mutations(wb, [MutationSpec("split_table", {"sheet": "Budget", "at_row": 2, "gap_rows": 3})], seed=1)
    sheet = new_wb.sheets[0]

    regions = sorted(detect_regions(sheet, gap_tolerance=1), key=lambda r: r.min_row)

    assert len(regions) == 2
    assert regions[0].max_row == 1
    assert regions[1].min_row == 5


def test_split_table_merges_back_under_generous_tolerance(wb):
    """The same split, but with a gap tolerance wide enough to bridge the
    3-row gap, should see one table again."""
    new_wb, _ = apply_mutations(wb, [MutationSpec("split_table", {"sheet": "Budget", "at_row": 2, "gap_rows": 3})], seed=1)
    sheet = new_wb.sheets[0]

    regions = detect_regions(sheet, gap_tolerance=3)

    assert len(regions) == 1


def test_side_by_side_tables_are_separate_regions():
    """Two tables side by side (a common layout: raw data on the left,
    a summary table a few columns to the right) should split on columns
    the same way split_table splits on rows."""
    cells = {}
    for r in range(3):
        for c in range(2):
            cells[CellAddress(r, c)] = Cell(CellAddress(r, c), value=1, data_type=CellType.NUMBER)
    for r in range(3):
        for c in range(6, 8):
            cells[CellAddress(r, c)] = Cell(CellAddress(r, c), value=2, data_type=CellType.NUMBER)
    sheet = Sheet(name="Sheet1", cells=cells, n_rows=3, n_cols=10)

    regions = sorted(detect_regions(sheet, gap_tolerance=1), key=lambda r: r.min_col)

    assert len(regions) == 2
    assert regions[0].max_col == 1
    assert regions[1].min_col == 6
