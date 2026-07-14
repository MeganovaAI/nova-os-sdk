"""Archetype model for the synthetic-customer simulator.

An *archetype* describes a synthetic customer persona that the simulator
loop will play against a target LibraOS agent during evaluation. It is the
partner-supplied input to ``client.simulate()``.

This module ships:

- :class:`Archetype` — a Pydantic v2 model matching ``archetype.schema.json``
  with stricter field validators than the JSON Schema can express
  (kebab-case name rule, regex compile check on ``re:``-prefixed signals,
  gateway-shape check on ``model_override``).
- ``Archetype.from_dict`` / ``Archetype.from_yaml_path`` classmethod loaders.

On any validation failure the loaders raise :class:`ArchetypeValidationError`
with a field path + human-readable reason; partners surface this to
archetype authors before any ``/chat`` call is made.

See the SDK README and ``examples/simulator/`` for end-to-end usage.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from libraos.simulator.errors import ArchetypeValidationError

# Stricter kebab-case than the JSON Schema's `^[a-z0-9-]+$`: must start with
# a letter, must not end with a hyphen, single-character names allowed.
_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$")

# Gateway model-name shape — same rule the kernel enforces on agent.model
# (private nova-os issue #93). Distinct enforcement copy here so misspellings
# get caught before the kernel rejects them.
_MODEL_OVERRIDE_RE = re.compile(r"^[a-z0-9_-]+/[A-Za-z0-9._-]+$")

DisclosureWillingness = Literal["open", "cautious", "guarded"]
FailureSignalMatch = Literal["any", "all"]


class TerminationConditions(BaseModel):
    """Optional termination knobs for a simulator run.

    All three fields are optional; the SDK applies defaults at the call site
    (``max_turns=10``, ``success_signal_in_target_response=True``,
    ``failure_signal_match="any"``).
    """

    model_config = ConfigDict(extra="forbid")

    max_turns: int | None = Field(default=None, ge=1, le=50)
    success_signal_in_target_response: bool | None = None
    failure_signal_match: FailureSignalMatch | None = None


class Archetype(BaseModel):
    """A synthetic-customer persona definition.

    Required fields describe *who the customer is* and *what success looks
    like*; optional fields tune the simulator loop's termination + the
    underlying LLM choice.

    Construct via :meth:`from_dict` or :meth:`from_yaml_path` — both run the
    full validation chain and raise :class:`ArchetypeValidationError` on any
    failure (regex compile errors on ``re:``-prefixed signals, kebab-case
    violations, gateway-shape violations on ``model_override``).
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    name: str = Field(..., min_length=1, max_length=128)
    description: str = Field(..., min_length=1, max_length=4000)
    hidden_facts: list[str] = Field(..., min_length=1)
    disclosure_willingness: DisclosureWillingness
    success_signal: str = Field(..., min_length=1, max_length=1000)

    # Optional fields:
    language_register: str | None = Field(default=None, max_length=200)
    demographic: dict[str, Any] | None = None
    failure_signals: list[str] | None = None
    termination_conditions: TerminationConditions | None = None
    model_override: str | None = None

    # ------------------------------------------------------------------ name

    @field_validator("name")
    @classmethod
    def _validate_name_kebab(cls, v: str) -> str:
        if not _NAME_RE.match(v):
            raise ValueError(
                "must be lowercase kebab-case "
                "(letters, digits, internal hyphens; must start with a letter "
                "and not end with a hyphen)"
            )
        return v

    # ----------------------------------------------------------- hidden_facts

    @field_validator("hidden_facts")
    @classmethod
    def _validate_hidden_facts(cls, v: list[str]) -> list[str]:
        for i, item in enumerate(v):
            if not (1 <= len(item) <= 1000):
                raise ValueError(
                    f"item [{i}] must be 1-1000 chars (got {len(item)})"
                )
        return v

    # ---------------------------------------------------------- success_signal

    @field_validator("success_signal")
    @classmethod
    def _validate_success_signal(cls, v: str) -> str:
        _check_regex_prefix(v, "success_signal")
        return v

    # --------------------------------------------------------- failure_signals

    @field_validator("failure_signals")
    @classmethod
    def _validate_failure_signals(
        cls, v: list[str] | None
    ) -> list[str] | None:
        if v is None:
            return None
        for i, item in enumerate(v):
            if not (1 <= len(item) <= 1000):
                raise ValueError(
                    f"item [{i}] must be 1-1000 chars (got {len(item)})"
                )
            _check_regex_prefix(item, f"failure_signals[{i}]")
        return v

    # ---------------------------------------------------------- model_override

    @field_validator("model_override")
    @classmethod
    def _validate_model_override(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not _MODEL_OVERRIDE_RE.match(v):
            raise ValueError(
                "must match gateway-shape regex '<provider>/<name>' "
                "(e.g. 'anthropic/claude-haiku-4-5')"
            )
        return v

    # ------------------------------------------------------------- loaders

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Archetype:
        """Build an :class:`Archetype` from an in-memory dict.

        Raises :class:`ArchetypeValidationError` with a field path on any
        validation failure.
        """
        if not isinstance(d, dict):
            raise ArchetypeValidationError(
                "<root>", f"expected dict, got {type(d).__name__}"
            )
        try:
            return cls(**d)
        except ValidationError as exc:
            raise _to_archetype_error(exc) from exc

    @classmethod
    def from_yaml_path(cls, p: str | Path) -> Archetype:
        """Load an archetype from a YAML file on disk.

        Requires ``PyYAML`` (declared in the SDK's ``pyyaml`` dependency).
        Raises :class:`ArchetypeValidationError` on schema violation;
        :class:`FileNotFoundError` if the path does not exist.
        """
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover - dep is declared
            raise ImportError(
                "PyYAML is required for Archetype.from_yaml_path; "
                "install with `pip install libraos-sdk[simulator]` or "
                "`pip install pyyaml`"
            ) from exc

        path = Path(p)
        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        if raw is None:
            raise ArchetypeValidationError(
                "<root>", f"YAML file {path} is empty"
            )
        if not isinstance(raw, dict):
            raise ArchetypeValidationError(
                "<root>",
                f"YAML root must be a mapping, got {type(raw).__name__}",
            )
        return cls.from_dict(raw)


# ----------------------------------------------------------------- helpers


def _check_regex_prefix(value: str, field_label: str) -> None:
    """If ``value`` starts with ``re:``, validate the suffix compiles.

    Raises ``ValueError`` (caught + re-raised as
    :class:`ArchetypeValidationError` by the loader) when the regex is
    malformed. The ``field_label`` is purely informational — Pydantic
    overrides the path on its way out.
    """
    if value.startswith("re:"):
        pattern = value[len("re:") :]
        try:
            re.compile(pattern)
        except re.error as exc:
            raise ValueError(
                f"malformed regex after 're:' prefix ({exc!s}); "
                f"pattern was {pattern!r}"
            ) from exc


def _to_archetype_error(exc: ValidationError) -> ArchetypeValidationError:
    """Collapse a Pydantic ``ValidationError`` to our flat error type.

    The first error wins for the message; the field path is rendered as
    a dotted/indexed string (``hidden_facts``, ``failure_signals[2]``,
    ``termination_conditions.max_turns``).
    """
    errs = exc.errors()
    if not errs:  # defensive — Pydantic always has at least one
        return ArchetypeValidationError("<root>", str(exc))
    first = errs[0]
    loc = first.get("loc", ())
    field = _render_loc(loc) if loc else "<root>"
    reason = first.get("msg", "validation failed")
    return ArchetypeValidationError(field, reason)


def _render_loc(loc: tuple[Any, ...]) -> str:
    """Render a Pydantic ``loc`` tuple as ``a.b[2].c``."""
    parts: list[str] = []
    for item in loc:
        if isinstance(item, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{item}]"
            else:
                parts.append(f"[{item}]")
        else:
            parts.append(str(item))
    return ".".join(parts) if parts else "<root>"


__all__ = [
    "Archetype",
    "TerminationConditions",
    "DisclosureWillingness",
    "FailureSignalMatch",
]
