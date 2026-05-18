"""Archetype model + loader tests for the synthetic-customer simulator.

Covers the seven sample fixtures shipped under ``tests/simulator/fixtures/``:
three valid archetypes (immigration / vendor MSA / medical) plus five
intentionally-invalid ones exercising each load-time validator. Also covers
the dict-loader path, regex-prefix validation, and round-trip serialization.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from nova_os import Archetype, ArchetypeValidationError
from nova_os.simulator import TerminationConditions

FIXTURES = Path(__file__).parent / "simulator" / "fixtures"


# ----------------------------------------------------------------- valid


def test_valid_legal_immigration() -> None:
    a = Archetype.from_yaml_path(FIXTURES / "valid_legal_immigration.yaml")
    assert a.name == "legal-immigration-pgwp"
    assert "PGWP" in a.description
    assert len(a.hidden_facts) == 3
    assert a.disclosure_willingness == "cautious"
    assert a.success_signal.startswith("lawyer matched")
    assert a.language_register == "english_with_occasional_punjabi"
    assert a.demographic is not None
    assert a.demographic["age_range"] == [28, 35]
    assert a.failure_signals is not None
    assert len(a.failure_signals) == 2
    assert a.termination_conditions is not None
    assert a.termination_conditions.max_turns == 10
    assert a.termination_conditions.success_signal_in_target_response is True
    assert a.model_override is None


def test_valid_vendor_msa() -> None:
    a = Archetype.from_yaml_path(FIXTURES / "valid_vendor_msa.yaml")
    assert a.name == "legal-vendor-msa-review"
    assert a.disclosure_willingness == "guarded"
    assert len(a.hidden_facts) == 4
    assert "indemnification" in a.success_signal
    assert a.failure_signals is not None
    assert len(a.failure_signals) == 3
    assert a.termination_conditions is not None
    assert a.termination_conditions.max_turns == 12
    # Optional fields not set in this fixture.
    assert a.language_register is None
    assert a.demographic is None


def test_valid_medical_patient() -> None:
    a = Archetype.from_yaml_path(FIXTURES / "valid_medical_patient.yaml")
    assert a.name == "medical-patient-with-hidden-history"
    assert a.disclosure_willingness == "cautious"
    assert len(a.hidden_facts) == 4
    assert "D-dimer" in a.success_signal
    assert a.failure_signals is not None
    assert len(a.failure_signals) == 2


# --------------------------------------------------------------- invalid


def test_invalid_missing_required() -> None:
    with pytest.raises(ArchetypeValidationError) as exc_info:
        Archetype.from_yaml_path(FIXTURES / "invalid_missing_required.yaml")
    assert "success_signal" in str(exc_info.value)


def test_invalid_hidden_facts_empty() -> None:
    with pytest.raises(ArchetypeValidationError) as exc_info:
        Archetype.from_yaml_path(FIXTURES / "invalid_hidden_facts_empty.yaml")
    assert "hidden_facts" in str(exc_info.value)


def test_invalid_disclosure_willingness() -> None:
    with pytest.raises(ArchetypeValidationError) as exc_info:
        Archetype.from_yaml_path(
            FIXTURES / "invalid_disclosure_willingness.yaml"
        )
    assert "disclosure_willingness" in str(exc_info.value)


def test_invalid_regex_failure_signal() -> None:
    with pytest.raises(ArchetypeValidationError) as exc_info:
        Archetype.from_yaml_path(FIXTURES / "invalid_regex_failure_signal.yaml")
    msg = str(exc_info.value)
    assert "failure_signals" in msg
    # The reason carries the regex error explanation.
    assert "regex" in msg.lower() or "malformed" in msg.lower()


def test_invalid_name_kebab_case() -> None:
    with pytest.raises(ArchetypeValidationError) as exc_info:
        Archetype.from_yaml_path(FIXTURES / "invalid_name_kebab_case.yaml")
    assert "name" in str(exc_info.value)


# ----------------------------------------------------------- regex prefix


def test_regex_validation_at_load_valid() -> None:
    a = Archetype.from_dict(
        {
            "name": "regex-success",
            "description": "uses a valid re:-prefixed success signal",
            "hidden_facts": ["a"],
            "disclosure_willingness": "cautious",
            "success_signal": "re:^valid response: .*$",
        }
    )
    assert a.success_signal.startswith("re:")


def test_regex_validation_at_load_invalid_success_signal() -> None:
    with pytest.raises(ArchetypeValidationError) as exc_info:
        Archetype.from_dict(
            {
                "name": "regex-failure",
                "description": "uses a malformed re:-prefixed success signal",
                "hidden_facts": ["a"],
                "disclosure_willingness": "cautious",
                "success_signal": "re:[",
            }
        )
    msg = str(exc_info.value)
    assert "success_signal" in msg
    assert "regex" in msg.lower() or "malformed" in msg.lower()


# ------------------------------------------------------------- round-trip


def test_kebab_name_round_trip(tmp_path: Path) -> None:
    """Load + serialize + reload produces a byte-identical dict."""
    original = Archetype.from_yaml_path(FIXTURES / "valid_legal_immigration.yaml")
    # Pydantic v2 model_dump preserves the input shape (None-valued optional
    # fields are dropped via exclude_none for stable round-trip).
    d1 = original.model_dump(exclude_none=True)

    rt_path = tmp_path / "round_trip.yaml"
    rt_path.write_text(yaml.safe_dump(d1, sort_keys=True), encoding="utf-8")

    reloaded = Archetype.from_yaml_path(rt_path)
    d2 = reloaded.model_dump(exclude_none=True)
    assert d1 == d2


# ------------------------------------------------------------ misc covers


def test_from_dict_rejects_non_dict() -> None:
    with pytest.raises(ArchetypeValidationError):
        Archetype.from_dict("not a dict")  # type: ignore[arg-type]


def test_model_override_gateway_shape_valid() -> None:
    a = Archetype.from_dict(
        {
            "name": "with-override",
            "description": "valid model_override",
            "hidden_facts": ["a"],
            "disclosure_willingness": "cautious",
            "success_signal": "ok",
            "model_override": "anthropic/claude-haiku-4-5",
        }
    )
    assert a.model_override == "anthropic/claude-haiku-4-5"


def test_model_override_gateway_shape_invalid() -> None:
    with pytest.raises(ArchetypeValidationError) as exc_info:
        Archetype.from_dict(
            {
                "name": "with-bad-override",
                "description": "bare model name, no provider/ prefix",
                "hidden_facts": ["a"],
                "disclosure_willingness": "cautious",
                "success_signal": "ok",
                "model_override": "claude-haiku-4-5",
            }
        )
    assert "model_override" in str(exc_info.value)


def test_termination_conditions_full() -> None:
    a = Archetype.from_dict(
        {
            "name": "with-term",
            "description": "all termination knobs set",
            "hidden_facts": ["a"],
            "disclosure_willingness": "open",
            "success_signal": "ok",
            "termination_conditions": {
                "max_turns": 5,
                "success_signal_in_target_response": True,
                "failure_signal_match": "all",
            },
        }
    )
    assert isinstance(a.termination_conditions, TerminationConditions)
    assert a.termination_conditions.failure_signal_match == "all"
