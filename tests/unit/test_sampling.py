from sheetgrade.infer import (
    EXTRACTION_TEMPERATURE,
    PROSE_TEMPERATURE,
    CallSite,
    sampling_for,
)


def test_classification_call_site_is_deterministic():
    assert EXTRACTION_TEMPERATURE == 0.0
    assert sampling_for(CallSite.REGION_CLASSIFICATION).temperature == EXTRACTION_TEMPERATURE


def test_feedback_generation_uses_prose_temperature():
    assert sampling_for(CallSite.FEEDBACK_GENERATION).temperature == PROSE_TEMPERATURE
