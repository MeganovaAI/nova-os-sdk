from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TranscriptionSegment")


@_attrs_define
class TranscriptionSegment:
    """A timestamped transcript segment.

    Attributes:
        id (int | Unset):
        start (float | Unset): Segment start time in seconds.
        end (float | Unset): Segment end time in seconds.
        text (str | Unset):
    """

    id: int | Unset = UNSET
    start: float | Unset = UNSET
    end: float | Unset = UNSET
    text: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        start = self.start

        end = self.end

        text = self.text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if text is not UNSET:
            field_dict["text"] = text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        start = d.pop("start", UNSET)

        end = d.pop("end", UNSET)

        text = d.pop("text", UNSET)

        transcription_segment = cls(
            id=id,
            start=start,
            end=end,
            text=text,
        )

        transcription_segment.additional_properties = d
        return transcription_segment

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
