"""Messages resource — /v1/managed/agents/{id}/messages."""

from __future__ import annotations

from typing import Any

from nova_os.resources._base import Resource


class Messages(Resource):
    """Send messages to an agent. Streaming + custom-tool inline are
    wired in Phase 3.2 via the `c.messages.stream(...)` context manager."""

    async def create(
        self,
        agent_id: str,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST /v1/managed/agents/{agent_id}/messages — non-streaming.

        Streaming context manager lands in Phase 3.2.
        """
        body: dict[str, Any] = {"messages": messages, "stream": False}
        if model is not None:
            body["model"] = model
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if temperature is not None:
            body["temperature"] = temperature
        if system is not None:
            body["system"] = system
        if tools is not None:
            body["tools"] = tools
        if metadata is not None:
            body["metadata"] = metadata
        return await self._client._request(
            "POST",
            f"/v1/managed/agents/{agent_id}/messages",
            json_body=body,
            idempotency_key=idempotency_key,
        )
