"""Synthetic-customer simulator — archetype schema + simulate loop.

This sub-module ships:

- The :class:`Archetype` schema layer (Pydantic v2 model + JSON
  Schema) that partners author archetype YAML against.
- The deterministic :func:`build_simulator_prompt` template builder.
- The :func:`simulate` loop runner (sync) and its async sibling
  :func:`async_simulate`. Both also surface as
  ``Client.simulate(...)`` and ``Client.async_simulate(...)`` on the
  top-level client.

Example::

    from nova_os import Client, Archetype

    archetype = Archetype.from_yaml_path("./archetypes/my-customer.yaml")
    c = Client(base_url="https://nova-eval.partner.com", api_key="…")
    result = c.simulate(target_agent_id="legal-assistant", archetype=archetype)
    print(result.outcome, result.outcome_reason)

A streaming variant (yielding per-turn events) is on the roadmap for
a follow-up release.
"""

from __future__ import annotations

from nova_os.simulator.archetype import (
    Archetype,
    DisclosureWillingness,
    FailureSignalMatch,
    TerminationConditions,
)
from nova_os.simulator.errors import (
    ArchetypeValidationError,
    AuthenticationError,
    EvalInstanceUnreachableError,
    SimulatorError,
)
from nova_os.simulator.prompt import build_simulator_prompt
from nova_os.simulator.simulate import async_simulate, simulate
from nova_os.simulator.types import SimulationResult, Turn

__all__ = [
    "Archetype",
    "ArchetypeValidationError",
    "AuthenticationError",
    "EvalInstanceUnreachableError",
    "SimulatorError",
    "TerminationConditions",
    "DisclosureWillingness",
    "FailureSignalMatch",
    "build_simulator_prompt",
    "simulate",
    "async_simulate",
    "SimulationResult",
    "Turn",
]
