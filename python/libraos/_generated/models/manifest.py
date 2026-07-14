from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.persona_manifest_entry import PersonaManifestEntry


T = TypeVar("T", bound="Manifest")


@_attrs_define
class Manifest:
    """Boot-time persona discovery contract. Partners cache by
    ``manifest_version`` (sha256 over canonical-JSON) and use
    ``If-None-Match`` on subsequent fetches to short-circuit at 304.

        Attributes:
            manifest_version (str): ``sha256:<hex>`` — emitted as ``ETag``. Partners send
                ``If-None-Match: <manifest_version>`` to skip the body when
                unchanged.
            personas (list[PersonaManifestEntry]):
    """

    manifest_version: str
    personas: list[PersonaManifestEntry]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        manifest_version = self.manifest_version

        personas = []
        for personas_item_data in self.personas:
            personas_item = personas_item_data.to_dict()
            personas.append(personas_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "manifest_version": manifest_version,
                "personas": personas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.persona_manifest_entry import PersonaManifestEntry

        d = dict(src_dict)
        manifest_version = d.pop("manifest_version")

        personas = []
        _personas = d.pop("personas")
        for personas_item_data in _personas:
            personas_item = PersonaManifestEntry.from_dict(personas_item_data)

            personas.append(personas_item)

        manifest = cls(
            manifest_version=manifest_version,
            personas=personas,
        )

        manifest.additional_properties = d
        return manifest

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
