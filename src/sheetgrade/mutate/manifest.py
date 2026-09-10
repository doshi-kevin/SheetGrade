"""The receipt a mutation writes down about itself.

`expected_effect` is the categorical claim later parts get tested against:
- structural_only  -- shape changed (moved/renamed/reordered), no value is wrong
- cosmetic_only    -- only formatting changed, values and structure are untouched
- value_changed    -- a specific cell's actual answer is now wrong
- carry_through    -- an upstream input is wrong, but the formula reading it is correct
- excluded_from_grading -- content was added that should never be scored at all
- method_lost      -- a formula was replaced by a bare number; the *method* is gone,
                       independent of whether that number happens to still be correct
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ExpectedEffect = Literal[
    "structural_only",
    "cosmetic_only",
    "value_changed",
    "carry_through",
    "excluded_from_grading",
    "method_lost",
]


@dataclass(frozen=True, slots=True)
class MutationRecord:
    mutation: str
    sheet: str
    expected_effect: ExpectedEffect
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MutationSpec:
    """One entry in a composition request: which mutation, with which explicit params."""

    name: str
    kwargs: dict[str, Any] = field(default_factory=dict)
