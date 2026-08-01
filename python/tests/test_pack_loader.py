"""Vertical pack loader — load_pack + extension overlay + collisions (#31)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from libraos import Pack, load_pack
from libraos.simulator import PackValidationError, detect_pack_collisions, list_installed_packs

REF = Path(__file__).resolve().parents[2] / "examples" / "simulator" / "reference-pack"

_BASE_ARCH = {
    "name": "a-applicant",
    "description": "x",
    "hidden_facts": ["h"],
    "disclosure_willingness": "cautious",
    "success_signal": "s",
}


def _make_pack(tmp: Path, *, overlay: dict | None = None, arch_extra: dict | None = None,
               name: str = "p", requires_sdk: str | None = None, arch_name: str = "a-applicant") -> Path:
    (tmp / "archetypes").mkdir(parents=True)
    (tmp / "rubrics").mkdir()
    meta = {"name": name, "version": "0.1.0"}
    if requires_sdk:
        meta["requires_sdk"] = requires_sdk
    (tmp / "pack.yaml").write_text(yaml.safe_dump(meta))
    arch = {**_BASE_ARCH, "name": arch_name, **(arch_extra or {})}
    (tmp / "archetypes" / f"{arch_name}.yaml").write_text(yaml.safe_dump(arch))
    (tmp / "rubrics" / "r1.yaml").write_text(
        yaml.safe_dump({"case_id": "r1", "instruction": "do", "rubric": [{"criterion": "c"}]})
    )
    if overlay is not None:
        (tmp / "compliance").mkdir()
        (tmp / "compliance" / "overlay.yaml").write_text(
            yaml.safe_dump({"extension_fields": overlay})
        )
    return tmp


# ── reference pack (shipped) ──────────────────────────────────────────────

def test_reference_pack_loads() -> None:
    p = load_pack(path=REF)
    assert isinstance(p, Pack)
    assert "reference-applicant" in p.archetypes
    assert "reference-msa-review" in p.rubrics
    a = p.get("reference-applicant")
    assert a.name == "reference-applicant"
    assert p.get_extensions("reference-applicant")["jurisdiction"] == "ON"
    assert p.get_rubric("reference-msa-review").case_id == "legal-vendor-msa-review-v1"


# ── extension overlay composition ─────────────────────────────────────────

def test_extension_valid(tmp_path: Path) -> None:
    root = _make_pack(
        tmp_path,
        overlay={"required": [{"jurisdiction": {"type": "string", "enum": ["ON", "QC"]}}]},
        arch_extra={"jurisdiction": "ON"},
    )
    p = load_pack(path=root)
    a = p.get("a-applicant")               # base validates (extension key removed)
    assert a.name == "a-applicant"
    assert p.get_extensions("a-applicant") == {"jurisdiction": "ON"}


def test_extension_bad_type_rejected(tmp_path: Path) -> None:
    root = _make_pack(
        tmp_path,
        overlay={"optional": [{"lso_disclosure_required": {"type": "boolean"}}]},
        arch_extra={"lso_disclosure_required": "yes"},  # string, not boolean
    )
    with pytest.raises(PackValidationError, match="expected boolean"):
        load_pack(path=root).get("a-applicant")


def test_extension_enum_rejected(tmp_path: Path) -> None:
    root = _make_pack(
        tmp_path,
        overlay={"required": [{"jurisdiction": {"type": "string", "enum": ["ON", "QC"]}}]},
        arch_extra={"jurisdiction": "ZZ"},
    )
    with pytest.raises(PackValidationError, match="not in enum"):
        load_pack(path=root).get("a-applicant")


def test_extension_missing_required(tmp_path: Path) -> None:
    root = _make_pack(
        tmp_path,
        overlay={"required": [{"jurisdiction": {"type": "string"}}]},
        arch_extra={},  # missing required jurisdiction
    )
    with pytest.raises(PackValidationError, match="missing required"):
        load_pack(path=root).get("a-applicant")


# ── version compatibility ─────────────────────────────────────────────────

def test_requires_sdk_incompatible_rejected(tmp_path: Path) -> None:
    root = _make_pack(tmp_path, requires_sdk=">=99.0.0")
    with pytest.raises(PackValidationError, match="needs SDK"):
        load_pack(path=root)


def test_requires_sdk_compatible_ok(tmp_path: Path) -> None:
    root = _make_pack(tmp_path, requires_sdk=">=0.1.0")
    assert load_pack(path=root).name == "p"


# ── collisions + discovery + arg guard ────────────────────────────────────

def test_detect_cross_pack_collisions(tmp_path: Path) -> None:
    a = load_pack(path=_make_pack(tmp_path / "a", name="pack-a", arch_name="pgwp-applicant"))
    b = load_pack(path=_make_pack(tmp_path / "b", name="pack-b", arch_name="pgwp-applicant"))
    collisions = detect_pack_collisions([a, b])
    assert collisions["pgwp-applicant"] == ["pack-a", "pack-b"]


def test_load_pack_requires_exactly_one_source() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        load_pack()
    with pytest.raises(ValueError, match="exactly one"):
        load_pack(path="/x", git="http://y")


def test_list_installed_packs_empty_by_default() -> None:
    assert isinstance(list_installed_packs(), list)  # no packs registered in test env
