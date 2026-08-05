from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ocr_request_options import OcrRequestOptions


T = TypeVar("T", bound="OcrRequest")


@_attrs_define
class OcrRequest:
    """JSON alternative to the multipart upload for OCR.

    Attributes:
        file_base64 (str): Base64-encoded PDF bytes.
        file_sha256 (str | Unset): Optional caller-supplied SHA-256 of the file, used as the result-cache key.
        options (OcrRequestOptions | Unset):
    """

    file_base64: str
    file_sha256: str | Unset = UNSET
    options: OcrRequestOptions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_base64 = self.file_base64

        file_sha256 = self.file_sha256

        options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_base64": file_base64,
            }
        )
        if file_sha256 is not UNSET:
            field_dict["file_sha256"] = file_sha256
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ocr_request_options import OcrRequestOptions

        d = dict(src_dict)
        file_base64 = d.pop("file_base64")

        file_sha256 = d.pop("file_sha256", UNSET)

        _options = d.pop("options", UNSET)
        options: OcrRequestOptions | Unset
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = OcrRequestOptions.from_dict(_options)

        ocr_request = cls(
            file_base64=file_base64,
            file_sha256=file_sha256,
            options=options,
        )

        ocr_request.additional_properties = d
        return ocr_request

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
