"""Simulator-specific error types.

Two error families live here:

1. **Pre-flight errors** — raised BEFORE the loop sends any ``/chat``
   call. Partners catch these to surface config / connectivity issues
   to archetype authors and operators. These all derive from
   :class:`SimulatorError`.

   - :class:`ArchetypeValidationError` — archetype YAML / dict failed
     schema or semantic validation (also re-exported as the legacy
     top-level alias on ``libraos``).
   - :class:`AuthenticationError` — eval-instance bearer token is
     missing / invalid; raised when the SDK's pre-flight ``/health``
     ping returns 401.
   - :class:`EvalInstanceUnreachableError` — eval-instance URL is
     unreachable (DNS / connect timeout / wrong base URL).

2. **In-loop errors** — NOT raised. They are surfaced via
   :attr:`SimulationResult.outcome` / ``outcome_reason`` / ``error`` so
   partners can treat a failed simulation as data rather than as an
   exception. See ``_loop.run_loop`` for the failure table.

Note on naming: this module's :class:`AuthenticationError` is the
*simulator pre-flight* variant — it is intentionally distinct from
``libraos.errors.AuthenticationError`` (the generic transport-layer
401). Partners catching the simulator family by base class catch
both via :class:`SimulatorError`.
"""

from __future__ import annotations


class SimulatorError(Exception):
    """Base class for every simulator pre-flight error."""


class ArchetypeValidationError(SimulatorError, ValueError):
    """Raised when an archetype fails schema or semantic validation.

    Multiple inheritance keeps backwards compatibility — earlier
    archetype-loading tests catch ``ValueError`` because that was the
    only base before the simulator-error family landed.

    Carries a field path (e.g. ``"hidden_facts"`` or
    ``"failure_signals[2]"``) plus a human-readable reason. The string
    form is suitable for surfacing directly to archetype authors.
    """

    def __init__(self, field: str, reason: str) -> None:
        self.field = field
        self.reason = reason
        # ValueError's __init__ accepts *args; pass a single rendered
        # message so str(exc) renders as "field: reason" for partner
        # logging without extra effort.
        ValueError.__init__(self, f"{field}: {reason}")


class AuthenticationError(SimulatorError):
    """Pre-flight: eval-instance bearer token rejected.

    Distinct from ``libraos.errors.AuthenticationError`` — this one
    only fires on the simulator pre-flight check, before the loop
    runs. In-loop 401s are surfaced via
    :attr:`SimulationResult.outcome == "error"`.
    """


class EvalInstanceUnreachableError(SimulatorError):
    """Pre-flight: eval-instance URL did not respond.

    Carries a troubleshooting hint suitable for surfacing to the
    operator; the underlying transport error is chained via
    ``__cause__`` for callers that want it.
    """


__all__ = [
    "SimulatorError",
    "ArchetypeValidationError",
    "AuthenticationError",
    "EvalInstanceUnreachableError",
]
