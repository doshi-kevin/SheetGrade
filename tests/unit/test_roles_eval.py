from sheetgrade.detect import HeaderShape, Region
from sheetgrade.ir import Cell, CellAddress, CellType, Sheet
from sheetgrade.label import LabeledRegion, RegionRole, evaluate_classifier


def _dummy_example(expected: RegionRole) -> LabeledRegion:
    cells = {CellAddress(0, 0): Cell(CellAddress(0, 0), value="x", data_type=CellType.STRING)}
    sheet = Sheet(name="S", cells=cells, n_rows=1, n_cols=1)
    region = Region(sheet="S", min_row=0, max_row=0, min_col=0, max_col=0)
    return LabeledRegion(sheet, region, HeaderShape(None, None), expected)


def test_perfect_classifier_scores_full_accuracy_and_no_confusions():
    examples = [_dummy_example(RegionRole.GIVEN_INPUT), _dummy_example(RegionRole.SCRATCH_WORK)]

    def always_correct(sheet, region, header_shape):
        return next(e.expected_role for e in examples if e.sheet is sheet)

    matrix = evaluate_classifier(examples, always_correct)

    assert matrix.accuracy == 1.0
    assert matrix.confusions_for(RegionRole.GIVEN_INPUT) == {}


def test_known_bad_classifier_is_caught_by_the_matrix():
    """Stand-in for CLAUDE.md's "inject a known-bad grader" test: if the
    matrix can't catch an always-wrong classifier, it isn't measuring
    anything."""
    examples = [_dummy_example(RegionRole.GIVEN_INPUT), _dummy_example(RegionRole.SCRATCH_WORK)]

    def always_scratch_work(sheet, region, header_shape):
        return RegionRole.SCRATCH_WORK

    matrix = evaluate_classifier(examples, always_scratch_work)

    assert matrix.accuracy == 0.5
    assert matrix.confusions_for(RegionRole.GIVEN_INPUT) == {RegionRole.SCRATCH_WORK: 1}
    assert matrix.confusions_for(RegionRole.SCRATCH_WORK) == {}


def test_empty_corpus_is_not_treated_as_a_perfect_score_by_accident():
    matrix = evaluate_classifier([], lambda sheet, region, header_shape: RegionRole.GIVEN_INPUT)
    assert matrix.total == 0
    assert matrix.accuracy == 1.0
