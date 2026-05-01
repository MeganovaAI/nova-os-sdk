"""Jobs resource — /v1/managed/agents/jobs async-job CRUD."""

from __future__ import annotations

from typing import Any, AsyncIterator

from nova_os.resources._base import Resource


class Jobs(Resource):
    """Async-job submit/poll/cancel/list for long-running agent tasks.

    Stream endpoint (/jobs/{id}/stream) is Phase 3.2.
    """

    _PATH = "/v1/managed/agents/jobs"

    async def create(
        self,
        agent_id: str,
        messages: list[dict[str, Any]],
        *,
        idempotency_key: str | None = None,
        **kw: Any,
    ) -> dict[str, Any]:
        """POST /v1/managed/agents/jobs — submit a long-running job.

        Returns a job record with status='queued' and a job_id for polling.
        """
        body: dict[str, Any] = {"agent_id": agent_id, "messages": messages, **kw}
        return await self._client._request(
            "POST", self._PATH, json_body=body, idempotency_key=idempotency_key
        )

    async def get(self, job_id: str) -> dict[str, Any]:
        """GET /v1/managed/agents/jobs/{id} — poll job state."""
        return await self._client._request("GET", f"{self._PATH}/{job_id}")

    async def cancel(self, job_id: str) -> None:
        """DELETE /v1/managed/agents/jobs/{id} — cancel (graceful drain)."""
        await self._client._request("DELETE", f"{self._PATH}/{job_id}")

    async def list(
        self,
        *,
        status: str | None = None,
        agent_id: str | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """GET /v1/managed/agents/jobs — async-iterator that auto-paginates.

        Yields one job per iteration across pages.
        """
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if agent_id is not None:
            params["agent_id"] = agent_id
        if limit is not None:
            params["limit"] = limit

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
