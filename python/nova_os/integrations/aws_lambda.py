"""AWS Lambda + API Gateway proxy integration for WebhookRouter.

Returns a sync handler — Lambda runtimes invoke handlers synchronously,
so we bridge to the async core via asyncio.run().
"""

from __future__ import annotations

import asyncio
import base64
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nova_os.callbacks import WebhookRouter


def build_handler(wr: "WebhookRouter"):  # type: ignore[no-untyped-def]
    def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
        body_str = event.get("body") or ""
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body_str)
        else:
            body = body_str.encode() if isinstance(body_str, str) else body_str
        headers = event.get("headers") or {}
        try:
            result = asyncio.run(wr.handle(body=body, headers=headers))
        except PermissionError as exc:
            return _resp(401, {"error": str(exc)})
        except ValueError as exc:
            return _resp(400, {"error": str(exc)})
        return _resp(200, result)

    return handler


def _resp(status: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
    }


__all__ = ["build_handler"]
