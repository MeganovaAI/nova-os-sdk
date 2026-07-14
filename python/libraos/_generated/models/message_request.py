from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.message import Message
    from ..models.message_request_metadata import MessageRequestMetadata
    from ..models.tool_definition import ToolDefinition


T = TypeVar("T", bound="MessageRequest")


@_attrs_define
class MessageRequest:
    """
    Attributes:
        messages (list[Message]):
        model (str | Unset): Per-call override; matches Anthropic shape, also accepts <vendor>/<model>.
        max_tokens (int | Unset):  Default: 4096.
        temperature (float | Unset):
        system (str | Unset):
        tools (list[ToolDefinition] | Unset):
        stream (bool | Unset):  Default: False.
        metadata (MessageRequestMetadata | Unset):
    """

    messages: list[Message]
    model: str | Unset = UNSET
    max_tokens: int | Unset = 4096
    temperature: float | Unset = UNSET
    system: str | Unset = UNSET
    tools: list[ToolDefinition] | Unset = UNSET
    stream: bool | Unset = False
    metadata: MessageRequestMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        model = self.model

        max_tokens = self.max_tokens

        temperature = self.temperature

        system = self.system

        tools: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tools, Unset):
            tools = []
            for tools_item_data in self.tools:
                tools_item = tools_item_data.to_dict()
                tools.append(tools_item)

        stream = self.stream

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
            }
        )
        if model is not UNSET:
            field_dict["model"] = model
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if system is not UNSET:
            field_dict["system"] = system
        if tools is not UNSET:
            field_dict["tools"] = tools
        if stream is not UNSET:
            field_dict["stream"] = stream
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.message import Message
        from ..models.message_request_metadata import MessageRequestMetadata
        from ..models.tool_definition import ToolDefinition

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = Message.from_dict(messages_item_data)

            messages.append(messages_item)

        model = d.pop("model", UNSET)

        max_tokens = d.pop("max_tokens", UNSET)

        temperature = d.pop("temperature", UNSET)

        system = d.pop("system", UNSET)

        _tools = d.pop("tools", UNSET)
        tools: list[ToolDefinition] | Unset = UNSET
        if _tools is not UNSET:
            tools = []
            for tools_item_data in _tools:
                tools_item = ToolDefinition.from_dict(tools_item_data)

                tools.append(tools_item)

        stream = d.pop("stream", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: MessageRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = MessageRequestMetadata.from_dict(_metadata)

        message_request = cls(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            tools=tools,
            stream=stream,
            metadata=metadata,
        )

        message_request.additional_properties = d
        return message_request

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
