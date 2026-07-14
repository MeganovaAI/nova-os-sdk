from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.conversation_create_metadata import ConversationCreateMetadata


T = TypeVar("T", bound="ConversationCreate")


@_attrs_define
class ConversationCreate:
    """
    Attributes:
        id (str | Unset): Client-chosen id. Server generates one when omitted.
        agent_id (str | Unset):
        metadata (ConversationCreateMetadata | Unset): App-owned metadata. Reserved `nova_` key prefix rejected; capped
            at 4 KB serialized.
    """

    id: str | Unset = UNSET
    agent_id: str | Unset = UNSET
    metadata: ConversationCreateMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        agent_id = self.agent_id

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if agent_id is not UNSET:
            field_dict["agent_id"] = agent_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.conversation_create_metadata import ConversationCreateMetadata

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        agent_id = d.pop("agent_id", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: ConversationCreateMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ConversationCreateMetadata.from_dict(_metadata)

        conversation_create = cls(
            id=id,
            agent_id=agent_id,
            metadata=metadata,
        )

        conversation_create.additional_properties = d
        return conversation_create

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
