# Decisions

Every non-obvious choice: what was picked, what was rejected, the number or reason that decided it. Three lines each.

---

## License: MIT
- Picked: MIT
- Rejected: Apache 2.0 (explicit patent grant, more boilerplate)
- Reason: simpler and more familiar to contributors; revisit if a company tries to build a commercial product on the alignment algorithm

## Python version: 3.12, managed via uv
- Picked: Python 3.12, pinned per-project with `uv python pin`
- Rejected: system Python 3.14; a separately-managed venv via `python -m venv`
- Reason: openpyxl / formulas / pycel / python-calamine lag new CPython releases; uv pins the interpreter without touching system Python

## IR data model: frozen stdlib dataclasses
- Picked: `frozen=True, slots=True` dataclasses (Cell, Sheet, Workbook, etc.) in `src/sheetgrade/ir/models.py`
- Rejected: Pydantic (extra dependency, validation can mask real parsing bugs); attrs (less mainstream for contributors)
- Reason: matches PROJECT_PLAN.md's own wording; immutability prevents the mutation engine (Part 3) from ever corrupting the original key workbook via a shared reference

## Timeline: 2-week target, hand-write rule kept but paired live
- Picked: the 5 CLAUDE.md hand-write primitives (cosine/top-k, Needleman-Wunsch, Hungarian cost matrix, RRF, recursive-descent parser) are still written by hand, but as a live pairing session instead of write-alone-then-review
- Rejected: dropping the rule entirely (would queue all 5 into TO_UNDERSTAND.md, exceeding the "max 2 unreviewed" cap almost immediately)
- Reason: 2-week target concentrates risk in Phase C (alignment, 35-50 worst-case hours); pairing keeps the learning goal without the write-alone review round-trip cost
