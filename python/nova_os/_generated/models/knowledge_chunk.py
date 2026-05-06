from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.knowledge_chunk_metadata import KnowledgeChunkMetadata


T = TypeVar("T", bound="KnowledgeChunk")


@_attrs_define
class KnowledgeChunk:
    """
    Attributes:
        content (str):
        collection (str | Unset):
        document_id (str | Unset):
        score (float | Unset):
        metadata (KnowledgeChunkMetadata | Unset):
    """

    content: str
    collection: str | Unset = UNSET
    document_id: str | Unset = UNSET
    score: float | Unset = UNSET
    metadata: KnowledgeChunkMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        collection = self.collection

        document_id = self.document_id

        score = self.score

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
        if collection is not UNSET:
            field_dict["collection"] = collection
        if document_id is not UNSET:
            field_dict["document_id"] = document_id
        if score is not UNSET:
            field_dict["score"] = score
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.knowledge_chunk_metadata import KnowledgeChunkMetadata

        d = dict(src_dict)
        content = d.pop("content")

        collection = d.pop("collection", UNSET)

        document_id = d.pop("document_id", UNSET)

        score = d.pop("score", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: KnowledgeChunkMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = KnowledgeChunkMetadata.from_dict(_metadata)

        knowledge_chunk = cls(
            content=content,
            collection=collection,
            document_id=document_id,
            score=score,
            metadata=metadata,
        )

        knowledge_chunk.additional_properties = d
        return knowledge_chunk

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
