from __future__ import annotations

import socket
from collections.abc import Sequence
from pathlib import Path

import pytest

from sheetgrade.detect import Region, detect_header_shape
from sheetgrade.infer import EXTRACTION_TEMPERATURE, OllamaBackend
from sheetgrade.label import RegionRole, classify_region_llm
from sheetgrade.reader import read_xlsx

FIXTURE = Path(__file__).parents[1] / "fixtures" / "keys" / "sample_key.xlsx"


class FakeChoiceBackend:
    def __init__(self, answer: str) -> None:
        self._answer = answer
        self.last_choices: Sequence[str] | None = None
        self.last_temperature: float | None = None

    def generate_choice(self, prompt: str, choices: Sequence[str], temperature: float) -> str:
        self.last_choices = choices
        self.last_temperature = temperature
        return self._answer


def test_classify_region_llm_uses_extraction_temperature_and_all_roles():
    wb = read_xlsx(FIXTURE)
    sheet = wb.sheets[0]
    region = Region(sheet="Budget", min_row=0, max_row=sheet.n_rows - 1, min_col=0, max_col=sheet.n_cols - 1)
    shape = detect_header_shape(sheet, region)
    fake = FakeChoiceBackend(answer="GIVEN_INPUT")

    role = classify_region_llm(fake, sheet, region, shape)

    assert role is RegionRole.GIVEN_INPUT
    assert fake.last_temperature == EXTRACTION_TEMPERATURE
    assert set(fake.last_choices) == {r.name for r in RegionRole}


def _ollama_reachable() -> bool:
    try:
        with socket.create_connection(("localhost", 11434), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.mark.skipif(not _ollama_reachable(), reason="Ollama server not running locally")
def test_ollama_generate_choice_never_returns_outside_the_allowed_set():
    """The whole point of the format-constrained call (Part 9's fix for the
    Part 7 finding): the model is forced to answer with one of our exact
    words, not a sentence containing one of them."""
    backend = OllamaBackend()
    choices = [r.name for r in RegionRole]
    prompt = (
        "Region contents: Category, Q1, Q2, Q3, Q4, Total (header row); "
        "Revenue 1000 1100 1200 1300 4600 (data row). "
        "Which role best fits?"
    )
    answer = backend.generate_choice(prompt, choices, temperature=EXTRACTION_TEMPERATURE)
    assert answer in choices
