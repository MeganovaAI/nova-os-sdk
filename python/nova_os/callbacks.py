"""Mode B custom-tool webhook router — partner-side primitive.

Partners declare custom tools on their Nova OS agents (`custom_tools[]`
with a `callback.url`). Nova OS POSTs to that URL when the LLM invokes
the tool; this router decorates partner-side handlers, verifies the
HMAC-SHA256 signature, dedupes by `Idempotency-Key`, and dispatches.

HMAC scheme: signing input is `ts + "." + tool_use_id + "." + body`.
Signature header format is `t=<unix>,v1=<hex>`. Replay window default
5 min. The Nova OS server-side dispatcher signs with the same scheme.

Idempotency dedup is in-memory for v1 — a process restart loses the
dedup table. Production deployments serving the same partner across
multiple replicas should add a shared store (Redis, PG); v1 is
single-process. Cap the table size to avoid unbounded growth.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from collections import OrderedDict
from typing import Any, Awaitable, Callable, TypeVar

# Public type alias — partner-facing.
ToolHandler = Callable[[dict[str, Any], dict[str, Any]], Awaitable[str]]

_DEFAULT_REPLAY_WINDOW_SEC = 300
_DEDUP_CAP = 10_000


class WebhookRouter:
    """Partner-side dispatcher for Mode B custom-tool webhooks."""

    def __init__(
        self,
        secret: str,
        *,
        replay_window_sec: int = _DEFAULT_REPLAY_WINDOW_SEC,
        dedup_cap: int = _DEDUP_CAP,
    ) -> None:
        if not secret:
            raise ValueError("secret is required for WebhookRouter")
        self._secret = secret.encode()
        self._replay_window = replay_window_sec
        self._handlers: dict[str, ToolHandler] = {}
        self._dedup: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
        self._dedup_cap = dedup_cap

    # Decorator: @router.tool("fetch_invoice")
    def tool(self, name: str) -> Callable[[ToolHandler], ToolHandler]:
        def decorator(fn: ToolHandler) -> ToolHandler:
            self._handlers[name] = fn
            return fn

        return decorator

    async def handle(
        self,
        *,
        body: bytes,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Verify + dispatch. Returns `{"output": str, "is_error": bool}`.

        Raises PermissionError on signature verification failure (caller
        should turn that into HTTP 401 / 403).
        """
        sig_header = _get_header(headers, "X-Nova-Signature") or _get_header(headers, "x-nova-signature")
        idem_key = _get_header(headers, "X-Nova-Idempotency-Key") or _get_header(headers, "x-nova-idempotency-key")

        if not sig_header or not idem_key:
            raise PermissionError("missing X-Nova-Signature or X-Nova-Idempotency-Key")

        ts, v1 = _parse_signature(sig_header)
        now = int(time.time())
        if abs(now - ts) > self._replay_window:
            raise PermissionError("signature outside replay window")

        sign_input = f"{ts}.{idem_key}.".encode() + body
        expected = hmac.new(self._secret, sign_input, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, v1):
            raise PermissionError("signature mismatch")

        # Idempotency dedup
        if idem_key in self._dedup:
            return self._dedup[idem_key]

        try:
            payload = json.loads(body.decode())
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            raise ValueError("body is not valid JSON")

        tool_name = payload.get("name", "")
        handler = self._handlers.get(tool_name)
        if handler is None:
            result = {
                "output": f"unknown tool: {tool_name!r} not registered on this WebhookRouter",
                "is_error": True,
            }
            self._remember(idem_key, result)
            return result

        ctx = {
            "tool_use_id": payload.get("tool_use_id"),
            "agent_id": payload.get("agent_id"),
            "employee_id": payload.get("employee_id"),
            "session_id": payload.get("session_id"),
            "idempotency_key": idem_key,
        }
        try:
            output = await handler(payload.get("input", {}) or {}, ctx)
            result = {"output": output, "is_error": False}
        except Exception as exc:
            result = {"output": f"handler error: {exc}", "is_error": True}

        self._remember(idem_key, result)
        return result

    def _remember(self, key: str, value: dict[str, Any]) -> None:
        self._dedup[key] = value
        self._dedup.move_to_end(key)
        while len(self._dedup) > self._dedup_cap:
            self._dedup.popitem(last=False)

    # Integration mounts (Tasks 4-6) attach here.
    def fastapi_router(self):  # type: ignore[no-untyped-def]
        from nova_os.integrations.fastapi import build_router

        return build_router(self)

    def flask_blueprint(self, name: str = "nova_callbacks"):  # type: ignore[no-untyped-def]
        from nova_os.integrations.flask import build_blueprint

        return build_blueprint(self, name)

    def aws_lambda_handler(self):  # type: ignore[no-untyped-def]
        from nova_os.integrations.aws_lambda import build_handler

        return build_handler(self)


def _parse_signature(header: str) -> tuple[int, str]:
    """Parse `t=<unix>,v1=<hex>` (order-tolerant). Returns (ts, sig_hex)."""
    ts_str = ""
    sig = ""
    for part in header.split(","):
        kv = part.strip().split("=", 1)
        if len(kv) != 2:
            continue
        if kv[0] == "t":
            ts_str = kv[1]
        elif kv[0] == "v1":
            sig = kv[1]
    if not ts_str or not sig:
        raise PermissionError("malformed X-Nova-Signature")
    try:
        ts = int(ts_str)
    except ValueError:
        raise PermissionError("malformed X-Nova-Signature timestamp")
    return ts, sig


def _get_header(headers: dict[str, str], name: str) -> str | None:
    """Case-insensitive header lookup."""
    if name in headers:
        return headers[name]
    lower = name.lower()
    for k, v in headers.items():
        if k.lower() == lower:
            return v
    return None


__all__ = ["WebhookRouter", "ToolHandler"]
