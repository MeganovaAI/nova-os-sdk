from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ExtractRequest")


@_attrs_define
class ExtractRequest:
    """JSON alternative to the multipart upload for text extraction.

    Attributes:
        file_base64 (str): Base64-encoded document bytes.
        filename (str): Filename with a supported extension, used to route the parser.
    """

    file_base64: str
    filename: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_base64 = self.file_base64

        filename = self.filename

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_base64": file_base64,
                "filename": filename,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_base64 = d.pop("file_base64")

        filename = d.pop("filename")

        extract_request = cls(
            file_base64=file_base64,
            filename=filename,
        )

        extract_request.additional_properties = d
        return extract_request

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
