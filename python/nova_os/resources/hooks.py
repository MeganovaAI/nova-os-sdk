"""Hooks resource — /v1/managed/hooks (#177).

The 9 canonical lifecycle events are validated server-side; passing
any other event name raises ``InvalidRequestError``.

**Note:** as of v0.1.5 the in-memory store accepts subscriptions but
the runtime hook bus does not yet bridge to it. Subscriptions are
stored and retrievable via list/get; events do not yet fire to the
registered URLs. Persistence + bus bridge land in a follow-up — your
partner integration code can wire against this contract today and
will start receiving deliveries once the bridge ships.
"""

from __future__ import annotations

from typing import Any, Literal

from nova_os.resources._base import Resource


HookEvent = Literal[
    "SessionStart",
    "SessionEnd",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PreInference",
    "PostInference",
    "Stop",
    "Error",
]


class Hooks(Resource):
    _PATH = "/v1/managed/hooks"

    async def create(
        self,
        *,
        event: HookEvent,
        target_url: str,
        secret_env: str | None = None,
        description: str | None = None,
        enabled: bool = True,
    ) -> dict[str, Any]:
        """POST /v1/managed/hooks — register a subscription."""
        body: dict[str, Any] = {
            "event": event,
            "target_url": target_url,
            "enabled": enabled,
        }
        if secret_env is not None:
            body["secret_env"] = secret_env
        if description is not None:
            body["description"] = description
        return await self._client._request("POST", self._PATH, json_body=body)

    async def get(self, hook_id: str) -> dict[str, Any]:
        """GET /v1/managed/hooks/{id}."""
        return await self._client._request("GET", f"{self._PATH}/{hook_id}")

    async def delete(self, hook_id: str) -> None:
        """DELETE /v1/managed/hooks/{id} — idempotent (always 204)."""
        await self._client._request("DELETE", f"{self._PATH}/{hook_id}")

    async def list(self) -> list[dict[str, Any]]:
        """GET /v1/managed/hooks — return every subscription.

        No pagination today (the in-memory store is small). When persistence
        lands, this will switch to async-iterator auto-pagination matching
        the Documents/Employees/Agents pattern.
        """
        resp = await self._client._request("GET", self._PATH)
        return (resp or {}).get("data", [])
