from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.stream_event_tool_result_type import StreamEventToolResultType
from ..types import UNSET, Unset

T = TypeVar("T", bound="StreamEventToolResult")


@_attrs_define
class StreamEventToolResult:
    """
    Attributes:
        type_ (StreamEventToolResultType):
        tool_use_id (str):
        output_summary (str | Unset): Preview-truncated (~1KB on the wire); full payload in call_log.
        is_error (bool | Unset):
    """

    type_: StreamEventToolResultType
    tool_use_id: str
    output_summary: str | Unset = UNSET
    is_error: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        tool_use_id = self.tool_use_id

        output_summary = self.output_summary

        is_error = self.is_error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "tool_use_id": tool_use_id,
            }
        )
        if output_summary is not UNSET:
            field_dict["output_summary"] = output_summary
        if is_error is not UNSET:
            field_dict["is_error"] = is_error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = StreamEventToolResultType(d.pop("type"))

        tool_use_id = d.pop("tool_use_id")

        output_summary = d.pop("output_summary", UNSET)

        is_error = d.pop("is_error", UNSET)

        stream_event_tool_result = cls(
            type_=type_,
            tool_use_id=tool_use_id,
            output_summary=output_summary,
            is_error=is_error,
        )

        stream_event_tool_result.additional_properties = d
        return stream_event_tool_result

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
