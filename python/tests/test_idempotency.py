"""Idempotency-Key header propagation on POST resource methods."""

from __future__ import annotations

import httpx
import pytest

from nova_os import Client


def _mock_transport(handler):
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_idempotency_key_reaches_wire_on_agents_create() -> None:
    """Idempotency-Key kwarg must appear verbatim in request headers."""
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["idem"] = req.headers.get("idempotency-key", "")
        return httpx.Response(201, json={"id": "foo", "type": "skill"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        await c.agents.create(
            id="foo",
            type="skill",
            idempotency_key="my-idem-key-123",
        )

    assert captured["idem"] == "my-idem-key-123"


@pytest.mark.asyncio
async def test_no_idempotency_key_header_when_not_set() -> None:
    """When idempotency_key is not passed, the header must be absent."""
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["idem"] = req.headers.get("idempotency-key", None)
        return httpx.Response(201, json={"id": "bar", "type": "skill"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        await c.agents.create(id="bar", type="skill")

    assert captured["idem"] is None


@pytest.mark.asyncio
async def test_idempotency_key_on_employees_create() -> None:
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["idem"] = req.headers.get("idempotency-key", "")
        return httpx.Response(201, json={"id": "emp1"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        await c.employees.create(id="emp1", idempotency_key="emp-idem-456")

    assert captured["idem"] == "emp-idem-456"


@pytest.mark.asyncio
async def test_idempotency_key_on_messages_create() -> None:
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["idem"] = req.headers.get("idempotency-key", "")
        return httpx.Response(200, json={"id": "msg1", "role": "assistant", "content": "hi"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        await c.messages.create(
            "my-agent",
            messages=[{"role": "user", "content": "hi"}],
            idempotency_key="msg-idem-789",
        )

    assert captured["idem"] == "msg-idem-789"
