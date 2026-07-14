"""Smoke test: package imports cleanly and exposes the OpenAPI version."""

from __future__ import annotations


def test_package_reexports_version() -> None:
    """`libraos` package re-exports the symbols defined in `_version` unchanged.

    Asserting against literals would silently rot on every release; asserting
    re-export identity catches the actual drift risk (an __init__ that
    accidentally drops or renames a symbol).
    """
    import libraos
    from libraos import _version

    assert libraos.__version__ == _version.__version__
    assert libraos.OPENAPI_VERSION == _version.OPENAPI_VERSION


def test_generated_client_imports() -> None:
    """The generated client must import without ModuleNotFoundError or syntax errors."""
    from libraos._generated import client  # noqa: F401


def test_generated_models_module_present() -> None:
    """The generated models module must be importable."""
    from libraos._generated import models  # noqa: F401
    assert hasattr(models, "__file__") or hasattr(models, "__path__")


def test_client_and_errors_reexported() -> None:
    """Client + typed errors must be importable from the top-level package."""
    import libraos

    assert hasattr(libraos, "Client")
    assert hasattr(libraos, "NovaOSError")
    assert hasattr(libraos, "VertexSchemaError")
    assert hasattr(libraos, "RateLimitedError")
    assert hasattr(libraos, "BillingError")
    assert hasattr(libraos, "NotFoundError")
    # Client must be instantiable (just constructor — no network call)
    c = libraos.Client(base_url="https://example.com", api_key="test-key")
    assert hasattr(c, "agents")
    assert hasattr(c, "employees")
    assert hasattr(c, "messages")
    assert hasattr(c, "jobs")
    assert hasattr(c, "sync")


def test_streaming_and_webhook_reexported() -> None:
    """WebhookRouter and MessageStream must be re-exported from the top-level package."""
    import libraos

    assert hasattr(libraos, "WebhookRouter")
    assert hasattr(libraos, "MessageStream")

    # WebhookRouter must be instantiable with a secret
    router = libraos.WebhookRouter(secret="test-secret-at-least-16-chars")
    assert hasattr(router, "tool")
    assert hasattr(router, "handle")
    assert hasattr(router, "fastapi_router")
    assert hasattr(router, "flask_blueprint")
    assert hasattr(router, "aws_lambda_handler")

    # MessageStream must be the same class as libraos.streaming.MessageStream
    from libraos.streaming import MessageStream
    assert libraos.MessageStream is MessageStream
