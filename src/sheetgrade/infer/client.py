"""Part 7: the one place call sites actually go through.

Looks up the sampling policy for a call site, then asks the given backend to
run the prompt with it. Call sites never set a temperature themselves --
that would mean the same policy decision (extraction vs prose) living in
multiple places, drifting apart over time. They call `call()`, name which
call site they are, and the policy is applied for them.
"""

from __future__ import annotations

from sheetgrade.infer.backend import Backend, GenerationResult
from sheetgrade.infer.router import CallSite
from sheetgrade.infer.sampling import sampling_for


def call(backend: Backend, call_site: CallSite, prompt: str) -> GenerationResult:
    temperature = sampling_for(call_site).temperature
    return backend.generate(prompt, temperature)
