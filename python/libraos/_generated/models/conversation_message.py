from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConversationMessage")


@_attrs_define
class ConversationMessage:
    """
    Attributes:
        role (str): e.g. `user`, `assistant`.
        content (str):
        timestamp (datetime.datetime):
        id (str | Unset): Stable message id; user turns echo the request's `message_id`.
        seq (int | Unset): Server-assigned, 1-based monotonic ordering within the conversation.
    """

    role: str
    content: str
    timestamp: datetime.datetime
    id: str | Unset = UNSET
    seq: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role

        content = self.content

        timestamp = self.timestamp.isoformat()

        id = self.id

        seq = self.seq

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "content": content,
                "timestamp": timestamp,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if seq is not UNSET:
            field_dict["seq"] = seq

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = d.pop("role")

        content = d.pop("content")

        timestamp = isoparse(d.pop("timestamp"))

        id = d.pop("id", UNSET)

        seq = d.pop("seq", UNSET)

        conversation_message = cls(
            role=role,
            content=content,
            timestamp=timestamp,
            id=id,
            seq=seq,
        )

        conversation_message.additional_properties = d
        return conversation_message

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
