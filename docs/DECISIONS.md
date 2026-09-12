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

## Part 7: routing table is static and hand-set, not measured yet
- Picked: `ROUTING_TABLE` in `src/sheetgrade/infer/router.py` maps each call site to LOCAL or HOSTED once, as a flat dict -- no live fallback or runtime accuracy check
- Rejected: a runtime fallback (try local, escalate to hosted on low confidence or failure) -- harder to write a reliable "same input, same output" determinism test against, since the route itself could change between two runs of the same call
- Reason: today's values follow the 2026-09-10 scope-change reasoning (call volume + stakes), since no real classifier exists yet to measure against the Part 4 harness; each entry should be revisited once Part 9 exists and has real accuracy numbers

## Part 7: two sampling temperatures, not one shared value
- Picked: `EXTRACTION_TEMPERATURE = 0.0` and `PROSE_TEMPERATURE = 0.7` as separate named constants in `src/sheetgrade/infer/sampling.py`, mapped per call site
- Rejected: a single shared temperature for every call site
- Reason: classification call sites need the same input to always produce the same label (the required determinism test would fail intermittently otherwise); prose call sites (Part 21, not built yet) need some variation so feedback doesn't read identically for every student -- 0.7 sits in the typical 0.6-0.9 "coherent but not robotic" range but has no real call site to measure against yet

## Part 7: model choice makes the plan's "sequential loading" assumption moot
- Picked: `llama3.2:3b` (Q4_K_M, ~2.6GB) and `nomic-embed-text` (F16, ~0.3GB) resident in VRAM at the same time
- Rejected: sequentially loading/unloading models, which PROJECT_PLAN.md's Part 7 text assumed would be required on an 8GB card
- Reason: that assumption budgeted for a larger (7-8B) generation model, written before any model was actually chosen; measured on this machine (`nvidia-smi`), both models together use ~2.9GB of 8GB, leaving ~4.8GB free -- see `docs/vram_budget.md`

## Part 8: hand-write rule overridden for cosine similarity / top-k, by explicit choice
- Picked: Claude wrote `src/sheetgrade/label/similarity.py` directly, overriding the 2026-09-10 "hand-write primitives via live pairing" decision for this one primitive
- Rejected: the paired-writing approach (Claude writes the spec/tests, Kevin writes the function body), offered once and explicitly declined
- Reason: Kevin's call, made knowingly after the trade-off was explained -- logged here per CLAUDE.md's own rule that an algorithm implementation built under time pressure must be queued in TO_UNDERSTAND.md and walked through later, not silently skipped

## Part 8: shipped strategy is HYBRID, chosen by measurement with a stated caveat
- Picked: `DEFAULT_STRATEGY = MatchStrategy.HYBRID` in `src/sheetgrade/label/matching.py`
- Rejected: `STRING_ONLY`, which measured highest (94.3% vs hybrid's 88.6% on `tests/fixtures/header_pairs.json`) but only because most "true match" pairs in that fixture are exactly the synonyms hand-typed into `SYNONYM_GROUPS` -- it has no way to generalize to a real synonym neither of us anticipated (e.g. "Turnover" for "Revenue"). `EMBEDDING_ONLY` is rejected outright, not just for this fixture: measured cosine scores show "Q1" vs "Q2" (should not match) scoring higher (0.748) than several genuine synonyms like "Revenue" vs "Rev." (0.455) -- the score ranges overlap, so no threshold could separate them correctly
- Reason: Kevin's call, given the trade-off -- string-only wins today's biased benchmark but can't improve; hybrid is weaker on this benchmark but has a real path to handling wording nobody pre-typed. `MATCH_THRESHOLD` and `HYBRID_EMBEDDING_WEIGHT` stay untuned placeholders until the fixture set is expanded with synonyms neither of us listed by hand -- the current numbers can't be trusted to generalize

## Part 9: two classifiers kept side by side, neither replacing the other
- Picked: `classify_region_rules` (free, structural, no model call) and `classify_region_llm` (uses the Part 7 local model) both exist in `src/sheetgrade/label/roles.py`; `roles_eval.py`'s confusion matrix measures both, rather than shipping one as "the" classifier
- Rejected: picking one now and deferring the other to "later if needed"
- Reason: a real 4-example run showed each one gets a *different* case wrong at the same 75% overall accuracy (rules mislabels the mixed given-data/calculation Budget table as GIVEN_INPUT vs the LLM's FINAL_ANSWER guess; both are defensible readings of a genuinely mixed region) -- an aggregate number would have hidden that; a confusion matrix didn't

## Part 9: `generate_choice` added to OllamaBackend instead of reusing `generate`
- Picked: a new `ChoiceBackend` protocol (`generate_choice`, constrained to a fixed set of words via Ollama's `format` JSON-schema field) alongside Part 7's existing `Backend` protocol, not a change to `generate`'s signature
- Rejected: extending `generate`'s existing signature with an optional output-format parameter
- Reason: Part 7 flagged that a plain prompt ("answer in one word") doesn't reliably produce one word -- `format` genuinely constrains what the model is allowed to emit, which is stronger than asking nicely; keeping it a separate protocol meant Part 7's existing fakes and call sites didn't need to change

## Part 9: rules-classifier ordering bug found by actually running it, not assumed correct
- Picked: check "is this region all text?" before checking "is this region small?" in `classify_region_rules`
- Rejected: the original order (size check first), which looked reasonable on paper
- Reason: running the classifier against a real 6-line instructions example (not just unit tests written to match the code) showed it misclassified as SCRATCH_WORK, because a short block of pure prose also happens to be small -- caught by reading the actual output, per CLAUDE.md's "read the data" rule, not by review of the code itself
