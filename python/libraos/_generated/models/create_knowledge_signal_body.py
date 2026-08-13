from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateKnowledgeSignalBody")


@_attrs_define
class CreateKnowledgeSignalBody:
    """
    Attributes:
        fact_key (str):
        content (str):
        idempotency_key (str): Stable caller key; retries return the same pending signal.
        source_chunk_id (str | Unset):
        app (str | Unset):  Default: 'desk-knowledge-setup'.
    """

    fact_key: str
    content: str
    idempotency_key: str
    source_chunk_id: str | Unset = UNSET
    app: str | Unset = "desk-knowledge-setup"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fact_key = self.fact_key

        content = self.content

        idempotency_key = self.idempotency_key

        source_chunk_id = self.source_chunk_id

        app = self.app

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fact_key": fact_key,
                "content": content,
                "idempotency_key": idempotency_key,
            }
        )
        if source_chunk_id is not UNSET:
            field_dict["source_chunk_id"] = source_chunk_id
        if app is not UNSET:
            field_dict["app"] = app

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fact_key = d.pop("fact_key")

        content = d.pop("content")

        idempotency_key = d.pop("idempotency_key")

        source_chunk_id = d.pop("source_chunk_id", UNSET)

        app = d.pop("app", UNSET)

        create_knowledge_signal_body = cls(
            fact_key=fact_key,
            content=content,
            idempotency_key=idempotency_key,
            source_chunk_id=source_chunk_id,
            app=app,
        )

        create_knowledge_signal_body.additional_properties = d
        return create_knowledge_signal_body

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
