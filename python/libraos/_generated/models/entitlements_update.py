from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.entitlements_update_flags import EntitlementsUpdateFlags


T = TypeVar("T", bound="EntitlementsUpdate")


@_attrs_define
class EntitlementsUpdate:
    """Upsert payload for a tenant's entitlement flags.

    Attributes:
        flags (EntitlementsUpdateFlags):
    """

    flags: EntitlementsUpdateFlags
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        flags = self.flags.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "flags": flags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entitlements_update_flags import EntitlementsUpdateFlags

        d = dict(src_dict)
        flags = EntitlementsUpdateFlags.from_dict(d.pop("flags"))

        entitlements_update = cls(
            flags=flags,
        )

        entitlements_update.additional_properties = d
        return entitlements_update

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
