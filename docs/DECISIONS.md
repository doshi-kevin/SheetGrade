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
