from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MessageRequestMetadata")


@_attrs_define
class MessageRequestMetadata:
    """
    Attributes:
        brain (bool | Unset): Per-call planner toggle (3-state — null inherits server default).
        stream_events (bool | Unset): Per-call orchestration event streaming toggle.
        stream_thinking (bool | Unset): Per-call planner-thinking event toggle.
    """

    brain: bool | Unset = UNSET
    stream_events: bool | Unset = UNSET
    stream_thinking: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        brain = self.brain

        stream_events = self.stream_events

        stream_thinking = self.stream_thinking

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if brain is not UNSET:
            field_dict["brain"] = brain
        if stream_events is not UNSET:
            field_dict["stream_events"] = stream_events
        if stream_thinking is not UNSET:
            field_dict["stream_thinking"] = stream_thinking

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        brain = d.pop("brain", UNSET)

        stream_events = d.pop("stream_events", UNSET)

        stream_thinking = d.pop("stream_thinking", UNSET)

        message_request_metadata = cls(
            brain=brain,
            stream_events=stream_events,
            stream_thinking=stream_thinking,
        )

        message_request_metadata.additional_properties = d
        return message_request_metadata

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
