"""Smoke test: package imports cleanly and exposes the OpenAPI version."""

from __future__ import annotations


def test_package_reexports_version() -> None:
    """`nova_os` package re-exports the symbols defined in `_version` unchanged.

    Asserting against literals would silently rot on every release; asserting
    re-export identity catches the actual drift risk (an __init__ that
    accidentally drops or renames a symbol).
    """
    import nova_os
    from nova_os import _version

    assert nova_os.__version__ == _version.__version__
    assert nova_os.OPENAPI_VERSION == _version.OPENAPI_VERSION


def test_generated_client_imports() -> None:
    """The generated client must import without ModuleNotFoundError or syntax errors."""
    from nova_os._generated import client  # noqa: F401


def test_generated_models_module_present() -> None:
    """The generated models module must be importable."""
    from nova_os._generated import models  # noqa: F401
    assert hasattr(models, "__file__") or hasattr(models, "__path__")


def test_client_and_errors_reexported() -> None:
    """Client + typed errors must be importable from the top-level package."""
    import nova_os

    assert hasattr(nova_os, "Client")
    assert hasattr(nova_os, "NovaOSError")
    assert hasattr(nova_os, "VertexSchemaError")
    assert hasattr(nova_os, "RateLimitedError")
    assert hasattr(nova_os, "BillingError")
    assert hasattr(nova_os, "NotFoundError")
    # Client must be instantiable (just constructor — no network call)
    c = nova_os.Client(base_url="https://example.com", api_key="test-key")
    assert hasattr(c, "agents")
    assert hasattr(c, "employees")
    assert hasattr(c, "messages")
    assert hasattr(c, "jobs")
    assert hasattr(c, "sync")


def test_streaming_and_webhook_reexported() -> None:
    """Phase 3.2 additions — WebhookRouter and MessageStream must be re-exported."""
    import nova_os

    assert hasattr(nova_os, "WebhookRouter")
    assert hasattr(nova_os, "MessageStream")

    # WebhookRouter must be instantiable with a secret
    router = nova_os.WebhookRouter(secret="test-secret-at-least-16-chars")
    assert hasattr(router, "tool")
    assert hasattr(router, "handle")
    assert hasattr(router, "fastapi_router")
    assert hasattr(router, "flask_blueprint")
    assert hasattr(router, "aws_lambda_handler")

    # MessageStream must be the same class as nova_os.streaming.MessageStream
    from nova_os.streaming import MessageStream
    assert nova_os.MessageStream is MessageStream
