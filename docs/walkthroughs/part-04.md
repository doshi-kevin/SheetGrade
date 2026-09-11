# Part 4: can you trust the answer key you built yourself?

## The idea in one line

Part 3 gave every mutation a receipt claiming what it broke. Nobody had ever checked whether that receipt was telling the truth. Part 4 is the checker.

## Show, don't tell

`insert_column` on our test file, at column 2:

```
before: header row = Category, Q1, Q2, Q3, Q4, Total   (columns 0-5)
after:  header row = Category, Q1,     Q2, Q3, Q4, Total (columns 0-6, new blank at col 2)

manifest says: {"mutation": "insert_column", "at_col": 2}
```

The checker doesn't trust that number. It re-derives it: take every cell in the *before* sheet, compute where it *should* land (`col + 1` if `col >= at_col`, else unchanged), and confirm that's actually where it is in the *after* sheet. If the manifest lied — said `at_col: 2` when the code actually inserted at column 3 — every cell past column 2 would show up one position off from where the checker expects, and the check fails.

Same idea, different shape, for `wrong_input_correct_method` (the flagship carry-through mutation): the manifest claims a specific list of formulas are "correct, just fed a bad input." The checker walks the dependency graph from Part 2 *itself* — not the mutation's own copy of that logic — and confirms the list matches. Two independent computations of the same fact; if the mutation's own bookkeeping had a bug, this catches it instead of quietly agreeing with itself.

## Why bother

Every part from here on (region detection, alignment, scoring) gets graded against these mutated fixtures. If the ground truth is wrong, a broken aligner and a correct aligner can look identical on paper. This is the harness CLAUDE.md's testing philosophy calls for: "inject a known-bad grader and confirm the metrics drop." We did a version of that here — for each of the 13 mutation types, there's a test that tampers with the manifest (changes a claimed value, drops a claimed dependent) and confirms the checker's pass/fail flips. A checker that can't fail isn't checking anything.

## The decision

There's nothing to grade yet except the mutation engine — region detection, alignment, and scoring don't exist until Parts 5-19. So Part 4 measures **manifest self-consistency**: for every mutation applied, does its receipt match what actually happened in the file? The real metrics from the plan (region F1, alignment accuracy, score MAE, abstention rate) get added incrementally as the parts that produce those outputs land — no stub functions returning `None` in the meantime, since those aren't testable and would just get rewritten.

Second decision: when `delete_row` removes cells that have no counterpart afterward, that's exactly the "ground truth: no match should exist" case later alignment metrics need. Rather than inventing a new manifest field for it, the harness reuses the `deleted_cells` list Part 3 already records — it's already the right shape.

## One honest gap

The checkers for structural mutations (`insert_column`, `reorder_columns`, `shift_region`, `split_table`) verify "every old cell landed at the predicted new position" — but they don't independently verify that position formula is *correct*, only that the code was consistent with its own stated parameters. A mutation that inserted at the wrong column but *also* lied about `at_col` to match would slip through. Catching that needs a check with no access to the mutation's parameters at all — not something the harness does yet.

---

## Your turn

1. In your own words: why does the checker recompute the dependency graph itself instead of just checking that `record.details["formulas_correct_given_bad_input"]` is a non-empty list?
2. Suppose a future refactor of `insert_column` accidentally started inserting **before** `at_col` instead of at it. What's the first thing that would fail — the existing Part 3 test, or the new Part 4 checker — and why?
3. We could have made the harness re-run the entire mutation function and diff its output against itself (trivially always matching). What's wrong with that design, and how does the real checker avoid it?
