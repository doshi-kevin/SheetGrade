"""Part 8 -- cosine similarity and top-k search over embedding vectors.

Normally hand-written by Kevin per CLAUDE.md's primitive list; written by
Claude here at his explicit, knowing request to override that rule
(DECISIONS.md, 2026-09-12). Queued in docs/TO_UNDERSTAND.md for a walkthrough.

Two headers are "similar" if their embedding vectors point in roughly the
same direction, not if they're numerically close together. Cosine
similarity measures that angle: 1.0 means identical direction, 0.0 means
perpendicular (unrelated), -1.0 means opposite directions.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Vector = NDArray[np.float64]


def cosine_similarity(a: Vector, b: Vector) -> float:
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def top_k(query: Vector, candidates: Vector, k: int) -> list[tuple[int, float]]:
    """Indices into `candidates` (one row per vector) most similar to
    `query`, as (index, similarity) pairs sorted highest similarity first."""
    dots = candidates @ query
    candidate_norms = np.linalg.norm(candidates, axis=1)
    query_norm = float(np.linalg.norm(query))
    denom = candidate_norms * query_norm
    denom[denom == 0.0] = np.inf  # a zero-norm row scores 0.0, not divide-by-zero
    scores = dots / denom
    order = np.argsort(-scores)[:k]
    return [(int(i), float(scores[i])) for i in order]
