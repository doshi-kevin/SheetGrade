from sheetgrade.label.embeddings import EmbeddingCache
from sheetgrade.label.eval import LabeledPair, StrategyReport, evaluate_strategy, load_labeled_pairs
from sheetgrade.label.fallback import SYNONYM_GROUPS, normalize, string_similarity
from sheetgrade.label.matching import (
    DEFAULT_STRATEGY,
    HYBRID_EMBEDDING_WEIGHT,
    MATCH_THRESHOLD,
    MatchResult,
    MatchStrategy,
    score_pair,
)
from sheetgrade.label.roles import (
    FORMULA_COLUMN_RATIO,
    SCRATCH_WORK_MAX_CELLS,
    RegionRole,
    classify_region_llm,
    classify_region_rules,
    should_grade,
)
from sheetgrade.label.roles_eval import ConfusionMatrix, LabeledRegion, evaluate_classifier
from sheetgrade.label.similarity import cosine_similarity, top_k

__all__ = [
    "DEFAULT_STRATEGY",
    "FORMULA_COLUMN_RATIO",
    "HYBRID_EMBEDDING_WEIGHT",
    "MATCH_THRESHOLD",
    "SCRATCH_WORK_MAX_CELLS",
    "SYNONYM_GROUPS",
    "ConfusionMatrix",
    "EmbeddingCache",
    "LabeledPair",
    "LabeledRegion",
    "MatchResult",
    "MatchStrategy",
    "RegionRole",
    "StrategyReport",
    "classify_region_llm",
    "classify_region_rules",
    "cosine_similarity",
    "evaluate_classifier",
    "evaluate_strategy",
    "load_labeled_pairs",
    "normalize",
    "score_pair",
    "should_grade",
    "string_similarity",
    "top_k",
]
