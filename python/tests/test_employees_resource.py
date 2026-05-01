"""Employees resource — CRUD + pagination."""

from __future__ import annotations

import httpx
import pytest

from nova_os import Client


def _mock_transport(handler):
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_create_employee_returns_employee_dict() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/managed/employees"
        return httpx.Response(201, json={"id": "alice", "name": "Alice"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        emp = await c.employees.create(id="alice", name="Alice")

    assert emp["id"] == "alice"
    assert emp["name"] == "Alice"


@pytest.mark.asyncio
async def test_get_employee() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/managed/employees/alice"
        return httpx.Response(200, json={"id": "alice", "name": "Alice"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        emp = await c.employees.get("alice")
    assert emp["id"] == "alice"


@pytest.mark.asyncio
async def test_update_employee() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "PUT"
        assert req.url.path == "/v1/managed/employees/alice"
        return httpx.Response(200, json={"id": "alice", "name": "Alice Updated"})

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        emp = await c.employees.update("alice", name="Alice Updated")
    assert emp["name"] == "Alice Updated"


@pytest.mark.asyncio
async def test_delete_employee_returns_none() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(204)

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        result = await c.employees.delete("alice")
    assert result is None


@pytest.mark.asyncio
async def test_list_employees_paginates() -> None:
    pages = [
        {"data": [{"id": "alice"}, {"id": "bob"}], "has_more": True, "next_cursor": "page2"},
        {"data": [{"id": "carol"}], "has_more": False, "next_cursor": None},
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
        ids = [e["id"] async for e in c.employees.list()]

    assert ids == ["alice", "bob", "carol"]
