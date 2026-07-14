from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.stream_event_tool_use_type import StreamEventToolUseType

if TYPE_CHECKING:
    from ..models.stream_event_tool_use_input import StreamEventToolUseInput


T = TypeVar("T", bound="StreamEventToolUse")


@_attrs_define
class StreamEventToolUse:
    """
    Attributes:
        type_ (StreamEventToolUseType):
        id (str):
        name (str):
        input_ (StreamEventToolUseInput):
    """

    type_: StreamEventToolUseType
    id: str
    name: str
    input_: StreamEventToolUseInput
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
        from ..models.stream_event_tool_use_input import StreamEventToolUseInput

        d = dict(src_dict)
        type_ = StreamEventToolUseType(d.pop("type"))

        id = d.pop("id")

        name = d.pop("name")

        input_ = StreamEventToolUseInput.from_dict(d.pop("input"))

        stream_event_tool_use = cls(
            type_=type_,
            id=id,
            name=name,
            input_=input_,
        )

        stream_event_tool_use.additional_properties = d
        return stream_event_tool_use

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
