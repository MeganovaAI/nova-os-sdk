"""Sync proxy for the async Client resources — fleshed out in Task 9."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nova_os.client import Client


class _SyncProxy:
    """Placeholder — replaced with full implementation in Task 9."""

    def __init__(self, client: "Client") -> None:
        self._client = client
