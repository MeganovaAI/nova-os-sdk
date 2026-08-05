from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SpeechRequest")


@_attrs_define
class SpeechRequest:
    """
    Attributes:
        input_ (str): Text to synthesize into speech.
        model (str | Unset): TTS model (provider-prefixed, e.g. `gemini/gemini-2.5-flash-tts`). Overrides the server
            default for this call. Example: gemini/gemini-2.5-flash-tts.
        voice (str | Unset): Voice name. Must belong to the same provider as `model` (e.g. Gemini voices such as `Kore`
            for the default Gemini TTS model). Defaults to the server-configured voice when omitted. Example: Kore.
        response_format (str | Unset): Audio container/codec. Defaults to `mp3` (`audio/mpeg` body). Default: 'mp3'.
            Example: mp3.
    """

    input_: str
    model: str | Unset = UNSET
    voice: str | Unset = UNSET
    response_format: str | Unset = "mp3"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        input_ = self.input_

        model = self.model

        voice = self.voice

        response_format = self.response_format

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input": input_,
            }
        )
        if model is not UNSET:
            field_dict["model"] = model
        if voice is not UNSET:
            field_dict["voice"] = voice
        if response_format is not UNSET:
            field_dict["response_format"] = response_format

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        input_ = d.pop("input")

        model = d.pop("model", UNSET)

        voice = d.pop("voice", UNSET)

        response_format = d.pop("response_format", UNSET)

        speech_request = cls(
            input_=input_,
            model=model,
            voice=voice,
            response_format=response_format,
        )

        speech_request.additional_properties = d
        return speech_request

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
