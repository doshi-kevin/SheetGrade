"""Applies a sequence of mutations to a workbook under one seed.

One `random.Random(seed)` is created and threaded through every mutation in
order, so the same seed always reproduces the same sequence of random choices
-- even though each mutation function calls `rng` a different number of times.
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from sheetgrade.ir import Workbook
from sheetgrade.mutate.manifest import MutationRecord, MutationSpec
from sheetgrade.mutate.mutations import MUTATIONS

MutationStep = tuple[Workbook, Workbook, MutationRecord]


def apply_mutations_traced(
    workbook: Workbook, specs: Sequence[MutationSpec], seed: int
) -> tuple[Workbook, list[MutationStep]]:
    """Like `apply_mutations`, but also keeps the workbook before each step.

    Part 4's consistency checker needs both sides of a single mutation to
    verify its manifest claim; `apply_mutations` alone only ever exposes the
    final workbook, which is enough for grading but not for auditing.
    """
    rng = random.Random(seed)
    steps: list[MutationStep] = []
    current = workbook
    for spec in specs:
        fn = MUTATIONS[spec.name]
        before = current
        current, record = fn(current, rng, **spec.kwargs)
        steps.append((before, current, record))
    return current, steps


def apply_mutations(
    workbook: Workbook, specs: Sequence[MutationSpec], seed: int
) -> tuple[Workbook, list[MutationRecord]]:
    final, steps = apply_mutations_traced(workbook, specs, seed)
    return final, [record for _, _, record in steps]
