"""Jobs resource — create / get / cancel / list."""

from __future__ import annotations

import httpx
import pytest

from nova_os import Client


def _mock_transport(handler):
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_create_job_returns_job_dict() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/managed/agents/jobs"
        return httpx.Response(
            202,
            json={"job_id": "job_abc", "status": "queued", "agent_id": "my-agent"},
        )

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        job = await c.jobs.create(
            "my-agent",
            messages=[{"role": "user", "content": "deep research on X"}],
        )

    assert job["job_id"] == "job_abc"
    assert job["status"] == "queued"


@pytest.mark.asyncio
async def test_get_job() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/managed/agents/jobs/job_abc"
        return httpx.Response(
            200, json={"job_id": "job_abc", "status": "running"}
        )

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        job = await c.jobs.get("job_abc")

    assert job["status"] == "running"


@pytest.mark.asyncio
async def test_cancel_job_returns_none() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/managed/agents/jobs/job_abc"
        return httpx.Response(204)

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        result = await c.jobs.cancel("job_abc")

    assert result is None


@pytest.mark.asyncio
async def test_list_jobs_paginates() -> None:
    pages = [
        {"data": [{"job_id": "j1"}, {"job_id": "j2"}], "has_more": True, "next_cursor": "p2"},
        {"data": [{"job_id": "j3"}], "has_more": False, "next_cursor": None},
    ]
    page_idx = [0]

    def handler(req: httpx.Request) -> httpx.Response:
        idx = page_idx[0]
        page_idx[0] += 1
        return httpx.Response(200, json=pages[idx])

    async with Client("https://t.local", "k", transport=_mock_transport(handler)) as c:
        ids = [j["job_id"] async for j in c.jobs.list()]

    assert ids == ["j1", "j2", "j3"]
