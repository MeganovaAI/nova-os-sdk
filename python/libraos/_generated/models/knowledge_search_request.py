from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="KnowledgeSearchRequest")


@_attrs_define
class KnowledgeSearchRequest:
    """
    Attributes:
        query (str):
        collection (str | Unset): Collection to search; empty = caller's own collection.
        top_k (int | Unset):  Default: 5.
        threshold (float | Unset):
    """

    query: str
    collection: str | Unset = UNSET
    top_k: int | Unset = 5
    threshold: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        collection = self.collection

        top_k = self.top_k

        threshold = self.threshold

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if collection is not UNSET:
            field_dict["collection"] = collection
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if threshold is not UNSET:
            field_dict["threshold"] = threshold

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        collection = d.pop("collection", UNSET)

        top_k = d.pop("top_k", UNSET)

        threshold = d.pop("threshold", UNSET)

        knowledge_search_request = cls(
            query=query,
            collection=collection,
            top_k=top_k,
            threshold=threshold,
        )

        knowledge_search_request.additional_properties = d
        return knowledge_search_request

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
