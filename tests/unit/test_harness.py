from pathlib import Path

import pytest

from sheetgrade.eval import (
    ConsistencyResult,
    HarnessReport,
    MutationCase,
    append_results_csv,
    run_corpus,
)
from sheetgrade.mutate import MutationSpec
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"


def _case(name, specs, seed):
    return MutationCase(name=name, workbook=read_xlsx(FIXTURE), specs=specs, seed=seed)


def test_run_corpus_all_pass_on_untampered_mutations():
    cases = [
        _case("insert", [MutationSpec("insert_column", {"sheet": "Budget", "at_col": 2})], seed=1),
        _case("perturb", [MutationSpec("perturb_value", {"sheet": "Budget"})], seed=1),
        _case("chain", [MutationSpec("recolour", {"sheet": "Budget"}), MutationSpec("rename_sheet", {"sheet": "Budget", "new_name": "X"})], seed=1),
    ]
    report = run_corpus(cases)
    assert report.pass_rate == 1.0
    assert report.failures() == ()


def test_harness_pass_rate_drops_when_a_check_fails():
    """Stand-in for CLAUDE.md's "inject a known-bad grader" test: if the
    aggregate metric can't drop when a check fails, it isn't measuring
    anything."""
    good = ConsistencyResult("perturb_value", "Budget", True, "")
    bad = ConsistencyResult("insert_column", "Budget", False, "lied about at_col")
    report = HarnessReport((good, good, bad))
    assert report.pass_rate == pytest.approx(2 / 3)
    assert report.failures() == (bad,)
    assert report.pass_rate_by_mutation() == {"perturb_value": 1.0, "insert_column": 0.0}


def test_append_results_csv_writes_header_once(tmp_path):
    path = tmp_path / "results.csv"
    report = HarnessReport((ConsistencyResult("perturb_value", "Budget", True, ""),))

    append_results_csv(report, path, config="baseline")
    append_results_csv(report, path, config="baseline")

    lines = path.read_text().strip().splitlines()
    assert len(lines) == 3  # header + 2 rows
    assert "pass_rate" in lines[0]
    assert "1.0000" in lines[1]
