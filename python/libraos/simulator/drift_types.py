"""Value types for the persona-drift metric (#29).

Frozen dataclasses, like :class:`~libraos.simulator.SimulationResult` and
:class:`~libraos.simulator.RubricResult`, so partners can key them in dicts and
append them to result CSVs without surprise mutation.

The metric answers one question: **did the persona-playing side of a transcript
stay in character?** Kenneth Li's persona-drift work (arXiv 2402.10962) shows
that an LLM told to play a persona degrades toward its default assistant
behaviour within roughly eight turns, as attention on the system prompt decays.
A multi-turn eval that only reads the terminal outcome can therefore score
"success" on turn 8 of a 10-turn run while the synthetic customer has quietly
become a chatbot — and the agent under test was really being graded against a
different persona than the one the archetype declared.

Score convention (fixed, do not invert): ``0.0`` = perfect persona retention,
``1.0`` = complete drift.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


#: Default alert threshold. Per the EqualDocs SYNTHESIS spec; overridable
#: per-archetype via ``drift_alert_threshold`` in the archetype YAML, and
#: per-call via ``threshold=`` / ``DriftOptions(threshold=...)``.
DEFAULT_DRIFT_THRESHOLD = 0.15

#: Default probe cadence — score the persona at least every N of its turns.
DEFAULT_PROBE_EVERY = 2

ProbeMode = Literal["passive", "active"]


@dataclass(frozen=True)
class DriftTurn:
    """The drift verdict on one probe point.

    Attributes
    ----------
    turn_index:
        Position of the scored utterance in the transcript that was measured
        (0-based, counting **all** turns — persona and counterparty alike), so
        it can be used directly as ``transcript[turn_index]``.
    probe_index:
        0-based ordinal of this probe point among the probe points that were
        scored. ``0`` is the earliest probe, not the baseline.
    persona_turn_index:
        0-based ordinal of this utterance among the persona's own turns. The
        baseline is persona turn 0, so this is always ``>= 1``.
    score:
        Drift for this probe point alone, in ``[0.0, 1.0]``.
    components:
        Per-signal contribution, always the same four keys so the shape is
        stable for CSV/DataFrame output: ``character_break``,
        ``disposition_violation``, ``advisory_inversion``, ``format_break``.
        Values are the *raw* signal strengths in ``[0.0, 1.0]`` before
        weighting — see :mod:`libraos.simulator.drift` for the weights.
    probe_question:
        The injected probe this utterance answered, when the transcript was
        produced with ``probe_mode="active"``. ``None`` for passive scoring
        (where the persona's own in-band turn is the probe point).
    excerpt:
        First 200 characters of the scored utterance, so a drift report is
        readable without re-joining it against the transcript.
    evidence:
        Human-readable strings naming what actually fired (matched marker
        phrases, leaked hidden facts). Empty when ``score == 0.0``.
    """

    turn_index: int
    probe_index: int
    persona_turn_index: int
    score: float
    components: dict[str, float]
    probe_question: str | None = None
    excerpt: str = ""
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DriftMetric:
    """Persona-drift measurement over one transcript.

    Attributes
    ----------
    score:
        Aggregate drift in ``[0.0, 1.0]``. ``0.0`` = perfect retention,
        ``1.0`` = complete drift. Computed as
        ``0.5 * max(per-turn) + 0.5 * mean(per-turn)`` — severity-dominant, so
        a single total character break anywhere in a long run always lands at
        ``>= 0.5`` and cannot be diluted by a hundred clean turns. See the
        module docstring of :mod:`libraos.simulator.drift`.
    threshold:
        The alert threshold this measurement was evaluated against.
    alert_triggered:
        ``score > threshold``. Strictly greater — a score exactly equal to the
        threshold does not alert.
    method:
        The scoring method identifier that produced this metric.
    per_turn:
        One :class:`DriftTurn` per probe point, in transcript order.
    baseline_turn_index:
        Transcript index of the persona utterance used as the in-character
        baseline (the persona's first non-empty turn, when the system prompt
        still dominates attention). ``None`` if no baseline was available.
    first_drift_turn_index:
        Transcript index of the earliest probe point whose own score exceeded
        ``threshold`` — i.e. where drift first became visible. ``None`` when no
        individual probe crossed. Useful for reproducing Li's "degrades within
        ~8 turns" curve across a corpus of runs.
    probe_every:
        The cadence that selected the probe points.
    probe_mode:
        ``"passive"`` when the persona's own in-band turns were scored;
        ``"active"`` when out-of-band probe questions were injected and their
        answers scored.
    notes:
        Free-form diagnostics — persona turn count, resolved persona role,
        leaked hidden facts, and similar. Shape is not part of the frozen API;
        read it for debugging, do not assert on it.
    """

    score: float
    threshold: float = DEFAULT_DRIFT_THRESHOLD
    alert_triggered: bool = False
    method: str = "kenneth-li-probe"
    per_turn: list[DriftTurn] = field(default_factory=list)
    baseline_turn_index: int | None = None
    first_drift_turn_index: int | None = None
    probe_every: int = DEFAULT_PROBE_EVERY
    probe_mode: ProbeMode = "passive"
    notes: dict[str, Any] = field(default_factory=dict)

    @property
    def measured(self) -> bool:
        """``True`` when at least one probe point was actually scored.

        A transcript too short to measure (fewer than two non-empty persona
        turns) still yields a :class:`DriftMetric`, with ``score == 0.0``,
        ``per_turn == []`` and ``notes["reason"] ==
        "insufficient_persona_turns"``. That ``0.0`` means *not measured*, not
        *no drift* — **filter on this property before aggregating scores across
        runs**, or short runs will silently pull a corpus average toward zero.
        """
        return bool(self.per_turn)

    @property
    def max_turn_score(self) -> float:
        """Worst single probe point — the severity term of the aggregate."""
        return max((t.score for t in self.per_turn), default=0.0)

    @property
    def mean_turn_score(self) -> float:
        """Mean over probe points — the prevalence term of the aggregate."""
        if not self.per_turn:
            return 0.0
        return sum(t.score for t in self.per_turn) / len(self.per_turn)


@dataclass(frozen=True)
class DriftOptions:
    """Per-call drift configuration for ``simulate()`` / ``simulate_stream()``.

    Passed as ``simulate(..., drift=DriftOptions(...))``. The default
    (``drift=None``) enables passive monitoring with the archetype's threshold,
    which costs no extra model calls.

    Attributes
    ----------
    enabled:
        ``False`` disables measurement entirely — ``SimulationResult.drift``
        stays ``None`` and no ``drift_alert`` events are emitted.
    probe_every:
        Score the persona at least every N of its own turns. Must be ``>= 1``.
    threshold:
        Overrides ``archetype.drift_alert_threshold``, which in turn overrides
        :data:`DEFAULT_DRIFT_THRESHOLD`.
    method:
        Scoring method identifier — see
        :data:`libraos.simulator.drift.DRIFT_METHODS`.
    probe_mode:
        ``"passive"`` (default) scores the persona's own in-band turns and adds
        zero model calls. ``"active"`` additionally injects an out-of-band
        probe question to the *simulator* at each cadence point and scores the
        answer; the probe exchange is never shown to the target agent, but the
        answer IS appended to the transcript (tagged
        ``metadata["drift_probe"] = True``) so the measurement is reproducible
        offline. Active mode costs one extra simulator call per probe.
    probes:
        Probe questions for active mode. Falls back to
        ``archetype.drift_probes``, then to a built-in persona-agnostic set.
        Cycled deterministically by probe ordinal.
    alert:
        ``False`` measures drift but suppresses ``drift_alert`` stream events.
    """

    enabled: bool = True
    probe_every: int = DEFAULT_PROBE_EVERY
    threshold: float | None = None
    method: str = "kenneth-li-probe"
    probe_mode: ProbeMode = "passive"
    probes: list[str] | None = None
    alert: bool = True


__all__ = [
    "DriftMetric",
    "DriftTurn",
    "DriftOptions",
    "ProbeMode",
    "DEFAULT_DRIFT_THRESHOLD",
    "DEFAULT_PROBE_EVERY",
]
