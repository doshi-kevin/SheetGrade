# Part 7: teaching the pipeline where to ask its questions

## The idea in one line

Before any real model call exists in the pipeline, decide once, in one place, which questions go to the free local model and which go to a paid one — and prove the free one actually answers the same way twice.

## Show, don't tell

We asked the local model (`llama3.2:3b`, running on this machine) a realistic classification question:

> "Classify this spreadsheet region as one of: header, data, scratch_work. Region contents: Category, Q1, Q2, Q3, Q4, Total"

Expected: one word. Got:

> "I would classify this spreadsheet region as "header". The header typically contains the column names or labels, which in this case are "Category" and the quarterly labels "Q1", "Q2", "Q3", and "Q4"."

Right answer, wrapped in ~50 tokens of explanation instead of 1. Measured cost: ~2.5s per call at ~16.7 tokens/sec (`results/infer_benchmark.csv`) — across a real cohort's ~3,600 calls (Part 9's own estimate), that's a couple of hours of GPU time instead of a few minutes. Left alone for now, since nothing calls this for real work yet, but flagged for Part 9: constrain the output format, don't just lower the temperature.

## Why bother

Every later part that needs a model call (Part 9's classification, Part 21's feedback) goes through the same lookup table and the same sampling policy, instead of each part inventing its own "am I local or hosted" and "how random am I allowed to be" rule. Change the policy once, every call site gets the update.

## The decisions

1. **The routing table is a flat, hand-set lookup, not a live decision.** A call site's entry (`local` or `hosted`) is set once, not recomputed per request. A live "try local, escalate on failure" version would make the determinism test unreliable, since the route itself could vary run to run.
2. **Two sampling constants, not one.** `EXTRACTION_TEMPERATURE = 0.0` for anything producing a label, `PROSE_TEMPERATURE = 0.7` (untuned placeholder) for anything producing prose — determinism and variety are opposite goals, and no call site needs both at once.
3. **The plan's own "sequential loading forced" prediction didn't hold.** It was written before any model was picked, budgeting for something much bigger than the 3B model actually chosen. Measured on this machine, both models fit in VRAM together with room to spare (`docs/vram_budget.md`).

## Honest gaps

- The routing table's values are reasoned, not measured — there's no real classifier yet to check against the Part 4 harness. Revisit once Part 9 exists.
- `PROSE_TEMPERATURE` has no consumer yet and is an untuned guess, same situation as `GAP_TOLERANCE` in Part 5.
- The model answers classification questions in full sentences, not single words — fine for now, a real cost once Part 9 depends on parsing the answer.

---

## Your turn

1. In your own words: why is a flat lookup table safer to test than a version that tries local first and only calls hosted if local fails?
2. A future part adds a third model that needs to stay loaded in memory (say, a re-ranker in Part 17). What would you check before assuming it fits, based on what `docs/vram_budget.md` shows today?
3. We could have set one shared temperature for every call site instead of two. Using the header-classification vs. feedback-generation example, what would go wrong?
