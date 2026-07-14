from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutHouseProfileResponse409")


@_attrs_define
class PutHouseProfileResponse409:
    """
    Attributes:
        error (str | Unset):  Example: stale.
        current_updated_at (str | Unset):
    """

    error: str | Unset = UNSET
    current_updated_at: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        current_updated_at = self.current_updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error is not UNSET:
            field_dict["error"] = error
        if current_updated_at is not UNSET:
            field_dict["current_updated_at"] = current_updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error = d.pop("error", UNSET)

        current_updated_at = d.pop("current_updated_at", UNSET)

        put_house_profile_response_409 = cls(
            error=error,
            current_updated_at=current_updated_at,
        )

        put_house_profile_response_409.additional_properties = d
        return put_house_profile_response_409

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
