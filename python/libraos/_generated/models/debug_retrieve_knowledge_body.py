from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DebugRetrieveKnowledgeBody")


@_attrs_define
class DebugRetrieveKnowledgeBody:
    """
    Attributes:
        query (str):
        collections (list[str] | Unset):
        top_k (int | Unset):  Default: 10.
        skip_rerank (bool | Unset):
        skip_llm_filter (bool | Unset):
    """

    query: str
    collections: list[str] | Unset = UNSET
    top_k: int | Unset = 10
    skip_rerank: bool | Unset = UNSET
    skip_llm_filter: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        collections: list[str] | Unset = UNSET
        if not isinstance(self.collections, Unset):
            collections = self.collections

        top_k = self.top_k

        skip_rerank = self.skip_rerank

        skip_llm_filter = self.skip_llm_filter

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if collections is not UNSET:
            field_dict["collections"] = collections
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if skip_rerank is not UNSET:
            field_dict["skip_rerank"] = skip_rerank
        if skip_llm_filter is not UNSET:
            field_dict["skip_llm_filter"] = skip_llm_filter

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        collections = cast(list[str], d.pop("collections", UNSET))

        top_k = d.pop("top_k", UNSET)

        skip_rerank = d.pop("skip_rerank", UNSET)

        skip_llm_filter = d.pop("skip_llm_filter", UNSET)

        debug_retrieve_knowledge_body = cls(
            query=query,
            collections=collections,
            top_k=top_k,
            skip_rerank=skip_rerank,
            skip_llm_filter=skip_llm_filter,
        )

        debug_retrieve_knowledge_body.additional_properties = d
        return debug_retrieve_knowledge_body

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
