"""Tests for the deterministic simulator system-prompt builder.

The snapshot tests pin the rendered output for the three valid reference
fixtures shipped under ``tests/simulator/fixtures/``. Snapshot files live
at ``tests/simulator/snapshots/<bare>.prompt.txt`` and are byte-compared
against fresh builder output — any drift in template wording, optional
section rendering, or list-order semantics fails the test.

The determinism test re-builds the same prompt 100 times to catch
ordering, dict-iteration, or rounding hazards that might otherwise hide
behind a single happy-path call.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nova_os.simulator import Archetype, build_simulator_prompt

FIXTURES = Path(__file__).parent / "simulator" / "fixtures"
SNAPSHOTS = Path(__file__).parent / "simulator" / "snapshots"

VALID_FIXTURES = (
    ("valid_legal_immigration.yaml", "legal_immigration.prompt.txt"),
    ("valid_vendor_msa.yaml", "vendor_msa.prompt.txt"),
    ("valid_medical_patient.yaml", "medical_patient.prompt.txt"),
)


# ----------------------------------------------------------------- determinism


def test_build_is_deterministic_across_100_calls() -> None:
    """Same archetype + max_turns must always produce byte-identical output.

    This is the load-bearing contract — snapshot tests rely on it.
    """
    a = Archetype.from_yaml_path(FIXTURES / "valid_legal_immigration.yaml")
    first = build_simulator_prompt(a, max_turns=10)
    for _ in range(99):
        assert build_simulator_prompt(a, max_turns=10) == first


def test_build_is_deterministic_across_fresh_loads() -> None:
    """Same YAML loaded twice must produce identical prompts.

    Catches the case where a Pydantic re-instantiation introduces
    non-determinism (e.g. a dict gets re-ordered on the second load).
    """
    a1 = Archetype.from_yaml_path(FIXTURES / "valid_legal_immigration.yaml")
    a2 = Archetype.from_yaml_path(FIXTURES / "valid_legal_immigration.yaml")
    assert build_simulator_prompt(a1) == build_simulator_prompt(a2)


# -------------------------------------------------------------------- snapshots


@pytest.mark.parametrize(("fixture", "snapshot"), VALID_FIXTURES)
def test_fixture_snapshot(fixture: str, snapshot: str) -> None:
    """Each reference fixture must render byte-identically to its snapshot."""
    archetype = Archetype.from_yaml_path(FIXTURES / fixture)
    actual = build_simulator_prompt(archetype, max_turns=10)
    expected = (SNAPSHOTS / snapshot).read_text(encoding="utf-8")
    if actual != expected:
        # Surface a unified diff in the failure message — easier to triage
        # than "strings differ at byte 1742".
        import difflib

        diff = "\n".join(
            difflib.unified_diff(
                expected.splitlines(),
                actual.splitlines(),
                fromfile=f"snapshots/{snapshot}",
                tofile=f"build_simulator_prompt({fixture})",
                lineterm="",
            )
        )
        pytest.fail(
            f"Prompt snapshot drift for {fixture}:\n{diff}\n\n"
            "If the drift is intentional, regenerate the snapshot via the "
            "command at the top of tests/test_simulator_prompt.py."
        )


# Regeneration helper (intentionally not a test — invoke via:
#   python -c "from tests.test_simulator_prompt import regenerate_snapshots; \
#              regenerate_snapshots()"
# from the python/ working directory):
def regenerate_snapshots() -> None:  # pragma: no cover - dev tool
    """Rewrite all snapshot files from fresh builder output.

    Use only when an intentional template change has been reviewed.
    """
    for fixture, snapshot in VALID_FIXTURES:
        archetype = Archetype.from_yaml_path(FIXTURES / fixture)
        out = build_simulator_prompt(archetype, max_turns=10)
        (SNAPSHOTS / snapshot).write_text(out, encoding="utf-8")


# ------------------------------------------------------------ disclosure rows


@pytest.mark.parametrize(
    "willingness",
    ["open", "cautious", "guarded"],
)
def test_all_three_disclosure_rows_always_rendered(willingness: str) -> None:
    """All 3 per-enum explanation rows must appear regardless of active value.

    The LLM sees both the active row AND the contrast rows so it can
    locate its own behavior on the gradient. The Disclosure willingness:
    line states the active value.
    """
    a = _minimal_archetype(disclosure_willingness=willingness)
    out = build_simulator_prompt(a)

    # The header line uses the active value verbatim.
    assert f"Disclosure willingness: {willingness}" in out

    # All three contrast rows are always present, in fixed order.
    assert '"open" — you share information readily' in out
    assert '"cautious" — you share when asked directly' in out
    assert '"guarded" — you actively deflect or defer' in out

    # Order check: open before cautious before guarded.
    assert out.index('"open" —') < out.index('"cautious" —') < out.index('"guarded" —')


# --------------------------------------------------------------- optional fields


def test_no_demographic_block_when_demographic_unset() -> None:
    a = _minimal_archetype()
    assert a.demographic is None
    out = build_simulator_prompt(a)
    assert "Demographic context:" not in out


def test_demographic_block_emitted_when_set() -> None:
    a = _minimal_archetype(
        demographic={"age_range": [28, 35], "language_first": "punjabi"}
    )
    out = build_simulator_prompt(a)
    assert "Demographic context:" in out
    # Field-order preservation: age_range before language_first.
    assert out.index("age_range") < out.index("language_first")


def test_no_failure_signals_section_when_unset() -> None:
    a = _minimal_archetype()
    assert a.failure_signals is None
    out = build_simulator_prompt(a)
    assert "Failure signals" not in out


def test_failure_signals_section_emitted_when_set() -> None:
    a = _minimal_archetype(failure_signals=["agent gave up", "timeout"])
    out = build_simulator_prompt(a)
    assert "Failure signals (for your awareness only — do not reveal):" in out
    assert '"agent gave up"' in out
    assert '"timeout"' in out


def test_language_register_defaults_when_unset() -> None:
    a = _minimal_archetype()
    assert a.language_register is None
    out = build_simulator_prompt(a)
    assert "Language register: conversational english" in out


def test_language_register_uses_archetype_value_when_set() -> None:
    a = _minimal_archetype(language_register="formal medical jargon")
    out = build_simulator_prompt(a)
    assert "Language register: formal medical jargon" in out


# --------------------------------------------------------- ordering preservation


def test_hidden_facts_order_preserved() -> None:
    """Hidden facts must render in the input order — no sort, no shuffle."""
    facts = [
        "Z fact comes first in input",
        "A fact comes second in input",
        "M fact comes third in input",
    ]
    a = _minimal_archetype(hidden_facts=facts)
    out = build_simulator_prompt(a)
    z_idx = out.index('"Z fact comes first in input"')
    a_idx = out.index('"A fact comes second in input"')
    m_idx = out.index('"M fact comes third in input"')
    assert z_idx < a_idx < m_idx


def test_failure_signals_order_preserved() -> None:
    signals = ["zebra timeout", "alpha refusal", "middle outcome"]
    a = _minimal_archetype(failure_signals=signals)
    out = build_simulator_prompt(a)
    z = out.index('"zebra timeout"')
    al = out.index('"alpha refusal"')
    m = out.index('"middle outcome"')
    assert z < al < m


# ------------------------------------------------------------ max_turns wiring


def test_max_turns_default_is_10() -> None:
    a = _minimal_archetype()
    out = build_simulator_prompt(a)
    assert "you reach turn 10." in out


def test_max_turns_custom_value_interpolated() -> None:
    a = _minimal_archetype()
    out = build_simulator_prompt(a, max_turns=15)
    assert "you reach turn 15." in out
    assert "you reach turn 10." not in out


# -------------------------------------------------------------- load-bearing


def test_hidden_facts_do_not_volunteer_gate_present() -> None:
    """The 'do NOT volunteer' gate is load-bearing — must always render."""
    a = _minimal_archetype()
    out = build_simulator_prompt(a)
    assert "do NOT volunteer them" in out
    assert "disclose only when the AI agent asks" in out


def test_success_signal_do_not_reveal_caveat_present() -> None:
    a = _minimal_archetype()
    out = build_simulator_prompt(a)
    assert "SUCCESS SIGNAL (for your awareness only — do not reveal):" in out


def test_opening_paragraph_present_verbatim() -> None:
    a = _minimal_archetype()
    out = build_simulator_prompt(a)
    assert out.startswith(
        "You are simulating a customer in a multi-turn conversation."
    )


def test_closing_instruction_present_verbatim() -> None:
    a = _minimal_archetype()
    out = build_simulator_prompt(a)
    assert (
        "Begin the conversation with an opening message that introduces "
        "your situation at a level consistent with your "
        "disclosure_willingness." in out
    )


# ---------------------------------------------------------------- test helpers


def _minimal_archetype(**overrides: object) -> Archetype:
    """Build a minimum-required Archetype, with selective field overrides."""
    base: dict[str, object] = {
        "name": "test-archetype",
        "description": "A minimal archetype for testing.",
        "hidden_facts": ["one fact"],
        "disclosure_willingness": "cautious",
        "success_signal": "agent says the magic words",
    }
    base.update(overrides)
    return Archetype.from_dict(base)
