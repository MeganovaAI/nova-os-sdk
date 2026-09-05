from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_app_knowledge_body_metadata_filter import SearchAppKnowledgeBodyMetadataFilter


T = TypeVar("T", bound="SearchAppKnowledgeBody")


@_attrs_define
class SearchAppKnowledgeBody:
    """
    Attributes:
        query (str):
        collection (str | Unset):
        top_k (int | Unset):  Default: 5.
        threshold (float | Unset):
        metadata_filter (SearchAppKnowledgeBodyMetadataFilter | Unset):
        debug (bool | Unset):  Default: False.
    """

    query: str
    collection: str | Unset = UNSET
    top_k: int | Unset = 5
    threshold: float | Unset = UNSET
    metadata_filter: SearchAppKnowledgeBodyMetadataFilter | Unset = UNSET
    debug: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        collection = self.collection

        top_k = self.top_k

        threshold = self.threshold

        metadata_filter: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata_filter, Unset):
            metadata_filter = self.metadata_filter.to_dict()

        debug = self.debug

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
        if metadata_filter is not UNSET:
            field_dict["metadata_filter"] = metadata_filter
        if debug is not UNSET:
            field_dict["debug"] = debug

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_app_knowledge_body_metadata_filter import SearchAppKnowledgeBodyMetadataFilter

        d = dict(src_dict)
        query = d.pop("query")

        collection = d.pop("collection", UNSET)

        top_k = d.pop("top_k", UNSET)

        threshold = d.pop("threshold", UNSET)

        _metadata_filter = d.pop("metadata_filter", UNSET)
        metadata_filter: SearchAppKnowledgeBodyMetadataFilter | Unset
        if isinstance(_metadata_filter, Unset):
            metadata_filter = UNSET
        else:
            metadata_filter = SearchAppKnowledgeBodyMetadataFilter.from_dict(_metadata_filter)

        debug = d.pop("debug", UNSET)

        search_app_knowledge_body = cls(
            query=query,
            collection=collection,
            top_k=top_k,
            threshold=threshold,
            metadata_filter=metadata_filter,
            debug=debug,
        )

        search_app_knowledge_body.additional_properties = d
        return search_app_knowledge_body

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
