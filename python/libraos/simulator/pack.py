"""Vertical pack loader — archetype + rubric catalogs from partner repos (#31).

A *pack* lets a vertical (EqualDocs immigration, nova-os-school education, …)
maintain its own archetype + rubric catalog in its own repo/package, without
forking the SDK or bloating ``examples/``. A pack is a directory:

    my-pack/
    ├── pack.yaml          # name, version, requires_sdk
    ├── archetypes/*.yaml  # loaded as Archetype
    ├── rubrics/*.yaml     # loaded as RubricCase (composes with #30)
    └── compliance/
        └── overlay.yaml   # optional extension-field schema for archetypes

The **extension-field overlay** is the load-bearing primitive: it lets a pack
declare vertical-specific archetype fields (e.g. an Ontario ``jurisdiction``
enum) that the SDK base schema doesn't know about. Loading validates each
archetype against the base schema **plus** the pack's overlay — so the base
schema never has to grow a field per vertical.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from libraos.simulator.archetype import Archetype
from libraos.simulator.errors import ArchetypeValidationError
from libraos.simulator.rubric import RubricCase

PackValidationError = ArchetypeValidationError

_ENTRY_POINT_GROUP = "libraos.simulator.packs"


# ── extension-field overlay ────────────────────────────────────────────────

_TYPE_CHECKS: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
}


def _validate_extension(name: str, spec: dict[str, Any], value: Any) -> None:
    """Validate one extension-field value against its overlay spec."""
    t = spec.get("type")
    if t in _TYPE_CHECKS:
        py = _TYPE_CHECKS[t]
        # bool is an int subclass — reject bool where integer/number expected
        if t in {"integer", "number"} and isinstance(value, bool):
            raise PackValidationError(f"extensions.{name}", f"expected {t}, got boolean")
        if not isinstance(value, py):
            raise PackValidationError(
                f"extensions.{name}", f"expected {t}, got {type(value).__name__}"
            )
    elif t is not None:
        raise PackValidationError(f"extensions.{name}", f"unknown overlay type {t!r}")
    if "enum" in spec and value not in spec["enum"]:
        raise PackValidationError(f"extensions.{name}", f"{value!r} not in enum {spec['enum']}")
    if "pattern" in spec and isinstance(value, str) and not re.search(spec["pattern"], value):
        raise PackValidationError(f"extensions.{name}", f"{value!r} does not match {spec['pattern']}")


def _split_and_validate_extensions(
    data: dict[str, Any], overlay: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Pull overlay-declared fields out of ``data``, validate them, and return
    ``(base_data, extension_values)``.

    Base data (extension keys removed) is what the strict :class:`Archetype`
    model validates; the extension values are validated here against the
    overlay's type/enum/pattern rules.
    """
    fields: dict[str, dict[str, Any]] = {}
    for req in overlay.get("required", []) or []:
        fields.update({k: (v or {}) for k, v in req.items()})
    for opt in overlay.get("optional", []) or []:
        fields.update({k: (v or {}) for k, v in opt.items()})
    required_names = {k for req in (overlay.get("required", []) or []) for k in req}

    base = dict(data)
    ext: dict[str, Any] = {}
    for fname, spec in fields.items():
        if fname in base:
            _validate_extension(fname, spec, base[fname])
            ext[fname] = base.pop(fname)
    missing = required_names - ext.keys()
    if missing:
        raise PackValidationError(
            "extensions", f"missing required extension field(s): {sorted(missing)}"
        )
    return base, ext


# ── Pack ────────────────────────────────────────────────────────────────────


class Pack:
    """A loaded archetype + rubric catalog. Construct via :func:`load_pack`."""

    def __init__(self, root: Path, meta: dict[str, Any], overlay: dict[str, Any]) -> None:
        self._root = root
        self.name: str = str(meta.get("name") or root.name)
        self.version: str = str(meta.get("version") or "0.0.0")
        self.requires_sdk: str | None = meta.get("requires_sdk")
        self._overlay = overlay
        self._extensions: dict[str, dict[str, Any]] = {}
        self._arch_files = self._index(root / "archetypes")
        self._rubric_files = self._index(root / "rubrics")

    @staticmethod
    def _index(d: Path) -> dict[str, Path]:
        if not d.is_dir():
            return {}
        return {f.stem: f for f in sorted([*d.glob("*.yaml"), *d.glob("*.yml")])}

    @property
    def archetypes(self) -> list[str]:
        return sorted(self._arch_files)

    @property
    def rubrics(self) -> list[str]:
        return sorted(self._rubric_files)

    def get(self, name: str) -> Archetype:
        """Load and validate an archetype (base schema + pack overlay)."""
        if name not in self._arch_files:
            raise KeyError(f"archetype {name!r} not in pack {self.name!r}")
        import yaml  # type: ignore[import-untyped]

        raw = yaml.safe_load(self._arch_files[name].read_text(encoding="utf-8")) or {}
        base, ext = _split_and_validate_extensions(raw, self._overlay)
        self._extensions[name] = ext
        return Archetype.from_dict(base)

    def get_extensions(self, name: str) -> dict[str, Any]:
        """The validated overlay-field values for an archetype (``{}`` if none).

        Call after :meth:`get` — the base archetype stays the clean SDK type;
        vertical-specific fields live here so the base schema never bloats.
        """
        if name not in self._extensions:
            self.get(name)
        return dict(self._extensions.get(name, {}))

    def get_rubric(self, name: str) -> RubricCase:
        if name not in self._rubric_files:
            raise KeyError(f"rubric {name!r} not in pack {self.name!r}")
        return RubricCase.from_yaml_path(self._rubric_files[name])

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Pack(name={self.name!r}, version={self.version!r}, archetypes={len(self._arch_files)}, rubrics={len(self._rubric_files)})"


# ── loaders ──────────────────────────────────────────────────────────────────


def _check_sdk_compat(requires: str | None) -> None:
    if not requires:
        return
    try:
        from packaging.specifiers import SpecifierSet
        from packaging.version import Version

        import libraos

        if Version(libraos.__version__) not in SpecifierSet(requires):
            raise PackValidationError(
                "requires_sdk",
                f"pack needs SDK {requires}; installed {libraos.__version__}",
            )
    except ImportError:  # pragma: no cover - packaging is a transitive dep
        pass


def _load_from_path(root: Path) -> Pack:
    if not root.is_dir():
        raise NotADirectoryError(f"pack path is not a directory: {root}")
    import yaml  # type: ignore[import-untyped]

    meta_file = root / "pack.yaml"
    meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) if meta_file.is_file() else {}
    meta = meta or {}
    _check_sdk_compat(meta.get("requires_sdk"))
    overlay_file = root / "compliance" / "overlay.yaml"
    overlay = {}
    if overlay_file.is_file():
        loaded = yaml.safe_load(overlay_file.read_text(encoding="utf-8")) or {}
        overlay = loaded.get("extension_fields", {}) or {}
    return Pack(root, meta, overlay)


def load_pack(
    name: str | None = None,
    *,
    path: str | Path | None = None,
    git: str | None = None,
) -> Pack:
    """Load a vertical pack from a local path, an installed package, or a git URL.

    Exactly one source must be given:

    - ``path=`` — a local pack directory (the primary, offline path).
    - ``name=`` — resolve to a pip-installed pack registered under the
      ``libraos.simulator.packs`` entry-point group.
    - ``git=`` — shallow-clone the repo to a temp dir, then load it (requires
      the ``git`` binary and network).
    """
    given = [x is not None for x in (path, name, git)]
    if sum(given) != 1:
        raise ValueError("load_pack: pass exactly one of name=, path=, or git=")

    if path is not None:
        return _load_from_path(Path(path))

    if name is not None:
        packs = _installed_pack_paths()
        if name not in packs:
            raise PackValidationError(
                "name", f"no installed pack named {name!r} (found: {sorted(packs)})"
            )
        return _load_from_path(packs[name])

    # git=
    import subprocess
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="libraos-pack-"))
    subprocess.run(["git", "clone", "--depth", "1", git, str(tmp)], check=True)  # noqa: S603,S607
    return _load_from_path(tmp)


def _installed_pack_paths() -> dict[str, Path]:
    """Map pack-name → directory for every pip-installed pack.

    Packs register a ``libraos.simulator.packs`` entry point whose value is an
    importable module (or ``module:attr``) resolving to the pack directory.
    """
    from importlib import import_module
    from importlib.metadata import entry_points

    out: dict[str, Path] = {}
    try:
        eps = entry_points(group=_ENTRY_POINT_GROUP)
    except TypeError:  # pragma: no cover - Python <3.10 signature
        eps = entry_points().get(_ENTRY_POINT_GROUP, [])  # type: ignore[assignment]
    for ep in eps:
        target = ep.value.split(":", 1)[0]
        mod = import_module(target)
        d = Path(mod.__file__).parent if mod.__file__ else None
        if d and d.is_dir():
            out[ep.name] = d
    return out


def list_installed_packs() -> list[str]:
    """Names of every pip-installed pack (see :func:`load_pack` ``name=``)."""
    return sorted(_installed_pack_paths())


def detect_pack_collisions(packs: list[Pack]) -> dict[str, list[str]]:
    """Report archetype/rubric names that appear in more than one pack.

    Returns ``{content_name: [pack_name, ...]}`` for every name owned by ≥2
    packs — so a harness merging multiple verticals can refuse ambiguous ids
    (e.g. two packs both shipping ``pgwp-applicant``).
    """
    owners: dict[str, list[str]] = {}
    for p in packs:
        for content in (*p.archetypes, *p.rubrics):
            owners.setdefault(content, []).append(p.name)
    return {k: v for k, v in owners.items() if len(v) > 1}
