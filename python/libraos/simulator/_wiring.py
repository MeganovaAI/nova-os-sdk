"""Wiring strategy: how the simulator side calls ``/chat``.

Two strategies, in order of preference:

1. **PRIMARY: harness agent.** A pre-created agent (id
   ``nova-os-simulator-harness``) with a minimal, instructive-only
   baked system prompt. The SDK lands the archetype-derived system
   prompt as ``messages[0].role == "system"`` on each call, and the
   harness agent's small baked prompt does not fight it.

2. **FALLBACK: transient agent.** When the harness is not present
   on the eval instance, the SDK creates a one-off agent via
   ``POST /v1/agents`` carrying the archetype's system prompt as its
   baked prompt, uses it for the simulate run, then ``DELETE``s it
   in a ``try/finally``. Each transient agent is cached per
   ``(base_url, archetype.name)`` so a CI invocation that runs the
   same archetype N times pays the create/delete cost ONCE.

The harness agent's baked prompt — when partners ship it themselves
— SHOULD match :data:`HARNESS_AGENT_SYSTEM_PROMPT` below.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from libraos.errors import NotFoundError
from libraos.simulator.archetype import Archetype

if TYPE_CHECKING:
    from libraos.client import Client


HARNESS_AGENT_ID = "nova-os-simulator-harness"

HARNESS_AGENT_SYSTEM_PROMPT = (
    "You will receive a customer archetype as the first system message "
    "in each request. Follow it strictly. Do not deviate from the "
    "archetype in any response."
)


# Per-process cache: (base_url, archetype_name) → (agent_id, is_transient).
# Module-level by design — partners typically construct one Client per
# eval instance, so cache scope = process lifetime is correct.
_AGENT_CACHE: dict[tuple[str, str], tuple[str, bool]] = {}


async def ensure_simulator_agent(
    client: "Client",
    archetype: Archetype,
    *,
    simulator_system_prompt: str | None = None,
) -> tuple[str, bool]:
    """Return ``(agent_id, is_transient)`` for the simulator side.

    Strategy:

    1. If the harness agent (id :data:`HARNESS_AGENT_ID`) exists,
       return it; ``is_transient=False``. Cached.
    2. Else create a transient agent whose baked ``system`` prompt is
       ``simulator_system_prompt`` (or :data:`HARNESS_AGENT_SYSTEM_PROMPT`
       if not supplied). Return it; ``is_transient=True``. Cached.

    Callers MUST eventually invoke :func:`teardown_transient_agent` on
    the returned id in a ``try/finally``; that helper is a no-op for the
    non-transient (harness) branch, so callers can always call it.
    """
    cache_key = (client._base_url, archetype.name)
    cached = _AGENT_CACHE.get(cache_key)
    if cached is not None:
        return cached

    # Step 1: probe for the harness agent.
    try:
        await client.agents.get(HARNESS_AGENT_ID)
        result = (HARNESS_AGENT_ID, False)
        _AGENT_CACHE[cache_key] = result
        return result
    except NotFoundError:
        pass

    # Step 2: fallback — create a transient agent. Use the harness'
    # baked-prompt shape (instructive-only) by default; partners can
    # override via the explicit simulator_system_prompt arg.
    baked_prompt = simulator_system_prompt or HARNESS_AGENT_SYSTEM_PROMPT
    transient_name = f"nova-os-simulator-transient-{archetype.name}"
    created = await client.agents.create(
        name=transient_name,
        agent_type="skill",
        system=baked_prompt,
    )
    transient_id = created.get("id") or transient_name
    result = (transient_id, True)
    _AGENT_CACHE[cache_key] = result
    return result


async def teardown_transient_agent(
    client: "Client", agent_id: str, *, is_transient: bool
) -> None:
    """Delete a transient simulator agent. No-op for the harness.

    Safe to call even on failure paths — DELETE failures are
    swallowed (a stale transient agent is recoverable; raising during
    cleanup would mask the original error).
    """
    if not is_transient:
        return
    try:
        await client.agents.delete(agent_id)
    except Exception:
        # Cleanup is best-effort — partners can list + sweep stale
        # transients out-of-band if needed. Don't shadow caller errors.
        pass
    # Drop the cache entry so a subsequent simulate against the same
    # archetype re-creates (otherwise we'd return a deleted agent_id).
    for key, value in list(_AGENT_CACHE.items()):
        if value[0] == agent_id:
            _AGENT_CACHE.pop(key, None)


def _reset_cache_for_tests() -> None:
    """Test-only helper. Drop the agent-cache between test cases."""
    _AGENT_CACHE.clear()


__all__ = [
    "HARNESS_AGENT_ID",
    "HARNESS_AGENT_SYSTEM_PROMPT",
    "ensure_simulator_agent",
    "teardown_transient_agent",
]
