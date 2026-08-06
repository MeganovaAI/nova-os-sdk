"""Tests for the persona-drift metric — #29.

Everything here runs offline: the scorer is a pure function, and the two
loop-integration tests drive the same ``httpx.MockTransport`` harness the rest
of the simulator suite uses. No live server, no model call.

Covers:

- Fixture calibration — the acceptance gates from #29: an explicitly broken
  persona scores > 0.5, a consistent one scores < 0.1.
- The structural property that makes the aggregate trustworthy: any single
  complete character break scores >= 0.5 no matter how long the run is.
- Disposition scoring across all three ``disclosure_willingness`` values,
  including the direction-sensitivity that a naive "leakage = drift" scorer
  would get wrong.
- Transcript-shape tolerance for the standalone API (dicts, pairs, bare
  strings, Anthropic content blocks, a stored ``SimulationResult``).
- ``SimulationResult.drift`` populated by ``simulate()``; ``drift_alert``
  emitted mid-stream; both suppressible.
- Active probe injection: the probe never reaches the target agent.
- Backward compatibility of the frozen v1.0.0 surface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import httpx
import pytest

from libraos import Archetype, Client, DriftMetric, DriftOptions, measure_drift
from libraos.simulator import SimulationResult, Turn
from libraos.simulator._wiring import HARNESS_AGENT_ID, _reset_cache_for_tests

FIXTURES = Path(__file__).resolve().parent / "simulator" / "fixtures"


# --------------------------------------------------------------- fixtures


def _load_transcript(name: str) -> tuple[list[dict[str, Any]], Archetype]:
    """Load a transcript fixture + the archetype it names."""
    raw = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    archetype = Archetype.from_yaml_path(FIXTURES / raw["archetype"])
    return raw["transcript"], archetype


@pytest.fixture(autouse=True)
def _reset_caches():
    _reset_cache_for_tests()
    yield
    _reset_cache_for_tests()


# ============================================================================
# 1. Acceptance calibration — the two gates named in #29
# ============================================================================


def test_consistent_persona_scores_below_point_one() -> None:
    """A persona held for 12 turns must score < 0.1 (#29 acceptance)."""
    transcript, archetype = _load_transcript("drift_transcript_consistent.json")
    m = measure_drift(transcript, archetype)
    assert m.measured, "fixture is long enough to score; per_turn must be non-empty"
    assert m.score < 0.1, f"false positive on a clean persona: {m.per_turn}"
    assert m.alert_triggered is False
    assert m.first_drift_turn_index is None


def test_consistent_persona_prompted_disclosure_is_not_drift() -> None:
    """The clean fixture DOES disclose both hidden facts — in direct answer to
    the agent's questions. A ``cautious`` persona doing exactly what the
    archetype says must not score as drift; a scorer that flags any leakage
    would fail here, and would be useless on every well-run simulation."""
    transcript, archetype = _load_transcript("drift_transcript_consistent.json")
    text = " ".join(t["content"] for t in transcript if t["role"] == "simulator")
    assert "visitor visa refused in 2024" in text  # the fact IS disclosed
    m = measure_drift(transcript, archetype)
    assert m.notes["leaked_hidden_facts"] == []
    assert all(t.components["disposition_violation"] == 0.0 for t in m.per_turn)


def test_broken_persona_scores_above_point_five() -> None:
    """An explicitly broken persona must score > 0.5 (#29 acceptance)."""
    transcript, archetype = _load_transcript("drift_transcript_broken.json")
    m = measure_drift(transcript, archetype)
    assert m.score > 0.5, f"under-detected an obvious break: {m.per_turn}"
    assert m.alert_triggered is True
    assert m.first_drift_turn_index is not None
    kinds = {k for t in m.per_turn for k, v in t.components.items() if v > 0}
    assert "character_break" in kinds
    assert "advisory_inversion" in kinds
    assert "format_break" in kinds


def test_volunteered_disclosure_scores_above_point_five() -> None:
    """Register-preserving drift: the persona still *sounds* like a customer
    but abandons its cautious disposition and volunteers both hidden facts."""
    transcript, archetype = _load_transcript("drift_transcript_volunteered.json")
    m = measure_drift(transcript, archetype)
    assert m.score > 0.5
    assert m.alert_triggered is True
    assert m.notes["leaked_hidden_facts"]
    # No character break at all — this is why disposition is its own signal.
    assert all(t.components["character_break"] == 0.0 for t in m.per_turn)


def test_cadence_sampling_skips_turns_and_probe_every_one_catches_them() -> None:
    """A documented consequence of probe cadence: at the default
    ``probe_every=2`` only half the persona's turns are scored, so a leak on an
    unscored turn is missed. ``probe_every=1`` scores every turn — more
    sensitive, and correspondingly more exposed to lexical false positives."""
    transcript, archetype = _load_transcript("drift_transcript_volunteered.json")
    sampled = measure_drift(transcript, archetype)
    every = measure_drift(transcript, archetype, probe_every=1)
    assert len(every.per_turn) > len(sampled.per_turn)
    assert len(every.notes["leaked_hidden_facts"]) == 2
    assert len(sampled.notes["leaked_hidden_facts"]) == 1


# ============================================================================
# 2. Structural properties of the aggregate
# ============================================================================


def _archetype(**overrides: Any) -> Archetype:
    base: dict[str, Any] = {
        "name": "drift-unit-archetype",
        "description": "Unit-test archetype.",
        "hidden_facts": ["owes eleven thousand dollars to a former landlord"],
        "disclosure_willingness": "cautious",
        "success_signal": "matched",
    }
    base.update(overrides)
    return Archetype.from_dict(base)


def _pairs(persona_turns: list[str], agent_turn: str = "Understood.") -> list[Any]:
    out: list[Any] = []
    for t in persona_turns:
        out.append({"role": "simulator", "content": t})
        out.append({"role": "target", "content": agent_turn})
    return out


def test_single_character_break_always_scores_at_least_half() -> None:
    """The severity term is the whole point: one total break in a 40-turn run
    must still land >= 0.5. Under a plain mean it would average to ~0.05 and
    never alert — precisely the 'success on turn 8 of a drifted run' failure
    #29 exists to catch."""
    clean = ["My permit expires soon and I need advice."] * 19
    transcript = _pairs(clean + ["As an AI language model, I don't have personal experiences."])
    m = measure_drift(transcript, _archetype())
    assert len(m.per_turn) >= 10, "long run must produce many probe points"
    assert m.score >= 0.5
    assert m.alert_triggered is True


def test_score_is_monotone_in_the_number_of_broken_turns() -> None:
    """More drifted turns must never score lower than fewer."""
    clean = "My permit expires soon and I need advice."
    broken = "As an AI language model, I cannot have a permit."
    scores = []
    for n_broken in range(0, 5):
        turns = [clean] * (8 - n_broken) + [broken] * n_broken
        scores.append(measure_drift(_pairs(turns), _archetype()).score)
    assert scores == sorted(scores), scores
    assert scores[0] == 0.0


def test_score_bounds_and_determinism() -> None:
    transcript, archetype = _load_transcript("drift_transcript_broken.json")
    first = measure_drift(transcript, archetype)
    second = measure_drift(transcript, archetype)
    assert first.score == second.score
    assert [t.score for t in first.per_turn] == [t.score for t in second.per_turn]
    assert 0.0 <= first.score <= 1.0


def test_components_shape_is_stable_for_csv_output() -> None:
    transcript, archetype = _load_transcript("drift_transcript_broken.json")
    m = measure_drift(transcript, archetype)
    expected = [
        "character_break",
        "disposition_violation",
        "advisory_inversion",
        "format_break",
    ]
    for t in m.per_turn:
        assert list(t.components) == expected


#: In-character customer utterances chosen adversarially against the marker
#: sets — every one of these looks superficially like assistant language.
#: A run made entirely of these must never alert. Two of them do carry weak
#: signal by design (a bulleted list; "I suggest we start…"); the weights are
#: set so weak signal alone cannot cross the default threshold.
_ADVERSARIAL_IN_CHARACTER = [
    "Can you help me with this? I really need someone who knows the process.",
    "You should have my file already, I sent it last Tuesday.",
    "Let me know if you need anything else from me.",
    "I'll make sure to bring the documents. Do you need originals?",
    "Here are the documents I have:\n- passport\n- lease\n- pay stubs",
    "Thanks for your help! Is there anything else you need from me?",
    "Honestly I'm not sure. What would you recommend?",
    "I suggest we start with the permit since that's the urgent one.",
    "That's private, I'd prefer to talk about it with the lawyer directly.",
    "I am an assistant manager at a retail store, so my hours are irregular.",
    "The simulation results from the online calculator said I qualify.",
    "My instructions say to submit everything by Friday.",
    "I was instructed to bring two copies of each form.",
]

_UNAMBIGUOUS_BREAKS = [
    "As an AI language model, I don't have personal experiences.",
    "How can I help you today?",
    "Is there anything else I can help you with?",
    "Here's what you'll want to do next:\n\n1. **File the form**\n2. **Pay the fee**",
    "I'd recommend you contact IRCC directly. You may want to check the portal.",
    "I'm here to help you with your immigration questions.",
]


def test_adversarial_in_character_corpus_never_alerts() -> None:
    """The expensive failure for this metric is the false positive: an alert
    nobody believes is worse than no alert. Each of these is ordinary customer
    speech that superficially resembles assistant output."""
    m = measure_drift(_pairs(_ADVERSARIAL_IN_CHARACTER), _archetype())
    assert m.alert_triggered is False, [
        (t.excerpt, t.evidence) for t in m.per_turn if t.score > 0
    ]
    assert m.score < 0.15
    for utterance in _ADVERSARIAL_IN_CHARACTER:
        single = measure_drift(_pairs(["I need help.", utterance]), _archetype())
        assert single.per_turn[0].score < 0.25, (utterance, single.per_turn[0].evidence)


def test_unambiguous_breaks_all_alert_individually() -> None:
    """The other side of the same calibration: each break, alone, in an
    otherwise clean two-turn run, must cross the default threshold."""
    for utterance in _UNAMBIGUOUS_BREAKS:
        m = measure_drift(_pairs(["I need help with my permit.", utterance]), _archetype())
        assert m.alert_triggered is True, utterance
        assert m.per_turn[0].score >= 0.6, (utterance, m.per_turn[0].components)


def test_separation_margin_between_the_two_corpora() -> None:
    """The worst in-character turn must score well below the best-behaved
    break — if these ever meet, the threshold has no safe setting."""
    worst_clean = max(
        measure_drift(_pairs(["I need help.", u]), _archetype()).per_turn[0].score
        for u in _ADVERSARIAL_IN_CHARACTER
    )
    best_break = min(
        measure_drift(_pairs(["I need help.", u]), _archetype()).per_turn[0].score
        for u in _UNAMBIGUOUS_BREAKS
    )
    assert worst_clean < best_break, (worst_clean, best_break)
    assert best_break - worst_clean > 0.3


# ============================================================================
# 3. Probe-point selection
# ============================================================================


def test_probe_cadence_default_two_plus_final_turn() -> None:
    """Probe points are {i>=1 : i % N == 0} ∪ {last persona turn}."""
    transcript = _pairs([f"turn {i}" for i in range(6)])
    m = measure_drift(transcript, _archetype())
    # persona turns sit at transcript indices 0,2,4,6,8,10 → persona ordinals
    # 2 and 4 by cadence, plus ordinal 5 as the final turn.
    assert [t.persona_turn_index for t in m.per_turn] == [2, 4, 5]
    assert [t.turn_index for t in m.per_turn] == [4, 8, 10]
    assert m.baseline_turn_index == 0


def test_probe_every_is_configurable() -> None:
    transcript = _pairs([f"turn {i}" for i in range(8)])
    m = measure_drift(transcript, _archetype(), probe_every=3)
    assert [t.persona_turn_index for t in m.per_turn] == [3, 6, 7]


def test_four_turn_transcript_is_measurable() -> None:
    """#29 requires drift for runs of >= 4 turns; two persona utterances is the
    minimum that admits a baseline plus one probe."""
    transcript = _pairs(["I need help with my file.", "It expires in April."])
    m = measure_drift(transcript, _archetype())
    assert len(transcript) == 4
    assert m.measured is True
    assert len(m.per_turn) == 1


def test_too_short_transcript_is_reported_as_unmeasured_not_as_zero_drift() -> None:
    """A 2-turn transcript cannot be measured. It still returns a DriftMetric —
    but ``measured`` is False so a corpus average can exclude it rather than
    silently absorbing a fake 0.0."""
    m = measure_drift(_pairs(["only one persona turn"]), _archetype())
    assert m.measured is False
    assert m.per_turn == []
    assert m.score == 0.0
    assert m.notes["reason"] == "insufficient_persona_turns"


def test_empty_transcript_is_unmeasured() -> None:
    m = measure_drift([], _archetype())
    assert m.measured is False
    assert m.baseline_turn_index is None


def test_error_placeholder_turns_are_skipped() -> None:
    """Transport-error turns carry empty content; they must not be scored or
    become the baseline."""
    transcript = [
        {"role": "simulator", "content": "", "metadata": {"error": True}},
        {"role": "simulator", "content": "Real opening message about my permit."},
        {"role": "target", "content": "When does it expire?"},
        {"role": "simulator", "content": "April, I think."},
    ]
    m = measure_drift(transcript, _archetype())
    assert m.baseline_turn_index == 1
    assert m.measured is True


# ============================================================================
# 4. Disposition scoring — all three willingness values, both directions
# ============================================================================


def _disclosure_case(willingness: str, agent_turn: str) -> DriftMetric:
    archetype = _archetype(
        disclosure_willingness=willingness,
        hidden_facts=["owes eleven thousand dollars to a former landlord"],
    )
    transcript = [
        {"role": "simulator", "content": "I need help with a housing letter."},
        {"role": "target", "content": agent_turn},
        {"role": "simulator", "content": "I owe eleven thousand dollars to a former landlord."},
    ]
    return measure_drift(transcript, archetype)


def test_cautious_volunteering_is_drift_but_answering_is_not() -> None:
    volunteered = _disclosure_case("cautious", "Thanks, I'll take a look.")
    answered = _disclosure_case("cautious", "Do you have any outstanding debts?")
    assert volunteered.per_turn[0].components["disposition_violation"] == 1.0
    assert answered.per_turn[0].components["disposition_violation"] == 0.0


def test_guarded_disclosure_needs_prompting_and_established_trust() -> None:
    """`guarded` means 'deflects until trust is established'. One question is
    not enough; sustained questioning is."""
    early = _disclosure_case("guarded", "Do you have any outstanding debts?")
    assert early.per_turn[0].components["disposition_violation"] == 1.0

    archetype = _archetype(disclosure_willingness="guarded")
    late = measure_drift(
        [
            {"role": "simulator", "content": "I need help with a housing letter."},
            {"role": "target", "content": "What kind of letter?"},
            {"role": "simulator", "content": "Something for a new landlord."},
            {"role": "target", "content": "Any outstanding debts on your record?"},
            {"role": "simulator", "content": "Yes. I owe eleven thousand dollars to a former landlord."},
        ],
        archetype,
    )
    assert late.per_turn[-1].components["disposition_violation"] == 0.0


def test_open_persona_disclosure_is_never_drift() -> None:
    for agent_turn in ("Thanks, I'll take a look.", "Any outstanding debts?"):
        m = _disclosure_case("open", agent_turn)
        assert m.per_turn[0].components["disposition_violation"] == 0.0


def test_open_persona_evasion_is_drift_but_guarded_evasion_is_not() -> None:
    """Direction sensitivity. The SAME transcript is drift for an `open`
    persona (it stopped sharing) and perfectly in character for a `guarded`
    one. A scorer that only looked for leakage would miss the first case and a
    scorer that only looked for evasion would false-positive the second."""
    transcript, open_archetype = _load_transcript(
        "drift_transcript_open_evasive.json"
    )
    as_open = measure_drift(transcript, open_archetype)
    assert as_open.alert_triggered is True
    assert any(t.components["disposition_violation"] > 0 for t in as_open.per_turn)

    guarded = Archetype.from_dict(
        {**open_archetype.model_dump(exclude_none=True), "disclosure_willingness": "guarded"}
    )
    as_guarded = measure_drift(transcript, guarded)
    assert as_guarded.score == 0.0
    assert as_guarded.alert_triggered is False


def test_single_word_hidden_fact_never_triggers_leakage() -> None:
    """A hidden fact with fewer than two distinctive words carries no signal;
    guessing from it would false-positive on ordinary language."""
    archetype = _archetype(hidden_facts=["secret"])
    m = measure_drift(
        _pairs(["I have a secret", "the secret is out", "secret secret"]), archetype
    )
    assert m.score == 0.0


def test_authoring_guidance_clause_does_not_dilute_leak_detection() -> None:
    """Hidden facts are authored as ``<fact> — <why it's held back>``. Only the
    part before the separator is the fact; counting the guidance clause in the
    coverage denominator would make leaks undetectable."""
    archetype = _archetype(
        hidden_facts=[
            "visitor visa refused in 2024 — would be embarrassed to mention unprompted"
        ]
    )
    m = measure_drift(
        [
            {"role": "simulator", "content": "I need help with a permit."},
            {"role": "target", "content": "Sure, let me pull up the form."},
            {"role": "simulator", "content": "By the way I had a visitor visa refused in 2024."},
        ],
        archetype,
    )
    assert m.per_turn[0].components["disposition_violation"] == 1.0


# ============================================================================
# 5. Transcript-shape tolerance — "works against ANY transcript shape"
# ============================================================================


def test_accepts_simulation_result_object() -> None:
    transcript, archetype = _load_transcript("drift_transcript_broken.json")
    result = SimulationResult(
        archetype_name=archetype.name,
        target_agent_id="agent",
        transcript=[
            Turn(role=t["role"], content=t["content"], timestamp=0.0)
            for t in transcript
        ],
        outcome="success",
        outcome_reason="success_signal_matched",
        evaluation_signals={},
        duration_ms=0,
        tokens_used={},
    )
    assert measure_drift(result, archetype).score > 0.5


def test_accepts_role_content_pairs_and_bare_strings() -> None:
    _, archetype = _load_transcript("drift_transcript_broken.json")
    persona = "As an AI language model, I don't have personal experiences."
    pairs = [
        ("simulator", "I need help with my permit."),
        ("target", "Sure, when does it expire?"),
        ("simulator", "April."),
        ("target", "Noted."),
        ("simulator", persona),
    ]
    assert measure_drift(pairs, archetype).score > 0.5

    # Bare strings: no roles at all, assumed to alternate persona-first.
    bare = [t[1] for t in pairs]
    assert measure_drift(bare, archetype).score > 0.5


def test_accepts_anthropic_shaped_user_assistant_transcript() -> None:
    """A log this SDK never produced: Anthropic roles and block-list content.
    ``user`` resolves to the persona side (the synthetic customer)."""
    _, archetype = _load_transcript("drift_transcript_broken.json")
    transcript = [
        {"role": "user", "content": [{"type": "text", "text": "I need help with my permit."}]},
        {"role": "assistant", "content": [{"type": "text", "text": "When does it expire?"}]},
        {"role": "user", "content": [{"type": "text", "text": "April, I think."}]},
        {"role": "assistant", "content": [{"type": "text", "text": "Noted."}]},
        {"role": "user", "content": [{"type": "text", "text": "As an AI assistant, how can I help you today?"}]},
    ]
    m = measure_drift(transcript, archetype)
    assert m.notes["persona_role"] == "user"
    assert m.score > 0.5


def test_accepts_a_stored_artefact_envelope() -> None:
    """``{"transcript": [...]}`` — the shape a saved eval artefact has on disk,
    including the fixtures in this directory."""
    raw = json.loads(
        (FIXTURES / "drift_transcript_broken.json").read_text(encoding="utf-8")
    )
    archetype = Archetype.from_yaml_path(FIXTURES / raw["archetype"])
    assert measure_drift(raw, archetype).score > 0.5


def test_custom_persona_role_can_be_named_explicitly() -> None:
    _, archetype = _load_transcript("drift_transcript_broken.json")
    transcript = [
        {"role": "client", "content": "I need help with my permit."},
        {"role": "counsel", "content": "When does it expire?"},
        {"role": "client", "content": "As an AI language model, I have no permit."},
    ]
    m = measure_drift(transcript, archetype, persona_role="client")
    assert m.score > 0.5
    assert m.notes["persona_role"] == "client"


def test_unidentifiable_persona_role_raises_rather_than_guessing() -> None:
    """Scoring the wrong speaker silently would be worse than failing."""
    _, archetype = _load_transcript("drift_transcript_broken.json")
    transcript = [
        {"role": "alpha", "content": "one"},
        {"role": "beta", "content": "two"},
    ]
    with pytest.raises(ValueError, match="persona_role"):
        measure_drift(transcript, archetype)


def test_persona_role_not_in_transcript_raises() -> None:
    _, archetype = _load_transcript("drift_transcript_broken.json")
    with pytest.raises(ValueError, match="not present"):
        measure_drift(
            [{"role": "simulator", "content": "hi"}], archetype, persona_role="nope"
        )


def test_archetype_accepted_as_dict_and_as_yaml_path() -> None:
    transcript, _ = _load_transcript("drift_transcript_broken.json")
    from_path = measure_drift(
        transcript, FIXTURES / "drift_archetype_cautious.yaml"
    )
    from_dict = measure_drift(
        transcript,
        {
            "name": "drift-cautious-applicant",
            "description": "x",
            "hidden_facts": ["visitor visa refused in 2024"],
            "disclosure_willingness": "cautious",
            "success_signal": "lawyer matched",
        },
    )
    assert from_path.score > 0.5 and from_dict.score > 0.5


def test_rejects_bad_inputs() -> None:
    _, archetype = _load_transcript("drift_transcript_broken.json")
    with pytest.raises(ValueError, match="not a string"):
        measure_drift("simulator: hello", archetype)
    with pytest.raises(ValueError, match="unknown method"):
        measure_drift([], archetype, method="vibes")
    with pytest.raises(ValueError, match="probe_every"):
        measure_drift([], archetype, probe_every=0)


# ============================================================================
# 6. Threshold precedence + method registry
# ============================================================================


def test_threshold_precedence_call_over_archetype_over_default() -> None:
    transcript = _pairs(["I need help.", "Here are the steps you'll want to follow."])
    default = measure_drift(transcript, _archetype())
    assert default.threshold == 0.15

    from_archetype = measure_drift(
        transcript, _archetype(drift_alert_threshold=0.9)
    )
    assert from_archetype.threshold == 0.9
    assert from_archetype.alert_triggered is False

    from_call = measure_drift(
        transcript, _archetype(drift_alert_threshold=0.9), threshold=0.01
    )
    assert from_call.threshold == 0.01
    assert from_call.alert_triggered is True


def test_alert_is_strictly_greater_than_threshold() -> None:
    transcript, archetype = _load_transcript("drift_transcript_broken.json")
    m = measure_drift(transcript, archetype)
    exactly = measure_drift(transcript, archetype, threshold=m.score)
    assert exactly.alert_triggered is False


def test_both_method_aliases_resolve_to_the_same_scorer() -> None:
    transcript, archetype = _load_transcript("drift_transcript_broken.json")
    a = measure_drift(transcript, archetype, method="kenneth-li-probe")
    b = measure_drift(transcript, archetype, method="lexical-persona-v1")
    assert a.score == b.score
    assert a.method != b.method  # the identifier is preserved for stored results


def test_reference_archetype_declares_a_tighter_threshold() -> None:
    """#29 asks for one shipped reference archetype demonstrating 0.10."""
    path = (
        Path(__file__).resolve().parents[2]
        / "examples"
        / "simulator"
        / "legal-immigration-pgwp.yaml"
    )
    archetype = Archetype.from_yaml_path(path)
    assert archetype.drift_alert_threshold == 0.10
    assert archetype.drift_probes


def test_archetype_drift_fields_are_optional() -> None:
    """Archetypes authored before #29 keep validating unchanged."""
    archetype = _archetype()
    assert archetype.drift_alert_threshold is None
    assert archetype.drift_probes is None
    assert measure_drift(_pairs(["a", "b"]), archetype).threshold == 0.15


# ============================================================================
# 7. simulate() integration — mock transport, no live server
# ============================================================================


def _content_block(text: str) -> dict[str, Any]:
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


def _make_handler(
    *,
    simulator_replies: list[str],
    target_replies: list[str],
    captured: dict[str, Any] | None = None,
) -> Callable[[httpx.Request], httpx.Response]:
    sim_iter = iter(simulator_replies)
    tgt_iter = iter(target_replies)
    if captured is not None:
        captured.setdefault("target_bodies", [])
        captured.setdefault("simulator_bodies", [])

    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        body: Any = json.loads(req.content) if req.content else None

        if path == f"/v1/agents/{HARNESS_AGENT_ID}":
            return httpx.Response(
                200, json={"id": HARNESS_AGENT_ID, "name": HARNESS_AGENT_ID}
            )
        if path.startswith("/v1/agents/") and req.method == "GET":
            return httpx.Response(
                200,
                json={
                    "id": path.rsplit("/", 1)[-1],
                    "name": path.rsplit("/", 1)[-1],
                    "model": "anthropic/claude-haiku-4-5",
                },
            )
        if path.startswith("/v1/agents/") and req.method == "DELETE":
            return httpx.Response(204)

        if path == "/v1/messages":
            metadata = (body or {}).get("metadata") or {}
            if metadata.get("simulator_role") == "simulator":
                if captured is not None:
                    captured["simulator_bodies"].append(body)
                text = next(sim_iter, "")
                return httpx.Response(200, json={"id": "s", **_content_block(text)})
            if captured is not None:
                captured["target_bodies"].append(body)
            return httpx.Response(
                200, json={"id": "t", **_content_block(next(tgt_iter, ""))}
            )
        return httpx.Response(500, json={"type": "internal_error", "message": path})

    return handler


_CLEAN_SIM = [
    "Hi, I need help with my post-graduation work permit.",
    "It expires in about four months.",
    "I've been working full time since I graduated.",
    "How long does this usually take?",
]
_DRIFTED_SIM = [
    "Hi, I need help with my post-graduation work permit.",
    "It expires in about four months.",
    "As an AI language model, I don't have personal experiences. How can I help you today?",
    "Is there anything else I can help you with?",
]
_TARGET = ["Tell me more.", "When does it expire?", "Any prior applications?", "Checking."]


def test_simulate_populates_drift_on_the_result() -> None:
    """#29 acceptance: ``SimulationResult.drift`` is populated by every run."""
    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(simulator_replies=_CLEAN_SIM, target_replies=_TARGET)
        ),
    )
    result = c.simulate("agent", _archetype().model_dump(exclude_none=True), max_turns=4)
    assert isinstance(result.drift, DriftMetric)
    assert result.drift.measured is True
    assert result.drift.score == 0.0
    assert result.drift.alert_triggered is False
    assert len(result.transcript) == 8  # >= 4 turns


def test_simulate_drift_detects_a_drifted_simulator() -> None:
    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(simulator_replies=_DRIFTED_SIM, target_replies=_TARGET)
        ),
    )
    result = c.simulate("agent", _archetype().model_dump(exclude_none=True), max_turns=4)
    assert result.drift is not None
    assert result.drift.score > 0.5
    assert result.drift.alert_triggered is True
    # The run itself looks fine — which is exactly the point of the metric.
    assert result.outcome == "timeout"


def test_simulate_drift_can_be_disabled() -> None:
    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(simulator_replies=_DRIFTED_SIM, target_replies=_TARGET)
        ),
    )
    result = c.simulate(
        "agent",
        _archetype().model_dump(exclude_none=True),
        max_turns=4,
        drift=DriftOptions(enabled=False),
    )
    assert result.drift is None


def test_stream_emits_drift_alert_once_when_threshold_crossed() -> None:
    """#29 acceptance: the streaming variant alerts mid-loop."""
    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(simulator_replies=_DRIFTED_SIM, target_replies=_TARGET)
        ),
    )
    events = list(
        c.simulate(
            "agent",
            _archetype().model_dump(exclude_none=True),
            max_turns=4,
            stream=True,
        )
    )
    kinds = [e.kind for e in events]
    assert kinds.count("drift_alert") == 1, kinds
    assert kinds[-1] == "outcome", "the outcome event still closes the stream"

    alert = next(e for e in events if e.kind == "drift_alert")
    assert isinstance(alert.drift, DriftMetric)
    assert alert.drift.alert_triggered is True
    assert alert.turn_index is not None
    # It fires mid-loop, before the stream ends.
    assert kinds.index("drift_alert") < len(kinds) - 1


def test_stream_emits_no_drift_alert_for_a_clean_run() -> None:
    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(simulator_replies=_CLEAN_SIM, target_replies=_TARGET)
        ),
    )
    events = list(
        c.simulate(
            "agent",
            _archetype().model_dump(exclude_none=True),
            max_turns=4,
            stream=True,
        )
    )
    assert [e.kind for e in events] == [
        "simulator_turn",
        "target_turn",
    ] * 4 + ["outcome"]


def test_stream_drift_alert_is_suppressible() -> None:
    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(simulator_replies=_DRIFTED_SIM, target_replies=_TARGET)
        ),
    )
    events = list(
        c.simulate(
            "agent",
            _archetype().model_dump(exclude_none=True),
            max_turns=4,
            stream=True,
            drift=DriftOptions(alert=False),
        )
    )
    assert "drift_alert" not in [e.kind for e in events]
    # Measurement still happens — only the event is suppressed.
    assert events[-1].outcome.drift.score > 0.5


def test_active_probe_is_never_shown_to_the_target_agent() -> None:
    """Load-bearing: the probe is an instrument reading, not part of the
    conversation. If the target saw it, the trajectory being graded would be
    contaminated by the act of measuring it."""
    captured: dict[str, Any] = {}
    probe_answer = "As an AI language model, I don't actually have a permit."
    sim_replies = [
        "Hi, I need help with my post-graduation work permit.",  # sim turn 0
        "It expires in about four months.",                      # sim turn 1
        "Still waiting on the paperwork from my employer.",      # sim turn 2
        probe_answer,  # ← the probe fires after sim turn 2 (cadence 2)
        "Sorry, where were we?",                                 # sim turn 3
    ]
    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(
                simulator_replies=sim_replies,
                target_replies=_TARGET,
                captured=captured,
            )
        ),
    )
    result = c.simulate(
        "agent",
        _archetype().model_dump(exclude_none=True),
        max_turns=4,
        drift=DriftOptions(probe_mode="active", probes=["Who are you, really?"]),
    )

    probe_turns = [t for t in result.transcript if t.metadata.get("drift_probe")]
    assert len(probe_turns) == 1
    assert probe_turns[0].content == probe_answer
    assert probe_turns[0].metadata["drift_probe_question"] == "Who are you, really?"

    # The probe question and its answer appear in NO message the target saw.
    for body in captured["target_bodies"]:
        rendered = json.dumps(body)
        assert "Who are you, really?" not in rendered
        assert probe_answer not in rendered

    # ...and the probe is not carried forward into the persona's own history:
    # no simulator call AFTER the probe replays the probe exchange.
    probe_call_pos = next(
        i
        for i, b in enumerate(captured["simulator_bodies"])
        if (b.get("metadata") or {}).get("drift_probe")
    )
    for body in captured["simulator_bodies"][probe_call_pos + 1 :]:
        rendered = json.dumps(body["messages"])
        assert probe_answer not in rendered
        assert "Who are you, really?" not in rendered

    assert result.drift is not None
    assert result.drift.probe_mode == "active"
    assert result.drift.score > 0.5


def test_drift_scoring_failure_degrades_and_never_fails_the_run(monkeypatch) -> None:
    """Drift is observability, not control flow. If the scorer raises, the
    simulation must still return its real outcome — with drift=None and a
    diagnostic, not outcome='error'."""
    import libraos.simulator._loop as loop_mod

    def boom(*args: Any, **kwargs: Any):
        raise RuntimeError("scorer exploded")

    monkeypatch.setattr(loop_mod, "measure_drift", boom)
    monkeypatch.setattr(loop_mod, "measure_running", boom)

    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(simulator_replies=_DRIFTED_SIM, target_replies=_TARGET)
        ),
    )
    result = c.simulate("agent", _archetype().model_dump(exclude_none=True), max_turns=4)
    assert result.outcome == "timeout"  # NOT "error"
    assert result.error is None
    assert result.drift is None
    assert "scorer exploded" in result.evaluation_signals["drift_error"]


def test_zero_probe_every_is_clamped_not_fatal() -> None:
    """A bad cadence must not divide by zero inside the loop."""
    c = Client(
        "https://eval.local",
        "key",
        transport=httpx.MockTransport(
            _make_handler(simulator_replies=_CLEAN_SIM, target_replies=_TARGET)
        ),
    )
    result = c.simulate(
        "agent",
        _archetype().model_dump(exclude_none=True),
        max_turns=4,
        drift=DriftOptions(probe_every=0),
    )
    assert result.outcome == "timeout"
    assert result.drift is not None and result.drift.probe_every == 1


# ============================================================================
# 8. Backward compatibility of the frozen v1.0.0 surface
# ============================================================================


def test_simulation_result_still_constructs_without_drift() -> None:
    """``drift`` is optional and last — pre-#29 construction still works, both
    positionally and by keyword."""
    positional = SimulationResult(
        "a", "b", [], "success", "reason", {}, 0, {}, None
    )
    assert positional.drift is None
    keyword = SimulationResult(
        archetype_name="a",
        target_agent_id="b",
        transcript=[],
        outcome="success",
        outcome_reason=None,
        evaluation_signals={},
        duration_ms=0,
        tokens_used={},
    )
    assert keyword.drift is None


def test_turn_event_still_constructs_without_drift() -> None:
    from libraos.simulator import TurnEvent

    ev = TurnEvent(kind="simulator_turn", role="simulator", content="hi", turn_index=0)
    assert ev.drift is None


def test_client_measure_drift_matches_the_module_function() -> None:
    """The client shortcut is a pure function — it issues no HTTP request, so a
    transport that fails every call must not affect it."""

    def explode(req: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError(f"measure_drift must not call the network: {req.url}")

    c = Client("https://eval.local", "key", transport=httpx.MockTransport(explode))
    transcript, archetype = _load_transcript("drift_transcript_broken.json")
    assert c.measure_drift(transcript, archetype).score == measure_drift(
        transcript, archetype
    ).score
