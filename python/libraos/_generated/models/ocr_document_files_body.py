from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="OcrDocumentFilesBody")


@_attrs_define
class OcrDocumentFilesBody:
    """
    Attributes:
        file (File): The PDF to OCR.
        file_sha256 (str | Unset): Optional caller-supplied SHA-256 of the file, used as the result-cache key.
        max_pages (int | Unset): Optional cap on pages to process (0 or omitted = all pages).
    """

    file: File
    file_sha256: str | Unset = UNSET
    max_pages: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        file_sha256 = self.file_sha256

        max_pages = self.max_pages

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
            }
        )
        if file_sha256 is not UNSET:
            field_dict["file_sha256"] = file_sha256
        if max_pages is not UNSET:
            field_dict["max_pages"] = max_pages

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file", self.file.to_tuple()))

        if not isinstance(self.file_sha256, Unset):
            files.append(("file_sha256", (None, str(self.file_sha256).encode(), "text/plain")))

        if not isinstance(self.max_pages, Unset):
            files.append(("max_pages", (None, str(self.max_pages).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = File(payload=BytesIO(d.pop("file")))

        file_sha256 = d.pop("file_sha256", UNSET)

        max_pages = d.pop("max_pages", UNSET)

        ocr_document_files_body = cls(
            file=file,
            file_sha256=file_sha256,
            max_pages=max_pages,
        )

        ocr_document_files_body.additional_properties = d
        return ocr_document_files_body

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
