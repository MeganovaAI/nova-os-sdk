from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutHouseProfileResponse413")


@_attrs_define
class PutHouseProfileResponse413:
    """
    Attributes:
        error (str | Unset):  Example: too_large.
        max_bytes (int | Unset):
    """

    error: str | Unset = UNSET
    max_bytes: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        max_bytes = self.max_bytes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error is not UNSET:
            field_dict["error"] = error
        if max_bytes is not UNSET:
            field_dict["max_bytes"] = max_bytes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error = d.pop("error", UNSET)

        max_bytes = d.pop("max_bytes", UNSET)

        put_house_profile_response_413 = cls(
            error=error,
            max_bytes=max_bytes,
        )

        put_house_profile_response_413.additional_properties = d
        return put_house_profile_response_413

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
