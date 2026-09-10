from pathlib import Path

import pytest

from sheetgrade.ir import CellAddress, CellType
from sheetgrade.mutate import MutationSpec, apply_mutations
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"


@pytest.fixture
def wb():
    return read_xlsx(FIXTURE)


def test_insert_column_shifts_cells_right(wb):
    new_wb, [record] = apply_mutations(wb, [MutationSpec("insert_column", {"sheet": "Budget", "at_col": 2})], seed=1)
    sheet = new_wb.sheets[0]
    assert sheet.n_cols == wb.sheets[0].n_cols + 1
    # what was column 2 (C, Q2 header) should now be at column 3
    assert sheet.cells[CellAddress(1, 3)].value == "Q2"
    assert record.expected_effect == "structural_only"


def test_delete_row_shifts_cells_up(wb):
    new_wb, _records = apply_mutations(wb, [MutationSpec("delete_row", {"sheet": "Budget", "at_row": 2})], seed=1)
    sheet = new_wb.sheets[0]
    assert sheet.n_rows == wb.sheets[0].n_rows - 1
    # what was row 3 (Expenses) should now be at row 2
    assert sheet.cells[CellAddress(2, 0)].value == "Expenses"


def test_rename_header(wb):
    address = CellAddress(1, 1)
    new_wb, [record] = apply_mutations(
        wb, [MutationSpec("rename_header", {"sheet": "Budget", "address": address, "new_name": "Quarter 1"})], seed=1
    )
    assert new_wb.sheets[0].cells[address].value == "Quarter 1"
    assert record.details["before"] == "Q1"


def test_reorder_columns_is_a_permutation(wb):
    new_wb, [record] = apply_mutations(wb, [MutationSpec("reorder_columns", {"sheet": "Budget"})], seed=3)
    mapping = record.details["old_to_new"]
    assert sorted(mapping) == list(range(wb.sheets[0].n_cols))
    assert len(new_wb.sheets[0].cells) == len(wb.sheets[0].cells)


def test_recolour_only_changes_fill(wb):
    address = CellAddress(1, 0)
    new_wb, [record] = apply_mutations(
        wb, [MutationSpec("recolour", {"sheet": "Budget", "address": address, "new_rgb": "FFAA0000"})], seed=1
    )
    new_cell = new_wb.sheets[0].cells[address]
    old_cell = wb.sheets[0].cells[address]
    assert new_cell.fill_color_rgb == "FFAA0000"
    assert new_cell.value == old_cell.value  # only the color changed
    assert record.expected_effect == "cosmetic_only"


def test_hardcode_formula_drops_the_formula(wb):
    address = CellAddress(2, 5)  # F3, =SUM(B3:E3)
    new_wb, [record] = apply_mutations(
        wb, [MutationSpec("hardcode_formula", {"sheet": "Budget", "address": address})], seed=1
    )
    new_cell = new_wb.sheets[0].cells[address]
    assert new_cell.formula is None
    assert new_cell.data_type is CellType.NUMBER
    assert record.expected_effect == "method_lost"


def test_perturb_value_changes_a_number(wb):
    address = CellAddress(2, 1)  # B3 = 1000
    new_wb, [record] = apply_mutations(
        wb, [MutationSpec("perturb_value", {"sheet": "Budget", "address": address, "delta": 5})], seed=1
    )
    assert new_wb.sheets[0].cells[address].value == 1005
    assert record.expected_effect == "value_changed"


def test_merge_cells_clears_non_anchor_cell(wb):
    new_wb, _records = apply_mutations(
        wb, [MutationSpec("merge_cells", {"sheet": "Budget", "cell_range": "A2:B2"})], seed=1
    )
    sheet = new_wb.sheets[0]
    assert sheet.cells[CellAddress(1, 0)].merge_range == "A2:B2"
    assert CellAddress(1, 1) not in sheet.cells  # absorbed into the merge


def test_rename_sheet_updates_dependency_graph_keys(wb):
    new_wb, _records = apply_mutations(wb, [MutationSpec("rename_sheet", {"sheet": "Budget", "new_name": "Q1Actuals"})], seed=1)
    assert new_wb.sheets[0].name == "Q1Actuals"
    assert any(key.startswith("Q1Actuals!") for key in new_wb.dependency_graph)
    assert not any(key.startswith("Budget!") for key in new_wb.dependency_graph)


def test_split_table_inserts_a_gap(wb):
    new_wb, _records = apply_mutations(
        wb, [MutationSpec("split_table", {"sheet": "Budget", "at_row": 3, "gap_rows": 4})], seed=1
    )
    sheet = new_wb.sheets[0]
    assert sheet.n_rows == wb.sheets[0].n_rows + 4
    # what was row 3 (Expenses) should now be 4 rows further down
    assert sheet.cells[CellAddress(7, 0)].value == "Expenses"


def test_add_scratch_work_is_tagged_excluded(wb):
    new_wb, [record] = apply_mutations(wb, [MutationSpec("add_scratch_work", {"sheet": "Budget"})], seed=1)
    assert record.expected_effect == "excluded_from_grading"
    assert new_wb.sheets[0].cells[CellAddress(wb.sheets[0].n_rows + 2, 0)].value == record.details["text"]


def test_wrong_input_correct_method_flags_dependent_formulas(wb):
    address = CellAddress(3, 1)  # B4 = 700, feeds B5 (=B3-B4) and F4 (=SUM(B4:E4))
    new_wb, [record] = apply_mutations(
        wb,
        [MutationSpec("wrong_input_correct_method", {"sheet": "Budget", "input_address": address, "delta": -5})],
        seed=1,
    )
    assert new_wb.sheets[0].cells[address].value == 695
    assert record.expected_effect == "carry_through"
    assert set(record.details["formulas_correct_given_bad_input"]) == {"Budget!B5", "Budget!F4"}


def test_seeded_composition_is_reproducible(wb):
    specs = [
        MutationSpec("insert_column", {"sheet": "Budget"}),
        MutationSpec("perturb_value", {"sheet": "Budget"}),
        MutationSpec("recolour", {"sheet": "Budget"}),
    ]
    _, records_a = apply_mutations(wb, specs, seed=99)
    _, records_b = apply_mutations(wb, specs, seed=99)
    assert records_a == records_b
    assert len(records_a) == 3  # composing N mutations produces N manifest entries


def test_mutation_never_modifies_the_original_workbook(wb):
    original_cols = wb.sheets[0].n_cols
    original_cell_count = len(wb.sheets[0].cells)
    apply_mutations(wb, [MutationSpec("insert_column", {"sheet": "Budget", "at_col": 0})], seed=1)
    assert wb.sheets[0].n_cols == original_cols
    assert len(wb.sheets[0].cells) == original_cell_count
