"""Agents resource — CRUD + pagination."""

from __future__ import annotations

import httpx
import pytest

from nova_os import Client


def _mock_transport(handler):
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_create_agent_returns_agent_dict() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/managed/agents"
        return httpx.Response(201, json={"id": "marketing-assistant", "type": "skill"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        agent = await c.agents.create(id="marketing-assistant", type="skill")

    assert agent["id"] == "marketing-assistant"
    assert agent["type"] == "skill"


@pytest.mark.asyncio
async def test_get_agent() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/managed/agents/foo"
        return httpx.Response(200, json={"id": "foo", "type": "skill"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        agent = await c.agents.get("foo")
    assert agent["id"] == "foo"


@pytest.mark.asyncio
async def test_update_agent() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "PUT"
        return httpx.Response(200, json={"id": "foo", "max_turns": 20})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        agent = await c.agents.update("foo", max_turns=20)
    assert agent["max_turns"] == 20


@pytest.mark.asyncio
async def test_delete_agent_returns_none() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(204)

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        result = await c.agents.delete("foo")
    assert result is None


@pytest.mark.asyncio
async def test_list_paginates_until_has_more_false() -> None:
    pages = [
        {"data": [{"id": "a"}, {"id": "b"}], "has_more": True, "next_cursor": "page2"},
        {"data": [{"id": "c"}], "has_more": False, "next_cursor": None},
    ]
    page_idx = [0]

    def handler(req: httpx.Request) -> httpx.Response:
        idx = page_idx[0]
        page_idx[0] += 1
        if idx == 0:
            assert "cursor" not in req.url.params
        else:
            assert req.url.params["cursor"] == "page2"
        return httpx.Response(200, json=pages[idx])

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        ids = [a["id"] async for a in c.agents.list()]

    assert ids == ["a", "b", "c"]
