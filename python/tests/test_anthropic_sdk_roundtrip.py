"""Recorded fixture test: Anthropic SDK call replays unchanged against
a LibraOS-shaped mock response. This is the contract gate — if this
test breaks, drop-in Anthropic SDK compat is broken.

The test intercepts the SDK's outbound httpx call via httpx.MockTransport
(supported in anthropic>=0.30 via the http_client= kwarg) and verifies:
  1. The SDK sends the right request shape to LibraOS.
  2. The SDK targets the exact path LibraOS implements (/v1/messages).
  3. The standard Anthropic ``metadata`` field passes through, so partners
     can route per-call via ``metadata={"agent_id": "..."}``.
  4. The SDK parses a LibraOS-shaped response without error.
"""

from __future__ import annotations

import json

import httpx
import pytest

anthropic = pytest.importorskip("anthropic")

from libraos import AnthropicCompatClient


@pytest.fixture
def libraos_mock_response() -> dict:
    """The shape LibraOS's /v1/messages compat endpoint returns.

    Mirrors Anthropic Messages API 1:1 with LibraOS extensions
    (model_used, fallback_triggered) appended — unknown fields are
    silently ignored by the Anthropic SDK.
    """
    return {
        "id": "msg_01ABC",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello from LibraOS"}],
        "model": "anthropic/claude-opus-4-7",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 5, "output_tokens": 4},
        # LibraOS extensions — Anthropic SDK ignores unknown fields gracefully.
        "model_used": "anthropic/claude-opus-4-7",
        "fallback_triggered": False,
    }


def test_anthropic_sdk_messages_create_against_libraos(libraos_mock_response: dict) -> None:
    """An Anthropic SDK consumer sends the same request shape Anthropic
    expects, and LibraOS must respond with a shape the SDK can parse.
    This test verifies the round-trip by intercepting the SDK's outbound
    HTTP call via httpx.MockTransport.

    anthropic>=0.30 accepts ``http_client=httpx.Client(transport=...)`` which
    is how we hook in the mock transport.

    CRITICAL: base_url is the BARE LibraOS server URL — the SDK appends
    /v1/messages itself. Pre-appending /v1/managed (a v0.1.0-alpha bug
    in the AnthropicCompatClient factory, fixed in v1.0.0) breaks path
    resolution.
    """
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["method"] = req.method
        captured["path"] = req.url.path
        captured["auth_header"] = req.headers.get("authorization", "")
        captured["x_api_key"] = req.headers.get("x-api-key", "")
        captured["body"] = json.loads(req.content)
        return httpx.Response(200, json=libraos_mock_response)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)

    client = anthropic.Anthropic(
        base_url="https://nova.partner.com",          # BARE — SDK appends /v1/messages itself
        api_key="msk_live_test",
        http_client=http_client,
    )

    msg = client.messages.create(
        model="anthropic/claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": "ping"}],
        metadata={"agent_id": "invoice-bot"},   # LibraOS routes by this field
    )

    # --- Outbound path check (strict) ---
    # LibraOS implements POST /v1/messages. Any deviation (e.g. /v1/managed/v1/messages
    # caused by base_url pre-suffixing) means partners using vanilla Anthropic SDK
    # against our compat surface are getting 404s and we'd never know.
    assert captured["method"] == "POST"
    assert captured["path"] == "/v1/messages", (
        f"Anthropic SDK path resolution drifted — expected /v1/messages, got {captured['path']!r}"
    )

    # --- Auth header (SDK uses either Authorization: Bearer or x-api-key) ---
    has_auth = (
        captured["auth_header"].startswith("Bearer ")
        or bool(captured["x_api_key"])
    )
    assert has_auth, (
        "SDK did not send authentication header "
        f"(authorization={captured['auth_header']!r}, x-api-key={captured['x_api_key']!r})"
    )

    # --- Body shape ---
    assert captured["body"]["model"] == "anthropic/claude-opus-4-7"
    assert captured["body"]["messages"][0]["content"] == "ping"
    assert captured["body"]["max_tokens"] == 1024

    # The metadata field MUST pass through unchanged — this is how partners
    # route to a specific LibraOS persona (LibraOS reads metadata.agent_id
    # server-side and dispatches accordingly, with Brain orchestration when
    # the resolved agent has brain:true).
    assert captured["body"]["metadata"]["agent_id"] == "invoice-bot", (
        "metadata.agent_id was dropped on the wire — LibraOS persona dispatch broken"
    )

    # --- Response parsing ---
    assert msg.id == "msg_01ABC"
    assert msg.role == "assistant"
    assert msg.model == "anthropic/claude-opus-4-7"
    assert len(msg.content) == 1
    assert msg.content[0].text == "Hello from LibraOS"
    assert msg.stop_reason == "end_turn"
    assert msg.usage.input_tokens == 5
    assert msg.usage.output_tokens == 4


def test_anthropic_compat_client_does_not_pre_suffix_base_url(libraos_mock_response: dict) -> None:
    """The AnthropicCompatClient factory MUST pass base_url through unchanged
    to the Anthropic SDK. Pre-appending /v1/managed (the v0.1.0-alpha
    behaviour) breaks path resolution because the Anthropic SDK then targets
    /v1/managed/v1/messages — which LibraOS does not implement.
    """
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["path"] = req.url.path
        return httpx.Response(200, json=libraos_mock_response)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)

    client = AnthropicCompatClient(
        base_url="https://nova.partner.com",
        api_key="msk_live_test",
        http_client=http_client,
    )

    client.messages.create(
        model="anthropic/claude-opus-4-7",
        max_tokens=64,
        messages=[{"role": "user", "content": "x"}],
    )

    assert captured["path"] == "/v1/messages", (
        f"AnthropicCompatClient regressed to pre-suffixing base_url — "
        f"SDK now targets {captured['path']!r}, breaking partner integrations"
    )


def test_anthropic_compat_client_strips_trailing_slash(libraos_mock_response: dict) -> None:
    """Trailing slash on base_url should not double up the path."""
    captured: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured["path"] = req.url.path
        return httpx.Response(200, json=libraos_mock_response)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)

    client = AnthropicCompatClient(
        base_url="https://nova.partner.com/",   # trailing slash
        api_key="k",
        http_client=http_client,
    )
    client.messages.create(
        model="anthropic/claude-opus-4-7",
        max_tokens=64,
        messages=[{"role": "user", "content": "x"}],
    )

    assert captured["path"] == "/v1/messages", (
        f"trailing slash mishandled — got {captured['path']!r}"
    )
