"""Validation tests for the reference archetypes shipped under
``examples/simulator/``.

These are partner-facing tutorial files, not test fixtures — but every
shipped archetype must load cleanly against the v1 schema and its
``name`` field must agree with its filename. If either invariant breaks
we ship a broken tutorial, so these tests gate the directory.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nova_os import Archetype

# examples/simulator/ sits next to python/ at the repo root.
EXAMPLES_DIR = (
    Path(__file__).resolve().parent.parent.parent / "examples" / "simulator"
)

EXPECTED_ARCHETYPES = (
    "legal-immigration-pgwp",
    "legal-vendor-msa-review",
    "medical-patient-with-hidden-history",
)


def _yaml_paths() -> list[Path]:
    return sorted(EXAMPLES_DIR.glob("*.yaml"))


def test_examples_dir_exists() -> None:
    assert EXAMPLES_DIR.is_dir(), (
        f"expected examples/simulator/ at {EXAMPLES_DIR}; this test "
        "lives at python/tests/ and walks up two levels to the repo root"
    )


def test_all_expected_archetypes_present() -> None:
    found = {p.stem for p in _yaml_paths()}
    missing = set(EXPECTED_ARCHETYPES) - found
    assert not missing, f"missing reference archetypes: {sorted(missing)}"


@pytest.mark.parametrize("filename", EXPECTED_ARCHETYPES)
def test_archetype_loads(filename: str) -> None:
    path = EXAMPLES_DIR / f"{filename}.yaml"
    archetype = Archetype.from_yaml_path(path)
    # file-stem ↔ archetype.name agreement: prevents the slow-leak rename
    # where someone edits the YAML but not the filename (or vice versa).
    assert archetype.name == filename, (
        f"{path.name}: archetype.name={archetype.name!r} does not match "
        f"filename stem {filename!r}"
    )


def test_every_yaml_in_dir_validates() -> None:
    """Any future *.yaml added to examples/simulator/ must also load."""
    paths = _yaml_paths()
    assert paths, "no *.yaml files found under examples/simulator/"
    for path in paths:
        # Will raise ArchetypeValidationError on failure; pytest surfaces it.
        Archetype.from_yaml_path(path)
