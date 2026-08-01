"""Messages resource — /v1/messages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from libraos.models import Message, parse_message
from libraos.resources._base import Resource

if TYPE_CHECKING:
    from libraos.streaming import MessageStream


class Messages(Resource):
    """Send messages to an agent.

    For streaming + Mode A custom-tool inline, use the
    ``c.messages.stream(...)`` async context manager. ``create()`` below
    is the non-streaming variant.
    """

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
    ) -> Message:
        """POST /v1/messages — non-streaming.

        Returns a dict-compatible :class:`~libraos.models.Message`:
        ``resp["content"][0]["text"]`` and ``resp.content[0].text`` both work,
        and ``resp.text`` joins all text blocks.
        """
        # /v1/messages requires a `model` field for Anthropic-SDK wire
        # compatibility even though routing uses metadata.agent_id (the
        # server treats model as cosmetic and echoes it back). Default it
        # to the agent id so callers never need to pass it.
        body: dict[str, Any] = {
            "messages": messages,
            "stream": False,
            "model": model if model is not None else agent_id,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if temperature is not None:
            body["temperature"] = temperature
        if system is not None:
            body["system"] = system
        if tools is not None:
            body["tools"] = tools
        merged_metadata = dict(metadata or {})
        merged_metadata["agent_id"] = agent_id
        body["metadata"] = merged_metadata
        payload = await self._client._request(
            "POST",
            "/v1/messages",
            json_body=body,
            idempotency_key=idempotency_key,
        )
        return parse_message(payload)

    def stream(
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
        message_id: str | None = None,
    ) -> "MessageStream":
        """Open a streaming chat — returns an async context manager.

        Use:
            async with c.messages.stream(agent_id, messages=[...]) as s:
                async for event in s:
                    ...

        `message_id` is optional but required up-front if the caller wants to
        `submit_tool_result()` before the `done` event arrives. Pass any
        deterministic id you control (e.g. uuid4) and LibraOS will use it
        for the response identifier.
        """
        from libraos.streaming import MessageStream

        # See create(): model is required on the wire but cosmetic —
        # default to the agent id.
        body: dict[str, Any] = {
            "messages": messages,
            "stream": True,
            "model": model if model is not None else agent_id,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if temperature is not None:
            body["temperature"] = temperature
        if system is not None:
            body["system"] = system
        if tools is not None:
            body["tools"] = tools
        merged_metadata = dict(metadata or {})
        merged_metadata["agent_id"] = agent_id
        body["metadata"] = merged_metadata
        return MessageStream(self._client, agent_id, body, message_id=message_id)
