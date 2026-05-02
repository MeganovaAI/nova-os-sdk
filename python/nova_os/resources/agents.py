"""Agents resource — /v1/managed/agents CRUD + paginated list."""

from __future__ import annotations

from typing import Any, AsyncIterator

from nova_os.resources._base import Resource


class Agents(Resource):
    """CRUD + list for /v1/managed/agents.

    All methods are async-first; `.sync` mirror on the parent Client.
    Methods return / accept dicts (the underlying generated typed models
    are available under `nova_os._generated` for callers that need them).
    """

    _PATH = "/v1/managed/agents"

    async def create(self, *, idempotency_key: str | None = None, **fields: Any) -> dict[str, Any]:
        """POST /v1/managed/agents — create an agent."""
        if "id" not in fields:
            raise ValueError("id is required")
        if "type" not in fields:
            raise ValueError("type is required (persona|skill)")
        return await self._client._request(
            "POST", self._PATH, json_body=fields, idempotency_key=idempotency_key
        )

    async def get(self, agent_id: str) -> dict[str, Any]:
        """GET /v1/managed/agents/{id}."""
        return await self._client._request("GET", f"{self._PATH}/{agent_id}")

    async def update(self, agent_id: str, **fields: Any) -> dict[str, Any]:
        """PUT /v1/managed/agents/{id} — partial update."""
        return await self._client._request("PUT", f"{self._PATH}/{agent_id}", json_body=fields)

    async def delete(self, agent_id: str) -> None:
        """DELETE /v1/managed/agents/{id}."""
        await self._client._request("DELETE", f"{self._PATH}/{agent_id}")

    async def list(
        self,
        *,
        limit: int | None = None,
        owner_employee: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """GET /v1/managed/agents — async-iterator that auto-paginates.

        Yields one agent per iteration; transparent across pages via
        `has_more` + `next_cursor`. Set `limit` to constrain page size.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if owner_employee is not None:
            params["owner_employee"] = owner_employee

        cursor: str | None = None
        while True:
            page_params = dict(params)
            if cursor:
                page_params["cursor"] = cursor
            page = await self._client._request("GET", self._PATH, params=page_params)
            for item in (page or {}).get("data", []):
                yield item
            if not (page or {}).get("has_more"):
                return
            cursor = page.get("next_cursor")
            if not cursor:
                return
