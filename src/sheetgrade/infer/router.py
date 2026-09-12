"""Part 7: which backend handles a given call site -- the local model on
this machine, or a hosted API.

The table below is a flat lookup, decided once ahead of time, not a live
decision made at request time. A "try local, fall back to hosted if it
fails" scheme would make a same-input-same-output determinism test
unreliable, since the routing itself could change between two runs of the
exact same call. Each entry instead reflects a measured or reasoned choice --
today that's the 2026-09-10 scope-change entry in DECISIONS.md: high call
volume + low per-call stakes routes local (Part 13 abstains below confidence
anyway, so a shaky local answer isn't the last word); low volume +
quality-critical routes hosted. Once Part 9's classifier exists, its entry
should be revisited against real accuracy numbers from the Part 4 harness,
not left on today's reasoning alone.
"""

from __future__ import annotations

from enum import Enum, auto


class CallSite(Enum):
    """Every place in the pipeline that needs a model call registers itself
    here. Adding a call site means adding one line to ROUTING_TABLE too --
    there's no default, so a forgotten entry fails loudly (KeyError) instead
    of silently guessing local or hosted."""

    HEADER_EMBEDDING = auto()  # Part 8: header similarity via embeddings
    REGION_CLASSIFICATION = auto()  # Part 9: header/data/scratch-work labels
    FEEDBACK_GENERATION = auto()  # Part 21: prose feedback for a student


class BackendTarget(Enum):
    LOCAL = auto()
    HOSTED = auto()


ROUTING_TABLE: dict[CallSite, BackendTarget] = {
    CallSite.HEADER_EMBEDDING: BackendTarget.LOCAL,
    CallSite.REGION_CLASSIFICATION: BackendTarget.LOCAL,
    CallSite.FEEDBACK_GENERATION: BackendTarget.HOSTED,
}


def route(call_site: CallSite) -> BackendTarget:
    return ROUTING_TABLE[call_site]
