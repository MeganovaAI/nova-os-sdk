"""Persona-drift scoring — ``client.measure_drift()`` (#29).

Where :mod:`libraos.simulator.rubric` scores a *work product* against a
checklist and the ``simulate()`` loop scores a *trajectory* against termination
signals, this module scores the **synthetic customer itself**: across a
multi-turn transcript, did the persona-playing side stay the character the
archetype declared?

Why this is a separate metric
=============================

Kenneth Li's persona-drift work (arXiv `2402.10962
<https://arxiv.org/html/2402.10962v1>`_) shows that an LLM instructed to play a
persona reverts toward its default assistant behaviour within roughly eight
turns as attention on the system prompt decays. That failure is invisible to
every signal ``simulate()`` already reports: a run can match its
``success_signal`` on turn 8 of a 10-turn trajectory while the "customer" has
been a helpful chatbot since turn 5 — which means the agent under test was
graded against a persona nobody authored.

Note carefully **which side is measured**. The archetype constrains the
*simulator*, not the target agent. ``measure_drift`` therefore scores the
persona-playing speaker's turns. It says nothing about the quality of the agent
under test; it tells you whether the evaluation harness itself was still valid.

The scoring function
====================

At each **probe point** (see below) the persona's utterance is scored on four
independent signals, each a raw strength in ``[0, 1]``:

``character_break`` (weight 1.0)
    The persona speaks as an AI/assistant rather than as the customer. Two
    families: explicit model self-reference ("as an AI", "language model", "my
    system prompt") scores ``1.0``; assistant-service framing ("how can I help
    you", "is there anything else I can help with") scores ``0.8``. This is the
    canonical drift Li documents — a persona-playing model falling back to its
    RLHF-default assistant voice — and it is the highest-precision signal
    available without a model-based judge.

``disposition_violation`` (weight 0.9)
    The utterance contradicts the disposition implied by
    ``archetype.disclosure_willingness`` + ``archetype.hidden_facts``. A hidden
    fact counts as *disclosed* when the utterance covers >= 60% of the fact's
    distinctive content words with at least two matches. Then:

    - ``open`` — disclosure is expected, so it scores ``0.0``; instead, explicit
      *deflection* markers ("I'd rather not say", "that's private") score
      ``0.7``, because an open persona that turns evasive has drifted.
    - ``cautious`` — the archetype semantics are "shares when asked directly,
      never volunteers". Disclosure scores ``0.0`` when the preceding
      counterparty turn asked a question (or, in active mode, when the
      utterance answers an injected probe), and ``1.0`` when volunteered.
    - ``guarded`` — "deflects or defers until trust is established". Disclosure
      scores ``0.0`` only when it is both prompted *and* the counterparty has
      already asked at least two questions; otherwise ``1.0``.

``advisory_inversion`` (weight 0.6)
    Role inversion: the help-seeker starts giving advice. Fires on advisory
    phrasings ("I'd recommend", "here's what you", "you may want to"). Scores
    ``1.0`` when the utterance is also second-person dominant (strictly more
    "you/your" than "I/me/my", and at least two second-person pronouns), and
    ``0.35`` otherwise — a customer can occasionally say "I suggest we…" in
    character, so bare marker presence is deliberately weak evidence.

``format_break`` (weight 0.2)
    Markdown structure (headings, bullet/numbered lists, bold runs) in a turn
    that the simulator system prompt explicitly forbids. Real but weak: a
    customer might legitimately list their documents. Weighted so that a single
    formatted turn never alone crosses the default threshold, while a persistent
    pattern does.

The per-turn score combines them with a **noisy-OR**::

    turn_score = 1 - Π (1 - weight_c * strength_c)

Noisy-OR is the right combiner because these are independent pieces of evidence
for one latent event ("the persona is gone"): any single strong signal
dominates, several weak ones accumulate, and the result is bounded by 1.0
without arbitrary clipping.

The transcript-level score is **severity-dominant**::

    score = 0.5 * max(turn_scores) + 0.5 * mean(turn_scores)

A plain mean is wrong here: one total character break in a 20-probe run would
average to 0.05 and never alert, which is precisely the failure mode the metric
exists to catch. The ``max`` term guarantees that **any single complete
character break scores >= 0.5**, regardless of run length; the ``mean`` term
still rewards transcripts that recover and penalises persistent low-grade drift.

Probe points
============

The persona's first non-empty turn is the **baseline** — the point at which the
system prompt still dominates attention. Probe points are its subsequent turns
at cadence ``probe_every`` (default 2), plus always the final persona turn,
which is the most-drifted point and the one a partner most wants scored:
``{i >= 1 : i % probe_every == 0} ∪ {last}``.

In ``probe_mode="active"`` the simulator is additionally asked an out-of-band
probe question at each cadence point; its answer is scored instead of the
in-band turn. Probe questions are deliberately **persona-agnostic** — they must
not restate ``archetype.description``, because re-stating the persona refreshes
the model's attention on it and destroys the very quantity being measured.

Limits of this metric
=====================

This is a deterministic lexical scorer, by design: it must run offline, in CI,
with no model call and no server. It reliably detects overt character breaks,
role inversion, formatting reversion, and near-verbatim hidden-fact leakage.

It does **not** detect: semantic drift that keeps the register (a persona that
stays conversational but contradicts its own biography); paraphrased hidden-fact
leakage that shares few surface tokens with the archetype text; tone or
emotional-stance drift; or drift in a language other than English. Treat a low
score as "no drift *of the kinds this detects*", not as proof of persona
fidelity. A model-graded method can be registered alongside this one under a new
``method=`` identifier without changing any existing signature.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libraos.simulator.archetype import Archetype
from libraos.simulator.drift_types import (
    DEFAULT_DRIFT_THRESHOLD,
    DEFAULT_PROBE_EVERY,
    DriftMetric,
    DriftTurn,
    ProbeMode,
)

# ── method registry ─────────────────────────────────────────────────────────

#: Supported ``method=`` identifiers. ``"kenneth-li-probe"`` is the name from
#: the issue's API sketch and the documented default; ``"lexical-persona-v1"``
#: is an implementation-precise alias for the same scorer, so a partner who
#: later pins a model-graded method can tell the two apart in stored results.
DRIFT_METHODS: tuple[str, ...] = ("kenneth-li-probe", "lexical-persona-v1")

DEFAULT_DRIFT_METHOD = "kenneth-li-probe"


# ── signal weights (see module docstring for the rationale) ─────────────────

_WEIGHTS: dict[str, float] = {
    "character_break": 1.0,
    "disposition_violation": 0.9,
    "advisory_inversion": 0.6,
    "format_break": 0.2,
}

#: Stable component order — keeps CSV / DataFrame columns deterministic.
_COMPONENT_ORDER = (
    "character_break",
    "disposition_violation",
    "advisory_inversion",
    "format_break",
)


# ── marker sets ─────────────────────────────────────────────────────────────
# Every marker below is chosen for PRECISION over recall: a false drift alert
# costs a partner more than a missed one, because it erodes trust in the whole
# metric. Phrases a help-seeking customer could plausibly utter are excluded
# even when they are common in assistant output (e.g. "let me know if you have
# any questions", "make sure to", "you should").

#: Explicit model/meta self-reference. Unambiguous character break → 1.0.
_META_AI_MARKERS: tuple[str, ...] = (
    "as an ai",
    "as a ai",
    "i am an ai",
    "i'm an ai",
    "an ai assistant",
    "ai language model",
    "language model",
    "my training data",
    "i don't have personal experiences",
    "i do not have personal experiences",
    "i'm just a program",
    "i am just a program",
    "i'm simulating",
    "i am simulating",
    "my system prompt",
    "the system prompt",
    "playing the role of",
    "i'm your assistant",
    "i am your assistant",
    "as your ai",
)

# Rejected meta-marker candidates, kept here so nobody re-adds them:
#   "the simulation" / "this simulation" — "the simulation results from the
#       calculator said I qualify" is ordinary customer speech and would have
#       scored a maximum-severity 1.0.
#   "my instructions say" / "i was instructed to" — "my instructions say to
#       submit by Friday" is what a customer relaying agency guidance sounds
#       like.
#   "i'm an assistant" / "as the assistant" — matches "I'm an assistant manager
#       at a retail store".
# Each was caught by adversarial in-character probing, not by review. Any new
# marker should be run against the same corpus before it ships.

#: Assistant-service framing — the persona offering help rather than seeking
#: it. Strong role inversion, but conceivably a very polite customer → 0.8.
_SERVICE_OFFER_MARKERS: tuple[str, ...] = (
    "how can i help you",
    "how may i help you",
    "how can i assist",
    "how may i assist",
    "is there anything else i can help",
    "anything else i can assist",
    "i'd be happy to help you",
    "i would be happy to help you",
    "i'm happy to assist",
    "i am happy to assist",
    "i'm here to help you",
    "i am here to help you",
    "let me know how i can help",
    "what can i do for you",
    "how can i be of assistance",
)

#: Advisory voice — the help-seeker dispensing guidance.
_ADVISORY_MARKERS: tuple[str, ...] = (
    "i recommend",
    "i'd recommend",
    "i would recommend",
    "my recommendation is",
    "i suggest",
    "i'd suggest",
    "i would suggest",
    "here's what you",
    "here is what you",
    "here are the steps",
    "you'll want to",
    "you will want to",
    "you may want to",
    "you might want to",
    "you should consider",
    "let me walk you through",
    "the next step is to",
    "i can help you with",
    "i'd be glad to help",
)

#: Explicit refusal / evasion — drift only for an ``open`` persona.
_DEFLECTION_MARKERS: tuple[str, ...] = (
    "i'd rather not",
    "i would rather not",
    "i prefer not to",
    "i'd prefer not to",
    "that's private",
    "that is private",
    "i can't share that",
    "i cannot share that",
    "i don't want to discuss",
    "no comment",
    "why do you need to know",
    "i'm not comfortable sharing",
    "that's personal",
)

_FIRST_PERSON = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours"}
_SECOND_PERSON = {"you", "your", "yours", "yourself"}

_STOPWORDS = {
    "the", "and", "for", "was", "were", "has", "have", "had", "not", "but",
    "with", "that", "this", "they", "them", "their", "there", "then", "than",
    "from", "into", "onto", "out", "about", "would", "could", "should", "will",
    "shall", "can", "may", "might", "must", "are", "been", "being", "its",
    "his", "her", "him", "she", "you", "your", "yours", "our", "ours", "who",
    "whom", "which", "what", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "only",
    "own", "same", "too", "very", "just", "get", "got", "one", "two",
    "because", "before", "after", "while", "during", "until", "unless",
    "still", "also", "here", "does", "did", "done", "doing", "say", "says",
    "said", "like", "want", "need", "make", "made", "take", "took", "come",
    "came", "know", "knew", "think", "thought",
}

#: Built-in probe questions for ``probe_mode="active"``. Deliberately
#: persona-agnostic — a probe that restated ``archetype.description`` would
#: re-prime the model's attention on the persona and erase the drift it is
#: supposed to expose. Cycled deterministically by probe ordinal.
AUTO_PROBES: tuple[str, ...] = (
    "Before we go on — in your own words, who are you and what brought you "
    "here today?",
    "Quick aside: is there anything on your mind that you have not mentioned "
    "yet?",
    "How are you feeling about this conversation so far?",
    "If you were describing your situation to a friend right now, what would "
    "you say?",
)


# ── text helpers ────────────────────────────────────────────────────────────

_WORD_RE = re.compile(r"[a-z0-9]+")
_APOSTROPHES = str.maketrans({"’": "'", "ʼ": "'", "`": "'"})
_MARKDOWN_LINE_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|#{1,6}\s+)")


def _normalise(text: str) -> str:
    """Lowercase, unify apostrophes, collapse whitespace — for marker matching."""
    return re.sub(r"\s+", " ", text.translate(_APOSTROPHES).lower()).strip()


def _pronoun_counts(text: str) -> tuple[int, int]:
    """``(first_person, second_person)`` pronoun counts in ``text``."""
    words = _WORD_RE.findall(_normalise(text))
    first = sum(1 for w in words if w in _FIRST_PERSON)
    second = sum(1 for w in words if w in _SECOND_PERSON)
    return first, second


def _content_tokens(text: str) -> set[str]:
    """Distinctive content tokens: lowercase, >= 3 chars, de-pluralised, no stopwords."""
    out: set[str] = set()
    for w in _WORD_RE.findall(_normalise(text)):
        if len(w) < 3 or w in _STOPWORDS:
            continue
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.add(w)
    return out


def _fact_core(fact: str) -> str:
    """Strip the authoring-guidance clause from a hidden fact.

    The SDK's authoring guide recommends framing hidden facts with an explicit
    consequence clause after an em-dash — ``"visitor visa refused in 2024 —
    reluctant to disclose unless asked directly"``. Only the text before that
    separator is the *fact*; the rest is instruction to the simulator and must
    not dilute the leakage-coverage denominator.
    """
    for sep in ("—", "–", " -- ", " - ", ";"):
        if sep in fact:
            return fact.split(sep, 1)[0]
    return fact


def _matched_markers(text_norm: str, markers: Iterable[str]) -> list[str]:
    return [m for m in markers if m in text_norm]


def _is_question(text: str) -> bool:
    """Did this counterparty turn ask something?

    Deterministic proxy for "the agent asked a question that would naturally
    elicit the fact". A literal ``?`` covers the overwhelming majority; the
    imperative-elicit phrases cover the common question-shaped commands.
    """
    if "?" in text:
        return True
    norm = _normalise(text)
    return any(
        p in norm
        for p in (
            "tell me about",
            "tell me more",
            "walk me through",
            "describe your",
            "let me know what",
            "let me know if you",
        )
    )


def _is_markdown_formatted(text: str) -> bool:
    """>= 2 markdown structure markers across >= 2 lines."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    structural = sum(1 for ln in lines if _MARKDOWN_LINE_RE.match(ln))
    bold = text.count("**") // 2
    return (structural + bold) >= 2 and len(lines) >= 2


# ── transcript normalisation ────────────────────────────────────────────────


@dataclass(frozen=True)
class _Utterance:
    """One normalised transcript entry."""

    index: int
    is_persona: bool
    content: str
    is_probe: bool = False
    probe_question: str | None = None


#: Role aliases treated as "the persona-playing side", most specific first.
#: ``user`` is last: in an Anthropic-shaped log of a simulated customer the
#: customer is the ``user`` role, but any of the explicit names wins over it.
_PERSONA_ROLE_PRIORITY: tuple[str, ...] = (
    "simulator",
    "persona",
    "customer",
    "applicant",
    "patient",
    "user",
)


def _entry_fields(entry: Any) -> tuple[str | None, str, dict[str, Any]]:
    """Pull ``(role, content, metadata)`` out of one transcript entry.

    Accepts: :class:`~libraos.simulator.Turn`, any object exposing
    ``.role``/``.content``, a mapping with ``role``/``content`` (or ``text`` /
    ``message`` / ``utterance``), a ``(role, content)`` pair, or a bare string.
    """
    if isinstance(entry, str):
        return None, entry, {}
    if isinstance(entry, dict):
        role = entry.get("role") or entry.get("speaker") or entry.get("author")
        content = (
            entry.get("content")
            if entry.get("content") is not None
            else entry.get("text")
            if entry.get("text") is not None
            else entry.get("message")
            if entry.get("message") is not None
            else entry.get("utterance")
        )
        meta = entry.get("metadata") or {}
        return (
            str(role) if role is not None else None,
            _flatten_content(content),
            meta if isinstance(meta, dict) else {},
        )
    if isinstance(entry, (tuple, list)) and len(entry) == 2:
        return str(entry[0]), _flatten_content(entry[1]), {}
    role = getattr(entry, "role", None)
    content = getattr(entry, "content", None)
    if content is None:
        content = getattr(entry, "text", None)
    meta = getattr(entry, "metadata", None)
    return (
        str(role) if role is not None else None,
        _flatten_content(content),
        meta if isinstance(meta, dict) else {},
    )


def _flatten_content(content: Any) -> str:
    """Coerce a content value to text, including Anthropic block lists."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and isinstance(block.get("text"), str):
                    parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


def _normalise_transcript(
    transcript: Any, persona_role: str | None
) -> tuple[list[_Utterance], str]:
    """Coerce any transcript shape to ``(utterances, resolved_persona_role)``.

    Raises :class:`ValueError` when the persona side cannot be identified —
    silently scoring the wrong speaker would be worse than a loud failure.
    """
    # SimulationResult (or anything else carrying .transcript), and the
    # equivalent envelope shape ``{"transcript": [...]}`` that stored eval
    # artefacts tend to use.
    if isinstance(transcript, dict) and "transcript" in transcript:
        transcript = transcript["transcript"]
    else:
        inner = getattr(transcript, "transcript", None)
        if inner is not None and not isinstance(transcript, (list, tuple)):
            transcript = inner

    if transcript is None:
        return [], persona_role or "simulator"
    if isinstance(transcript, (str, bytes)):
        raise ValueError(
            "measure_drift: transcript must be a sequence of turns, not a string"
        )
    if not isinstance(transcript, Sequence):
        transcript = list(transcript)

    parsed = [_entry_fields(e) for e in transcript]
    roles = {r.strip().lower() for r, _, _ in parsed if r}

    if persona_role is not None:
        resolved = persona_role.strip().lower()
        if roles and resolved not in roles:
            raise ValueError(
                f"measure_drift: persona_role={persona_role!r} not present in "
                f"transcript roles {sorted(roles)}"
            )
    elif not roles:
        # No roles at all (bare strings) — assume strict alternation starting
        # with the persona, which is the shape ``simulate()`` produces.
        resolved = "simulator"
    else:
        resolved = next((a for a in _PERSONA_ROLE_PRIORITY if a in roles), "")
        if not resolved:
            raise ValueError(
                "measure_drift: could not identify the persona-playing side "
                f"from transcript roles {sorted(roles)}; pass persona_role= "
                "explicitly (e.g. persona_role='client')"
            )

    utterances: list[_Utterance] = []
    for i, (role, content, meta) in enumerate(parsed):
        if role is None:
            is_persona = (i % 2) == 0  # alternation fallback, persona first
        else:
            is_persona = role.strip().lower() == resolved
        utterances.append(
            _Utterance(
                index=i,
                is_persona=is_persona,
                content=content or "",
                is_probe=bool(meta.get("drift_probe")),
                probe_question=meta.get("drift_probe_question"),
            )
        )
    return utterances, resolved


def _normalise_archetype(archetype: Any) -> Archetype:
    if isinstance(archetype, Archetype):
        return archetype
    if isinstance(archetype, dict):
        return Archetype.from_dict(archetype)
    if isinstance(archetype, (str, Path)):
        return Archetype.from_yaml_path(archetype)
    raise ValueError(
        "measure_drift: archetype must be Archetype | dict | str | Path, got "
        f"{type(archetype).__name__}"
    )


# ── per-turn scoring ────────────────────────────────────────────────────────


def _score_character_break(text_norm: str) -> tuple[float, list[str]]:
    meta = _matched_markers(text_norm, _META_AI_MARKERS)
    if meta:
        return 1.0, [f"meta-ai marker: {m!r}" for m in meta[:3]]
    offers = _matched_markers(text_norm, _SERVICE_OFFER_MARKERS)
    if offers:
        return 0.8, [f"assistant-service marker: {m!r}" for m in offers[:3]]
    return 0.0, []


def _score_advisory_inversion(text: str, text_norm: str) -> tuple[float, list[str]]:
    markers = _matched_markers(text_norm, _ADVISORY_MARKERS)
    if not markers:
        return 0.0, []
    first, second = _pronoun_counts(text)
    evidence = [f"advisory marker: {m!r}" for m in markers[:3]]
    # Second-person dominance is the gate that separates "the persona is now
    # advising the agent" from "the customer said 'I suggest we start with the
    # permit'". Two second-person pronouns, or any at all in a turn with no
    # first-person voice left, is enough.
    if second > first and (second >= 2 or first == 0):
        evidence.append(f"second-person dominant ({second} vs {first})")
        return 1.0, evidence
    return 0.35, evidence


def _disclosed_facts(text: str, hidden_facts: Sequence[str]) -> list[str]:
    """Hidden facts this utterance appears to disclose (lexical coverage)."""
    tokens = _content_tokens(text)
    if not tokens:
        return []
    out: list[str] = []
    for fact in hidden_facts:
        core = _content_tokens(_fact_core(fact))
        if len(core) < 2:
            # Too few distinctive words to judge — refusing to guess is
            # deliberate: a one-word "fact" would false-positive constantly.
            continue
        matched = len(core & tokens)
        if matched >= 2 and (matched / len(core)) >= 0.6:
            out.append(fact)
    return out


def _score_disposition(
    text: str,
    text_norm: str,
    archetype: Archetype,
    *,
    prompted: bool,
    trust_established: bool,
) -> tuple[float, list[str]]:
    willingness = archetype.disclosure_willingness
    leaked = _disclosed_facts(text, archetype.hidden_facts)

    if willingness == "open":
        if leaked:
            return 0.0, []
        deflections = _matched_markers(text_norm, _DEFLECTION_MARKERS)
        if deflections:
            return 0.7, [
                "open persona deflecting: " + repr(deflections[0])
            ]
        return 0.0, []

    if not leaked:
        return 0.0, []

    excerpt = leaked[0][:80]
    if willingness == "cautious":
        if prompted:
            return 0.0, []
        return 1.0, [f"cautious persona volunteered hidden fact: {excerpt!r}"]

    # guarded
    if prompted and trust_established:
        return 0.0, []
    reason = (
        "guarded persona disclosed hidden fact "
        + ("without being asked" if not prompted else "before trust was established")
        + f": {excerpt!r}"
    )
    return 1.0, [reason]


def _noisy_or(components: dict[str, float]) -> float:
    retained = 1.0
    for name, strength in components.items():
        retained *= 1.0 - (_WEIGHTS[name] * strength)
    return round(max(0.0, min(1.0, 1.0 - retained)), 6)


def _score_utterance(
    utt: _Utterance,
    archetype: Archetype,
    *,
    prompted: bool,
    trust_established: bool,
) -> tuple[float, dict[str, float], list[str]]:
    text = utt.content
    text_norm = _normalise(text)
    evidence: list[str] = []

    cb, ev = _score_character_break(text_norm)
    evidence += ev
    dv, ev = _score_disposition(
        text,
        text_norm,
        archetype,
        prompted=prompted,
        trust_established=trust_established,
    )
    evidence += ev
    ai, ev = _score_advisory_inversion(text, text_norm)
    evidence += ev
    fb = 1.0 if _is_markdown_formatted(text) else 0.0
    if fb:
        evidence.append("markdown formatting in a persona turn")

    components = {
        "character_break": cb,
        "disposition_violation": dv,
        "advisory_inversion": ai,
        "format_break": fb,
    }
    ordered = {k: components[k] for k in _COMPONENT_ORDER}
    return _noisy_or(ordered), ordered, evidence


# ── probe-point selection ───────────────────────────────────────────────────


def _probe_points(
    persona_positions: Sequence[int],
    *,
    probe_every: int,
    include_last: bool,
) -> list[int]:
    """Indices *into ``persona_positions``* that should be scored.

    ``{i >= 1 : i % probe_every == 0}``, plus the final persona turn when
    ``include_last`` — the last turn is the most-drifted point and the one a
    partner most wants scored.

    ``include_last=False`` is used for mid-loop alerting so that the alert
    points are always a strict subset of the final probe points; otherwise
    "latest turn so far" would make every turn a probe point mid-run and a
    stream could alert on a turn the final metric never scored.
    """
    n = len(persona_positions)
    if n < 2:
        return []
    points = {i for i in range(1, n) if i % probe_every == 0}
    if include_last:
        points.add(n - 1)
    return sorted(points)


# ── public API ──────────────────────────────────────────────────────────────


def measure_drift(
    transcript: Any,
    archetype: Any,
    *,
    method: str = DEFAULT_DRIFT_METHOD,
    threshold: float | None = None,
    probe_every: int = DEFAULT_PROBE_EVERY,
    persona_role: str | None = None,
) -> DriftMetric:
    """Score persona drift over a transcript. Deterministic; no model call.

    Parameters
    ----------
    transcript:
        Any transcript shape. Accepted: a :class:`~libraos.simulator.SimulationResult`
        (its ``.transcript`` is used), a list of
        :class:`~libraos.simulator.Turn`, a list of ``{"role": ..., "content": ...}``
        dicts (``content`` may be an Anthropic block list), a list of
        ``(role, content)`` pairs, a list of objects exposing ``.role`` /
        ``.content``, or a bare list of strings (assumed to alternate,
        persona first).
    archetype:
        :class:`~libraos.simulator.Archetype`, a dict matching the archetype
        schema, or a path to archetype YAML. Supplies ``hidden_facts`` and
        ``disclosure_willingness`` — the disposition the persona is scored
        against — and, when set, the default ``drift_alert_threshold``.
    method:
        Scoring method identifier; see :data:`DRIFT_METHODS`.
    threshold:
        Alert threshold. Precedence: this argument →
        ``archetype.drift_alert_threshold`` → :data:`DEFAULT_DRIFT_THRESHOLD`
        (0.15).
    probe_every:
        Score the persona at least every N of its own turns. Default 2.
    persona_role:
        Which role string identifies the persona-playing side. When ``None``
        the first of ``simulator`` / ``persona`` / ``customer`` / ``applicant``
        / ``patient`` / ``user`` present in the transcript wins; if none of
        those appear the call raises rather than guessing.

        **One ambiguity auto-detection cannot resolve.** In a bare
        ``user``/``assistant`` log, ``user`` is assumed to be the persona —
        correct for a log recorded from the target agent's point of view, wrong
        for one recorded from the persona-playing model's own point of view
        (where the persona is the ``assistant``). There is no way to tell the
        two apart from the data. Pass ``persona_role="assistant"`` for the
        latter, and check ``result.notes["persona_role"]`` to confirm which
        side was scored.

    Returns
    -------
    DriftMetric
        ``score`` is ``0.0`` for perfect retention and ``1.0`` for complete
        drift. A transcript with fewer than two non-empty persona turns yields
        ``score=0.0`` with an empty ``per_turn`` and
        ``notes["reason"] == "insufficient_persona_turns"`` — read
        ``per_turn`` (or that note) before treating a ``0.0`` as measured.

    Raises
    ------
    ValueError
        Unknown ``method``, ``probe_every < 1``, an unusable ``transcript``
        shape, or an unidentifiable persona role.
    ArchetypeValidationError
        The supplied ``archetype`` dict / YAML failed schema validation.
    """
    if method not in DRIFT_METHODS:
        raise ValueError(
            f"measure_drift: unknown method {method!r}; supported: {list(DRIFT_METHODS)}"
        )
    if probe_every < 1:
        raise ValueError(f"measure_drift: probe_every must be >= 1, got {probe_every}")

    arche = _normalise_archetype(archetype)
    effective_threshold = _resolve_threshold(threshold, arche)
    utterances, resolved_role = _normalise_transcript(transcript, persona_role)

    return _measure(
        utterances,
        arche,
        method=method,
        threshold=effective_threshold,
        probe_every=probe_every,
        include_last=True,
        persona_role=resolved_role,
    )


def resolve_threshold(threshold: float | None, archetype: Archetype) -> float:
    """Public alias of the threshold precedence rule — see :func:`measure_drift`."""
    return _resolve_threshold(threshold, archetype)


def _resolve_threshold(threshold: float | None, archetype: Archetype) -> float:
    if threshold is not None:
        return float(threshold)
    arche_threshold = getattr(archetype, "drift_alert_threshold", None)
    if arche_threshold is not None:
        return float(arche_threshold)
    return DEFAULT_DRIFT_THRESHOLD


def _measure(
    utterances: Sequence[_Utterance],
    archetype: Archetype,
    *,
    method: str,
    threshold: float,
    probe_every: int,
    include_last: bool,
    persona_role: str,
) -> DriftMetric:
    """Core scorer over already-normalised utterances.

    Shared by :func:`measure_drift` (``include_last=True``) and the mid-loop
    alerting path in ``_loop.py`` (``include_last=False``).
    """
    probe_mode: ProbeMode = "active" if any(u.is_probe for u in utterances) else "passive"

    persona = [u for u in utterances if u.is_persona and u.content.strip()]
    if probe_mode == "active":
        baseline_pool = [u for u in persona if not u.is_probe]
        probe_utts = [u for u in persona if u.is_probe]
        baseline = baseline_pool[0] if baseline_pool else None
        scored = probe_utts
    else:
        baseline = persona[0] if persona else None
        positions = [u.index for u in persona]
        picks = _probe_points(
            positions, probe_every=probe_every, include_last=include_last
        )
        scored = [persona[i] for i in picks]

    base_notes: dict[str, Any] = {
        "persona_role": persona_role,
        "persona_turns": len(persona),
        "transcript_turns": len(utterances),
    }

    if baseline is None or not scored:
        return DriftMetric(
            score=0.0,
            threshold=threshold,
            alert_triggered=False,
            method=method,
            per_turn=[],
            baseline_turn_index=baseline.index if baseline else None,
            first_drift_turn_index=None,
            probe_every=probe_every,
            probe_mode=probe_mode,
            notes={**base_notes, "reason": "insufficient_persona_turns"},
        )

    # Counterparty context, precomputed once: for each transcript index, was the
    # nearest preceding counterparty turn a question, and how many questions had
    # the counterparty asked by then?
    prev_question: dict[int, bool] = {}
    questions_before: dict[int, int] = {}
    last_was_question = False
    q_count = 0
    for u in utterances:
        prev_question[u.index] = last_was_question
        questions_before[u.index] = q_count
        if not u.is_persona and u.content.strip():
            asked = _is_question(u.content)
            last_was_question = asked
            if asked:
                q_count += 1

    persona_ordinal = {u.index: i for i, u in enumerate(persona)}

    per_turn: list[DriftTurn] = []
    leaked_all: list[str] = []
    for probe_index, utt in enumerate(scored):
        # An active probe answer is by construction prompted — it answers a
        # direct question. A passive turn is prompted only when the preceding
        # counterparty turn actually asked something.
        prompted = utt.is_probe or prev_question.get(utt.index, False)
        trust = questions_before.get(utt.index, 0) >= 2
        score, components, evidence = _score_utterance(
            utt, archetype, prompted=prompted, trust_established=trust
        )
        if components["disposition_violation"] > 0:
            leaked_all.extend(_disclosed_facts(utt.content, archetype.hidden_facts))
        per_turn.append(
            DriftTurn(
                turn_index=utt.index,
                probe_index=probe_index,
                persona_turn_index=persona_ordinal.get(utt.index, probe_index),
                score=score,
                components=components,
                probe_question=utt.probe_question,
                excerpt=utt.content[:200],
                evidence=evidence,
            )
        )

    scores = [t.score for t in per_turn]
    aggregate = round(0.5 * max(scores) + 0.5 * (sum(scores) / len(scores)), 6)
    first_drift = next((t.turn_index for t in per_turn if t.score > threshold), None)

    return DriftMetric(
        score=aggregate,
        threshold=threshold,
        alert_triggered=aggregate > threshold,
        method=method,
        per_turn=per_turn,
        baseline_turn_index=baseline.index,
        first_drift_turn_index=first_drift,
        probe_every=probe_every,
        probe_mode=probe_mode,
        notes={
            **base_notes,
            "probe_points": [t.turn_index for t in per_turn],
            "leaked_hidden_facts": sorted(set(leaked_all)),
        },
    )


def measure_running(
    transcript: Any,
    archetype: Archetype,
    *,
    method: str,
    threshold: float,
    probe_every: int,
) -> DriftMetric:
    """Mid-run drift over a transcript prefix — used by the streaming loop.

    Identical to :func:`measure_drift` except that the "always score the final
    persona turn" rule is switched off. During a live run every turn is
    momentarily the last one, so including it would make every turn a probe
    point and let a stream alert on a turn the final metric never scores. With
    it off, the mid-run probe points are a strict subset of the final ones.
    """
    utterances, resolved_role = _normalise_transcript(transcript, "simulator")
    return _measure(
        utterances,
        archetype,
        method=method,
        threshold=threshold,
        probe_every=probe_every,
        include_last=False,
        persona_role=resolved_role,
    )


def resolve_probes(
    archetype: Archetype, probes: Sequence[str] | None = None
) -> tuple[str, ...]:
    """Probe questions for active mode: explicit → archetype → built-in.

    See :data:`AUTO_PROBES` for why the built-ins are persona-agnostic rather
    than generated from ``archetype.description``.
    """
    if probes:
        return tuple(probes)
    declared = getattr(archetype, "drift_probes", None)
    if declared:
        return tuple(declared)
    return AUTO_PROBES


__all__ = [
    "measure_drift",
    "measure_running",
    "resolve_probes",
    "resolve_threshold",
    "DRIFT_METHODS",
    "DEFAULT_DRIFT_METHOD",
    "AUTO_PROBES",
]
