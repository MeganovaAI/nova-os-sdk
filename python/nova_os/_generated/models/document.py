from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_metadata import DocumentMetadata


T = TypeVar("T", bound="Document")


@_attrs_define
class Document:
    """
    Attributes:
        id (str):
        title (str): File name or extracted title
        path (str | Unset): Collection path (e.g. "contracts/2026")
        type_ (str | Unset): Document type — pdf
        size_bytes (int | Unset):
        collection_id (str | Unset): Parent collection (empty = root)
        metadata (DocumentMetadata | Unset): Mime, pages, author, etc.
        created_at (datetime.datetime | Unset):
    """

    id: str
    title: str
    path: str | Unset = UNSET
    type_: str | Unset = UNSET
    size_bytes: int | Unset = UNSET
    collection_id: str | Unset = UNSET
    metadata: DocumentMetadata | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        path = self.path

        type_ = self.type_

        size_bytes = self.size_bytes

        collection_id = self.collection_id

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
            }
        )
        if path is not UNSET:
            field_dict["path"] = path
        if type_ is not UNSET:
            field_dict["type"] = type_
        if size_bytes is not UNSET:
            field_dict["size_bytes"] = size_bytes
        if collection_id is not UNSET:
            field_dict["collection_id"] = collection_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_metadata import DocumentMetadata

        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        path = d.pop("path", UNSET)

        type_ = d.pop("type", UNSET)

        size_bytes = d.pop("size_bytes", UNSET)

        collection_id = d.pop("collection_id", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: DocumentMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DocumentMetadata.from_dict(_metadata)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        document = cls(
            id=id,
            title=title,
            path=path,
            type_=type_,
            size_bytes=size_bytes,
            collection_id=collection_id,
            metadata=metadata,
            created_at=created_at,
        )

        document.additional_properties = d
        return document

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
