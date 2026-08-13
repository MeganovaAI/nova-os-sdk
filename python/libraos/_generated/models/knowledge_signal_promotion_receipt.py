from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="KnowledgeSignalPromotionReceipt")


@_attrs_define
class KnowledgeSignalPromotionReceipt:
    """
    Attributes:
        id (str):
        signal_id (str):
        tenant (str):
        knowledge_document_id (str):
        collection (str):
        audience (str):
        actor (str):
        published_at (datetime.datetime):
        source_chunk_id (str | Unset):
    """

    id: str
    signal_id: str
    tenant: str
    knowledge_document_id: str
    collection: str
    audience: str
    actor: str
    published_at: datetime.datetime
    source_chunk_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        signal_id = self.signal_id

        tenant = self.tenant

        knowledge_document_id = self.knowledge_document_id

        collection = self.collection

        audience = self.audience

        actor = self.actor

        published_at = self.published_at.isoformat()

        source_chunk_id = self.source_chunk_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "signal_id": signal_id,
                "tenant": tenant,
                "knowledge_document_id": knowledge_document_id,
                "collection": collection,
                "audience": audience,
                "actor": actor,
                "published_at": published_at,
            }
        )
        if source_chunk_id is not UNSET:
            field_dict["source_chunk_id"] = source_chunk_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        signal_id = d.pop("signal_id")

        tenant = d.pop("tenant")

        knowledge_document_id = d.pop("knowledge_document_id")

        collection = d.pop("collection")

        audience = d.pop("audience")

        actor = d.pop("actor")

        published_at = isoparse(d.pop("published_at"))

        source_chunk_id = d.pop("source_chunk_id", UNSET)

        knowledge_signal_promotion_receipt = cls(
            id=id,
            signal_id=signal_id,
            tenant=tenant,
            knowledge_document_id=knowledge_document_id,
            collection=collection,
            audience=audience,
            actor=actor,
            published_at=published_at,
            source_chunk_id=source_chunk_id,
        )

        knowledge_signal_promotion_receipt.additional_properties = d
        return knowledge_signal_promotion_receipt

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
