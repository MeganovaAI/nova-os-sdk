"""Importability smoke test for ``examples/simulator/run_eval.py``.

The example lives outside the ``python/`` package tree (``examples/``
is not an importable package — it ships next to ``python/`` at the repo
root) so we load it by file path via :mod:`importlib.util`. The test
verifies:

* The example file exists at the expected location.
* It parses + imports cleanly (no stale imports, no syntax errors,
  no missing names from the public SDK surface).
* It exposes a ``main()`` callable so partners can invoke it from CI
  or a notebook without having to re-stitch the entrypoint.

We deliberately do NOT execute ``main()`` — it makes live HTTP calls
against an evaluation ``nova-os`` instance that the test environment is
not expected to bring up. The point of this test is to catch
public-surface drift (e.g. someone renaming
``libraos.simulator.SimulationResult``) at the unit-test gate rather
than at partner-CI runtime.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# examples/simulator/run_eval.py sits next to python/ at the repo root.
EXAMPLE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "examples"
    / "simulator"
    / "run_eval.py"
)


def test_example_file_exists() -> None:
    assert EXAMPLE_PATH.is_file(), (
        f"expected canonical eval example at {EXAMPLE_PATH}; this test "
        "lives at python/tests/ and walks up two levels to the repo root"
    )


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "examples_simulator_run_eval", EXAMPLE_PATH
    )
    assert spec is not None and spec.loader is not None, (
        f"could not build module spec for {EXAMPLE_PATH}"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # raises on syntax / import errors
    return module


def test_example_imports_cleanly() -> None:
    """File parses + every ``from libraos...`` import resolves."""
    _load_module()


def test_example_exposes_main() -> None:
    module = _load_module()
    assert hasattr(module, "main"), "run_eval.py must expose a main() function"
    assert callable(module.main), "run_eval.main must be callable"


@pytest.mark.parametrize(
    "name",
    [
        "Client",
        "Archetype",
        "SimulationResult",
        "TurnEvent",
    ],
)
def test_example_pulls_public_surface(name: str) -> None:
    """Sanity-check that the example references the public SDK names
    that downstream partners rely on. If any of these get renamed, the
    example breaks and so do partner CI scripts that mirror it."""
    module = _load_module()
    assert name in dir(module), (
        f"run_eval.py is expected to import {name!r} from libraos; "
        "if you renamed the public surface, update the example as well"
    )
