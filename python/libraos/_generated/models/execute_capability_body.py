from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExecuteCapabilityBody")


@_attrs_define
class ExecuteCapabilityBody:
    """
    Attributes:
        params (Any):
        purpose (str):
        external_ref (str | Unset):
        session_id (str | Unset):
    """

    params: Any
    purpose: str
    external_ref: str | Unset = UNSET
    session_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        params = self.params

        purpose = self.purpose

        external_ref = self.external_ref

        session_id = self.session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "params": params,
                "purpose": purpose,
            }
        )
        if external_ref is not UNSET:
            field_dict["external_ref"] = external_ref
        if session_id is not UNSET:
            field_dict["session_id"] = session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        params = d.pop("params")

        purpose = d.pop("purpose")

        external_ref = d.pop("external_ref", UNSET)

        session_id = d.pop("session_id", UNSET)

        execute_capability_body = cls(
            params=params,
            purpose=purpose,
            external_ref=external_ref,
            session_id=session_id,
        )

        execute_capability_body.additional_properties = d
        return execute_capability_body

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
