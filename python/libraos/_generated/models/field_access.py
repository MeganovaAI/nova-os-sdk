from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldAccess")


@_attrs_define
class FieldAccess:
    """The computed access contract. An omitted field list means "all fields"; a present list (including empty) is the
    explicit permitted set.

        Attributes:
            visible_fields (list[str] | Unset):
            writable_fields (list[str] | Unset):
    """

    visible_fields: list[str] | Unset = UNSET
    writable_fields: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        visible_fields: list[str] | Unset = UNSET
        if not isinstance(self.visible_fields, Unset):
            visible_fields = self.visible_fields

        writable_fields: list[str] | Unset = UNSET
        if not isinstance(self.writable_fields, Unset):
            writable_fields = self.writable_fields

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if visible_fields is not UNSET:
            field_dict["visibleFields"] = visible_fields
        if writable_fields is not UNSET:
            field_dict["writableFields"] = writable_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        visible_fields = cast(list[str], d.pop("visibleFields", UNSET))

        writable_fields = cast(list[str], d.pop("writableFields", UNSET))

        field_access = cls(
            visible_fields=visible_fields,
            writable_fields=writable_fields,
        )

        field_access.additional_properties = d
        return field_access

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
