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
