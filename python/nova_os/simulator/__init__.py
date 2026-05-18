"""Synthetic-customer simulator — archetype schema + (future) simulate loop.

This sub-module ships the schema layer for the simulator pattern: a Pydantic
v2 model + JSON Schema for partner-supplied customer archetypes. The loop
itself (``client.simulate()``) lands in a follow-up release.

Example::

    from nova_os import Archetype

    archetype = Archetype.from_yaml_path("./archetypes/my-customer.yaml")
    assert archetype.disclosure_willingness in ("open", "cautious", "guarded")
"""

from __future__ import annotations

from nova_os.simulator.archetype import (
    Archetype,
    DisclosureWillingness,
    FailureSignalMatch,
    TerminationConditions,
)
from nova_os.simulator.errors import ArchetypeValidationError
from nova_os.simulator.prompt import build_simulator_prompt

__all__ = [
    "Archetype",
    "ArchetypeValidationError",
    "TerminationConditions",
    "DisclosureWillingness",
    "FailureSignalMatch",
    "build_simulator_prompt",
]
