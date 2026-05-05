"""Sessions resource — /v1/managed/sessions (#185).

Nova OS native session create/get. Shares state with the
Anthropic-compat /v1/sessions surface — partners can mix the two
mounts freely; a session created via either is readable via either.
"""

from __future__ import annotations

from typing import Any

from nova_os.resources._base import Resource


class Sessions(Resource):
    _PATH = "/v1/managed/sessions"

    async def create(
        self,
        *,
        agent_id: str,
        environment_id: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """POST /v1/managed/sessions — create a session bound to an agent.

        ``model`` is a session-default LLM override. Per-event ``model``
        on subsequent message calls takes precedence.
        """
        body: dict[str, Any] = {"agent_id": agent_id}
        if environment_id is not None:
            body["environment_id"] = environment_id
        if model is not None:
            body["model"] = model
        return await self._client._request("POST", self._PATH, json_body=body)

    async def get(self, session_id: str) -> dict[str, Any]:
        """GET /v1/managed/sessions/{id}."""
        return await self._client._request("GET", f"{self._PATH}/{session_id}")
