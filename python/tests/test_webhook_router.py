"""WebhookRouter — receives Nova OS Mode B custom_tool dispatches."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

import pytest

from nova_os.callbacks import WebhookRouter


def _sign(secret: str, tool_use_id: str, body: bytes, ts: int | None = None) -> tuple[str, int]:
    if ts is None:
        ts = int(time.time())
    sign_input = f"{ts}.{tool_use_id}.".encode() + body
    sig_hex = hmac.new(secret.encode(), sign_input, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig_hex}", ts


@pytest.mark.asyncio
async def test_router_dispatches_to_registered_handler() -> None:
    router = WebhookRouter(secret="test-secret-1234567890")

    @router.tool("fetch_invoice")
    async def fetch_invoice(input: dict[str, Any], ctx: dict[str, Any]) -> str:
        assert input["invoice_id"] == "INV-9912"
        return "INV-9912 amount $42"

    body_dict = {
        "tool_use_id": "toolu_test_1",
        "agent_id": "invoice-bot",
        "name": "fetch_invoice",
        "input": {"invoice_id": "INV-9912"},
    }
    body = json.dumps(body_dict).encode()
    sig, _ = _sign("test-secret-1234567890", "toolu_test_1", body)

    result = await router.handle(
        body=body,
        headers={"X-Nova-Signature": sig, "X-Nova-Idempotency-Key": "toolu_test_1"},
    )
    assert result["output"] == "INV-9912 amount $42"
    assert result["is_error"] is False


@pytest.mark.asyncio
async def test_router_rejects_invalid_signature() -> None:
    router = WebhookRouter(secret="real-secret")

    @router.tool("fetch_invoice")
    async def fetch_invoice(input: dict, ctx: dict) -> str:
        return "should not reach"

    body = json.dumps({"tool_use_id": "x", "name": "fetch_invoice", "input": {}}).encode()
    bad_sig, _ = _sign("WRONG-SECRET", "x", body)

    with pytest.raises(PermissionError):
        await router.handle(
            body=body,
            headers={"X-Nova-Signature": bad_sig, "X-Nova-Idempotency-Key": "x"},
        )


@pytest.mark.asyncio
async def test_router_rejects_outside_replay_window() -> None:
    router = WebhookRouter(secret="s", replay_window_sec=10)

    @router.tool("t")
    async def _(_input: dict, _ctx: dict) -> str:
        return "x"

    body = b'{"tool_use_id":"x","name":"t","input":{}}'
    old_ts = int(time.time()) - 9999
    sig, _ = _sign("s", "x", body, ts=old_ts)

    with pytest.raises(PermissionError):
        await router.handle(
            body=body,
            headers={"X-Nova-Signature": sig, "X-Nova-Idempotency-Key": "x"},
        )


@pytest.mark.asyncio
async def test_router_unknown_tool_returns_error_payload() -> None:
    router = WebhookRouter(secret="s")
    body = b'{"tool_use_id":"x","name":"unknown","input":{}}'
    sig, _ = _sign("s", "x", body)

    result = await router.handle(
        body=body,
        headers={"X-Nova-Signature": sig, "X-Nova-Idempotency-Key": "x"},
    )
    assert result["is_error"] is True
    assert "unknown" in result["output"].lower() or "not registered" in result["output"].lower()


@pytest.mark.asyncio
async def test_router_dedupes_by_idempotency_key() -> None:
    router = WebhookRouter(secret="s")
    call_count = 0

    @router.tool("t")
    async def t(input: dict, ctx: dict) -> str:
        nonlocal call_count
        call_count += 1
        return f"call #{call_count}"

    body = b'{"tool_use_id":"toolu_dedupe","name":"t","input":{}}'
    sig, _ = _sign("s", "toolu_dedupe", body)
    headers = {"X-Nova-Signature": sig, "X-Nova-Idempotency-Key": "toolu_dedupe"}

    r1 = await router.handle(body=body, headers=headers)
    r2 = await router.handle(body=body, headers=headers)
    assert r1["output"] == r2["output"] == "call #1"
    assert call_count == 1
