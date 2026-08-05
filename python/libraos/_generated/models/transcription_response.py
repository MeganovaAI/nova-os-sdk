from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.transcription_segment import TranscriptionSegment


T = TypeVar("T", bound="TranscriptionResponse")


@_attrs_define
class TranscriptionResponse:
    """JSON transcript. Shape follows the underlying model; `segments` and timestamp detail are present for verbose
    formats.

        Attributes:
            text (str | Unset): The full transcript.
            language (str | Unset): Detected or supplied language.
            duration (float | Unset): Audio duration in seconds, when reported.
            segments (list[TranscriptionSegment] | Unset): Per-segment breakdown with timestamps, when available.
    """

    text: str | Unset = UNSET
    language: str | Unset = UNSET
    duration: float | Unset = UNSET
    segments: list[TranscriptionSegment] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        language = self.language

        duration = self.duration

        segments: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.segments, Unset):
            segments = []
            for segments_item_data in self.segments:
                segments_item = segments_item_data.to_dict()
                segments.append(segments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if text is not UNSET:
            field_dict["text"] = text
        if language is not UNSET:
            field_dict["language"] = language
        if duration is not UNSET:
            field_dict["duration"] = duration
        if segments is not UNSET:
            field_dict["segments"] = segments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.transcription_segment import TranscriptionSegment

        d = dict(src_dict)
        text = d.pop("text", UNSET)

        language = d.pop("language", UNSET)

        duration = d.pop("duration", UNSET)

        _segments = d.pop("segments", UNSET)
        segments: list[TranscriptionSegment] | Unset = UNSET
        if _segments is not UNSET:
            segments = []
            for segments_item_data in _segments:
                segments_item = TranscriptionSegment.from_dict(segments_item_data)

                segments.append(segments_item)

        transcription_response = cls(
            text=text,
            language=language,
            duration=duration,
            segments=segments,
        )

        transcription_response.additional_properties = d
        return transcription_response

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
