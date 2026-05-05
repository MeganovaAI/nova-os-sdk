"""Settings resource — /v1/managed/settings (#179)."""

from __future__ import annotations

from typing import Any

from nova_os.resources._base import Resource


class Settings(Resource):
    """Read/write platform settings.

    Settings values are heterogeneously typed (strings for model
    identifiers like ``anthropic/claude-opus-4-7``, ints for
    thresholds, bools for feature flags). This SDK preserves whatever
    value the partner sends.

    The current server-side implementation is in-process / in-memory;
    persistence is a separate follow-up. The SDK surface is forward-
    compatible — once persistence lands, no client change is needed.
    """

    _PATH = "/v1/managed/settings"

    async def all(self) -> dict[str, Any]:
        """GET /v1/managed/settings — read every setting."""
        return await self._client._request("GET", self._PATH)

    async def get(self, key: str) -> Any:
        """GET /v1/managed/settings/{key} — read one. Returns the value."""
        resp = await self._client._request("GET", f"{self._PATH}/{key}")
        return (resp or {}).get("value")

    async def put(self, key: str, value: Any) -> dict[str, Any]:
        """PUT /v1/managed/settings/{key} — write one. Returns ``{key, value}``."""
        return await self._client._request(
            "PUT", f"{self._PATH}/{key}", json_body={"value": value}
        )
