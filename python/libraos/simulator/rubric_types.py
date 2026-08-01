"""Result dataclasses returned by ``client.evaluate()`` (#30).

Frozen, like :class:`~libraos.simulator.SimulationResult`, so partners can key
them in dicts and append to CSVs without surprise mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CriterionResult:
    """The grader's verdict on one rubric criterion."""

    criterion: str
    required: bool
    passed: bool
    reason: str = ""


@dataclass(frozen=True)
class RubricResult:
    """The outcome of one ``client.evaluate(target, case)`` call.

    ``task_passed`` uses the Harvey 100% threshold: it is ``True`` only when
    **every required criterion passed**. ``pass_rate`` is the fraction of *all*
    criteria (required and optional) that passed, for a softer signal.
    """

    case_id: str
    criteria: list[CriterionResult]
    task_passed: bool
    pass_rate: float
    work_product: str
    input_tokens: int = 0
    output_tokens: int = 0
    duration_s: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def required_pass_rate(self) -> float:
        req = [c for c in self.criteria if c.required]
        if not req:
            return 1.0
        return sum(c.passed for c in req) / len(req)
