from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_message import ChatMessage
    from ..models.native_chat_metadata import NativeChatMetadata


T = TypeVar("T", bound="NativeChatRequest")


@_attrs_define
class NativeChatRequest:
    """Native chat request. Supply either `message` (simple form) or `messages` (OpenAI array form).

    Attributes:
        message (str | Unset): Simple single-message form (mutually usable with `messages`).
        messages (list[ChatMessage] | Unset): OpenAI-style conversation history.
        conversation_id (str | Unset): Conversation/session identifier for continuity.
        session_id (str | Unset): Alternate session identifier.
        model (str | Unset): Optional model hint (server-side routing may override).
        stream (bool | Unset): When true the response is delivered as an SSE stream.
        fast (bool | Unset): Dispatch directly to the agent's primary skill, skipping planning. Returns 400 if the agent
            has no skills. No-op on single-skill agents.
        include_metadata (bool | Unset): When true, include additional diagnostic fields (e.g. tools_used, per-stage
            details) in the response.
        metadata (NativeChatMetadata | Unset): Opaque per-request metadata. Nova OS does not interpret arbitrary keys
            (they are threaded through tenant isolation and audit), but a few reserved keys control per-call behavior.
    """

    message: str | Unset = UNSET
    messages: list[ChatMessage] | Unset = UNSET
    conversation_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    model: str | Unset = UNSET
    stream: bool | Unset = UNSET
    fast: bool | Unset = UNSET
    include_metadata: bool | Unset = UNSET
    metadata: NativeChatMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        messages: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.messages, Unset):
            messages = []
            for messages_item_data in self.messages:
                messages_item = messages_item_data.to_dict()
                messages.append(messages_item)

        conversation_id = self.conversation_id

        session_id = self.session_id

        model = self.model

        stream = self.stream

        fast = self.fast

        include_metadata = self.include_metadata

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["message"] = message
        if messages is not UNSET:
            field_dict["messages"] = messages
        if conversation_id is not UNSET:
            field_dict["conversation_id"] = conversation_id
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if model is not UNSET:
            field_dict["model"] = model
        if stream is not UNSET:
            field_dict["stream"] = stream
        if fast is not UNSET:
            field_dict["fast"] = fast
        if include_metadata is not UNSET:
            field_dict["include_metadata"] = include_metadata
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_message import ChatMessage
        from ..models.native_chat_metadata import NativeChatMetadata

        d = dict(src_dict)
        message = d.pop("message", UNSET)

        _messages = d.pop("messages", UNSET)
        messages: list[ChatMessage] | Unset = UNSET
        if _messages is not UNSET:
            messages = []
            for messages_item_data in _messages:
                messages_item = ChatMessage.from_dict(messages_item_data)

                messages.append(messages_item)

        conversation_id = d.pop("conversation_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        model = d.pop("model", UNSET)

        stream = d.pop("stream", UNSET)

        fast = d.pop("fast", UNSET)

        include_metadata = d.pop("include_metadata", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: NativeChatMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = NativeChatMetadata.from_dict(_metadata)

        native_chat_request = cls(
            message=message,
            messages=messages,
            conversation_id=conversation_id,
            session_id=session_id,
            model=model,
            stream=stream,
            fast=fast,
            include_metadata=include_metadata,
            metadata=metadata,
        )

        native_chat_request.additional_properties = d
        return native_chat_request

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
