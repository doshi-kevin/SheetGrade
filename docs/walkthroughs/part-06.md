# Part 6: what's inside a table — headers and column types

## The idea in one line

Once we know *where* a table is (Part 5), we need to know *what's a label and what's data* inside it — without relying on the professor having bothered to bold or color anything.

## Show, don't tell

Our Budget sheet, rows 0-4:

```
row 0: "Quarterly Budget"                              -- all text (1 cell)
row 1: "Category" "Q1" "Q2" "Q3" "Q4" "Total"           -- all text (6/6)
row 2: "Revenue"   1000  1100  1200  1300  =SUM(...)    -- 1/6 text
row 3: "Expenses"  700   750   800   820   =SUM(...)
row 4: "Profit"    =B3-B4  ...
```

Row 1 is 100% text; row 2 drops to 17% text. That drop is the header boundary — `detect_header_shape` finds it and reports `header_row = 1`, correctly skipping row 0's title (which is also all-text, but nothing drops right after it — row 1 is *also* all-text, so there's no discontinuity there).

Same logic sideways found something we didn't expect going in: column A ("Category", "Revenue", "Expenses", "Profit") is *also* 100% text, top to bottom, while every other column mixes text and numbers. So the sheet has both a header **row** and a header **column** — column A is functioning as row labels. The code found this for free, from the same discontinuity check run on columns instead of rows.

For column types, the sharper example is the Total column: it holds the exact same kind of value as Q1 (a dollar amount), but its cells are formatted `"General"` while Q1's are formatted `"$#,##0"`. `infer_column_type` looks at the actual values first — Q1 comes out `CURRENCY` (numbers + a `$` format hint), Total comes out `FORMULA` (every cell is a computed formula, not `CURRENCY`) — which is arguably more useful: it tells you Total is *computed*, not hardcoded, and Part 3's `hardcode_formula` mutation is exactly the case where that stops being true.

## Why bother

Nothing about *comparing* two files makes sense until we know which row is labels and which column in each table means what. Part 11 (column alignment) will directly use these types as matching evidence: a `CURRENCY` column in the key should only ever match a `CURRENCY` or `NUMERIC` column in a submission, never a `TEXT` one.

## The decisions — and how we got there

Both of today's decisions came from you reasoning it through, not from me picking:

1. **Headers are found by a type discontinuity** (text → non-text), not by formatting. You noticed color/size *could* matter, but when we checked our own fixture, the title and header row have identical font size — so size wouldn't have separated them anyway, and color is optional in a way a professor can just skip. The text-vs-data shift is structural and survives even with zero formatting.
2. **Column type comes from the actual values, not the number_format string.** You initially weren't sure, so we checked the real file: Q1 is formatted as currency, Total isn't, despite meaning the same thing. That's a real, present bug waiting to happen if format-string were trusted, not a hypothetical.

## Honest gaps

- **Multi-row headers** aren't handled — the function returns a single header row/column, not a range. A two-line header ("Q1 / (thousands)") would only register the second line.
- **Categorical vs text** uses one hardcoded ratio (`CATEGORICAL_DISTINCT_RATIO = 0.5`) as a config constant, untuned — same situation as Part 5's gap tolerance, waiting on real labeled data.

---

## Your turn

1. In your own words: why did column A come out as a "header column" even though nobody told the code to look for one specifically?
2. A student deletes the header row entirely, so their table starts straight at "Revenue, 1000, ...". What does `detect_header_shape` report, and is silently reporting "no header" the right behavior, or should it do something else?
3. We could have used the number_format string as the *only* signal and skipped checking real values entirely. Using the Total-vs-Q1 example, explain concretely what would have gone wrong.
