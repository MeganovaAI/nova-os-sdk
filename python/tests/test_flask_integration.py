"""Flask integration mount for WebhookRouter."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time

import pytest

flask = pytest.importorskip("flask")

from flask import Flask

from nova_os.callbacks import WebhookRouter


def _sign(secret: str, tool_use_id: str, body: bytes) -> str:
    ts = int(time.time())
    sign_input = f"{ts}.{tool_use_id}.".encode() + body
    sig_hex = hmac.new(secret.encode(), sign_input, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig_hex}"


def test_flask_dispatches() -> None:
    router = WebhookRouter(secret="s-flask")

    @router.tool("fetch")
    async def fetch(input, ctx):
        return f"got {input['x']}"

    app = Flask(__name__)
    app.register_blueprint(router.flask_blueprint(), url_prefix="/nova")

    client = app.test_client()
    body = json.dumps({"tool_use_id": "tu1", "name": "fetch", "input": {"x": 42}}).encode()
    sig = _sign("s-flask", "tu1", body)

    resp = client.post(
        "/nova/",
        data=body,
        headers={
            "X-Nova-Signature": sig,
            "X-Nova-Idempotency-Key": "tu1",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["output"] == "got 42"


def test_flask_rejects_bad_signature() -> None:
    router = WebhookRouter(secret="s")
    app = Flask(__name__)
    app.register_blueprint(router.flask_blueprint(), url_prefix="/nova")
    client = app.test_client()

    body = b'{"tool_use_id":"x","name":"f","input":{}}'
    bad_sig = _sign("WRONG", "x", body)
    resp = client.post(
        "/nova/",
        data=body,
        headers={
            "X-Nova-Signature": bad_sig,
            "X-Nova-Idempotency-Key": "x",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code in (401, 403)
