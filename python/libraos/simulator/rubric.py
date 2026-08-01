"""Rubric model for the work-product evaluation harness (#30).

Where the :class:`~libraos.simulator.Archetype` + ``simulate()`` loop scores a
*trajectory* (does the agent behave correctly across a multi-turn conversation),
a **rubric** scores a *static work product*: given an instruction and matter
context, does the agent's output satisfy each of a checklist of criteria a
domain expert would apply? The shape mirrors Harvey LAB's published rubric
structure — an instruction, a matter, an expected work-product shape, and a
list of pass/fail criteria — and evaluation uses the **Harvey 100% threshold**:
a case only *passes* if every required criterion passes.

This module ships the :class:`RubricCase` / :class:`RubricCriterion` Pydantic
models with ``from_dict`` / ``from_yaml_path`` loaders (mirroring
:class:`Archetype`) and :func:`load_rubric_pack` for a directory of cases.
The runner lives in :mod:`libraos.simulator.evaluate`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from libraos.simulator.errors import ArchetypeValidationError

# Reuse the archetype error type so partners catch one exception class across
# both authoring surfaces; the field path makes the source unambiguous.
RubricValidationError = ArchetypeValidationError

WorkProductShape = Literal[
    "legal-memo", "redline", "recommendation-letter", "intake-form", "other"
]


class RubricCriterion(BaseModel):
    """One checklist item a grader applies to the work product."""

    model_config = ConfigDict(extra="forbid")

    criterion: str = Field(min_length=1)
    required: bool = True


class RubricMatter(BaseModel):
    """The inputs the agent is asked to work over.

    ``documents`` are file-path references; ``context`` is free text. v1 of the
    harness passes ``context`` (and the document paths, as references) to the
    target agent inline — binary document upload/attachment is a follow-up, so
    ship rubric cases whose signal lives in ``context`` for now.
    """

    model_config = ConfigDict(extra="forbid")

    documents: list[dict[str, Any]] = Field(default_factory=list)
    context: str = ""


class RubricCase(BaseModel):
    """One gradeable case. See the module docstring for the shape rationale."""

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(min_length=1)
    practice_area: str = ""
    instruction: str = Field(min_length=1)
    matter: RubricMatter = Field(default_factory=RubricMatter)
    expected_work_product_shape: WorkProductShape = "other"
    rubric: list[RubricCriterion] = Field(min_length=1)

    @field_validator("rubric")
    @classmethod
    def _at_least_one_required(cls, v: list[RubricCriterion]) -> list[RubricCriterion]:
        if not any(c.required for c in v):
            raise ValueError(
                "at least one criterion must be required (task_passed is "
                "gated on required criteria under the Harvey 100% threshold)"
            )
        return v

    # ── loaders (mirror Archetype.from_dict / from_yaml_path) ──────────────

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RubricCase":
        if not isinstance(d, dict):
            raise RubricValidationError("<root>", f"expected dict, got {type(d).__name__}")
        try:
            return cls(**d)
        except ValidationError as exc:
            first = exc.errors()[0]
            loc = ".".join(str(p) for p in first.get("loc", ())) or "<root>"
            raise RubricValidationError(loc, first.get("msg", "invalid")) from exc

    @classmethod
    def from_yaml_path(cls, p: str | Path) -> "RubricCase":
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover - dep is declared
            raise ImportError(
                "PyYAML is required for RubricCase.from_yaml_path; "
                "install with `pip install pyyaml`"
            ) from exc
        path = Path(p)
        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        return cls.from_dict(raw)


def load_rubric_pack(path: str | Path) -> list[RubricCase]:
    """Load every ``*.yaml`` / ``*.yml`` rubric case under a directory.

    Mirrors the archetype pack convention. Files are loaded in sorted order for
    deterministic runs; a single invalid case raises :class:`RubricValidationError`
    identifying the offending file.
    """
    root = Path(path)
    if not root.is_dir():
        raise NotADirectoryError(f"rubric pack path is not a directory: {root}")
    cases: list[RubricCase] = []
    for f in sorted([*root.glob("*.yaml"), *root.glob("*.yml")]):
        try:
            cases.append(RubricCase.from_yaml_path(f))
        except RubricValidationError as exc:
            raise RubricValidationError(f"{f.name}:{exc.field}", exc.reason) from exc
    return cases
