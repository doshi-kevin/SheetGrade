"""Part 8: measure embedding-only vs string-only vs hybrid against a
hand-labeled set of header pairs (tests/fixtures/header_pairs.json), instead
of guessing which one to ship. Mirrors the Part 4 harness's own philosophy:
the number replaces the guess.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from sheetgrade.label.embeddings import EmbeddingCache
from sheetgrade.label.matching import MatchStrategy, score_pair


@dataclass(frozen=True, slots=True)
class LabeledPair:
    header_a: str
    header_b: str
    same_meaning: bool


@dataclass(frozen=True, slots=True)
class StrategyReport:
    strategy: MatchStrategy
    accuracy: float
    false_positives: tuple[LabeledPair, ...]
    false_negatives: tuple[LabeledPair, ...]


def load_labeled_pairs(path: Path) -> tuple[LabeledPair, ...]:
    raw = json.loads(path.read_text())
    return tuple(
        LabeledPair(entry["header_a"], entry["header_b"], entry["same_meaning"]) for entry in raw
    )


def evaluate_strategy(
    pairs: Sequence[LabeledPair], embeddings: EmbeddingCache, strategy: MatchStrategy
) -> StrategyReport:
    false_positives: list[LabeledPair] = []
    false_negatives: list[LabeledPair] = []
    correct = 0
    for pair in pairs:
        result = score_pair(pair.header_a, pair.header_b, embeddings, strategy)
        if result.is_match == pair.same_meaning:
            correct += 1
        elif result.is_match and not pair.same_meaning:
            false_positives.append(pair)
        else:
            false_negatives.append(pair)
    accuracy = correct / len(pairs) if pairs else 1.0
    return StrategyReport(strategy, accuracy, tuple(false_positives), tuple(false_negatives))
