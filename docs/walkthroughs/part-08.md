# Part 8: matching headers by meaning, not spelling

## The idea in one line

Decide whether two headers mean the same thing — `"Revenue"` and `"Rev."`, or `"Category"` and `"Item"` — using a meaning-map (embeddings) built by the local embedding model, backed up by a plain spelling/synonym check for the cases meaning-based matching gets wrong.

## Show, don't tell

Real cosine similarity scores, measured against `nomic-embed-text` on this machine:

| Pair | Should match? | Cosine score |
|---|---|---|
| Revenue vs Rev. | yes | 0.455 |
| Revenue vs Sales | yes | 0.663 |
| Category vs Item | yes | 0.590 |
| **Q1 vs Q2** | **no** | **0.748** |
| Email vs Phone | no | 0.509 |

`Q1` vs `Q2` — which should *never* match — scored higher than every genuine synonym pair. That's the exact trap the plan warned about: `Q1` and `Q2` show up in near-identical sentences everywhere ("Q1 revenue," "Q2 revenue"), so the embedding model places them close together on the meaning-map despite being opposite for grading purposes. There is no single similarity cutoff that separates "should match" from "should not match" here — the ranges overlap.

## Why bother

Alignment (Part 11 onward) needs to know that a key's `"Revenue"` column and a student's `"Rev."` column are the same column, even though nothing about their spelling says so. Get this wrong and the grader compares the wrong cells with full confidence — the exact failure this whole project exists to fix.

## The decisions

1. **Cosine similarity / top-k hand-write rule was overridden, by explicit choice.** CLAUDE.md schedules this as a hand-written primitive; Kevin chose to have Claude write it directly instead, logged in `DECISIONS.md` and queued in `TO_UNDERSTAND.md` for a walkthrough, since the project's own rule says an algorithm implementation never silently skips review.
2. **Shipped strategy is `HYBRID`, not the best-measured one.** `STRING_ONLY` scored highest on our own test set (94.3% vs hybrid's 88.6%), but that test set is biased — most "true match" pairs are exactly the synonyms hand-typed into `SYNONYM_GROUPS`, so string-only can't lose there. It also can't improve: a real synonym neither of us anticipated (e.g. "Turnover" for "Revenue") scores as unrelated, permanently, until someone notices and edits the list by hand. `EMBEDDING_ONLY` is rejected outright — the Q1/Q2 overlap above means no threshold makes it safe alone. `HYBRID` is the only one with a real path to improving on wording nobody pre-typed.
3. **`MATCH_THRESHOLD` (0.75) and `HYBRID_EMBEDDING_WEIGHT` (0.5) stay untuned placeholders.** Same situation as `GAP_TOLERANCE` in Part 5 — a real number exists, but it's not trustworthy yet.

## Honest gaps

- The 34-pair fixture (`tests/fixtures/header_pairs.json`) is a curated starter set, not the plan's full hand-verified 200 pairs — and it's self-referential, since the same synonym list backs both the fixture labels and the string matcher being tested against them. A fair benchmark needs synonym pairs neither of us typed into `SYNONYM_GROUPS`.
- `EmbeddingCache` is in-memory only — cleared every run, no persistence across processes.
- No confidence/abstention wiring yet (that's Part 13) — `score_pair` returns a hard match/no-match, nothing in between.

---

## Your turn

1. In your own words: why did `Q1` vs `Q2` score *higher* on the meaning-map than genuine synonyms like `Revenue` vs `Rev.`? What does that tell you about what embeddings actually capture?
2. A student's file has a column called `"Turnover"` where the key says `"Revenue"`. Walk through what `STRING_ONLY`, `EMBEDDING_ONLY`, and `HYBRID` would each do with that pair, given everything measured above.
3. Why is it dishonest to call `STRING_ONLY`'s 94.3% "the more accurate strategy," even though the number itself is real and correctly computed?
