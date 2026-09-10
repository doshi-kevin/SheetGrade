# Part 3: manufacturing test files with known-correct answers

## The idea in one line

We can't test whether "detect a misaligned column" works without a file where we already know a column is misaligned. So we build the broken files ourselves, and write down exactly what we broke.

## Show, don't tell

Take the flagship mutation and run it on our real test file:

```
before: B4 (Expenses, Q1) = 700
after:  B4 = 695                      <- a "typo"

B4 feeds two formulas:
  B5 = B3 - B4    (Profit)
  F4 = SUM(B4:E4) (Total Expenses)
```

The mutation doesn't touch B5 or F4's formulas at all — only B4's value. But it *records* that both B5 and F4 are "correct methods fed a bad input." That record is the whole point: later, when the real grader sees B5 come out wrong, it'll be able to check this receipt and know not to blame the Profit formula itself.

## Why bother

Without a manifest like this, there's no way to check whether a later part actually works, except eyeballing it forever. With it, Part 4 (next) can run this same trick hundreds of times and automatically score "did the grader dock points only where it should have."

This is the same trick as unit testing, one level up: instead of testing code with known inputs and outputs, we're testing *the grader* with known-broken spreadsheets and known-correct diagnoses.

## The decision

The plan lists 13 kinds of damage (insert a column, rename a header, typo a value, merge cells, etc.) — you chose to build all 13 now rather than a smaller starter set, accepting more code to review before any of it gets used by a real downstream part.

## A real bug, caught before any test ran

Our data model is "frozen" (Part 1) specifically so a mutation can never corrupt the original answer key. Turns out `frozen` has a gap: it stops you *replacing* a field, but if that field is a dict, nothing stops you from reaching in and changing what's *inside* the dict — the original and the "new" version would then secretly share the same corrupted data. Every mutation now builds a fresh copy of the dict first. Caught this by reasoning about it while writing the code, not by a test failing — worth remembering that "immutable" in Python often means "shallow," not "safe all the way down."

## One honest gap

Mutations that move cells around (insert a column, delete a row) don't update formula text to match. If `=B3-B4` moves because a column got inserted before B, the formula still says B3 and B4 — even though different data now lives in different cells. Fine for testing "can the code detect this column moved," not fine yet for "does the math still work." Flagged, not fixed — needs the formula parser from Part 14.

---

## Your turn

1. In your own words: what does "ground truth by construction" mean, and why did we need it before building anything else?
2. Suppose Part 5 (region detection) runs on a file where we used `split_table` (inserted a gap in the middle of the data). What should the *correct* answer be, and how would you check the code got it right?
3. We could have skipped writing manifests and just kept pairs of (original file, mutated file). What do we lose without the manifest?
