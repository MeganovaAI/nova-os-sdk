"""Messages resource — non-streaming create."""

from __future__ import annotations

import json

import httpx
import pytest

from nova_os import Client


def _mock_transport(handler):
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_messages_create_basic() -> None:
    captured = {}

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/managed/agents/my-agent/messages"
        captured["body"] = json.loads(req.content)
        return httpx.Response(200, json={"id": "msg_123", "role": "assistant", "content": "Hello!"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        resp = await c.messages.create(
            "my-agent",
            messages=[{"role": "user", "content": "Hello"}],
        )

    assert resp["id"] == "msg_123"
    assert resp["role"] == "assistant"
    # stream: false must always be sent
    assert captured["body"]["stream"] is False
    assert captured["body"]["messages"] == [{"role": "user", "content": "Hello"}]


@pytest.mark.asyncio
async def test_messages_create_with_metadata_brain_flag() -> None:
    captured = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(req.content)
        return httpx.Response(200, json={"id": "msg_456", "role": "assistant", "content": "Done"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        resp = await c.messages.create(
            "my-agent",
            messages=[{"role": "user", "content": "Deep research please"}],
            metadata={"brain": True, "stream_events": True},
            model="gemini/gemini-2.5-flash",
            max_tokens=1024,
        )

    assert resp["id"] == "msg_456"
    assert captured["body"]["metadata"] == {"brain": True, "stream_events": True}
    assert captured["body"]["model"] == "gemini/gemini-2.5-flash"
    assert captured["body"]["max_tokens"] == 1024
    # Optional fields NOT passed should be absent from the body
    assert "temperature" not in captured["body"]
    assert "system" not in captured["body"]
