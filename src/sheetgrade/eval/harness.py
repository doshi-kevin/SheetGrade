"""Part 4: run the mutation corpus and report whether the ground truth holds.

Nothing before this part has ever been checked by a machine end to end. This
module is the harness the plan calls for: one entry point that takes a corpus
of (key workbook, mutations to apply) and reports, as numbers, whether every
resulting manifest actually matches the IR. As Parts 5-19 add region
detection, alignment and scoring, this is where their metrics (F1, alignment
accuracy, score MAE, abstention rate) will get columns of their own -- for now
the only grader that exists is the mutation engine, so the only thing to
measure is whether *its own* ground truth is trustworthy.
"""

from __future__ import annotations

import csv
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sheetgrade.eval.consistency import ConsistencyResult, check_step
from sheetgrade.ir import Workbook
from sheetgrade.mutate.engine import apply_mutations_traced
from sheetgrade.mutate.manifest import MutationSpec


@dataclass(frozen=True, slots=True)
class MutationCase:
    """One corpus entry: a key workbook plus the mutations to apply to it."""

    name: str
    workbook: Workbook
    specs: Sequence[MutationSpec]
    seed: int


@dataclass(frozen=True, slots=True)
class HarnessReport:
    results: tuple[ConsistencyResult, ...]

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 1.0
        return sum(1 for r in self.results if r.ok) / len(self.results)

    def pass_rate_by_mutation(self) -> dict[str, float]:
        totals: dict[str, int] = {}
        passed: dict[str, int] = {}
        for r in self.results:
            totals[r.mutation] = totals.get(r.mutation, 0) + 1
            if r.ok:
                passed[r.mutation] = passed.get(r.mutation, 0) + 1
        return {name: passed.get(name, 0) / total for name, total in totals.items()}

    def failures(self) -> tuple[ConsistencyResult, ...]:
        return tuple(r for r in self.results if not r.ok)


def run_corpus(cases: Sequence[MutationCase]) -> HarnessReport:
    results: list[ConsistencyResult] = []
    for case in cases:
        _, steps = apply_mutations_traced(case.workbook, case.specs, case.seed)
        for before, after, record in steps:
            results.append(check_step(before, after, record))
    return HarnessReport(tuple(results))


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def append_results_csv(report: HarnessReport, path: Path, config: str = "") -> None:
    row = {
        "timestamp": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "config": config,
        "n_checks": len(report.results),
        "pass_rate": f"{report.pass_rate:.4f}",
    }
    is_new = not path.exists()
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        if is_new:
            writer.writeheader()
        writer.writerow(row)
