"""AWS Lambda integration for WebhookRouter."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

from nova_os.callbacks import WebhookRouter


def _sign(secret: str, tool_use_id: str, body: bytes) -> str:
    ts = int(time.time())
    sign_input = f"{ts}.{tool_use_id}.".encode() + body
    return f"t={ts},v1={hmac.new(secret.encode(), sign_input, hashlib.sha256).hexdigest()}"


def test_lambda_dispatches() -> None:
    router = WebhookRouter(secret="s-lambda")

    @router.tool("fetch")
    async def fetch(input, ctx):
        return f"got {input['k']}"

    handler = router.aws_lambda_handler()

    body = json.dumps({"tool_use_id": "tu1", "name": "fetch", "input": {"k": "abc"}})
    sig = _sign("s-lambda", "tu1", body.encode())

    event = {
        "body": body,
        "isBase64Encoded": False,
        "headers": {
            "X-Nova-Signature": sig,
            "X-Nova-Idempotency-Key": "tu1",
        },
    }
    resp = handler(event, None)
    assert resp["statusCode"] == 200
    payload = json.loads(resp["body"])
    assert payload["output"] == "got abc"


def test_lambda_rejects_bad_signature() -> None:
    router = WebhookRouter(secret="s")
    handler = router.aws_lambda_handler()

    body = '{"tool_use_id":"x","name":"f","input":{}}'
    bad = _sign("WRONG", "x", body.encode())

    event = {
        "body": body,
        "isBase64Encoded": False,
        "headers": {"X-Nova-Signature": bad, "X-Nova-Idempotency-Key": "x"},
    }
    resp = handler(event, None)
    assert resp["statusCode"] == 401


def test_lambda_handles_base64_encoded_body() -> None:
    import base64

    router = WebhookRouter(secret="s")

    @router.tool("t")
    async def t(input, ctx):
        return "ok"

    handler = router.aws_lambda_handler()

    body = b'{"tool_use_id":"y","name":"t","input":{}}'
    sig = _sign("s", "y", body)
    encoded = base64.b64encode(body).decode()

    event = {
        "body": encoded,
        "isBase64Encoded": True,
        "headers": {"X-Nova-Signature": sig, "X-Nova-Idempotency-Key": "y"},
    }
    resp = handler(event, None)
    assert resp["statusCode"] == 200
