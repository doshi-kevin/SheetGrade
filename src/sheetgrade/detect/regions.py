"""Part 5: find rectangular blocks of related content on a sheet.

A student's sheet isn't a table in a database -- it's cells scattered
wherever someone typed them. Before anything can be aligned or graded, we
need to find the actual chunks of data: which filled-in cells belong to the
same table.

The algorithm is connected components: treat every filled cell as a graph
node, connect two cells if they're close enough to belong to the same table
(same row or column, within `gap_tolerance` blank cells of each other), then
each connected group becomes one region. Its bounding box is the region's
rectangle.

GAP_TOLERANCE: how many consecutive blank rows/columns can sit between two
filled cells while still calling them one region (a stylistic spacer) rather
than two separate tables. 0 = any single blank row/column splits; higher
values tolerate bigger gaps but risk merging genuinely separate tables that
sit close together. Not yet tuned against real fixtures -- see
docs/DECISIONS.md.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from sheetgrade.ir import CellAddress, Sheet

GAP_TOLERANCE = 1


@dataclass(frozen=True, slots=True)
class Region:
    sheet: str
    min_row: int
    max_row: int
    min_col: int
    max_col: int

    def contains(self, address: CellAddress) -> bool:
        return self.min_row <= address.row <= self.max_row and self.min_col <= address.col <= self.max_col


def detect_regions(sheet: Sheet, gap_tolerance: int = GAP_TOLERANCE) -> list[Region]:
    filled = set(sheet.cells)
    if not filled:
        return []

    by_row: dict[int, list[int]] = {}
    by_col: dict[int, list[int]] = {}
    for addr in filled:
        by_row.setdefault(addr.row, []).append(addr.col)
        by_col.setdefault(addr.col, []).append(addr.row)
    for cols in by_row.values():
        cols.sort()
    for rows in by_col.values():
        rows.sort()

    reach = gap_tolerance + 1
    visited: set[CellAddress] = set()
    regions: list[Region] = []

    for start in filled:
        if start in visited:
            continue
        component: set[CellAddress] = {start}
        visited.add(start)
        queue: deque[CellAddress] = deque([start])
        while queue:
            addr = queue.popleft()
            for col in by_row[addr.row]:
                neighbor = CellAddress(addr.row, col)
                if neighbor not in visited and abs(col - addr.col) <= reach:
                    visited.add(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
            for row in by_col[addr.col]:
                neighbor = CellAddress(row, addr.col)
                if neighbor not in visited and abs(row - addr.row) <= reach:
                    visited.add(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)

        rows = [a.row for a in component]
        cols = [a.col for a in component]
        regions.append(Region(sheet.name, min(rows), max(rows), min(cols), max(cols)))

    return regions
