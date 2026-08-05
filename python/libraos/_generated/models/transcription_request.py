from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..models.transcription_request_response_format import TranscriptionRequestResponseFormat
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="TranscriptionRequest")


@_attrs_define
class TranscriptionRequest:
    """
    Attributes:
        file (File): Audio file to transcribe (e.g. mp3, wav, m4a, webm).
        model (str | Unset): Transcription model (provider-prefixed, e.g. `Systran/faster-whisper-large-v3`). Overrides
            the server default for this call. A bare model name is rejected by the gateway. Example: Systran/faster-whisper-
            large-v3.
        language (str | Unset): ISO-639-1 language hint. Omit to let the model auto-detect (supports mixed-language
            audio). Example: en.
        response_format (TranscriptionRequestResponseFormat | Unset): Output format. Defaults to `json`. Default:
            TranscriptionRequestResponseFormat.JSON.
    """

    file: File
    model: str | Unset = UNSET
    language: str | Unset = UNSET
    response_format: TranscriptionRequestResponseFormat | Unset = TranscriptionRequestResponseFormat.JSON
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        model = self.model

        language = self.language

        response_format: str | Unset = UNSET
        if not isinstance(self.response_format, Unset):
            response_format = self.response_format.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
            }
        )
        if model is not UNSET:
            field_dict["model"] = model
        if language is not UNSET:
            field_dict["language"] = language
        if response_format is not UNSET:
            field_dict["response_format"] = response_format

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file", self.file.to_tuple()))

        if not isinstance(self.model, Unset):
            files.append(("model", (None, str(self.model).encode(), "text/plain")))

        if not isinstance(self.language, Unset):
            files.append(("language", (None, str(self.language).encode(), "text/plain")))

        if not isinstance(self.response_format, Unset):
            files.append(("response_format", (None, str(self.response_format.value).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        model = d.pop("model", UNSET)

        language = d.pop("language", UNSET)

        _response_format = d.pop("response_format", UNSET)
        response_format: TranscriptionRequestResponseFormat | Unset
        if isinstance(_response_format, Unset):
            response_format = UNSET
        else:
            response_format = TranscriptionRequestResponseFormat(_response_format)

        transcription_request = cls(
            file=file,
            model=model,
            language=language,
            response_format=response_format,
        )

        transcription_request.additional_properties = d
        return transcription_request

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
