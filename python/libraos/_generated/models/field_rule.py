from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.field_tier import FieldTier

T = TypeVar("T", bound="FieldRule")


@_attrs_define
class FieldRule:
    """Maps a role to its read/write tiers.

    Attributes:
        role (str):
        read (FieldTier): A read or write access level over a record's fields.
        write (FieldTier): A read or write access level over a record's fields.
    """

    role: str
    read: FieldTier
    write: FieldTier
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role

        read = self.read.value

        write = self.write.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "read": read,
                "write": write,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = d.pop("role")

        read = FieldTier(d.pop("read"))

        write = FieldTier(d.pop("write"))

        field_rule = cls(
            role=role,
            read=read,
            write=write,
        )

        field_rule.additional_properties = d
        return field_rule

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
