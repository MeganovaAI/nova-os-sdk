"""Employees resource — /v1/managed/employees CRUD + paginated list."""

from __future__ import annotations

from typing import Any, AsyncIterator

from nova_os.resources._base import Resource


class Employees(Resource):
    """CRUD + list for /v1/managed/employees.

    All methods are async-first; `.sync` mirror on the parent Client.
    Methods return / accept dicts.
    """

    _PATH = "/v1/managed/employees"

    async def create(self, *, idempotency_key: str | None = None, **fields: Any) -> dict[str, Any]:
        """POST /v1/managed/employees — create an employee."""
        if "id" not in fields:
            raise ValueError("id is required")
        return await self._client._request(
            "POST", self._PATH, json_body=fields, idempotency_key=idempotency_key
        )

    async def get(self, employee_id: str) -> dict[str, Any]:
        """GET /v1/managed/employees/{id}."""
        return await self._client._request("GET", f"{self._PATH}/{employee_id}")

    async def update(self, employee_id: str, **fields: Any) -> dict[str, Any]:
        """PUT /v1/managed/employees/{id} — partial update."""
        return await self._client._request(
            "PUT", f"{self._PATH}/{employee_id}", json_body=fields
        )

    async def delete(self, employee_id: str) -> None:
        """DELETE /v1/managed/employees/{id}."""
        await self._client._request("DELETE", f"{self._PATH}/{employee_id}")

    async def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """GET /v1/managed/employees — async-iterator that auto-paginates.

        Yields one employee per iteration; transparent across pages via
        `has_more` + `next_cursor`. Set `limit` to constrain page size.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit

        current_cursor: str | None = cursor
        while True:
            page_params = dict(params)
            if current_cursor:
                page_params["cursor"] = current_cursor
            page = await self._client._request("GET", self._PATH, params=page_params)
            for item in (page or {}).get("data", []):
                yield item
            if not (page or {}).get("has_more"):
                return
            current_cursor = page.get("next_cursor")
            if not current_cursor:
                return
