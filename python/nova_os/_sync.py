"""Sync proxy for the async Client resources.

Provides `Client.sync.agents`, `Client.sync.employees`, etc. — a mirror
of the async resources that runs coroutines synchronously via anyio.run().

Intended use: scripts and notebooks that don't already have a running
event loop. Do NOT use inside async handlers (use `await c.agents.create(...)`
directly — mixing sync-from-async causes errors).

Special case for `list()`: async iterators can't be trivially bridged via
anyio.run (each call would restart the generator). Instead, `.sync.*.list()`
exhausts the async iterator inside a single anyio.run call and returns a
plain Python list.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable

import anyio

if TYPE_CHECKING:
    from nova_os.client import Client


class _SyncResourceProxy:
    """Wraps a single async resource and makes its methods synchronous."""

    def __init__(self, resource: Any) -> None:
        self._r = resource

    def __getattr__(self, name: str) -> Callable[..., Any]:
        attr = getattr(self._r, name)

        # Special case: async generator methods (list). Exhaust inside one
        # anyio.run call so callers get a plain list rather than an
        # unusable async generator.
        if name == "list":
            def list_wrapper(*args: Any, **kw: Any) -> list:
                async def _collect() -> list:
                    return [item async for item in attr(*args, **kw)]
                return anyio.run(_collect)
            return list_wrapper

        # Regular coroutine methods (create, get, update, delete, cancel).
        if asyncio.iscoroutinefunction(attr):
            def wrapper(*args: Any, **kw: Any) -> Any:
                return anyio.run(lambda: attr(*args, **kw))
            return wrapper

        # Non-coroutine attributes (properties, plain methods) — pass through.
        return attr


class _SyncProxy:
    """Top-level sync mirror that mirrors Client.agents, .employees, etc."""

    def __init__(self, client: "Client") -> None:
        # These references are live: if the resource is replaced on the
        # client (e.g. in tests), the proxy picks up the new object via
        # __getattr__ on self._client instead.
        self._client = client

    @property
    def agents(self) -> _SyncResourceProxy:
        return _SyncResourceProxy(self._client.agents)

    @property
    def employees(self) -> _SyncResourceProxy:
        return _SyncResourceProxy(self._client.employees)

    @property
    def messages(self) -> _SyncResourceProxy:
        return _SyncResourceProxy(self._client.messages)

    @property
    def jobs(self) -> _SyncResourceProxy:
        return _SyncResourceProxy(self._client.jobs)
