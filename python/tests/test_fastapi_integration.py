"""FastAPI integration mount for WebhookRouter."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

fastapi = pytest.importorskip("fastapi")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from nova_os.callbacks import WebhookRouter


def _sign(secret: str, tool_use_id: str, body: bytes) -> tuple[str, str]:
    ts = int(time.time())
    sign_input = f"{ts}.{tool_use_id}.".encode() + body
    sig_hex = hmac.new(secret.encode(), sign_input, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig_hex}", str(ts)


def test_fastapi_mount_dispatches_and_signs() -> None:
    router = WebhookRouter(secret="s-1234567890")

    @router.tool("fetch_invoice")
    async def fetch_invoice(input, ctx):
        return f"got {input['invoice_id']}"

    app = FastAPI()
    app.include_router(router.fastapi_router(), prefix="/nova")

    client = TestClient(app)
    body_obj = {"tool_use_id": "tu1", "name": "fetch_invoice", "input": {"invoice_id": "INV-1"}}
    body = json.dumps(body_obj).encode()
    sig, _ = _sign("s-1234567890", "tu1", body)

    resp = client.post(
        "/nova/",
        content=body,
        headers={
            "X-Nova-Signature": sig,
            "X-Nova-Idempotency-Key": "tu1",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["output"] == "got INV-1"
    assert payload["is_error"] is False


def test_fastapi_mount_rejects_bad_signature() -> None:
    router = WebhookRouter(secret="s-1")
    app = FastAPI()
    app.include_router(router.fastapi_router(), prefix="/nova")
    client = TestClient(app)

    body = b'{"tool_use_id":"x","name":"t","input":{}}'
    sig, _ = _sign("WRONG", "x", body)
    resp = client.post(
        "/nova/",
        content=body,
        headers={
            "X-Nova-Signature": sig,
            "X-Nova-Idempotency-Key": "x",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code in (401, 403)
