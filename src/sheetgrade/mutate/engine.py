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


def apply_mutations(
    workbook: Workbook, specs: Sequence[MutationSpec], seed: int
) -> tuple[Workbook, list[MutationRecord]]:
    rng = random.Random(seed)
    records: list[MutationRecord] = []
    current = workbook
    for spec in specs:
        fn = MUTATIONS[spec.name]
        current, record = fn(current, rng, **spec.kwargs)
        records.append(record)
    return current, records
