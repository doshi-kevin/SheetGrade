"""Part 7: the actual wire format for talking to a local model.

Ollama runs as a background server on this machine and exposes models over
plain HTTP -- the same idea as calling a website's API, except the address
is this machine (localhost) instead of the internet. `Backend` is the shape
any model backend must have; `OllamaBackend` is the one concrete
implementation that exists today (a hosted backend is future work, Part 21).
Call sites and tests depend on the `Backend` shape, not on `OllamaBackend`
directly, so tests can hand in a fake instead of hitting a real server.
"""

from __future__ import annotations

import json
import time
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol

OLLAMA_HOST = "http://localhost:11434"
GENERATION_MODEL = "llama3.2:3b"
EMBEDDING_MODEL = "nomic-embed-text"

# Ollama has no built-in request timeout; without one, a hung server call
# would block forever. 30s comfortably covers a single classification-sized
# generation on this hardware -- see benchmark.py for measured throughput.
REQUEST_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True, slots=True)
class GenerationResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    duration_seconds: float


class Backend(Protocol):
    def generate(self, prompt: str, temperature: float) -> GenerationResult: ...
    def embed(self, text: str) -> list[float]: ...


class ChoiceBackend(Protocol):
    """A backend that can be forced to answer with exactly one of a fixed
    set of words -- Part 9's fix for the Part 7 finding that a plain prompt
    ("answer in one word") gets a full sentence back anyway. Separate from
    `Backend` so Part 7's existing call sites and fakes don't need to change
    just because Part 9 needs a stricter guarantee."""

    def generate_choice(self, prompt: str, choices: Sequence[str], temperature: float) -> str: ...


class OllamaBackend:
    """Talks to a local Ollama server over HTTP. No retry, no fallback --
    a call site that needs resilience wraps this; this class just makes the
    one call and reports what happened."""

    def __init__(self, host: str = OLLAMA_HOST) -> None:
        self._host = host

    def generate(self, prompt: str, temperature: float) -> GenerationResult:
        payload = {
            "model": GENERATION_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        start = time.monotonic()
        body = self._post("/api/generate", payload)
        duration = time.monotonic() - start
        return GenerationResult(
            text=body["response"],
            prompt_tokens=body.get("prompt_eval_count", 0),
            completion_tokens=body.get("eval_count", 0),
            duration_seconds=duration,
        )

    def embed(self, text: str) -> list[float]:
        body = self._post("/api/embed", {"model": EMBEDDING_MODEL, "input": text})
        embedding: list[float] = body["embeddings"][0]
        return embedding

    def generate_choice(self, prompt: str, choices: Sequence[str], temperature: float) -> str:
        """Ollama's `format` field accepts a JSON schema and constrains the
        model's output to match it exactly -- here, one of `choices` and
        nothing else. This is a real constraint enforced while generating,
        not a request the model can politely ignore the way "please answer
        in one word" can."""
        payload = {
            "model": GENERATION_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": {"type": "string", "enum": list(choices)},
            "options": {"temperature": temperature},
        }
        body = self._post("/api/generate", payload)
        choice: str = json.loads(body["response"])
        return choice

    def _post(self, path: str, payload: dict[str, object]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self._host}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body: dict[str, Any] = json.loads(response.read())
            return body
