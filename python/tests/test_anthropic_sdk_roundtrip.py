"""Recorded fixture test: Anthropic SDK call replays unchanged against
a Nova OS-shaped mock response. This is the contract gate — if this
test breaks, drop-in Anthropic SDK compat is broken.

The test intercepts the SDK's outbound httpx call via httpx.MockTransport
(supported in anthropic>=0.30 via the http_client= kwarg) and verifies:
  1. The SDK sends the right request shape to Nova OS.
  2. The SDK parses a Nova OS-shaped response without error.
"""

from __future__ import annotations

import json

import httpx
import pytest

anthropic = pytest.importorskip("anthropic")


@pytest.fixture
def nova_os_mock_response() -> dict:
    """The shape Nova OS's /v1/managed compat endpoint returns.

    Mirrors Anthropic Messages API 1:1 with Nova OS extensions
    (model_used, fallback_triggered) appended — unknown fields are
    silently ignored by the Anthropic SDK.
    """
    return {
        "id": "msg_01ABC",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello from Nova OS"}],
        "model": "anthropic/claude-opus-4-7",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 5, "output_tokens": 4},
        # Nova OS extensions — Anthropic SDK ignores unknown fields gracefully.
        "model_used": "anthropic/claude-opus-4-7",
        "fallback_triggered": False,
    }


def test_anthropic_sdk_messages_create_against_nova_os(nova_os_mock_response: dict) -> None:
    """An Anthropic SDK consumer sends the same request shape Anthropic
    Managed Agents expects, and Nova OS must respond with a shape the SDK
    can parse. This test verifies the round-trip by intercepting the SDK's
    outbound HTTP call via httpx.MockTransport.

    anthropic>=0.30 accepts `http_client=httpx.Client(transport=...)` which
    is how we hook in the mock transport.
    """
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["method"] = req.method
        captured["path"] = req.url.path
        # Collect auth header — SDK may use Authorization: Bearer or x-api-key.
        captured["auth_header"] = req.headers.get("authorization", "")
        captured["x_api_key"] = req.headers.get("x-api-key", "")
        captured["body"] = json.loads(req.content)
        return httpx.Response(200, json=nova_os_mock_response)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)

    client = anthropic.Anthropic(
        base_url="https://nova.partner.com/v1/managed",
        api_key="msk_live_test",
        http_client=http_client,
    )

    msg = client.messages.create(
        model="anthropic/claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": "ping"}],
    )

    # --- Outbound shape checks ---
    # The SDK must POST to a path ending in /messages (relative to base_url).
    assert captured["method"] == "POST"
    assert captured["path"].endswith("/messages"), (
        f"Expected path ending in /messages, got: {captured['path']}"
    )
    # Auth: SDK uses either Authorization: Bearer <key> or x-api-key header.
    has_auth = (
        captured["auth_header"].startswith("Bearer ")
        or bool(captured["x_api_key"])
    )
    assert has_auth, (
        "SDK did not send authentication header "
        f"(authorization={captured['auth_header']!r}, x-api-key={captured['x_api_key']!r})"
    )
    assert captured["body"]["model"] == "anthropic/claude-opus-4-7"
    assert captured["body"]["messages"][0]["content"] == "ping"
    assert captured["body"]["max_tokens"] == 1024

    # --- Response parsing ---
    # The Anthropic SDK must parse a Nova OS-shaped response cleanly.
    assert msg.id == "msg_01ABC"
    assert msg.role == "assistant"
    assert msg.model == "anthropic/claude-opus-4-7"
    assert len(msg.content) == 1
    assert msg.content[0].text == "Hello from Nova OS"
    assert msg.stop_reason == "end_turn"
    assert msg.usage.input_tokens == 5
    assert msg.usage.output_tokens == 4
