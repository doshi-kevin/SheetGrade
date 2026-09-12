"""Part 9: measure a region-role classifier against labeled examples with a
confusion matrix -- which roles get mixed up with which, not just one
overall accuracy number. Mirrors the Part 4 harness's own philosophy: a
number replaces a guess about whether the classifier is good enough.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from sheetgrade.detect import HeaderShape
from sheetgrade.detect.regions import Region
from sheetgrade.ir import Sheet
from sheetgrade.label.roles import RegionRole


@dataclass(frozen=True, slots=True)
class LabeledRegion:
    sheet: Sheet
    region: Region
    header_shape: HeaderShape
    expected_role: RegionRole


Classifier = Callable[[Sheet, Region, HeaderShape], RegionRole]


@dataclass(frozen=True, slots=True)
class ConfusionMatrix:
    # (expected, predicted) -> count. A correct call has expected == predicted.
    counts: dict[tuple[RegionRole, RegionRole], int]
    total: int

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 1.0
        correct = sum(n for (expected, predicted), n in self.counts.items() if expected is predicted)
        return correct / self.total

    def confusions_for(self, expected: RegionRole) -> dict[RegionRole, int]:
        return {
            predicted: n
            for (exp, predicted), n in self.counts.items()
            if exp is expected and predicted is not expected
        }


def evaluate_classifier(
    labeled_regions: Sequence[LabeledRegion], classify: Classifier
) -> ConfusionMatrix:
    counts: dict[tuple[RegionRole, RegionRole], int] = {}
    for example in labeled_regions:
        predicted = classify(example.sheet, example.region, example.header_shape)
        key = (example.expected_role, predicted)
        counts[key] = counts.get(key, 0) + 1
    return ConfusionMatrix(counts, total=len(labeled_regions))
