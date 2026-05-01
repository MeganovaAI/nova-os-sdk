from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.stream_event_done_status import StreamEventDoneStatus
from ..models.stream_event_done_type import StreamEventDoneType
from ..types import UNSET, Unset

T = TypeVar("T", bound="StreamEventDone")


@_attrs_define
class StreamEventDone:
    """
    Attributes:
        type_ (StreamEventDoneType):
        status (StreamEventDoneStatus):
        message_id (str | Unset):
    """

    type_: StreamEventDoneType
    status: StreamEventDoneStatus
    message_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        status = self.status.value

        message_id = self.message_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "status": status,
            }
        )
        if message_id is not UNSET:
            field_dict["message_id"] = message_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = StreamEventDoneType(d.pop("type"))

        status = StreamEventDoneStatus(d.pop("status"))

        message_id = d.pop("message_id", UNSET)

        stream_event_done = cls(
            type_=type_,
            status=status,
            message_id=message_id,
        )

        stream_event_done.additional_properties = d
        return stream_event_done

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
