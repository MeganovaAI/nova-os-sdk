"""Base class for resources — keeps a backref to the parent Client."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nova_os.client import Client


class Resource:
    """Base class — every resource has a `_client` backref."""

    def __init__(self, client: "Client") -> None:
        self._client = client
