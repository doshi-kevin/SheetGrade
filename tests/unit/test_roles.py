from pathlib import Path

import pytest

from sheetgrade.detect import HeaderShape, Region, detect_header_shape
from sheetgrade.ir import Cell, CellAddress, CellType, Sheet
from sheetgrade.label import RegionRole, classify_region_rules, should_grade
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"


def _region(cells: dict[CellAddress, Cell], name: str = "Sheet1") -> tuple[Sheet, Region]:
    rows = [a.row for a in cells]
    cols = [a.col for a in cells]
    sheet = Sheet(name=name, cells=cells, n_rows=max(rows) + 1, n_cols=max(cols) + 1)
    region = Region(sheet=name, min_row=min(rows), max_row=max(rows), min_col=min(cols), max_col=max(cols))
    return sheet, region


def test_whole_budget_table_is_given_input():
    """The real fixture's single region mixes given data (Q1-Q4) with one
    computed column (Total) -- most of it is given, so GIVEN_INPUT is the
    defensible whole-region call. Distinguishing the Total column from the
    rest is a finer grain than region-level classification reaches; that's
    Part 11's job (column alignment), not Part 9's."""
    wb = read_xlsx(FIXTURE)
    sheet = wb.sheets[0]
    region = Region(sheet="Budget", min_row=0, max_row=sheet.n_rows - 1, min_col=0, max_col=sheet.n_cols - 1)
    shape = detect_header_shape(sheet, region)

    assert classify_region_rules(sheet, region, shape) is RegionRole.GIVEN_INPUT


def test_small_headerless_region_is_scratch_work():
    cells = {
        CellAddress(0, 0): Cell(CellAddress(0, 0), value="check", data_type=CellType.STRING),
        CellAddress(0, 1): Cell(CellAddress(0, 1), value=12.5, data_type=CellType.NUMBER),
    }
    sheet, region = _region(cells)
    shape = HeaderShape(header_row=None, header_col=None)

    role = classify_region_rules(sheet, region, shape)

    assert role is RegionRole.SCRATCH_WORK
    assert not should_grade(role)


def test_headerless_all_text_block_is_instructions():
    cells = {
        CellAddress(r, 0): Cell(CellAddress(r, 0), value=f"Instruction line {r}", data_type=CellType.STRING)
        for r in range(10)
    }
    sheet, region = _region(cells)
    shape = HeaderShape(header_row=None, header_col=None)

    role = classify_region_rules(sheet, region, shape)

    assert role is RegionRole.INSTRUCTIONS
    assert not should_grade(role)


def test_mostly_formula_region_with_header_is_student_calculation():
    header = {
        CellAddress(0, c): Cell(CellAddress(0, c), value=f"Step{c}", data_type=CellType.STRING)
        for c in range(3)
    }
    formulas = {
        CellAddress(1, c): Cell(CellAddress(1, c), value=None, formula=f"=A{c}+1", data_type=CellType.FORMULA)
        for c in range(3)
    }
    cells = {**header, **formulas}
    sheet, region = _region(cells)
    shape = HeaderShape(header_row=0, header_col=None)

    role = classify_region_rules(sheet, region, shape)

    assert role is RegionRole.STUDENT_CALCULATION
    assert should_grade(role)


def test_rules_classifier_never_predicts_chart_source_or_final_answer():
    """Documented gap, not a bug: neither structural signal exists yet for
    these two roles. See docs/walkthroughs/part-09.md."""
    wb = read_xlsx(FIXTURE)
    sheet = wb.sheets[0]
    region = Region(sheet="Budget", min_row=0, max_row=sheet.n_rows - 1, min_col=0, max_col=sheet.n_cols - 1)
    shape = detect_header_shape(sheet, region)

    role = classify_region_rules(sheet, region, shape)

    assert role not in (RegionRole.CHART_SOURCE, RegionRole.FINAL_ANSWER)


@pytest.mark.parametrize("role", list(RegionRole))
def test_should_grade_excludes_only_scratch_and_instructions(role):
    expected = role not in (RegionRole.SCRATCH_WORK, RegionRole.INSTRUCTIONS)
    assert should_grade(role) is expected
