"""Public API entry point for the synthetic-customer simulator.

Two flavors, both backed by the same async loop runner in
``_loop.py``:

- :func:`simulate` — top-level sync function. Wraps
  :func:`async_simulate` in ``anyio.run``. Suited for scripts,
  notebooks, and CI test bodies.
- :func:`async_simulate` — async coroutine. Suited for callers that
  already have an event loop running (FastAPI handlers, etc.).

The Nova OS ``Client`` exposes both — see ``Client.simulate(...)``
(sync) and ``Client.async_simulate(...)`` (async).
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

import anyio

from nova_os.simulator._loop import run_loop
from nova_os.simulator._wiring import (
    ensure_simulator_agent,
    teardown_transient_agent,
)
from nova_os.simulator.archetype import Archetype
from nova_os.simulator.errors import ArchetypeValidationError
from nova_os.simulator.prompt import build_simulator_prompt
from nova_os.simulator.types import SimulationResult

if TYPE_CHECKING:
    from nova_os.client import Client


_DEFAULT_SIMULATOR_MODEL = "anthropic/claude-haiku-4-5"
_DEFAULT_MAX_TURNS = 10


def simulate(
    client: "Client",
    target_agent_id: str,
    archetype: dict[str, Any] | str | Path | Archetype,
    *,
    max_turns: int = _DEFAULT_MAX_TURNS,
    simulator_model: str = _DEFAULT_SIMULATOR_MODEL,
    simulator_system_prompt: str | None = None,
    metadata: dict[str, Any] | None = None,
    target_api_key: str | None = None,
) -> SimulationResult:
    """Run a synthetic-customer simulation against ``target_agent_id``.

    Synchronous variant — wraps :func:`async_simulate` in
    :func:`anyio.run`. Intended for scripts, notebooks, and CI
    bodies that do not already have an event loop.

    Parameters
    ----------
    client:
        A live :class:`~nova_os.Client` pointed at the EVAL instance.
        Production-instance use is supported but discouraged — eval
        traffic will accumulate in production ``call_log``.
    target_agent_id:
        The agent under test.
    archetype:
        One of: a Pydantic-validated :class:`Archetype` instance, a
        plain dict matching the archetype schema, or a filesystem
        path / :class:`pathlib.Path` to a YAML archetype on disk.
    max_turns:
        Absolute upper bound on the conversation length. Both this
        cap and ``archetype.termination_conditions.max_turns`` apply
        — the tighter of the two wins.
    simulator_model:
        Default LLM for the simulator side. Overridden by
        ``archetype.model_override`` when set.
    simulator_system_prompt:
        Override for the deterministic prompt built by
        :func:`build_simulator_prompt`. Useful for experimentation;
        typical callers leave this ``None``.
    metadata:
        Caller-supplied metadata merged into every ``/chat`` call.
        The SDK additionally augments each call with
        ``simulator_session_id`` (UUIDv7), ``simulator_role``
        (``"simulator"``/``"target"``), and ``simulator_turn_index``
        (int).
    target_api_key:
        Reserved — surfaced for symmetry with the public signature.
        v1 piggybacks on the client's default bearer; per-call key
        rotation is a v2 feature.

    Returns
    -------
    SimulationResult
        Frozen result dataclass — transcript, outcome, signals,
        timing, tokens. Never raises on in-loop failure; partners
        treat failed simulations as data.

    Raises
    ------
    ArchetypeValidationError
        When ``archetype`` (dict / YAML / Archetype) fails schema
        or semantic validation. Raised BEFORE any ``/chat`` call.
    """
    return anyio.run(
        lambda: async_simulate(
            client,
            target_agent_id,
            archetype,
            max_turns=max_turns,
            simulator_model=simulator_model,
            simulator_system_prompt=simulator_system_prompt,
            metadata=metadata,
            target_api_key=target_api_key,
        )
    )


async def async_simulate(
    client: "Client",
    target_agent_id: str,
    archetype: dict[str, Any] | str | Path | Archetype,
    *,
    max_turns: int = _DEFAULT_MAX_TURNS,
    simulator_model: str = _DEFAULT_SIMULATOR_MODEL,
    simulator_system_prompt: str | None = None,
    metadata: dict[str, Any] | None = None,
    target_api_key: str | None = None,
) -> SimulationResult:
    """Async variant of :func:`simulate`. Same contract."""

    # 1. Normalize archetype → validated Archetype instance.
    arche = _normalize_archetype(archetype)

    # 2. Build simulator system prompt (or accept caller override).
    effective_max_turns = _resolve_max_turns(max_turns, arche)
    prompt = (
        simulator_system_prompt
        if simulator_system_prompt is not None
        else build_simulator_prompt(arche, max_turns=effective_max_turns)
    )

    # 3. Resolve simulator model — archetype.model_override wins.
    effective_model = (
        arche.model_override
        if arche.model_override is not None
        else simulator_model
    )

    # 4. Stable session id. Prefer uuidv7 (Py 3.13+) for time-ordered
    # IDs; fall back to uuid4 on older runtimes.
    session_id = _new_session_id()

    # 5. Ensure simulator-side wiring. Returns is_transient so we know
    # whether to delete in the finally block.
    sim_agent_id, is_transient = await ensure_simulator_agent(
        client,
        arche,
        simulator_system_prompt=prompt,
    )

    try:
        result = await run_loop(
            client,
            target_agent_id=target_agent_id,
            archetype=arche,
            simulator_agent_id=sim_agent_id,
            simulator_system_prompt=prompt,
            effective_max_turns=effective_max_turns,
            simulator_model=effective_model,
            session_id=session_id,
            metadata=metadata,
            target_api_key=target_api_key,
        )
        return result
    finally:
        # Cleanup runs even on exception — load-bearing for the
        # transient-agent strategy. No-op for the harness branch.
        await teardown_transient_agent(
            client, sim_agent_id, is_transient=is_transient
        )


# --------------------------------------------------------------- helpers


def _normalize_archetype(
    archetype: dict[str, Any] | str | Path | Archetype,
) -> Archetype:
    """Coerce one of the three accepted input shapes to an Archetype.

    Raises :class:`ArchetypeValidationError` on any validation
    failure — surfaces before any ``/chat`` call is made.
    """
    if isinstance(archetype, Archetype):
        return archetype
    if isinstance(archetype, dict):
        return Archetype.from_dict(archetype)
    if isinstance(archetype, (str, Path)):
        return Archetype.from_yaml_path(archetype)
    raise ArchetypeValidationError(
        "<root>",
        f"expected Archetype | dict | str | Path, got {type(archetype).__name__}",
    )


def _resolve_max_turns(caller_cap: int, archetype: Archetype) -> int:
    """Tighter-wins: ``min(caller_cap, archetype.termination_conditions.max_turns)``.

    Both bounds are positive integers when set; the archetype cap is
    optional and falls through to the caller cap when ``None``.
    """
    arche_cap = (
        archetype.termination_conditions.max_turns
        if archetype.termination_conditions is not None
        else None
    )
    if arche_cap is None:
        return caller_cap
    return min(caller_cap, arche_cap)


def _new_session_id() -> str:
    """Return a stable, time-ordered session id.

    Prefers UUIDv7 (added to Python's ``uuid`` module in 3.13).
    Falls back to UUIDv4 on older runtimes — partners care about
    uniqueness more than time-ordering.
    """
    uuid7 = getattr(uuid, "uuid7", None)
    if uuid7 is not None:
        return str(uuid7())
    return str(uuid.uuid4())


__all__ = ["simulate", "async_simulate"]
