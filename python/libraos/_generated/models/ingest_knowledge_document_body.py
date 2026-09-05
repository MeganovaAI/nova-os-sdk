from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ingest_knowledge_document_body_metadata import IngestKnowledgeDocumentBodyMetadata


T = TypeVar("T", bound="IngestKnowledgeDocumentBody")


@_attrs_define
class IngestKnowledgeDocumentBody:
    """
    Attributes:
        content (str):
        id (str | Unset):
        source (str | Unset):
        filename (str | Unset):
        name (str | Unset):
        collection (str | Unset):  Default: 'default'.
        collection_id (str | Unset):
        metadata (IngestKnowledgeDocumentBodyMetadata | Unset):
    """

    content: str
    id: str | Unset = UNSET
    source: str | Unset = UNSET
    filename: str | Unset = UNSET
    name: str | Unset = UNSET
    collection: str | Unset = "default"
    collection_id: str | Unset = UNSET
    metadata: IngestKnowledgeDocumentBodyMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        id = self.id

        source = self.source

        filename = self.filename

        name = self.name

        collection = self.collection

        collection_id = self.collection_id

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
        if id is not UNSET:
            field_dict["id"] = id
        if source is not UNSET:
            field_dict["source"] = source
        if filename is not UNSET:
            field_dict["filename"] = filename
        if name is not UNSET:
            field_dict["name"] = name
        if collection is not UNSET:
            field_dict["collection"] = collection
        if collection_id is not UNSET:
            field_dict["collection_id"] = collection_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ingest_knowledge_document_body_metadata import IngestKnowledgeDocumentBodyMetadata

        d = dict(src_dict)
        content = d.pop("content")

        id = d.pop("id", UNSET)

        source = d.pop("source", UNSET)

        filename = d.pop("filename", UNSET)

        name = d.pop("name", UNSET)

        collection = d.pop("collection", UNSET)

        collection_id = d.pop("collection_id", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: IngestKnowledgeDocumentBodyMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = IngestKnowledgeDocumentBodyMetadata.from_dict(_metadata)

        ingest_knowledge_document_body = cls(
            content=content,
            id=id,
            source=source,
            filename=filename,
            name=name,
            collection=collection,
            collection_id=collection_id,
            metadata=metadata,
        )

        ingest_knowledge_document_body.additional_properties = d
        return ingest_knowledge_document_body

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
