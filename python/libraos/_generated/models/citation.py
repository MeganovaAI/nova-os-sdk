from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.citation_cite_source import CitationCiteSource
from ..models.citation_type import CitationType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Citation")


@_attrs_define
class Citation:
    """Evidence attached to a response text block. Document citations use
    location fields; grounded web citations use `web_uri`/`web_title`.
    Fields that do not apply to the selected variant are omitted.

        Attributes:
            type_ (CitationType):
            cite_source (CitationCiteSource):
            cited_text (str | Unset):
            document_index (int | Unset):
            document_title (str | Unset):
            start_char_index (int | Unset):
            end_char_index (int | Unset):
            start_page_number (int | Unset):
            end_page_number (int | Unset):
            start_block_index (int | Unset):
            end_block_index (int | Unset):
            web_uri (str | Unset):
            web_title (str | Unset):
            confidence_score (float | Unset):
            chunk_index (int | Unset):
    """

    type_: CitationType
    cite_source: CitationCiteSource
    cited_text: str | Unset = UNSET
    document_index: int | Unset = UNSET
    document_title: str | Unset = UNSET
    start_char_index: int | Unset = UNSET
    end_char_index: int | Unset = UNSET
    start_page_number: int | Unset = UNSET
    end_page_number: int | Unset = UNSET
    start_block_index: int | Unset = UNSET
    end_block_index: int | Unset = UNSET
    web_uri: str | Unset = UNSET
    web_title: str | Unset = UNSET
    confidence_score: float | Unset = UNSET
    chunk_index: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        cite_source = self.cite_source.value

        cited_text = self.cited_text

        document_index = self.document_index

        document_title = self.document_title

        start_char_index = self.start_char_index

        end_char_index = self.end_char_index

        start_page_number = self.start_page_number

        end_page_number = self.end_page_number

        start_block_index = self.start_block_index

        end_block_index = self.end_block_index

        web_uri = self.web_uri

        web_title = self.web_title

        confidence_score = self.confidence_score

        chunk_index = self.chunk_index

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "cite_source": cite_source,
            }
        )
        if cited_text is not UNSET:
            field_dict["cited_text"] = cited_text
        if document_index is not UNSET:
            field_dict["document_index"] = document_index
        if document_title is not UNSET:
            field_dict["document_title"] = document_title
        if start_char_index is not UNSET:
            field_dict["start_char_index"] = start_char_index
        if end_char_index is not UNSET:
            field_dict["end_char_index"] = end_char_index
        if start_page_number is not UNSET:
            field_dict["start_page_number"] = start_page_number
        if end_page_number is not UNSET:
            field_dict["end_page_number"] = end_page_number
        if start_block_index is not UNSET:
            field_dict["start_block_index"] = start_block_index
        if end_block_index is not UNSET:
            field_dict["end_block_index"] = end_block_index
        if web_uri is not UNSET:
            field_dict["web_uri"] = web_uri
        if web_title is not UNSET:
            field_dict["web_title"] = web_title
        if confidence_score is not UNSET:
            field_dict["confidence_score"] = confidence_score
        if chunk_index is not UNSET:
            field_dict["chunk_index"] = chunk_index

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = CitationType(d.pop("type"))

        cite_source = CitationCiteSource(d.pop("cite_source"))

        cited_text = d.pop("cited_text", UNSET)

        document_index = d.pop("document_index", UNSET)

        document_title = d.pop("document_title", UNSET)

        start_char_index = d.pop("start_char_index", UNSET)

        end_char_index = d.pop("end_char_index", UNSET)

        start_page_number = d.pop("start_page_number", UNSET)

        end_page_number = d.pop("end_page_number", UNSET)

        start_block_index = d.pop("start_block_index", UNSET)

        end_block_index = d.pop("end_block_index", UNSET)

        web_uri = d.pop("web_uri", UNSET)

        web_title = d.pop("web_title", UNSET)

        confidence_score = d.pop("confidence_score", UNSET)

        chunk_index = d.pop("chunk_index", UNSET)

        citation = cls(
            type_=type_,
            cite_source=cite_source,
            cited_text=cited_text,
            document_index=document_index,
            document_title=document_title,
            start_char_index=start_char_index,
            end_char_index=end_char_index,
            start_page_number=start_page_number,
            end_page_number=end_page_number,
            start_block_index=start_block_index,
            end_block_index=end_block_index,
            web_uri=web_uri,
            web_title=web_title,
            confidence_score=confidence_score,
            chunk_index=chunk_index,
        )

        citation.additional_properties = d
        return citation

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
