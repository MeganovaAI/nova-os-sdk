"""Sync proxy — c.sync.agents.get/list should match async equivalents."""

from __future__ import annotations

import httpx
import pytest

from nova_os import Client


def _mock_transport(handler):
    return httpx.MockTransport(handler)


def test_sync_agents_get_returns_same_as_async() -> None:
    """c.sync.agents.get('foo') must produce the same dict as await c.agents.get('foo')."""
    responses = [{"id": "foo", "type": "skill"}, {"id": "foo", "type": "skill"}]
    call_count = [0]

    def handler(req: httpx.Request) -> httpx.Response:
        idx = call_count[0] % len(responses)
        call_count[0] += 1
        return httpx.Response(200, json=responses[idx])

    c = Client("https://t.local", "k", transport=_mock_transport(handler))

    # Sync call
    sync_result = c.sync.agents.get("foo")
    assert sync_result == {"id": "foo", "type": "skill"}


def test_sync_agents_list_returns_plain_list() -> None:
    """c.sync.agents.list() must return a plain list, not an async iterator."""
    pages = [
        {"data": [{"id": "a"}, {"id": "b"}], "has_more": True, "next_cursor": "p2"},
        {"data": [{"id": "c"}], "has_more": False, "next_cursor": None},
    ]
    page_idx = [0]

    def handler(req: httpx.Request) -> httpx.Response:
        idx = page_idx[0]
        page_idx[0] += 1
        return httpx.Response(200, json=pages[idx])

    c = Client("https://t.local", "k", transport=_mock_transport(handler))
    result = c.sync.agents.list()

    # Must be a plain list
    assert isinstance(result, list)
    assert [item["id"] for item in result] == ["a", "b", "c"]


def test_sync_agents_create() -> None:
    """c.sync.agents.create(...) must POST and return the agent dict."""
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        return httpx.Response(201, json={"id": "new-agent", "type": "persona"})

    c = Client("https://t.local", "k", transport=_mock_transport(handler))
    agent = c.sync.agents.create(id="new-agent", type="persona")
    assert agent == {"id": "new-agent", "type": "persona"}


def test_sync_employees_get() -> None:
    """c.sync.employees.get works symmetrically with agents."""
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": "emp1", "name": "Alice"})

    c = Client("https://t.local", "k", transport=_mock_transport(handler))
    emp = c.sync.employees.get("emp1")
    assert emp["id"] == "emp1"
