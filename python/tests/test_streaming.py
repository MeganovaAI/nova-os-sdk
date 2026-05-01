"""Streaming context manager — Mode A SSE consumption."""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from nova_os import Client


def _sse_body(*events: tuple[str, str]) -> bytes:
    """Build a fake SSE response body from (event, data) tuples."""
    out = []
    for ev, data in events:
        out.append(f"event: {ev}\ndata: {data}\n\n")
    return "".join(out).encode()


@pytest.mark.asyncio
async def test_stream_yields_events() -> None:
    body = _sse_body(
        ("text", '{"type":"text","content":"hello"}'),
        ("text", '{"type":"text","content":" world"}'),
        ("done", '{"type":"done","status":"completed","message_id":"msg_1"}'),
    )

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        return httpx.Response(
            200,
            headers={"Content-Type": "text/event-stream"},
            content=body,
        )

    transport = httpx.MockTransport(handler)
    async with Client("https://t.local", "k", transport=transport) as c:
        events = []
        async with c.messages.stream(
            agent_id="invoice-bot",
            messages=[{"role": "user", "content": "hi"}],
        ) as s:
            async for e in s:
                events.append(e)

    types = [e["data"]["type"] for e in events]
    assert types == ["text", "text", "done"]


@pytest.mark.asyncio
async def test_stream_submit_tool_result() -> None:
    """Mode A: partner intercepts custom_tool_use, submits result mid-stream."""
    submit_calls = []

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/custom_tool_results"):
            submit_calls.append(req.url.path)
            return httpx.Response(202)
        # Streaming endpoint
        body = _sse_body(
            ("custom_tool_use", '{"type":"custom_tool_use","id":"toolu_1","name":"fetch","input":{}}'),
            ("done", '{"type":"done","status":"completed","message_id":"msg_42"}'),
        )
        return httpx.Response(
            200,
            headers={"Content-Type": "text/event-stream"},
            content=body,
        )

    transport = httpx.MockTransport(handler)
    async with Client("https://t.local", "k", transport=transport) as c:
        async with c.messages.stream(
            agent_id="invoice-bot",
            messages=[{"role": "user", "content": "fetch invoice"}],
            message_id="msg_42",  # caller provides upfront for mid-stream submit
        ) as s:
            async for e in s:
                if e["event"] == "custom_tool_use":
                    await s.submit_tool_result(e["data"]["id"], "INV-9912 amount $42")

    assert any("msg_42/custom_tool_results" in p for p in submit_calls)
