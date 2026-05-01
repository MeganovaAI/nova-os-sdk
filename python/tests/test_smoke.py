"""Smoke test: package imports cleanly and exposes the OpenAPI version."""

from __future__ import annotations


def test_package_imports() -> None:
    import nova_os

    assert nova_os.__version__ == "0.1.0a1"
    assert nova_os.OPENAPI_VERSION == "1.0.0-alpha.1"


def test_generated_client_imports() -> None:
    """The generated client must import without ModuleNotFoundError or syntax errors."""
    from nova_os._generated import client  # noqa: F401


def test_generated_models_module_present() -> None:
    """The generated models module must be importable."""
    from nova_os._generated import models  # noqa: F401
    assert hasattr(models, "__file__") or hasattr(models, "__path__")
