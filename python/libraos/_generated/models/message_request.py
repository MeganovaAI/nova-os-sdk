from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.conversation_scope import ConversationScope
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
        model (str): Anthropic-compatible required selector. Desk clients normally set
            this to the selected employee/persona id and also send the same id
            as `metadata.agent_id`. A `<vendor>/<model>` value may act as an
            answer-model override when the deployment permits it.
        conversation_id (str | Unset): Stable conversation id. When present, the user and assistant turns
            are persisted to this conversation; an unknown id is auto-created.
        thread_id (str | Unset): AG-UI alias for `conversation_id`; prefer `conversation_id` in Desk clients.
        message_id (str | Unset): Client-generated idempotency key for this user turn. Reuse it only
            when retrying the same turn. The value is returned as the persisted
            user `ConversationMessage.id`.
        scope (ConversationScope | Unset): Personal assistant data or governed organization data.
        max_tokens (int | Unset):  Default: 4096.
        temperature (float | Unset):
        system (str | Unset):
        tools (list[ToolDefinition] | Unset):
        stream (bool | Unset):  Default: False.
        metadata (MessageRequestMetadata | Unset):
    """

    messages: list[Message]
    model: str
    conversation_id: str | Unset = UNSET
    thread_id: str | Unset = UNSET
    message_id: str | Unset = UNSET
    scope: ConversationScope | Unset = UNSET
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

        conversation_id = self.conversation_id

        thread_id = self.thread_id

        message_id = self.message_id

        scope: str | Unset = UNSET
        if not isinstance(self.scope, Unset):
            scope = self.scope.value

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
                "model": model,
            }
        )
        if conversation_id is not UNSET:
            field_dict["conversation_id"] = conversation_id
        if thread_id is not UNSET:
            field_dict["threadId"] = thread_id
        if message_id is not UNSET:
            field_dict["message_id"] = message_id
        if scope is not UNSET:
            field_dict["scope"] = scope
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

        model = d.pop("model")

        conversation_id = d.pop("conversation_id", UNSET)

        thread_id = d.pop("threadId", UNSET)

        message_id = d.pop("message_id", UNSET)

        _scope = d.pop("scope", UNSET)
        scope: ConversationScope | Unset
        if isinstance(_scope, Unset):
            scope = UNSET
        else:
            scope = ConversationScope(_scope)

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
            conversation_id=conversation_id,
            thread_id=thread_id,
            message_id=message_id,
            scope=scope,
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
