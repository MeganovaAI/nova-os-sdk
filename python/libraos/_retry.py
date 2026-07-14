"""Auto-retry helper for idempotent verbs.

Retries are applied transparently to GET/PUT/DELETE on transient failures
(httpx.TransportError + 5xx). POST is NEVER auto-retried (Stripe SDK
convention) — POSTs that the SDK can compute a deterministic
Idempotency-Key for plumb the key into the request and let the server
dedupe; the client doesn't retry blindly.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
    base_delay_sec: float = 0.5
    max_delay_sec: float = 30.0
    backoff_factor: float = 2.0


def is_transient(exc: BaseException) -> bool:
    """Returns True if `exc` is a candidate for auto-retry.

    Transient = network/timeout failures + 5xx HTTP responses. Non-2xx
    that are NOT 5xx (e.g. 401/403/404/422) are deterministic and never
    retried.
    """
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return 500 <= exc.response.status_code < 600
    return False


async def with_retry(op: Callable[[], Awaitable[T]], cfg: RetryConfig) -> T:
    """Run `op()` up to `cfg.max_attempts` times, retrying transient errors.

    Backoff: `min(cfg.max_delay_sec, cfg.base_delay_sec * cfg.backoff_factor**attempt)`.
    """
    attempt = 0
    while True:
        try:
            return await op()
        except Exception as exc:
            attempt += 1
            if not is_transient(exc) or attempt >= cfg.max_attempts:
                raise
            delay = min(
                cfg.max_delay_sec,
                cfg.base_delay_sec * (cfg.backoff_factor ** (attempt - 1)),
            )
            logger.warning(
                "transient failure on attempt %d/%d: %s; retrying in %.2fs",
                attempt,
                cfg.max_attempts,
                exc,
                delay,
            )
            await asyncio.sleep(delay)


__all__ = ["RetryConfig", "with_retry", "is_transient"]
