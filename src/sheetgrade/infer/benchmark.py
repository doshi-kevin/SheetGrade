"""Part 7: how fast the local model actually runs on this machine, so
"local is free" doesn't turn out to be too slow to use in practice.

Nothing before this measured latency or throughput. These numbers feed the
routing decision alongside accuracy once a real call site (Part 9) exists to
weigh speed against, and are appended to a results CSV the same way the
Part 4 harness appends its own -- one row per benchmark run, with the git
SHA, so a regression (or a speedup) is visible across commits.
"""

from __future__ import annotations

import csv
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sheetgrade.infer.backend import Backend


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    prompt: str
    completion_tokens: int
    duration_seconds: float

    @property
    def tokens_per_second(self) -> float:
        if self.duration_seconds == 0:
            return 0.0
        return self.completion_tokens / self.duration_seconds


def run_benchmark(
    backend: Backend, prompts: Sequence[str], temperature: float
) -> tuple[BenchmarkResult, ...]:
    results: list[BenchmarkResult] = []
    for prompt in prompts:
        generation = backend.generate(prompt, temperature)
        results.append(
            BenchmarkResult(prompt, generation.completion_tokens, generation.duration_seconds)
        )
    return tuple(results)


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def append_benchmark_csv(results: Sequence[BenchmarkResult], path: Path, config: str = "") -> None:
    if not results:
        return
    avg_tps = sum(r.tokens_per_second for r in results) / len(results)
    avg_latency = sum(r.duration_seconds for r in results) / len(results)
    row = {
        "timestamp": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "config": config,
        "n_prompts": len(results),
        "avg_tokens_per_second": f"{avg_tps:.2f}",
        "avg_latency_seconds": f"{avg_latency:.3f}",
    }
    is_new = not path.exists()
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        if is_new:
            writer.writeheader()
        writer.writerow(row)
