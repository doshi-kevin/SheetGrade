"""Typed, immutable data model for a parsed workbook.

This is the contract every later stage (reader, mutator, detector, aligner,
scorer) reads and writes. Frozen so a downstream stage can never accidentally
mutate the instructor's key while comparing it to a submission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

CellValue = str | float | int | bool | None


class CellType(Enum):
    BLANK = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    DATE = auto()
    FORMULA = auto()
    ERROR = auto()


@dataclass(frozen=True, slots=True)
class CellAddress:
    """0-indexed (row, col) position within a single sheet."""

    row: int
    col: int


@dataclass(frozen=True, slots=True)
class Font:
    name: str | None = None
    size: float | None = None
    bold: bool = False
    italic: bool = False
    color_rgb: str | None = None  # e.g. "FF0000"


@dataclass(frozen=True, slots=True)
class Borders:
    top: str | None = None
    bottom: str | None = None
    left: str | None = None
    right: str | None = None


@dataclass(frozen=True, slots=True)
class Cell:
    address: CellAddress
    value: CellValue
    data_type: CellType
    formula: str | None = None  # raw formula string, e.g. "=SUM(A1:A3)"; None if not a formula
    computed_value: CellValue = None  # cached value Excel last stored for the formula
    number_format: str = "General"
    fill_color_rgb: str | None = None
    font: Font = field(default_factory=Font)
    borders: Borders = field(default_factory=Borders)
    merge_range: str | None = None  # e.g. "A1:C1" if this cell is part of a merge, else None
    comment: str | None = None


@dataclass(frozen=True, slots=True)
class DefinedName:
    name: str
    refers_to: str  # raw reference string, e.g. "Sheet1!$A$1:$A$10"


@dataclass(frozen=True, slots=True)
class Sheet:
    name: str
    cells: dict[CellAddress, Cell]
    n_rows: int
    n_cols: int


@dataclass(frozen=True, slots=True)
class Workbook:
    sheets: tuple[Sheet, ...]
    defined_names: tuple[DefinedName, ...] = ()
    # dependency_graph deferred to Part 2: depends on the string-vs-AST formula
    # decision, which is itself a separate call to make when the reader is built.
