"""Part 7: the router/sampling policy is tested against a fake backend
(no network, no GPU needed) -- the CLAUDE.md-required "router unit-tested
against a fake backend." The real OllamaBackend determinism test is
separate and skips itself if no local Ollama server is reachable, since CI
has no GPU and no Ollama installed.
"""

from __future__ import annotations

import socket

import pytest

from sheetgrade.infer import EXTRACTION_TEMPERATURE, CallSite, GenerationResult, OllamaBackend, call


class FakeBackend:
    """A stand-in for OllamaBackend that records what it was asked to do,
    instead of actually asking a model."""

    def __init__(self, response: str = "header") -> None:
        self._response = response
        self.last_temperature: float | None = None

    def generate(self, prompt: str, temperature: float) -> GenerationResult:
        self.last_temperature = temperature
        return GenerationResult(
            text=self._response, prompt_tokens=0, completion_tokens=0, duration_seconds=0.0
        )

    def embed(self, text: str) -> list[float]:
        return [0.0]


def test_call_applies_the_call_sites_sampling_policy():
    fake = FakeBackend()
    call(fake, CallSite.REGION_CLASSIFICATION, "classify this region")
    assert fake.last_temperature == EXTRACTION_TEMPERATURE


def _ollama_reachable() -> bool:
    try:
        with socket.create_connection(("localhost", 11434), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.mark.skipif(not _ollama_reachable(), reason="Ollama server not running locally")
def test_ollama_backend_is_deterministic_at_zero_temperature():
    backend = OllamaBackend()
    prompt = "Reply with exactly one word and nothing else: OK"
    first = backend.generate(prompt, temperature=EXTRACTION_TEMPERATURE)
    second = backend.generate(prompt, temperature=EXTRACTION_TEMPERATURE)
    assert first.text == second.text
