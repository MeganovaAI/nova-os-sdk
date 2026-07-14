from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomToolResultRequest")


@_attrs_define
class CustomToolResultRequest:
    """
    Attributes:
        tool_use_id (str):
        output (str):
        is_error (bool | Unset):  Default: False.
    """

    tool_use_id: str
    output: str
    is_error: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool_use_id = self.tool_use_id

        output = self.output

        is_error = self.is_error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tool_use_id": tool_use_id,
                "output": output,
            }
        )
        if is_error is not UNSET:
            field_dict["is_error"] = is_error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tool_use_id = d.pop("tool_use_id")

        output = d.pop("output")

        is_error = d.pop("is_error", UNSET)

        custom_tool_result_request = cls(
            tool_use_id=tool_use_id,
            output=output,
            is_error=is_error,
        )

        custom_tool_result_request.additional_properties = d
        return custom_tool_result_request

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
