"""Anthropic SDK compatibility shim.

Nova OS's ``/v1/managed/*`` endpoints mirror Anthropic Managed Agents 1:1
for the compat surface. Code written against ``anthropic.Anthropic(base_url=...)``
works against Nova OS unchanged. This module exposes a tiny factory that
pre-fills the base_url with Nova OS's compat path and forwards everything
else to ``anthropic.Anthropic(...)`` so consumers don't have to remember
the suffix.

Usage::

    from nova_os import AnthropicCompatClient

    c = AnthropicCompatClient(
        base_url="https://nova.partner.com",  # WITHOUT /v1/managed suffix
        api_key="msk_live_...",
    )
    # `c` is an `anthropic.Anthropic` instance — full SDK API available.
    msg = c.messages.create(
        model="anthropic/claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": "hello"}],
    )

The official ``anthropic`` package is an optional dep — partners install it
themselves. We do NOT vendor it.
"""

from __future__ import annotations

from typing import Any


def AnthropicCompatClient(
    base_url: str,
    api_key: str,
    **kwargs: Any,
):
    """Return a configured ``anthropic.Anthropic`` instance pointed at Nova OS.

    ``base_url`` is the Nova OS server URL WITHOUT the ``/v1/managed`` suffix —
    we append it for you. Pass any other ``anthropic.Anthropic`` kwarg through
    (timeout, max_retries, http_client, etc.).

    Raises:
        ImportError: when the ``anthropic`` package is not installed.
    """
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise ImportError(
            "AnthropicCompatClient requires the `anthropic` package. "
            "Install with `pip install anthropic`."
        ) from exc

    base = base_url.rstrip("/")
    if not base.endswith("/v1/managed"):
        base = f"{base}/v1/managed"
    return Anthropic(base_url=base, api_key=api_key, **kwargs)


__all__ = ["AnthropicCompatClient"]
