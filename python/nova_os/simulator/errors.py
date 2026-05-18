"""Simulator-specific error types.

Raised by archetype loading + validation; partners catch these to surface
config errors to archetype authors before any /chat call is made.
"""

from __future__ import annotations


class ArchetypeValidationError(ValueError):
    """Raised when an archetype fails schema or semantic validation.

    Carries a field path (e.g. ``"hidden_facts"`` or ``"failure_signals[2]"``)
    plus a human-readable reason. The string form is suitable for surfacing
    directly to archetype authors.
    """

    def __init__(self, field: str, reason: str) -> None:
        self.field = field
        self.reason = reason
        super().__init__(f"{field}: {reason}")


__all__ = ["ArchetypeValidationError"]
