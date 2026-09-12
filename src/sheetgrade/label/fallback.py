"""Part 8: a deterministic backup for header matching that needs no model at
all -- clean up spelling differences and check a small hand-curated synonym
list. Exists as a safety net for cases where the meaning-map (embeddings)
can also be misled, like "Q1" vs "Q2": nearly identical spelling, opposite
meaning, and used in near-identical sentences everywhere, which can pull
their embeddings close together too. See docs/walkthroughs/part-08.md.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

# Hand-curated groups of header words that mean the same thing in a
# budget/finance context, not learned from data. Expand as real student
# submissions surface new synonyms worth adding.
SYNONYM_GROUPS: tuple[frozenset[str], ...] = (
    frozenset({"revenue", "rev", "sales", "total sales"}),
    frozenset({"expenses", "expense", "costs", "cost", "expenditure"}),
    frozenset({"total", "sum", "grand total"}),
    frozenset({"category", "item", "label", "description"}),
    frozenset({"profit", "net income", "earnings"}),
)

_PUNCTUATION = re.compile(r"[.$,]")
_WHITESPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = _PUNCTUATION.sub("", text)
    text = _WHITESPACE.sub(" ", text)
    return text


def _synonym_group(text: str) -> frozenset[str] | None:
    for group in SYNONYM_GROUPS:
        if text in group:
            return group
    return None


def string_similarity(header_a: str, header_b: str) -> float:
    """1.0 for identical-after-normalization or known synonyms, otherwise a
    plain spelling-closeness ratio between 0.0 and 1.0."""
    norm_a, norm_b = normalize(header_a), normalize(header_b)
    if norm_a == norm_b:
        return 1.0
    group = _synonym_group(norm_a)
    if group is not None and norm_b in group:
        return 1.0
    return SequenceMatcher(None, norm_a, norm_b).ratio()
