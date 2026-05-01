"""Streaming context manager for /v1/managed/agents/{id}/messages.

Mode A custom-tool inline: partners hold an open SSE connection, intercept
`custom_tool_use` events, compute results, and submit them via
`stream.submit_tool_result(tool_use_id, output)` — Nova OS resumes the
agent loop on the original streaming connection.

Implementation note: httpx's MockTransport is fully buffered — it doesn't
stream `aiter_lines()` chunk-by-chunk. For real network usage, the
underlying `client.stream()` opens a chunked response and yields lines
as they arrive. The same code path works for both.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator

from nova_os._sse import parse_lines

if TYPE_CHECKING:
    from nova_os.client import Client


class MessageStream:
    """Async context manager exposing the SSE event stream + Mode A submit.

    Use:
        async with c.messages.stream(agent_id, messages=...) as s:
            async for event in s:
                if event["event"] == "custom_tool_use":
                    result = await my_handler(event["data"]["input"])
                    await s.submit_tool_result(event["data"]["id"], result)
    """

    def __init__(
        self,
        client: "Client",
        agent_id: str,
        body: dict[str, Any],
        *,
        message_id: str | None = None,
    ) -> None:
        self._client = client
        self._agent_id = agent_id
        self._body = body
        self._message_id = message_id
        self._response_cm = None
        self._response = None

    async def __aenter__(self) -> "MessageStream":
        self._response_cm = self._client._http.stream(
            "POST",
            f"/v1/managed/agents/{self._agent_id}/messages",
            json=self._body,
        )
        self._response = await self._response_cm.__aenter__()
        if self._response.status_code >= 400:
            # Surface as typed error; consume body first so the connection
            # is released cleanly before raising.
            try:
                content = await self._response.aread()
                from nova_os.errors import parse_error_response
                import json as _json
                try:
                    payload = _json.loads(content)
                except (_json.JSONDecodeError, ValueError):
                    payload = content.decode("utf-8", errors="replace")
                raise parse_error_response(self._response.status_code, payload)
            finally:
                await self._response_cm.__aexit__(None, None, None)
                self._response_cm = None
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        if self._response_cm is not None:
            await self._response_cm.__aexit__(*exc_info)
            self._response_cm = None

    def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        return self._iter_events()

    async def _iter_events(self) -> AsyncIterator[dict[str, Any]]:
        if self._response is None:
            raise RuntimeError("MessageStream used outside of `async with`")

        async def lines() -> AsyncIterator[str]:
            async for line in self._response.aiter_lines():
                yield line

        async for event in parse_lines(lines()):
            # Snoop for the message_id from the `done` event so callers
            # who didn't pass one upfront still get one for late submits.
            if (
                event.get("event") == "done"
                and isinstance(event.get("data"), dict)
                and event["data"].get("message_id")
                and self._message_id is None
            ):
                self._message_id = event["data"]["message_id"]
            yield event

    async def submit_tool_result(
        self,
        tool_use_id: str,
        output: str,
        *,
        is_error: bool = False,
    ) -> None:
        """POST /v1/managed/agents/messages/{message_id}/custom_tool_results.

        Caller MUST pass `message_id=` to `c.messages.stream(...)` upfront
        if they want to submit results before the `done` event arrives.
        """
        if self._message_id is None:
            raise RuntimeError(
                "submit_tool_result requires a known message_id; "
                "pass message_id= to c.messages.stream(...) at start"
            )
        await self._client._request(
            "POST",
            f"/v1/managed/agents/messages/{self._message_id}/custom_tool_results",
            json_body={
                "tool_use_id": tool_use_id,
                "output": output,
                "is_error": is_error,
            },
        )


__all__ = ["MessageStream"]
