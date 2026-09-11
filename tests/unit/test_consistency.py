"""Part 4: does each mutation's manifest tell the truth about the IR?

Every mutation type gets one "the honest manifest passes" test. A handful
also get a "a lying manifest gets caught" test -- these are the harness's own
version of CLAUDE.md's "inject a known-bad grader" requirement: if a checker
can't fail when the claim is wrong, it isn't checking anything.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from sheetgrade.eval import check_step
from sheetgrade.ir import CellAddress
from sheetgrade.mutate import MutationSpec, apply_mutations_traced
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"


@pytest.fixture
def wb():
    return read_xlsx(FIXTURE)


def _run(wb, name, seed, **kwargs):
    _, [(before, after, record)] = apply_mutations_traced(
        wb, [MutationSpec(name, {"sheet": "Budget", **kwargs})], seed=seed
    )
    return before, after, record


@pytest.mark.parametrize(
    "name,seed,kwargs",
    [
        ("insert_column", 1, {"at_col": 2}),
        ("delete_row", 1, {"at_row": 2}),
        ("rename_header", 1, {"address": CellAddress(1, 1), "new_name": "Quarter 1"}),
        ("reorder_columns", 3, {}),
        ("shift_region", 1, {"drow": 0, "dcol": 1, "min_row": 0, "max_row": 0, "min_col": 0, "max_col": 4}),
        ("recolour", 1, {"address": CellAddress(1, 0), "new_rgb": "FFAA0000"}),
        ("hardcode_formula", 1, {"address": CellAddress(4, 1)}),
        ("perturb_value", 1, {"address": CellAddress(2, 1), "delta": 5}),
        ("merge_cells", 1, {"cell_range": "A7:B7"}),
        ("rename_sheet", 1, {"new_name": "Q1 Budget"}),
        ("split_table", 1, {"at_row": 2, "gap_rows": 2}),
        ("add_scratch_work", 1, {}),
        ("wrong_input_correct_method", 42, {}),
    ],
)
def test_honest_manifest_passes(wb, name, seed, kwargs):
    before, after, record = _run(wb, name, seed, **kwargs)
    result = check_step(before, after, record)
    assert result.ok, result.reason


def test_lying_insert_column_at_col_is_caught(wb):
    before, after, record = _run(wb, "insert_column", 1, at_col=2)
    lie = replace(record, details={**record.details, "at_col": record.details["at_col"] + 1})
    result = check_step(before, after, lie)
    assert not result.ok


def test_lying_perturb_value_after_is_caught(wb):
    before, after, record = _run(wb, "perturb_value", 1, address=CellAddress(2, 1), delta=5)
    lie = replace(record, details={**record.details, "after": record.details["after"] + 1})
    result = check_step(before, after, lie)
    assert not result.ok


def test_lying_delete_row_deleted_cells_is_caught(wb):
    before, after, record = _run(wb, "delete_row", 1, at_row=2)
    lie = replace(record, details={**record.details, "deleted_cells": ["Z99"]})
    result = check_step(before, after, lie)
    assert not result.ok


def test_lying_wrong_input_correct_method_dependents_is_caught(wb):
    before, after, record = _run(wb, "wrong_input_correct_method", 42)
    claimed = record.details["formulas_correct_given_bad_input"]
    lie = replace(record, details={**record.details, "formulas_correct_given_bad_input": claimed[:-1]})
    result = check_step(before, after, lie)
    assert not result.ok


def test_unregistered_mutation_fails_rather_than_silently_passing(wb):
    before, after, record = _run(wb, "perturb_value", 1, address=CellAddress(2, 1), delta=5)
    unknown = replace(record, mutation="not_a_real_mutation")
    result = check_step(before, after, unknown)
    assert not result.ok
