from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.conversation_metadata import ConversationMetadata


T = TypeVar("T", bound="Conversation")


@_attrs_define
class Conversation:
    """Per-user conversation summary.

    Attributes:
        id (str):
        agent_id (str):
        created_at (datetime.datetime):
        last_active_at (datetime.datetime):
        message_count (int):
        title (None | str | Unset): Null until set via rename.
        metadata (ConversationMetadata | Unset): App-owned metadata map. Omitted when empty.
    """

    id: str
    agent_id: str
    created_at: datetime.datetime
    last_active_at: datetime.datetime
    message_count: int
    title: None | str | Unset = UNSET
    metadata: ConversationMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        agent_id = self.agent_id

        created_at = self.created_at.isoformat()

        last_active_at = self.last_active_at.isoformat()

        message_count = self.message_count

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "agent_id": agent_id,
                "created_at": created_at,
                "last_active_at": last_active_at,
                "message_count": message_count,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.conversation_metadata import ConversationMetadata

        d = dict(src_dict)
        id = d.pop("id")

        agent_id = d.pop("agent_id")

        created_at = isoparse(d.pop("created_at"))

        last_active_at = isoparse(d.pop("last_active_at"))

        message_count = d.pop("message_count")

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: ConversationMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ConversationMetadata.from_dict(_metadata)

        conversation = cls(
            id=id,
            agent_id=agent_id,
            created_at=created_at,
            last_active_at=last_active_at,
            message_count=message_count,
            title=title,
            metadata=metadata,
        )

        conversation.additional_properties = d
        return conversation

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
