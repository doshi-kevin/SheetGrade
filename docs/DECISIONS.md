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

## Scope change 2026-09-10: local inference, brief retrieval, grader memory added (20 → 24 parts)
- Local inference for high-volume calls. Chose a local quantized model for region classification over free hosted tiers. Decided by call volume (~3,600 per cohort) and FERPA exposure from sending student work off-premises. Hosted APIs retained for low-volume feedback generation where quality dominates.
- Qdrant over sqlite-vec. sqlite-vec was chosen for zero infrastructure when retrieval was a single misconception lookup. Part 17 needs native sparse+dense hybrid and payload filtering, which sqlite-vec does not provide. Cost is a Docker dependency.
- Brief-driven rubrics. Rubric YAML remains the machine-checkable source of truth, but is now drafted by retrieval over the assignment brief and confirmed by a human, rather than hand-authored. The LLM never auto-applies a rubric.
- No fine-tuning. Explicitly rejected for this project: 8 GB VRAM, no labelled corpus, and retrieval plus prompting is not yet the bottleneck. Revisit only if measurement shows otherwise.
- Abstention over guessing. Low-confidence alignments escalate to a human rather than producing a score. Accepts that the tool will punt on messy submissions; the alternative — confidently grading the wrong cells — is the exact failure this project exists to fix.

## Part 2: formula stored as string now, AST deferred to Part 14
- Picked: `Cell.formula` stays a raw string; a lightweight regex-based dependency graph (which cells a formula references) is built now without needing a full parser
- Rejected: building a full formula AST in Part 2, per the plan's own "answer: AST" note
- Reason: the recursive-descent parser is one of the 5 primitives Kevin hand-writes, timed right before Part 14 (formula equivalence) — building the AST now would mean Claude writes it, then he rewrites a version of it later; storing a string costs nothing today and doesn't block the dependency graph

## Part 2: reader normalizes openpyxl's value types at the boundary, fails loudly on unsupported ones
- Picked: a `_normalize_value` function converts `Decimal`→float, `date`/`time`→ISO string, `timedelta`→str, and raises `NotImplementedError` for rich text and array/data-table formulas
- Rejected: widening `CellValue` to cover every type openpyxl's stubs allow
- Reason: keeps the IR contract simple and typed everywhere else in the pipeline; per the plan's testing philosophy, an unsupported input should fail loudly at the boundary, not get silently mis-typed three modules downstream

## Part 3: built all 13 mutation types now, not a core subset
- Picked: implement the full taxonomy from PROJECT_PLAN.md immediately, rather than 5 now / 8 later
- Rejected: a smaller "core 5" first pass (one per failure category), which was the recommended option
- Reason: Kevin's call under the 2-week target — full taxonomy now means no later part blocks on adding a missing mutation type, at the cost of more code to review before any of it has been exercised by a real downstream part

## Part 3: structural mutations move cell positions, not formula text
- Picked: insert_column/delete_row/reorder_columns/shift_region/split_table shift where cells sit in the grid, but leave every formula's text untouched
- Rejected: rewriting formula references to match the new layout (e.g. `=B3-B4` becoming `=C3-C4` after a column is inserted before B)
- Reason: correctly rewriting a formula reference requires understanding formula text structurally, which needs the parser deferred to Part 14; the mutations are still useful now for testing structural detection and alignment (Parts 5-13), which don't depend on formula correctness

## Part 4: harness measures manifest self-consistency now, not future parts' metrics
- Picked: `check_step` re-derives each mutation's claimed effect directly from the before/after IR and flags a mismatch; the CSV/F1/MAE/abstention metrics from PROJECT_PLAN.md stay unimplemented until the parts that produce those outputs (5-19) exist
- Rejected: writing stub functions for region F1, alignment accuracy, score MAE, etc. now, returning None until real
- Reason: Kevin's call — a stub metric that always returns None isn't testable and would just be renamed later; the one thing that exists to grade today is the mutation engine itself, so that's what the harness checks

## Part 4: no-match ground truth reuses delete_row's existing `deleted_cells` field
- Picked: a deleted row's manifest already lists the exact cells that no longer have a counterpart; the harness treats that list as the "correct answer: abstain here" ground truth for later alignment metrics, rather than adding a new schema field
- Rejected: a new explicit `expected_no_match` marker added to `MutationRecord` now
- Reason: the data Part 3 already records is sufficient — `check_step` for delete_row already verifies that list against the IR; a schema change with no consumer yet would be speculative

## Part 5: gap tolerance left as an untuned config constant
- Picked: `GAP_TOLERANCE = 1` in `src/sheetgrade/detect/regions.py`, as a named, overridable default — not hardcoded, not yet chosen from real data
- Rejected: committing to a specific tuned value now (1 strict, or 2 more forgiving)
- Reason: Kevin's call — no labeled real-sheet corpus exists yet to measure against (that's Part 5's own stated test: "hand-label regions in 40 real sheets; measure F1"); picking a number now would be a guess dressed up as a decision

## Part 6: headers detected by type discontinuity, not formatting
- Picked: a header row/column is the last "mostly text" line right before the text fraction drops sharply (`HEADER_TEXT_FRACTION=0.6`, `HEADER_DROP_THRESHOLD=0.3`)
- Rejected: detecting headers from formatting (bold, fill colour) or from font size
- Reason: Kevin's own reasoning, worked through live — formatting is optional and a professor can skip it, but the shift from a row of text labels to a row of real data is structural and present even with zero formatting; verified on our fixture that font size doesn't even differ between the title and header rows, so it wouldn't have worked as the signal anyway

## Part 6: column type inferred from values first, number_format second
- Picked: `infer_column_type` decides NUMERIC vs CURRENCY etc. from `Cell.data_type` across the column; the `number_format` string is only consulted afterward, as a tiebreaker between NUMERIC and CURRENCY once "numeric" is already established
- Rejected: reading the number_format string as the primary signal for type
- Reason: caught directly in our own fixture — the Q1 column is formatted `"$#,##0"` and the Total column is formatted `"General"`, even though both hold the same kind of money value; trusting the format string would call identical data two different types depending on whether the professor bothered to format it
