"""Part 9: what kind of region is this -- given inputs, a student's
calculation, the final answer, a chart's source data, scratch work, or
instructions?

Getting SCRATCH_WORK or INSTRUCTIONS wrong in the "should have been graded"
direction is the one failure mode this part exists to prevent: grading a
student's rough side-notes with full confidence is exactly the kind of
mistake this whole project is built to avoid.

Two classifiers exist side by side, not one replacing the other: a cheap
rules-based guess using only what Parts 5-6 already computed (no model
call), and a local-model classifier that gets to see the region's actual
content. `roles_eval.py` measures both against labeled examples -- neither
is assumed better without a number.
"""

from __future__ import annotations

from enum import Enum, auto

from sheetgrade.detect import ColumnType, HeaderShape, Region, infer_column_type
from sheetgrade.infer import EXTRACTION_TEMPERATURE, ChoiceBackend
from sheetgrade.ir import CellAddress, CellType, Sheet


class RegionRole(Enum):
    GIVEN_INPUT = auto()
    STUDENT_CALCULATION = auto()
    FINAL_ANSWER = auto()
    CHART_SOURCE = auto()
    SCRATCH_WORK = auto()
    INSTRUCTIONS = auto()


# Neither classifier below ever predicts RegionRole.CHART_SOURCE today: the
# IR (Part 2) doesn't capture chart metadata yet, so there's no signal --
# structural or textual -- that a region feeds a chart. Honest gap, not a
# bug; see docs/walkthroughs/part-09.md.


def should_grade(role: RegionRole) -> bool:
    return role not in (RegionRole.SCRATCH_WORK, RegionRole.INSTRUCTIONS)


# A region with no header and this few filled cells or fewer reads as
# scratch work, not a real table -- too small to be a proper answer region.
# Untuned starting point, same situation as GAP_TOLERANCE in Part 5.
SCRATCH_WORK_MAX_CELLS = 6

# A region counts as "mostly computed," and therefore a calculation rather
# than given data, once at least this fraction of its columns are FORMULA
# type. Untuned starting point.
FORMULA_COLUMN_RATIO = 0.5


def classify_region_rules(sheet: Sheet, region: Region, header_shape: HeaderShape) -> RegionRole:
    """A deterministic guess from structure alone -- no model call, so it's
    free and instant, but it can only ever predict GIVEN_INPUT,
    STUDENT_CALCULATION, SCRATCH_WORK, or INSTRUCTIONS. It never predicts
    FINAL_ANSWER: telling "the last formula in a chain" apart from "a
    formula that's still being worked on" needs the dependency graph
    (Part 19), which this rule has no access to."""
    n_cells = sum(1 for addr in sheet.cells if region.contains(addr))
    has_header = header_shape.has_header_row or header_shape.has_header_col

    data_cols = range(region.min_col, region.max_col + 1)
    col_types = [infer_column_type(sheet, region, c, header_shape.header_row) for c in data_cols]
    if not col_types:
        return RegionRole.INSTRUCTIONS

    text_ratio = sum(1 for t in col_types if t is ColumnType.TEXT) / len(col_types)

    # All-text is checked before the size cutoff, not after: a short block
    # of pure prose (few rows, one column) would otherwise trip the size
    # check first and get called SCRATCH_WORK -- caught by actually running
    # this on a 6-line instructions example, not assumed correct on paper.
    if not has_header:
        if text_ratio == 1.0:
            return RegionRole.INSTRUCTIONS
        if n_cells <= SCRATCH_WORK_MAX_CELLS:
            return RegionRole.SCRATCH_WORK

    formula_ratio = sum(1 for t in col_types if t is ColumnType.FORMULA) / len(col_types)
    if formula_ratio >= FORMULA_COLUMN_RATIO:
        return RegionRole.STUDENT_CALCULATION

    return RegionRole.GIVEN_INPUT


def _describe_region(sheet: Sheet, region: Region, header_shape: HeaderShape) -> str:
    lines = [f"Region on sheet '{region.sheet}', rows {region.min_row}-{region.max_row}."]

    if header_shape.header_row is not None:
        headers = [
            sheet.cells[CellAddress(header_shape.header_row, c)].value
            for c in range(region.min_col, region.max_col + 1)
            if CellAddress(header_shape.header_row, c) in sheet.cells
        ]
        lines.append(f"Header row: {headers}")
    else:
        lines.append("No header row detected.")

    start_row = header_shape.header_row + 1 if header_shape.header_row is not None else region.min_row
    sample_rows = []
    for r in range(start_row, min(start_row + 3, region.max_row + 1)):
        row = [
            sheet.cells[CellAddress(r, c)].value if CellAddress(r, c) in sheet.cells else None
            for c in range(region.min_col, region.max_col + 1)
        ]
        sample_rows.append(row)
    lines.append(f"Sample rows: {sample_rows}")

    has_formulas = any(
        cell.data_type is CellType.FORMULA
        for addr, cell in sheet.cells.items()
        if region.contains(addr)
    )
    lines.append(f"Contains formulas: {has_formulas}")
    return "\n".join(lines)


_ROLE_DESCRIPTIONS = (
    "GIVEN_INPUT: data the professor supplied, not computed by the student.\n"
    "STUDENT_CALCULATION: an intermediate formula-driven working area.\n"
    "FINAL_ANSWER: the region holding the student's final computed answer.\n"
    "CHART_SOURCE: data whose only purpose is feeding a chart.\n"
    "SCRATCH_WORK: informal notes or rough work, not meant to be graded.\n"
    "INSTRUCTIONS: text describing the assignment, not data.\n"
)


def classify_region_llm(
    backend: ChoiceBackend, sheet: Sheet, region: Region, header_shape: HeaderShape
) -> RegionRole:
    description = _describe_region(sheet, region, header_shape)
    prompt = (
        "You are classifying one region of a student's spreadsheet for automated grading.\n\n"
        f"{description}\n\n"
        "Which role best describes this region?\n"
        f"{_ROLE_DESCRIPTIONS}"
    )
    choices = [role.name for role in RegionRole]
    label = backend.generate_choice(prompt, choices, temperature=EXTRACTION_TEMPERATURE)
    return RegionRole[label]
