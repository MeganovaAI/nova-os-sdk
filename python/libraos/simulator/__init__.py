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

    from libraos import Client, Archetype

    archetype = Archetype.from_yaml_path("./archetypes/my-customer.yaml")
    c = Client(base_url="https://nova-eval.partner.com", api_key="…")
    result = c.simulate(target_agent_id="legal-assistant", archetype=archetype)
    print(result.outcome, result.outcome_reason)

A streaming variant — :func:`simulate_stream` /
:func:`async_simulate_stream` — yields per-turn events instead of a
materialised :class:`SimulationResult`. The final event of any stream
is always a ``kind="outcome"`` event carrying the full result, so
partners that prefer the streaming surface still get the same outcome
data at the end.

Persona-drift monitoring (#29) rides along on both surfaces:
:class:`SimulationResult` carries a :class:`DriftMetric` on ``.drift``,
the stream emits an optional ``drift_alert`` event when the persona
decays mid-run, and :func:`measure_drift` scores any transcript
standalone. See :mod:`libraos.simulator.drift`.
"""

from __future__ import annotations

from libraos.simulator.archetype import (
    Archetype,
    DisclosureWillingness,
    FailureSignalMatch,
    TerminationConditions,
)
from libraos.simulator.errors import (
    ArchetypeValidationError,
    AuthenticationError,
    EvalInstanceUnreachableError,
    SimulatorError,
)
from libraos.simulator.prompt import build_simulator_prompt
from libraos.simulator.simulate import (
    async_simulate,
    async_simulate_stream,
    simulate,
    simulate_stream,
)
from libraos.simulator.types import SimulationResult, Turn, TurnEvent
from libraos.simulator.drift_types import (
    DEFAULT_DRIFT_THRESHOLD,
    DEFAULT_PROBE_EVERY,
    DriftMetric,
    DriftOptions,
    DriftTurn,
)
from libraos.simulator.drift import (
    AUTO_PROBES,
    DRIFT_METHODS,
    measure_drift,
)
from libraos.simulator.rubric import (
    RubricCase,
    RubricCriterion,
    RubricMatter,
    RubricValidationError,
    load_rubric_pack,
)
from libraos.simulator.rubric_types import CriterionResult, RubricResult
from libraos.simulator.evaluate import evaluate, async_evaluate
from libraos.simulator.pack import (
    Pack,
    PackValidationError,
    load_pack,
    list_installed_packs,
    detect_pack_collisions,
)

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
    "simulate_stream",
    "async_simulate_stream",
    "SimulationResult",
    "Turn",
    "TurnEvent",
    "DriftMetric",
    "DriftTurn",
    "DriftOptions",
    "measure_drift",
    "DRIFT_METHODS",
    "AUTO_PROBES",
    "DEFAULT_DRIFT_THRESHOLD",
    "DEFAULT_PROBE_EVERY",
    "RubricCase",
    "RubricCriterion",
    "RubricMatter",
    "RubricValidationError",
    "load_rubric_pack",
    "CriterionResult",
    "RubricResult",
    "evaluate",
    "async_evaluate",
    "Pack",
    "PackValidationError",
    "load_pack",
    "list_installed_packs",
    "detect_pack_collisions",
]
