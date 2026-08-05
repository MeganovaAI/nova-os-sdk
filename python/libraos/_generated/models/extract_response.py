from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExtractResponse")


@_attrs_define
class ExtractResponse:
    """
    Attributes:
        text (str | Unset): The extracted plain text.
        title (str | Unset): Document title when the parser can detect one.
        doc_type (str | Unset): Detected document type (e.g. docx, xlsx, pdf, odt, csv, eml).
        char_count (int | Unset): Length of the extracted text in characters.
        elapsed_ms (int | Unset): Server-side processing time in milliseconds.
    """

    text: str | Unset = UNSET
    title: str | Unset = UNSET
    doc_type: str | Unset = UNSET
    char_count: int | Unset = UNSET
    elapsed_ms: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        title = self.title

        doc_type = self.doc_type

        char_count = self.char_count

        elapsed_ms = self.elapsed_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if text is not UNSET:
            field_dict["text"] = text
        if title is not UNSET:
            field_dict["title"] = title
        if doc_type is not UNSET:
            field_dict["doc_type"] = doc_type
        if char_count is not UNSET:
            field_dict["char_count"] = char_count
        if elapsed_ms is not UNSET:
            field_dict["elapsed_ms"] = elapsed_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        text = d.pop("text", UNSET)

        title = d.pop("title", UNSET)

        doc_type = d.pop("doc_type", UNSET)

        char_count = d.pop("char_count", UNSET)

        elapsed_ms = d.pop("elapsed_ms", UNSET)

        extract_response = cls(
            text=text,
            title=title,
            doc_type=doc_type,
            char_count=char_count,
            elapsed_ms=elapsed_ms,
        )

        extract_response.additional_properties = d
        return extract_response

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
