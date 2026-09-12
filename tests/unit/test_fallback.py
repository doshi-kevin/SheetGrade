from sheetgrade.label.fallback import normalize, string_similarity


def test_normalize_lowercases_strips_and_collapses_whitespace():
    assert normalize("  Revenue  ") == "revenue"
    assert normalize("Rev.") == "rev"
    assert normalize("Q1   2023") == "q1 2023"


def test_identical_after_normalization_scores_one():
    assert string_similarity("Revenue", "REVENUE") == 1.0
    assert string_similarity("Expenses", "  expenses ") == 1.0


def test_known_synonyms_score_one():
    assert string_similarity("Revenue", "Rev") == 1.0
    assert string_similarity("Total", "Grand Total") == 1.0
    assert string_similarity("Profit", "Net Income") == 1.0


def test_q1_vs_q2_scores_high_on_spelling_despite_different_meaning():
    """The exact failure mode Part 8 is built around: one-character
    difference, spelling-similarity is high, meaning is unrelated."""
    score = string_similarity("Q1", "Q2")
    assert score >= 0.5


def test_unrelated_headers_score_low():
    assert string_similarity("Email", "Phone") < 0.5
