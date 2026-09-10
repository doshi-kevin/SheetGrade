# sheetgrade

Structure-aware grading of spreadsheet submissions against an instructor answer key,
where the two workbooks do **not** share the same structure.

Most autograders compare cells by address and break the moment a student inserts a
column or reorders a table. sheetgrade's core problem is **alignment**: detecting
regions, labeling them semantically, and matching columns/rows across structural
drift (insertions, deletions, renames, reordering) before any comparison happens.
It also grades the **formula dependency graph** rather than raw values, so a correct
method fed one wrong input is penalized once, not on every downstream cell.

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for the full 20-part build plan, and
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
