"""Client constructor + auth + base error parsing."""

from __future__ import annotations

import json

import httpx
import pytest

from nova_os import Client
from nova_os.errors import NotFoundError, RateLimitedError


def _mock_transport(handler):
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_client_attaches_bearer_token() -> None:
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen["auth"] = req.headers.get("authorization", "")
        return httpx.Response(200, json={"data": []})

    transport = _mock_transport(handler)
    async with Client(base_url="https://test.local", api_key="my-key", transport=transport) as c:
        await c._request("GET", "/v1/managed/agents")

    assert seen["auth"] == "Bearer my-key"


@pytest.mark.asyncio
async def test_404_raises_not_found_error() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"type": "not_found_error", "message": "no such agent"})

    transport = _mock_transport(handler)
    async with Client(base_url="https://test.local", api_key="k", transport=transport) as c:
        with pytest.raises(NotFoundError) as ei:
            await c._request("GET", "/v1/managed/agents/nope")

    assert "no such agent" in str(ei.value)


@pytest.mark.asyncio
async def test_429_raises_rate_limited_with_retry_after() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            json={"type": "rate_limit_error", "message": "slow down", "retry_after": 12},
        )

    transport = _mock_transport(handler)
    async with Client(base_url="https://test.local", api_key="k", transport=transport) as c:
        with pytest.raises(RateLimitedError) as ei:
            await c._request("GET", "/v1/managed/agents")

    assert ei.value.retry_after == 12


@pytest.mark.asyncio
async def test_client_aclose_idempotent() -> None:
    c = Client(base_url="https://test.local", api_key="k")
    await c.aclose()
    await c.aclose()  # second aclose must not raise
