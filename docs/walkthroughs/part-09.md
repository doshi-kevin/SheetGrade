# Part 9: what is this region actually for?

## The idea in one line

Before grading anything, decide what each region on the sheet *is* — given data, a student's working, the final answer, scratch notes, or instructions — because scratch notes and instructions must never be graded, no matter how confident the rest of the pipeline feels.

## Show, don't tell

Four regions, two classifiers, run for real:

| Region | Expected | Rules said | Local model said |
|---|---|---|---|
| Budget table (real fixture) | GIVEN_INPUT | GIVEN_INPUT | **FINAL_ANSWER** |
| Small 2-cell note | SCRATCH_WORK | SCRATCH_WORK | SCRATCH_WORK |
| 6-line instructions block | INSTRUCTIONS | INSTRUCTIONS | INSTRUCTIONS |
| 3-column formula block | STUDENT_CALCULATION | STUDENT_CALCULATION | STUDENT_CALCULATION |

Both scored 75% (3 of 4) — but they got *different* ones wrong. The rules classifier only ever looks at the ratio of formula columns (1 of 6 in the Budget table, below the 0.5 cutoff), so it calls the whole table GIVEN_INPUT. The local model actually reads the sample values and headers, notices the `Total` column is a computed sum, and reads that as the final answer. Neither is obviously wrong — the Budget table genuinely mixes given data and one computed column, which is exactly the kind of case a single region-level label struggles to describe. An aggregate "75% accurate" number would have hidden that these are two different failure modes; the confusion matrix didn't.

A second, more useful finding came from actually running the rules classifier, not just trusting the code by reading it: a 6-line block of pure instructions text got misclassified as `SCRATCH_WORK`, because the size check ("6 cells or fewer with no header") ran before the all-text check, and a short instructions block is also small. Fixed by checking "is this all text?" first — caught by running real input through the code, not by re-reading the code more carefully.

## Why bother

If a student's scratch notes get graded as if they were a real answer, the system produces a wrong score with total confidence — the exact failure this whole project exists to prevent. This part is also the first real user of Part 7's routing and sampling machinery: a real cohort's ~3,600 classification calls (300 students × ~12 regions) all go through the local-vs-hosted table and the deterministic-temperature policy built there.

## The decisions

1. **Both classifiers ship, permanently, not one replacing the other.** The 75%-vs-75%-but-different-mistakes result above is the reason: measuring only one would have hidden a real trade-off.
2. **A new `generate_choice` method, not a change to `generate`.** Part 7 found the local model answers in full sentences even when asked for one word. Ollama's `format` field can *force* the output to match a fixed set of words — a real constraint, not a polite request — so it's a separate capability (`ChoiceBackend`) rather than reworking `Backend.generate`, keeping every existing Part 7/8 call site untouched.
3. **The rules classifier never predicts `CHART_SOURCE` or `FINAL_ANSWER`.** No chart metadata exists in the IR yet (honest gap from Part 2), and telling "the last formula in a chain" apart from "one still being worked on" needs the dependency graph, which is Part 19.

## Honest gaps

- Only 4 labeled examples exist so far, built by hand in Python rather than real, varied fixture files — nowhere near the plan's real labeled corpus. The 75% numbers above describe this tiny set, not general accuracy.
- `SCRATCH_WORK_MAX_CELLS` (6) and `FORMULA_COLUMN_RATIO` (0.5) are untuned placeholders, same situation as `GAP_TOLERANCE` in Part 5.
- Region-level classification struggles with any table that legitimately mixes roles (like the Budget table's given data + one computed total) — a real limitation of classifying a whole rectangle as one thing, not a bug either classifier can fully fix alone.

---

## Your turn

1. In your own words: why did the rules classifier and the local model disagree about the Budget table, and why is neither one simply "wrong"?
2. What would you check in a real submission to decide whether a formula-heavy region is `STUDENT_CALCULATION` (still working) or `FINAL_ANSWER` (the answer), given that this part's rules classifier can't tell the difference?
3. Why does forcing the model's output to one of six exact words (via `generate_choice`) matter more here than it would have for Part 8's header matching?
