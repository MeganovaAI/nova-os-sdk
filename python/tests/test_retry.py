"""Auto-retry on transient failures for idempotent verbs."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from nova_os._retry import RetryConfig, with_retry


@pytest.mark.asyncio
async def test_no_retry_on_success() -> None:
    calls = 0

    async def op() -> str:
        nonlocal calls
        calls += 1
        return "ok"

    res = await with_retry(op, RetryConfig())
    assert res == "ok"
    assert calls == 1


@pytest.mark.asyncio
async def test_retries_on_transient_error() -> None:
    calls = 0

    async def op() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TransientNetworkError("connection reset")
        return "ok"

    cfg = RetryConfig(max_attempts=5, base_delay_sec=0.001)
    res = await with_retry(op, cfg)
    assert res == "ok"
    assert calls == 3


@pytest.mark.asyncio
async def test_gives_up_after_max_attempts() -> None:
    calls = 0

    async def op() -> str:
        nonlocal calls
        calls += 1
        raise TransientNetworkError("bad")

    cfg = RetryConfig(max_attempts=3, base_delay_sec=0.001)
    with pytest.raises(TransientNetworkError):
        await with_retry(op, cfg)
    assert calls == 3


@pytest.mark.asyncio
async def test_does_not_retry_non_transient() -> None:
    calls = 0

    async def op() -> str:
        nonlocal calls
        calls += 1
        raise ValueError("permanent failure — not retryable")

    cfg = RetryConfig(max_attempts=5, base_delay_sec=0.001)
    with pytest.raises(ValueError):
        await with_retry(op, cfg)
    assert calls == 1


# A test-local exception class so we control transient detection
class TransientNetworkError(Exception):
    """Simulates an httpx transport error or 5xx wrapping."""


# Patch is_transient to recognize our test class
@pytest.fixture(autouse=True)
def patch_transient(monkeypatch: Any) -> None:
    from nova_os import _retry

    def is_transient(exc: BaseException) -> bool:
        return isinstance(exc, TransientNetworkError)

    monkeypatch.setattr(_retry, "is_transient", is_transient)
