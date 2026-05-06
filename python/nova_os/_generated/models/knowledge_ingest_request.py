from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.knowledge_ingest_request_metadata import KnowledgeIngestRequestMetadata


T = TypeVar("T", bound="KnowledgeIngestRequest")


@_attrs_define
class KnowledgeIngestRequest:
    """
    Attributes:
        content (str): Document text (already extracted)
        title (str | Unset):
        collection (str | Unset): Target collection; defaults to "default". Default: 'default'.
        metadata (KnowledgeIngestRequestMetadata | Unset):
    """

    content: str
    title: str | Unset = UNSET
    collection: str | Unset = "default"
    metadata: KnowledgeIngestRequestMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        title = self.title

        collection = self.collection

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if collection is not UNSET:
            field_dict["collection"] = collection
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.knowledge_ingest_request_metadata import KnowledgeIngestRequestMetadata

        d = dict(src_dict)
        content = d.pop("content")

        title = d.pop("title", UNSET)

        collection = d.pop("collection", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: KnowledgeIngestRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = KnowledgeIngestRequestMetadata.from_dict(_metadata)

        knowledge_ingest_request = cls(
            content=content,
            title=title,
            collection=collection,
            metadata=metadata,
        )

        knowledge_ingest_request.additional_properties = d
        return knowledge_ingest_request

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
