"""Part 8: turn header text into an embedding (a meaning-map point), cached
so the same header text is never sent to the model twice in one run.
"""

from __future__ import annotations

from sheetgrade.infer import Backend


class EmbeddingCache:
    def __init__(self, backend: Backend) -> None:
        self._backend = backend
        self._cache: dict[str, list[float]] = {}

    def embed(self, text: str) -> list[float]:
        if text not in self._cache:
            self._cache[text] = self._backend.embed(text)
        return self._cache[text]
