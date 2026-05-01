"""Typed-error hierarchy + parse-from-response."""

from __future__ import annotations

import pytest

from nova_os.errors import (
    BillingError,
    ModelNotFoundError,
    NovaOSError,
    RateLimitedError,
    VertexSchemaError,
    parse_error_response,
)


def test_hierarchy() -> None:
    assert issubclass(VertexSchemaError, NovaOSError)
    assert issubclass(BillingError, NovaOSError)
    assert issubclass(RateLimitedError, NovaOSError)
    assert issubclass(ModelNotFoundError, NovaOSError)


def test_parse_vertex_schema_error() -> None:
    body = {
        "type": "vertex_schema_error",
        "message": "function_declarations[0].parameters.properties.results.items: missing field",
        "tool_name": "search_web",
        "parameter_path": "results.items",
        "fix_hint": "add items schema to type:array properties",
    }
    err = parse_error_response(400, body)
    assert isinstance(err, VertexSchemaError)
    assert err.tool_name == "search_web"
    assert err.parameter_path == "results.items"
    assert err.fix_hint.startswith("add items")
    assert "search_web" in str(err)


def test_parse_rate_limit() -> None:
    body = {"type": "rate_limit_error", "message": "slow down", "retry_after": 30}
    err = parse_error_response(429, body)
    assert isinstance(err, RateLimitedError)
    assert err.retry_after == 30


def test_parse_billing_error() -> None:
    body = {"type": "billing_error", "message": "out of credits", "code": "credits_exhausted"}
    err = parse_error_response(402, body)
    assert isinstance(err, BillingError)
    assert err.code == "credits_exhausted"


def test_parse_unknown_falls_to_base() -> None:
    body = {"type": "weird_unknown_error", "message": "huh"}
    err = parse_error_response(500, body)
    assert isinstance(err, NovaOSError)
    assert not isinstance(err, (VertexSchemaError, BillingError, RateLimitedError))


def test_parse_non_json_body() -> None:
    err = parse_error_response(500, "internal server error (plain text)")
    assert isinstance(err, NovaOSError)
    assert "500" in str(err)
