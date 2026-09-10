# sheetgrade

**Sheetgrade** grades spreadsheet submissions against an instructor's answer key when the two workbooks do not share the same structure.

Existing autograders compare by cell address. That assumes the student's file is shaped identically to the key, so the moment a student reorders a column, inserts a helper row, or renames a header, those tools silently grade the wrong cells and report the result with full confidence. This is the failure that makes spreadsheet autograding unusable in practice.

The project rests on two bets.

**First: the hard problem is correspondence, not comparison.** Before anything can be graded, the system must work out which regions, columns and rows of two differently-shaped workbooks map to each other, under insertions, deletions, reorderings and renames. This is a genuine algorithms problem — assignment problems, sequence alignment, connected components — and it is where the product's value lives. Comparison after alignment is bookkeeping.

**Second: grade the formula dependency graph, not the values.** A workbook is a program. A student who used the correct method but typed one wrong input should lose points once, not on every downstream cell that inherited the error. Carry-through handling is what makes the grader pedagogically fair rather than mechanically strict, and it is the behaviour professors notice first.

A third property is a hard requirement rather than a bet: **the system abstains rather than guessing.** Every alignment carries a confidence, and below threshold the region is escalated to a human instead of graded. In grading, a confident wrong answer is far worse than "I need a person here."

Everything else — embeddings for header matching, retrieval over assignment briefs, misconception clustering, LLM-written feedback, learned grading preferences — exists in service of those three properties. None of it is the point on its own.

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for the full 24-part build plan, and
[docs/DECISIONS.md](docs/DECISIONS.md) / [docs/PREDICTIONS.md](docs/PREDICTIONS.md) / [docs/FAILURES.md](docs/FAILURES.md)
for the running log of choices, experiments, and bugs.

## Status

Early scaffolding — Part 1 (skeleton and contracts) in progress. No working pipeline yet.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for Python and dependency management.

```bash
uv sync            # install dependencies into .venv
uv run pytest      # run tests
uv run ruff check .   # lint
uv run mypy src    # type check
```

## License

MIT — see [LICENSE](LICENSE).
