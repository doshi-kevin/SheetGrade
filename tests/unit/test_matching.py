from typing import ClassVar

from sheetgrade.infer import GenerationResult
from sheetgrade.label.embeddings import EmbeddingCache
from sheetgrade.label.matching import MatchStrategy, score_pair


class FakeEmbeddingBackend:
    """Hands back a fixed, hand-picked vector per header text, so tests are
    deterministic and need no real model."""

    _VECTORS: ClassVar[dict[str, list[float]]] = {
        "Revenue": [1.0, 0.0],
        "Rev": [0.9, 0.1],
        "Q1": [0.0, 1.0],
        "Q2": [0.0, 0.99],  # deliberately near Q1: the known embedding trap
        "Email": [-1.0, 0.0],
    }

    def generate(self, prompt: str, temperature: float) -> GenerationResult:
        raise NotImplementedError("not exercised by these tests")

    def embed(self, text: str) -> list[float]:
        return self._VECTORS[text]


def test_string_only_uses_spelling_and_synonyms_not_embeddings():
    embeddings = EmbeddingCache(FakeEmbeddingBackend())
    result = score_pair("Revenue", "Rev", embeddings, MatchStrategy.STRING_ONLY)
    assert result.is_match
    assert embeddings._cache == {}  # never called .embed() at all


def test_embedding_only_matches_close_vectors():
    embeddings = EmbeddingCache(FakeEmbeddingBackend())
    result = score_pair("Revenue", "Rev", embeddings, MatchStrategy.EMBEDDING_ONLY)
    assert result.is_match


def test_embedding_only_falls_for_the_q1_q2_trap():
    """Documents the known weakness: our fake vectors deliberately place Q1
    and Q2 close together, the way a real embedding model can too."""
    embeddings = EmbeddingCache(FakeEmbeddingBackend())
    result = score_pair("Q1", "Q2", embeddings, MatchStrategy.EMBEDDING_ONLY)
    assert result.is_match  # wrong! -- this is exactly why the fallback exists


def test_unrelated_headers_do_not_match_on_any_strategy():
    embeddings = EmbeddingCache(FakeEmbeddingBackend())
    for strategy in MatchStrategy:
        result = score_pair("Revenue", "Email", embeddings, strategy)
        assert not result.is_match
