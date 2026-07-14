"""Typed exception hierarchy for LibraOS SDK.

Mirrors the OpenAPI Error.type enum:

  - invalid_request_error / validation_error → NovaOSError (base)
  - authentication_error                      → AuthenticationError
  - permission_error                          → PermissionError
  - not_found_error                           → NotFoundError
  - rate_limit_error                          → RateLimitedError
  - billing_error                             → BillingError
  - upstream_error                            → UpstreamError
  - vertex_schema_error                       → VertexSchemaError
  - internal_error                            → InternalError

Resource-specific shortcuts (ModelNotFoundError) are also defined for
common cases the SDK can detect from the message body even when the
server uses a generic invalid_request_error code.
"""

from __future__ import annotations

from typing import Any


class NovaOSError(Exception):
    """Base class for every LibraOS SDK error."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        code: str | None = None,
        param: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.param = param

    def __str__(self) -> str:
        parts = [self.message]
        if self.status is not None:
            parts.append(f"(status={self.status})")
        if self.code:
            parts.append(f"(code={self.code})")
        return " ".join(parts)


class AuthenticationError(NovaOSError):
    """401 — missing or invalid bearer token."""


class PermissionError(NovaOSError):  # noqa: A001 — shadows builtin intentionally for parity with OpenAPI Error.type
    """403 — token valid but lacks permission."""


class NotFoundError(NovaOSError):
    """404 — resource not found (or hidden from this token's scope)."""


class RateLimitedError(NovaOSError):
    """429 — too many requests. retry_after is seconds."""

    def __init__(self, message: str, *, retry_after: int | None = None, **kw: Any) -> None:
        super().__init__(message, **kw)
        self.retry_after = retry_after


class BillingError(NovaOSError):
    """402/403 — billing issue (credits exhausted, monthly cap, etc).

    Detect via `code` (e.g. credits_exhausted, USAGE_LIMIT_EXCEEDED).
    """


class UpstreamError(NovaOSError):
    """5xx propagated from an upstream provider (gateway, vendor)."""


class VertexSchemaError(NovaOSError):
    """400 root-caused to Vertex AI's strict tool-schema validation.

    Surfaces the offending tool + parameter path so partners can fix the
    schema rather than retrying as transient. See nova-os CLAUDE.md for
    the detailed root-cause pattern.
    """

    def __init__(
        self,
        message: str,
        *,
        tool_name: str | None = None,
        parameter_path: str | None = None,
        fix_hint: str | None = None,
        **kw: Any,
    ) -> None:
        super().__init__(message, **kw)
        self.tool_name = tool_name
        self.parameter_path = parameter_path
        self.fix_hint = fix_hint

    def __str__(self) -> str:
        base = super().__str__()
        extras = []
        if self.tool_name:
            extras.append(f"tool={self.tool_name}")
        if self.parameter_path:
            extras.append(f"param={self.parameter_path}")
        if extras:
            return f"{base} [{' '.join(extras)}]"
        return base


class ModelNotFoundError(NovaOSError):
    """Bare model name (no <vendor>/ prefix) or unknown model id."""


class InternalError(NovaOSError):
    """500 — server bug. Report at https://github.com/libraos/sdk/issues."""


class PersonaNotFound(NotFoundError):
    """Raised when GET /agents/v1/personas/{id} 404s.

    The persona-manifest endpoint uses a distinct error envelope
    ``{"error": "persona not found", "id": "<requested>"}`` rather than
    the standard partner Error type — this exception preserves the
    requested id on ``.persona_id`` for caller convenience.
    """

    def __init__(self, persona_id: str, message: str = "persona not found"):
        super().__init__(message)
        self.persona_id = persona_id


_TYPE_TO_CLASS: dict[str, type[NovaOSError]] = {
    "authentication_error": AuthenticationError,
    "permission_error": PermissionError,
    "not_found_error": NotFoundError,
    # Server also emits "not_found" (without _error suffix) on some endpoints
    # (notably /v1/agents/* via parse_error_response wrapped envelope) — alias.
    "not_found": NotFoundError,
    "rate_limit_error": RateLimitedError,
    "billing_error": BillingError,
    "upstream_error": UpstreamError,
    "vertex_schema_error": VertexSchemaError,
    "internal_error": InternalError,
}

# Status-code fallback when the server returns a 4xx/5xx with no recognized
# ``type`` field. Defensive — keeps `except NotFoundError` paths working even
# when the server adds a new endpoint that doesn't follow the type convention.
_STATUS_TO_CLASS: dict[int, type[NovaOSError]] = {
    401: AuthenticationError,
    403: PermissionError,
    404: NotFoundError,
    429: RateLimitedError,
}


def parse_error_response(status: int, body: Any) -> NovaOSError:
    """Convert an HTTP error response into a typed NovaOSError.

    `body` is the parsed JSON body (dict) or the raw text fallback (str).
    Returns the most specific NovaOSError subclass we can identify.

    Handles three server envelope shapes observed in practice:
    1. Flat:    ``{"message": "...", "type": "...", "code": ...}``
    2. Wrapped: ``{"error": {"message": "...", "type": "..."}}`` (e.g. /v1/agents/*)
    3. String:  ``{"error": "not_found"}`` (e.g. /v1/conversations/* unknown id)

    All three normalize to the same typed subclass on the way out.
    """
    if not isinstance(body, dict):
        return NovaOSError(f"HTTP {status}: {body}", status=status)

    # Persona-manifest endpoint uses a distinct envelope:
    #     {"error": "persona not found", "id": "<requested>"}
    # Detect it before the standard parser so c.personas.get() maps
    # cleanly to PersonaNotFound without the resource having to fish
    # at the body shape itself.
    if status == 404 and "id" in body and body.get("error") == "persona not found":
        return PersonaNotFound(body["id"], "persona not found")

    # Wrapped envelope: unwrap `body["error"]` into the inner dict so the
    # flat-envelope code below works unchanged for both shapes.
    if isinstance(body.get("error"), dict):
        body = body["error"]
    # String-only envelope: `{"error": "not_found"}` — synthesize a flat
    # body so 404 short-strings still produce typed NotFoundError.
    elif isinstance(body.get("error"), str) and status >= 400:
        err_str = body["error"]
        # Common server shorthand: "not_found" string IS the type code.
        guess_type = err_str if err_str in _TYPE_TO_CLASS else ""
        body = {"message": err_str, "type": guess_type}

    type_str = body.get("type", "")
    message = body.get("message", str(body))
    common = {
        "status": status,
        "code": body.get("code"),
        "param": body.get("param"),
    }

    cls = _TYPE_TO_CLASS.get(type_str)
    if cls is RateLimitedError:
        return RateLimitedError(message, retry_after=body.get("retry_after"), **common)
    if cls is VertexSchemaError:
        return VertexSchemaError(
            message,
            tool_name=body.get("tool_name"),
            parameter_path=body.get("parameter_path"),
            fix_hint=body.get("fix_hint"),
            **common,
        )
    if cls is not None:
        return cls(message, **common)

    # Specific message-level matchers for cases the server uses a generic
    # type code but we can recognize the case. Keep small and focused.
    msg_lower = message.lower()
    if "model" in msg_lower and ("not found" in msg_lower or "unknown" in msg_lower):
        return ModelNotFoundError(message, **common)

    # Status-code fallback — last resort so 404s map to NotFoundError even
    # when the server returns an unknown ``type`` field. Keeps SDK-side
    # ``except NotFoundError`` paths working as the server evolves.
    status_cls = _STATUS_TO_CLASS.get(status)
    if status_cls is not None:
        return status_cls(message, **common)

    return NovaOSError(message, **common)


__all__ = [
    "NovaOSError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "RateLimitedError",
    "BillingError",
    "UpstreamError",
    "VertexSchemaError",
    "ModelNotFoundError",
    "InternalError",
    "parse_error_response",
]
