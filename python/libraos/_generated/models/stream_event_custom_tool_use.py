from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.stream_event_custom_tool_use_type import StreamEventCustomToolUseType

if TYPE_CHECKING:
    from ..models.stream_event_custom_tool_use_input import StreamEventCustomToolUseInput


T = TypeVar("T", bound="StreamEventCustomToolUse")


@_attrs_define
class StreamEventCustomToolUse:
    """
    Attributes:
        type_ (StreamEventCustomToolUseType):
        id (str):
        name (str):
        input_ (StreamEventCustomToolUseInput):
    """

    type_: StreamEventCustomToolUseType
    id: str
    name: str
    input_: StreamEventCustomToolUseInput
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        id = self.id

        name = self.name

        input_ = self.input_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "id": id,
                "name": name,
                "input": input_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stream_event_custom_tool_use_input import StreamEventCustomToolUseInput

        d = dict(src_dict)
        type_ = StreamEventCustomToolUseType(d.pop("type"))

        id = d.pop("id")

        name = d.pop("name")

        input_ = StreamEventCustomToolUseInput.from_dict(d.pop("input"))

        stream_event_custom_tool_use = cls(
            type_=type_,
            id=id,
            name=name,
            input_=input_,
        )

        stream_event_custom_tool_use.additional_properties = d
        return stream_event_custom_tool_use

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
