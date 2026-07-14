from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.field_tier import FieldTier
from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldOwnerOverride")


@_attrs_define
class FieldOwnerOverride:
    """Raises (never lowers) the caller's tiers when the caller owns the record. An empty tier leaves the corresponding
    tier unchanged.

        Attributes:
            read (FieldTier | Unset): A read or write access level over a record's fields.
            write (FieldTier | Unset): A read or write access level over a record's fields.
    """

    read: FieldTier | Unset = UNSET
    write: FieldTier | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        read: str | Unset = UNSET
        if not isinstance(self.read, Unset):
            read = self.read.value

        write: str | Unset = UNSET
        if not isinstance(self.write, Unset):
            write = self.write.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if read is not UNSET:
            field_dict["read"] = read
        if write is not UNSET:
            field_dict["write"] = write

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _read = d.pop("read", UNSET)
        read: FieldTier | Unset
        if isinstance(_read, Unset):
            read = UNSET
        else:
            read = FieldTier(_read)

        _write = d.pop("write", UNSET)
        write: FieldTier | Unset
        if isinstance(_write, Unset):
            write = UNSET
        else:
            write = FieldTier(_write)

        field_owner_override = cls(
            read=read,
            write=write,
        )

        field_owner_override.additional_properties = d
        return field_owner_override

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
