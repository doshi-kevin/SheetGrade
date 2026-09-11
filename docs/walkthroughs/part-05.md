# Part 5: finding the tables on a blank canvas

## The idea in one line

A spreadsheet has no built-in idea of "table" — it's just cells with stuff typed into them, anywhere. We taught the code to look at *which filled cells sit close to which other filled cells* and group them into candidate tables.

## Show, don't tell

Run it on our real test file, untouched:

```
detect_regions(sheet, gap_tolerance=1)
-> Region(min_row=0, max_row=4, min_col=0, max_col=5)   # one table, correctly
```

Now break it with Part 3's `split_table` mutation — inserts a 3-row blank gap starting at row 2:

```
before:  rows 0-4 all filled
after:   rows 0-1 filled, rows 2-4 blank, rows 5-7 filled (shifted down by 3)

detect_regions(sheet, gap_tolerance=1)
-> Region(min_row=0, max_row=1, ...)   # top half
-> Region(min_row=5, max_row=7, ...)   # bottom half
```

With `gap_tolerance=1`, a 3-row gap is too wide to bridge, so it correctly splits into two tables. Bump the tolerance to 3 and it merges back into one — same file, different answer, because "how big a gap counts as a real separation" isn't a fact about the file, it's a judgment call we have to make.

## Why bother

Nothing downstream — headers, alignment, scoring — can run until we know *where the tables are*. Get this wrong and everything after it is confidently grading the wrong rectangle.

## The decision

`GAP_TOLERANCE = 1` lives as a named constant in `src/sheetgrade/detect/regions.py`, not tuned yet. We don't have real hand-labeled sheets to measure against, so picking a "final" number now would be a guess wearing a decision's clothes. Once Part 5's own test plan item happens — hand-label 40 real sheets — this becomes a one-time sweep: try a few values, measure which one best matches the human labels, hardcode the winner. No per-file human tuning, ever.

## The real limitation, named honestly

One global number can't be right for every table on a busy sheet. A sheet with 15 tables might have some separated by a 1-row spacer and others genuinely 1 row apart — no single cutoff gets both right. The fix isn't a bigger constant, it's smarter: an adaptive per-sheet threshold, combining the gap with other evidence like "does a header row start right after it" (Part 6), and — per this project's hard requirement — abstaining on the genuinely ambiguous ones instead of guessing. Not built yet; needs real multi-table fixtures to test against first.

---

## Your turn

1. In your own words: what's the difference between Part 2's dependency graph and Part 5's connected components? (They both talk about "which cells relate to which" — how do they differ?)
2. A professor's sheet has 3 side-by-side tables (same rows, different column ranges) with 2 blank columns between each. What does `gap_tolerance=1` do here, and is that right?
3. Why didn't we just pick the "obviously correct" gap tolerance value ourselves right now instead of leaving it as an untuned constant?
