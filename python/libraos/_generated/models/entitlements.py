from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.entitlements_flags import EntitlementsFlags


T = TypeVar("T", bound="Entitlements")


@_attrs_define
class Entitlements:
    """A tenant's effective entitlement flag map.

    Attributes:
        tenant_id (str):
        flags (EntitlementsFlags): Effective flag values (free floor overlaid with stored overrides).
    """

    tenant_id: str
    flags: EntitlementsFlags
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        flags = self.flags.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tenant_id": tenant_id,
                "flags": flags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entitlements_flags import EntitlementsFlags

        d = dict(src_dict)
        tenant_id = d.pop("tenant_id")

        flags = EntitlementsFlags.from_dict(d.pop("flags"))

        entitlements = cls(
            tenant_id=tenant_id,
            flags=flags,
        )

        entitlements.additional_properties = d
        return entitlements

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
