import numpy as np

from sheetgrade.label.similarity import cosine_similarity, top_k


def test_identical_vectors_have_similarity_one():
    v = np.array([1.0, 2.0, 3.0])
    assert cosine_similarity(v, v) == 1.0


def test_perpendicular_vectors_have_similarity_zero():
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    assert cosine_similarity(a, b) == 0.0


def test_opposite_vectors_have_similarity_minus_one():
    a = np.array([1.0, 0.0])
    b = np.array([-1.0, 0.0])
    assert cosine_similarity(a, b) == -1.0


def test_similarity_ignores_magnitude_not_just_direction():
    a = np.array([1.0, 0.0])
    b = np.array([5.0, 0.0])
    assert cosine_similarity(a, b) == 1.0


def test_zero_vector_scores_zero_not_a_crash():
    a = np.array([0.0, 0.0])
    b = np.array([1.0, 0.0])
    assert cosine_similarity(a, b) == 0.0


def test_top_k_returns_closest_first():
    query = np.array([1.0, 0.0])
    candidates = np.array(
        [
            [0.0, 1.0],  # index 0: perpendicular, least similar
            [1.0, 0.0],  # index 1: identical direction, most similar
            [0.7, 0.7],  # index 2: 45 degrees, in between
        ]
    )
    ranked = top_k(query, candidates, k=2)
    assert [i for i, _ in ranked] == [1, 2]


def test_top_k_respects_k():
    query = np.array([1.0, 0.0])
    candidates = np.array([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]])
    assert len(top_k(query, candidates, k=1)) == 1
