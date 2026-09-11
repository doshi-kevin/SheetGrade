"""Part 6: does a region have a header row, a header column, and what type is
each column?

Two things came out of reasoning through this with Kevin (2026-09-11), not
picked by default:

- A header line (row or column) is found by a *type discontinuity*: the
  boundary where "this line is basically all text" stops being true one
  step later. Not by formatting (bold, fill colour) -- formatting is
  optional, a professor can skip it, but the shift from label text to real
  data is structural and almost always present.
- A column's type is inferred primarily from the actual stored values
  (`Cell.data_type`), not the cosmetic `number_format` string. Our own
  Total column proves why: it holds the same kind of money as the Q1
  column, but its format string is "General" while Q1's is "$#,##0" --
  trusting the format string would call the same kind of data two
  different things. The format string is only consulted afterward, to
  tell plain numbers apart from currency once "numeric" is already decided
  from the values.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum, auto

from sheetgrade.detect.regions import Region
from sheetgrade.ir import CellAddress, CellType, Sheet

# A row/column counts as "header-like" if at least this fraction of its
# filled cells are plain text. Lower = more tolerant of a stray non-text
# cell in the header (e.g. a numeric column id); higher = stricter, but a
# single blank or oddly-typed header cell then breaks detection entirely.
HEADER_TEXT_FRACTION = 0.6

# How far the text fraction must drop between a candidate header line and
# the line right after it to count as a real boundary rather than noise.
HEADER_DROP_THRESHOLD = 0.3

# A text column counts as "categorical" (a small set of repeating labels,
# like "Revenue"/"Expenses") rather than "text" (freeform) when the number
# of distinct values is at most this fraction of the total values. Lower
# = stricter about what counts as categorical.
CATEGORICAL_DISTINCT_RATIO = 0.5

_CURRENCY_SYMBOLS = ("$", "€", "£", "¥")


class ColumnType(Enum):
    NUMERIC = auto()
    CURRENCY = auto()
    DATE = auto()
    CATEGORICAL = auto()
    FORMULA = auto()
    TEXT = auto()


@dataclass(frozen=True, slots=True)
class HeaderShape:
    header_row: int | None
    header_col: int | None

    @property
    def has_header_row(self) -> bool:
        return self.header_row is not None

    @property
    def has_header_col(self) -> bool:
        return self.header_col is not None


def _row_text_fraction(sheet: Sheet, region: Region, row: int) -> float:
    cells = [sheet.cells[CellAddress(row, c)] for c in range(region.min_col, region.max_col + 1) if CellAddress(row, c) in sheet.cells]
    if not cells:
        return 0.0
    return sum(1 for c in cells if c.data_type is CellType.STRING) / len(cells)


def _col_text_fraction(sheet: Sheet, region: Region, col: int) -> float:
    cells = [sheet.cells[CellAddress(r, col)] for r in range(region.min_row, region.max_row + 1) if CellAddress(r, col) in sheet.cells]
    if not cells:
        return 0.0
    return sum(1 for c in cells if c.data_type is CellType.STRING) / len(cells)


def _find_discontinuity(fractions: list[float]) -> int | None:
    """`fractions` runs from the region's outer edge inward. Returns the
    index of the last "mostly text" line right before a real drop, or None
    if the line-by-line fraction never actually falls."""
    for i in range(len(fractions) - 1):
        if fractions[i] >= HEADER_TEXT_FRACTION and (fractions[i] - fractions[i + 1]) >= HEADER_DROP_THRESHOLD:
            return i
    return None


def detect_header_shape(sheet: Sheet, region: Region) -> HeaderShape:
    row_fractions = [_row_text_fraction(sheet, region, r) for r in range(region.min_row, region.max_row + 1)]
    col_fractions = [_col_text_fraction(sheet, region, c) for c in range(region.min_col, region.max_col + 1)]

    row_offset = _find_discontinuity(row_fractions)
    col_offset = _find_discontinuity(col_fractions)

    header_row = region.min_row + row_offset if row_offset is not None else None
    header_col = region.min_col + col_offset if col_offset is not None else None
    return HeaderShape(header_row, header_col)


def infer_column_type(sheet: Sheet, region: Region, col: int, header_row: int | None) -> ColumnType:
    start_row = header_row + 1 if header_row is not None else region.min_row
    cells = [sheet.cells[CellAddress(r, col)] for r in range(start_row, region.max_row + 1) if CellAddress(r, col) in sheet.cells]
    if not cells:
        return ColumnType.TEXT

    majority_type, _ = Counter(c.data_type for c in cells).most_common(1)[0]

    if majority_type is CellType.FORMULA:
        return ColumnType.FORMULA
    if majority_type is CellType.DATE:
        return ColumnType.DATE
    if majority_type is CellType.NUMBER:
        formats = [c.number_format for c in cells if c.data_type is CellType.NUMBER]
        if any(symbol in fmt for fmt in formats for symbol in _CURRENCY_SYMBOLS):
            return ColumnType.CURRENCY
        return ColumnType.NUMERIC
    if majority_type is CellType.STRING:
        values = [c.value for c in cells if c.data_type is CellType.STRING]
        distinct_ratio = len(set(values)) / len(values)
        return ColumnType.CATEGORICAL if distinct_ratio <= CATEGORICAL_DISTINCT_RATIO else ColumnType.TEXT
    return ColumnType.TEXT
