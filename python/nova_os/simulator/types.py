"""Dataclasses returned by ``client.simulate()``.

A simulation is described by two value types:

- :class:`Turn` — a single utterance by either the simulator (the
  synthetic customer) or the target agent.
- :class:`SimulationResult` — the full outcome of one ``simulate()``
  call: transcript, terminal outcome, evaluation signals, and token /
  duration metadata.

Both are frozen dataclasses so partners can use them as keys in
dicts / append to result CSVs without surprise mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Role = Literal["simulator", "target"]
Outcome = Literal["success", "failure", "timeout", "error"]


@dataclass(frozen=True)
class Turn:
    """One side of one round-trip in the simulation transcript.

    Attributes
    ----------
    role:
        ``"simulator"`` for utterances from the synthetic customer;
        ``"target"`` for utterances from the agent under test.
    content:
        The full text body sent / received on the ``/chat`` round-trip.
        Never truncated. Empty string is possible (e.g. simulator-silent
        case).
    timestamp:
        UNIX epoch seconds at the moment the turn was recorded
        (``time.time()`` after the round-trip returned).
    metadata:
        The ``metadata`` dict that was sent on the ``/chat`` call for
        this turn — surfaced so partners can post-hoc filter by the
        SDK-attached ``simulator_session_id`` / ``simulator_role`` /
        ``simulator_turn_index`` keys (plus any caller-supplied keys).
        For error turns the dict may also include ``error: True``.
    """

    role: Role
    content: str
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulationResult:
    """The outcome of a single ``client.simulate()`` call.

    Attributes
    ----------
    archetype_name:
        The ``name`` field of the archetype that drove this run.
    target_agent_id:
        The agent id that was the subject of the evaluation.
    transcript:
        Alternating list of :class:`Turn` objects in conversation order
        — typically ``simulator``, ``target``, ``simulator``, ``target``,
        ... but in the error case the trailing turn may carry
        ``metadata.error: True``.
    outcome:
        One of ``"success"`` / ``"failure"`` / ``"timeout"`` / ``"error"``.
        See the SDK's simulator README for the precedence rules
        (success → failure → timeout, with ``error`` only on transport
        failure).
    outcome_reason:
        Human-readable explanation, e.g. ``"success_signal_matched"``,
        ``"max_turns_reached: 10"``, ``"failure_signal_matched: I give up"``,
        ``"target_agent_error: 503"``, ``"simulator_error"``,
        ``"simulator_silent"``. ``None`` only for partial / unfinished
        states which v1 does not produce.
    evaluation_signals:
        ``success_signal_match`` (bool), ``failure_signal_matches``
        (list of matched signal strings — possibly multi-element when
        ``failure_signal_match == "all"``), ``turn_count`` (int).
    duration_ms:
        Wall-clock duration of the simulate call in milliseconds.
    tokens_used:
        Best-effort accumulation. Keys: ``simulator_input``,
        ``simulator_output``, ``target_input``, ``target_output``.
        Values are 0 when the gateway response did not surface token
        counts (never raised).
    error:
        Free-form error string for ``outcome == "error"``; ``None``
        for the success / failure / timeout cases.
    """

    archetype_name: str
    target_agent_id: str
    transcript: list[Turn]
    outcome: Outcome
    outcome_reason: str | None
    evaluation_signals: dict[str, Any]
    duration_ms: int
    tokens_used: dict[str, int]
    error: str | None = None


TurnEventKind = Literal["simulator_turn", "target_turn", "outcome"]


@dataclass(frozen=True)
class TurnEvent:
    """One event from the streaming simulator iterator.

    Three kinds:

    - ``"simulator_turn"`` — emitted after a simulator-side ``/v1/messages``
      call returns. ``content`` is the full simulator text;
      ``role == "simulator"``; ``turn_index`` is the position in the
      transcript (0-based).
    - ``"target_turn"`` — emitted after a target-side ``/v1/messages``
      call returns. ``content`` is the full target text;
      ``role == "target"``; ``turn_index`` is the position in the
      transcript (0-based, one greater than the preceding simulator
      event for the same simulator-target pair).
    - ``"outcome"`` — emitted exactly once as the LAST event in any
      stream. ``outcome`` carries the full materialised
      :class:`SimulationResult`. Per spec, error / timeout / failure
      states are surfaced via this event (never raised mid-iteration).

    The event order contract is load-bearing: each pair
    ``simulator_turn`` → ``target_turn`` mirrors the underlying loop;
    the stream always closes with exactly one ``outcome`` event, even
    on error / cancellation paths.
    """

    kind: TurnEventKind
    role: Role | None = None
    content: str | None = None
    outcome: SimulationResult | None = None
    turn_index: int | None = None
    timestamp: float | None = None


__all__ = [
    "Turn",
    "SimulationResult",
    "TurnEvent",
    "TurnEventKind",
    "Role",
    "Outcome",
]
