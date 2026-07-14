"""Public API entry point for the synthetic-customer simulator.

Two flavors, both backed by the same async loop runner in
``_loop.py``:

- :func:`simulate` — top-level sync function. Wraps
  :func:`async_simulate` in ``anyio.run``. Suited for scripts,
  notebooks, and CI test bodies.
- :func:`async_simulate` — async coroutine. Suited for callers that
  already have an event loop running (FastAPI handlers, etc.).

The LibraOS ``Client`` exposes both — see ``Client.simulate(...)``
(sync) and ``Client.async_simulate(...)`` (async).
"""

from __future__ import annotations

import queue
import threading
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterator

import anyio

from libraos.simulator._loop import run_loop, stream_loop
from libraos.simulator._wiring import (
    ensure_simulator_agent,
    teardown_transient_agent,
)
from libraos.simulator.archetype import Archetype
from libraos.simulator.errors import ArchetypeValidationError
from libraos.simulator.prompt import build_simulator_prompt
from libraos.simulator.types import SimulationResult, TurnEvent

if TYPE_CHECKING:
    from libraos.client import Client


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
    target_model: str | None = None,
) -> SimulationResult:
    """Run a synthetic-customer simulation against ``target_agent_id``.

    Synchronous variant — wraps :func:`async_simulate` in
    :func:`anyio.run`. Intended for scripts, notebooks, and CI
    bodies that do not already have an event loop.

    Parameters
    ----------
    client:
        A live :class:`~libraos.Client` pointed at the EVAL instance.
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
    target_model:
        Optional gateway model string (``<provider>/<name>``) to use
        on the target side. /v1/messages is Anthropic-spec and requires
        ``model`` on every request — the kernel does not fall through
        to the target agent's baked model. When ``None``, the SDK
        auto-discovers via one ``client.agents.get(target_agent_id)``
        round-trip at simulate-start. Pass this explicitly to skip the
        discovery call (e.g. in tests with mocked HTTP).

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
            target_model=target_model,
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
    target_model: str | None = None,
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

    # 6. Resolve target model. Caller can pin it via the ``target_model``
    # parameter (skips the round-trip — useful in tests with mocked HTTP and
    # in production deployments where the partner already knows the target's
    # model). When None, fetch via one ``client.agents.get`` round-trip.
    # Required because /v1/messages is Anthropic-spec and demands ``model``
    # on every request — kernel doesn't fall through to baked agent model.
    effective_target_model = (
        target_model
        if target_model is not None
        else await _fetch_target_model(client, target_agent_id)
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
            target_model=effective_target_model,
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


async def _fetch_target_model(client: "Client", target_agent_id: str) -> str:
    """Fetch the target agent's baked ``model`` field.

    /v1/messages is Anthropic-spec and requires ``model`` on every request —
    the kernel does NOT fall through to the agent's baked model on that
    endpoint. We fetch it once here so the loop can supply it on each call.
    Raises :class:`AuthenticationError` on 401 and :class:`NotFoundError`
    (which the caller surfaces as a clear error) on 404. Other errors
    propagate as-is.
    """
    agent = await client.agents.get(target_agent_id)
    # Resource shape: managed-agents GET returns the agent with a top-level
    # ``model`` field. If that's missing or null, fall back to a sensible
    # default for the simulator pattern — partners can override per-archetype
    # via ``model_override`` on the archetype YAML.
    model = getattr(agent, "model", None) or "anthropic/claude-haiku-4-5"
    return model


# ----------------------------------------------------------- streaming surface


async def async_simulate_stream(
    client: "Client",
    target_agent_id: str,
    archetype: dict[str, Any] | str | Path | Archetype,
    *,
    max_turns: int = _DEFAULT_MAX_TURNS,
    simulator_model: str = _DEFAULT_SIMULATOR_MODEL,
    simulator_system_prompt: str | None = None,
    metadata: dict[str, Any] | None = None,
    target_api_key: str | None = None,
    target_model: str | None = None,
) -> AsyncIterator[TurnEvent]:
    """Async-iterator variant of :func:`async_simulate`.

    Yields one :class:`~libraos.simulator.types.TurnEvent` per turn —
    a ``simulator_turn`` immediately followed by a ``target_turn`` —
    and ends with exactly ONE ``outcome`` event carrying the full
    :class:`SimulationResult`. The outcome event always fires, even on
    error / timeout / cancellation paths (per spec §F: runtime errors
    are surfaced as data, not raised through the iterator).

    Cancellation contract: if the caller breaks out of the
    ``async for`` loop or calls ``await it.aclose()`` mid-stream, any
    transient simulator agent that was created during wiring is still
    DELETEd via the ``try/finally`` below. Partners can rely on this
    for resource hygiene regardless of how iteration ends.

    Parameters mirror :func:`async_simulate`. See its docstring for
    field-by-field semantics.
    """
    # Archetype normalisation + wiring happen BEFORE the first yield;
    # validation failures still raise (they're not in-loop errors).
    arche = _normalize_archetype(archetype)
    effective_max_turns = _resolve_max_turns(max_turns, arche)
    prompt = (
        simulator_system_prompt
        if simulator_system_prompt is not None
        else build_simulator_prompt(arche, max_turns=effective_max_turns)
    )
    effective_model = (
        arche.model_override
        if arche.model_override is not None
        else simulator_model
    )
    session_id = _new_session_id()

    sim_agent_id, is_transient = await ensure_simulator_agent(
        client,
        arche,
        simulator_system_prompt=prompt,
    )

    # Resolve target model — caller-supplied wins; else fetch once via
    # ``client.agents.get``. /v1/messages requires ``model`` explicitly.
    effective_target_model = (
        target_model
        if target_model is not None
        else await _fetch_target_model(client, target_agent_id)
    )

    try:
        async for event in stream_loop(
            client,
            target_agent_id=target_agent_id,
            archetype=arche,
            simulator_agent_id=sim_agent_id,
            simulator_system_prompt=prompt,
            effective_max_turns=effective_max_turns,
            simulator_model=effective_model,
            target_model=effective_target_model,
            session_id=session_id,
            metadata=metadata,
            target_api_key=target_api_key,
        ):
            yield event
    finally:
        # Cleanup runs whether the consumer exhausts the stream,
        # breaks out early, or aclose()s the generator — this is the
        # load-bearing cancellation-cleanup contract.
        await teardown_transient_agent(
            client, sim_agent_id, is_transient=is_transient
        )


def simulate_stream(
    client: "Client",
    target_agent_id: str,
    archetype: dict[str, Any] | str | Path | Archetype,
    *,
    max_turns: int = _DEFAULT_MAX_TURNS,
    simulator_model: str = _DEFAULT_SIMULATOR_MODEL,
    simulator_system_prompt: str | None = None,
    metadata: dict[str, Any] | None = None,
    target_api_key: str | None = None,
    target_model: str | None = None,
) -> Iterator[TurnEvent]:
    """Sync facade over :func:`async_simulate_stream`.

    The async iterator is driven on a dedicated thread (running its
    own anyio event loop); events are handed back to the calling
    thread via a bounded :mod:`queue` so the caller can ``for event
    in simulate_stream(...)`` from synchronous code.

    Cancellation: if the caller stops iterating (``break`` /
    ``return`` from the ``for`` loop) and lets the iterator be
    garbage-collected, the generator's ``close()`` runs on next
    consumption attempt; the producer thread observes the closed
    queue and cancels the async iterator (triggering the
    ``try/finally`` cleanup inside :func:`async_simulate_stream`).
    """
    # Sentinel marker that signals "iterator exhausted" — any non-
    # TurnEvent placeholder would do; we use a fresh object identity
    # so users can't accidentally synthesize one.
    _DONE = object()
    # Sentinel marker that signals "caller wants us to stop", set by
    # the consuming side when it gives up early.
    _STOP = threading.Event()

    q: "queue.Queue[Any]" = queue.Queue(maxsize=8)

    def _producer() -> None:
        async def _drive() -> None:
            agen = async_simulate_stream(
                client,
                target_agent_id,
                archetype,
                max_turns=max_turns,
                simulator_model=simulator_model,
                simulator_system_prompt=simulator_system_prompt,
                metadata=metadata,
                target_api_key=target_api_key,
                target_model=target_model,
            )
            try:
                async for event in agen:
                    if _STOP.is_set():
                        break
                    q.put(event)
            finally:
                # Ensure the async generator's own finally (transient
                # agent DELETE) fires before the thread exits, even on
                # mid-stream cancellation.
                await agen.aclose()

        try:
            anyio.run(_drive)
        except BaseException as exc:  # noqa: BLE001 — surface to consumer
            q.put(exc)
        finally:
            q.put(_DONE)

    thread = threading.Thread(target=_producer, daemon=True)
    thread.start()

    try:
        while True:
            item = q.get()
            if item is _DONE:
                return
            if isinstance(item, BaseException):
                raise item
            yield item
    finally:
        # If the consumer abandons the generator early (break / return /
        # exception), signal the producer to stop and let its finally
        # fire (which closes the async generator and triggers cleanup).
        _STOP.set()
        # Drain remaining queue items so the producer thread can put _DONE
        # without blocking on a full queue.
        try:
            while True:
                q.get_nowait()
        except queue.Empty:
            pass
        thread.join(timeout=5.0)


__all__ = [
    "simulate",
    "async_simulate",
    "simulate_stream",
    "async_simulate_stream",
]
