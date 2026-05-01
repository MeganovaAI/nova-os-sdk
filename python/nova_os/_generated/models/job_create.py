from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_create_metadata import JobCreateMetadata
    from ..models.message import Message
    from ..models.tool_definition import ToolDefinition


T = TypeVar("T", bound="JobCreate")


@_attrs_define
class JobCreate:
    """
    Attributes:
        agent_id (str):
        messages (list[Message]):
        model (str | Unset):
        tools (list[ToolDefinition] | Unset):
        metadata (JobCreateMetadata | Unset):
    """

    agent_id: str
    messages: list[Message]
    model: str | Unset = UNSET
    tools: list[ToolDefinition] | Unset = UNSET
    metadata: JobCreateMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent_id = self.agent_id

        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        model = self.model

        tools: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tools, Unset):
            tools = []
            for tools_item_data in self.tools:
                tools_item = tools_item_data.to_dict()
                tools.append(tools_item)

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent_id": agent_id,
                "messages": messages,
            }
        )
        if model is not UNSET:
            field_dict["model"] = model
        if tools is not UNSET:
            field_dict["tools"] = tools
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_create_metadata import JobCreateMetadata
        from ..models.message import Message
        from ..models.tool_definition import ToolDefinition

        d = dict(src_dict)
        agent_id = d.pop("agent_id")

        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = Message.from_dict(messages_item_data)

            messages.append(messages_item)

        model = d.pop("model", UNSET)

        _tools = d.pop("tools", UNSET)
        tools: list[ToolDefinition] | Unset = UNSET
        if _tools is not UNSET:
            tools = []
            for tools_item_data in _tools:
                tools_item = ToolDefinition.from_dict(tools_item_data)

                tools.append(tools_item)

        _metadata = d.pop("metadata", UNSET)
        metadata: JobCreateMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = JobCreateMetadata.from_dict(_metadata)

        job_create = cls(
            agent_id=agent_id,
            messages=messages,
            model=model,
            tools=tools,
            metadata=metadata,
        )

        job_create.additional_properties = d
        return job_create

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
