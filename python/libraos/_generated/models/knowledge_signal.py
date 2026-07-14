from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.knowledge_signal_status import KnowledgeSignalStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="KnowledgeSignal")


@_attrs_define
class KnowledgeSignal:
    """
    Attributes:
        id (str | Unset):
        tenant (str | Unset):
        app (str | Unset): Source application that captured the signal.
        employee_id (str | Unset): Persona associated with the signal.
        type_ (str | Unset): Signal type.
        fact_key (str | Unset): Normalised dedupe key identifying the same fact across signals.
        content (str | Unset): The captured fact text.
        source_chunk_id (str | Unset): Identifier of the source chunk the signal was derived from.
        status (KnowledgeSignalStatus | Unset):
        created_at (datetime.datetime | Unset):
        signature (str | Unset): Integrity signature over the signal contents.
    """

    id: str | Unset = UNSET
    tenant: str | Unset = UNSET
    app: str | Unset = UNSET
    employee_id: str | Unset = UNSET
    type_: str | Unset = UNSET
    fact_key: str | Unset = UNSET
    content: str | Unset = UNSET
    source_chunk_id: str | Unset = UNSET
    status: KnowledgeSignalStatus | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    signature: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tenant = self.tenant

        app = self.app

        employee_id = self.employee_id

        type_ = self.type_

        fact_key = self.fact_key

        content = self.content

        source_chunk_id = self.source_chunk_id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        signature = self.signature

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if tenant is not UNSET:
            field_dict["tenant"] = tenant
        if app is not UNSET:
            field_dict["app"] = app
        if employee_id is not UNSET:
            field_dict["employee_id"] = employee_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if fact_key is not UNSET:
            field_dict["fact_key"] = fact_key
        if content is not UNSET:
            field_dict["content"] = content
        if source_chunk_id is not UNSET:
            field_dict["source_chunk_id"] = source_chunk_id
        if status is not UNSET:
            field_dict["status"] = status
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if signature is not UNSET:
            field_dict["signature"] = signature

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        tenant = d.pop("tenant", UNSET)

        app = d.pop("app", UNSET)

        employee_id = d.pop("employee_id", UNSET)

        type_ = d.pop("type", UNSET)

        fact_key = d.pop("fact_key", UNSET)

        content = d.pop("content", UNSET)

        source_chunk_id = d.pop("source_chunk_id", UNSET)

        _status = d.pop("status", UNSET)
        status: KnowledgeSignalStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = KnowledgeSignalStatus(_status)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        signature = d.pop("signature", UNSET)

        knowledge_signal = cls(
            id=id,
            tenant=tenant,
            app=app,
            employee_id=employee_id,
            type_=type_,
            fact_key=fact_key,
            content=content,
            source_chunk_id=source_chunk_id,
            status=status,
            created_at=created_at,
            signature=signature,
        )

        knowledge_signal.additional_properties = d
        return knowledge_signal

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
