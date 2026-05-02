"""Anthropic SDK compatibility shim.

Nova OS's ``POST /v1/messages`` endpoint mirrors Anthropic's Messages API
1:1 for the compat surface — same request shape, same response shape, same
SSE event names. Code written against ``anthropic.Anthropic(base_url=...)``
works against Nova OS unchanged.

Per-call routing to a specific Nova OS persona is done via the standard
Anthropic ``metadata`` field — Nova OS reads ``metadata.agent_id`` from the
request body and dispatches accordingly. Brain orchestration fires
automatically when the resolved persona has ``brain: true`` in its
frontmatter.

Usage::

    from nova_os import AnthropicCompatClient

    c = AnthropicCompatClient(
        base_url="https://nova.partner.com",  # bare server URL — SDK appends /v1/messages itself
        api_key="msk_live_...",
    )
    # `c` is an `anthropic.Anthropic` instance — full SDK API available.
    msg = c.messages.create(
        model="anthropic/claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": "hello"}],
        metadata={"agent_id": "invoice-bot"},  # routes to that agent + Brain dispatch when configured
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

    ``base_url`` is the bare Nova OS server URL (e.g. ``https://nova.partner.com``).
    The Anthropic SDK appends ``/v1/messages`` itself when calling
    ``c.messages.create(...)`` — do NOT pre-append ``/v1/managed`` or any
    other path segment.

    Pass any other ``anthropic.Anthropic`` kwarg through (timeout, max_retries,
    http_client, etc.).

    For per-call agent selection, use the standard Anthropic ``metadata``
    field::

        msg = c.messages.create(
            model="anthropic/claude-opus-4-7",
            messages=[...],
            metadata={"agent_id": "invoice-bot"},
        )

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

    return Anthropic(base_url=base_url.rstrip("/"), api_key=api_key, **kwargs)


__all__ = ["AnthropicCompatClient"]
