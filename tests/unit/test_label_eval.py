from pathlib import Path

from sheetgrade.infer import GenerationResult
from sheetgrade.label.embeddings import EmbeddingCache
from sheetgrade.label.eval import LabeledPair, evaluate_strategy, load_labeled_pairs
from sheetgrade.label.matching import MatchStrategy

FIXTURE = Path(__file__).parents[1] / "fixtures" / "header_pairs.json"


class FakeEmbeddingBackend:
    def generate(self, prompt: str, temperature: float) -> GenerationResult:
        raise NotImplementedError("not exercised by these tests")

    def embed(self, text: str) -> list[float]:
        # Every header gets an identical vector, so embedding-only always
        # says "match" -- exists to prove the accuracy math itself is
        # correct, not to test real embedding quality.
        return [1.0, 0.0]


def test_load_labeled_pairs_reads_the_real_fixture():
    pairs = load_labeled_pairs(FIXTURE)
    assert len(pairs) > 0
    assert any(p.same_meaning for p in pairs)
    assert any(not p.same_meaning for p in pairs)


def test_evaluate_strategy_scores_a_known_bad_matcher():
    """Stand-in for CLAUDE.md's "inject a known-bad grader" test: an
    always-says-match embedding gets every 'different' pair wrong."""
    pairs = (
        LabeledPair("Revenue", "Rev", same_meaning=True),
        LabeledPair("Email", "Phone", same_meaning=False),
    )
    embeddings = EmbeddingCache(FakeEmbeddingBackend())
    report = evaluate_strategy(pairs, embeddings, MatchStrategy.EMBEDDING_ONLY)
    assert report.accuracy == 0.5
    assert len(report.false_positives) == 1
    assert report.false_positives[0].header_a == "Email"


def test_evaluate_strategy_perfect_matcher_scores_one():
    pairs = (LabeledPair("Revenue", "Rev", same_meaning=True),)
    embeddings = EmbeddingCache(FakeEmbeddingBackend())
    report = evaluate_strategy(pairs, embeddings, MatchStrategy.EMBEDDING_ONLY)
    assert report.accuracy == 1.0
    assert report.false_positives == ()
    assert report.false_negatives == ()
