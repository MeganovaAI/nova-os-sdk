from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.text_block_type import TextBlockType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.citation import Citation


T = TypeVar("T", bound="TextBlock")


@_attrs_define
class TextBlock:
    """
    Attributes:
        type_ (TextBlockType):
        text (str):
        citations (list[Citation] | Unset): Present only when the answer contains structured citations.
    """

    type_: TextBlockType
    text: str
    citations: list[Citation] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        text = self.text

        citations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.citations, Unset):
            citations = []
            for citations_item_data in self.citations:
                citations_item = citations_item_data.to_dict()
                citations.append(citations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "text": text,
            }
        )
        if citations is not UNSET:
            field_dict["citations"] = citations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.citation import Citation

        d = dict(src_dict)
        type_ = TextBlockType(d.pop("type"))

        text = d.pop("text")

        _citations = d.pop("citations", UNSET)
        citations: list[Citation] | Unset = UNSET
        if _citations is not UNSET:
            citations = []
            for citations_item_data in _citations:
                citations_item = Citation.from_dict(citations_item_data)

                citations.append(citations_item)

        text_block = cls(
            type_=type_,
            text=text,
            citations=citations,
        )

        text_block.additional_properties = d
        return text_block

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
