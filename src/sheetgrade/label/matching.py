"""Part 8: decide whether two headers refer to the same thing -- using the
embedding meaning-map, the spelling/synonym backup, or a blend of both.
Which one actually wins is decided by measurement (see eval.py and
docs/walkthroughs/part-08.md), not picked here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import numpy as np

from sheetgrade.label.embeddings import EmbeddingCache
from sheetgrade.label.fallback import string_similarity
from sheetgrade.label.similarity import cosine_similarity


class MatchStrategy(Enum):
    EMBEDDING_ONLY = auto()
    STRING_ONLY = auto()
    HYBRID = auto()


# A pair counts as "the same header" once its score clears this bar.
# Untuned starting point, same situation as GAP_TOLERANCE in Part 5 --
# tests/fixtures/header_pairs.json + eval.py exist specifically to replace
# this guess with a measured value.
MATCH_THRESHOLD = 0.75

# Hybrid score = HYBRID_EMBEDDING_WEIGHT * embedding_similarity
#              + (1 - HYBRID_EMBEDDING_WEIGHT) * string_similarity.
# 0.5 means "trust both signals equally" as a starting point.
HYBRID_EMBEDDING_WEIGHT = 0.5

# Shipped default per docs/walkthroughs/part-08.md: string-only scored
# highest (94.3%) on tests/fixtures/header_pairs.json, but that benchmark is
# biased -- most "true match" pairs are exactly the synonyms hand-typed into
# SYNONYM_GROUPS, so string-only can't lose there. HYBRID is chosen instead
# because it degrades gracefully on real headers nobody pre-typed a synonym
# for, which string-only cannot do at all. Revisit once the fixture set is
# expanded with synonyms neither of us listed by hand.
DEFAULT_STRATEGY = MatchStrategy.HYBRID


@dataclass(frozen=True, slots=True)
class MatchResult:
    score: float
    is_match: bool


def score_pair(
    header_a: str, header_b: str, embeddings: EmbeddingCache, strategy: MatchStrategy
) -> MatchResult:
    if strategy is MatchStrategy.STRING_ONLY:
        score = string_similarity(header_a, header_b)
    else:
        vec_a = np.array(embeddings.embed(header_a))
        vec_b = np.array(embeddings.embed(header_b))
        embed_score = cosine_similarity(vec_a, vec_b)
        if strategy is MatchStrategy.EMBEDDING_ONLY:
            score = embed_score
        else:
            str_score = string_similarity(header_a, header_b)
            score = HYBRID_EMBEDDING_WEIGHT * embed_score + (1 - HYBRID_EMBEDDING_WEIGHT) * str_score
    return MatchResult(score=score, is_match=score >= MATCH_THRESHOLD)
