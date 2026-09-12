"""Part 7: how much randomness the model is allowed when picking its next
word, per call site.

Temperature controls that randomness. At 0.0 the model always takes the
single most likely next word -- same input, same output, every time. Above
0, it can pick a less-likely word at random, which is wanted for prose (Part
21 feedback shouldn't read identically for 300 students) but actively breaks
a classification call site's determinism: Part 7 requires "same input, same
output," and a call site that occasionally relabels the same header row
would fail that test intermittently, not because the code is buggy but
because the model itself was allowed to be non-deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass

from sheetgrade.infer.router import CallSite

# Classification-style calls (a label out of a fixed set) should never vary
# run to run. Accuracy comes from the classification logic, not from adding
# randomness, so there's no reason to move this above 0.
EXTRACTION_TEMPERATURE = 0.0

# Prose generation (Part 21 feedback) has no call site yet -- nothing
# consumes this today. Placeholder, honestly untuned, same situation as
# GAP_TOLERANCE in Part 5: 0.6 is safer and more repetitive, 0.9 is more
# varied with more risk of drifting off-topic. Revisit once Part 21 exists
# and real generated feedback can be measured.
PROSE_TEMPERATURE = 0.7


@dataclass(frozen=True, slots=True)
class SamplingParams:
    temperature: float


SAMPLING_TABLE: dict[CallSite, SamplingParams] = {
    # Embeddings aren't generated word-by-word, so temperature is meaningless
    # here -- kept at 0.0 only so every CallSite has an entry.
    CallSite.HEADER_EMBEDDING: SamplingParams(temperature=0.0),
    CallSite.REGION_CLASSIFICATION: SamplingParams(temperature=EXTRACTION_TEMPERATURE),
    CallSite.FEEDBACK_GENERATION: SamplingParams(temperature=PROSE_TEMPERATURE),
}


def sampling_for(call_site: CallSite) -> SamplingParams:
    return SAMPLING_TABLE[call_site]
