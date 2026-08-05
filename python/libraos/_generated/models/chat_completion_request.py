from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_completion_request_metadata import ChatCompletionRequestMetadata
    from ..models.chat_message import ChatMessage


T = TypeVar("T", bound="ChatCompletionRequest")


@_attrs_define
class ChatCompletionRequest:
    """OpenAI-compatible chat completion request.

    Attributes:
        messages (list[ChatMessage]):
        model (str | Unset): Target model/agent id. When gateway mode is enabled, a value of the form
            `llm:<provider>/<model>` selects raw provider passthrough.
        stream (bool | Unset): When true the response is an SSE stream terminated by `[DONE]`.
        max_tokens (int | Unset): Output-token cap (folded into the per-call answer limit).
        max_completion_tokens (int | Unset): Newer OpenAI field for the output-token cap; preferred over max_tokens when
            both are set.
        temperature (float | Unset): Sampling temperature. Accepted for OpenAI-client compatibility; server-side routing
            controls the effective value on the agent path.
        metadata (ChatCompletionRequestMetadata | Unset): Nova OS extension channel for per-call fields (e.g. a per-call
            model override).
    """

    messages: list[ChatMessage]
    model: str | Unset = UNSET
    stream: bool | Unset = UNSET
    max_tokens: int | Unset = UNSET
    max_completion_tokens: int | Unset = UNSET
    temperature: float | Unset = UNSET
    metadata: ChatCompletionRequestMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        model = self.model

        stream = self.stream

        max_tokens = self.max_tokens

        max_completion_tokens = self.max_completion_tokens

        temperature = self.temperature

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
        if stream is not UNSET:
            field_dict["stream"] = stream
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if max_completion_tokens is not UNSET:
            field_dict["max_completion_tokens"] = max_completion_tokens
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_completion_request_metadata import ChatCompletionRequestMetadata
        from ..models.chat_message import ChatMessage

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = ChatMessage.from_dict(messages_item_data)

            messages.append(messages_item)

        model = d.pop("model", UNSET)

        stream = d.pop("stream", UNSET)

        max_tokens = d.pop("max_tokens", UNSET)

        max_completion_tokens = d.pop("max_completion_tokens", UNSET)

        temperature = d.pop("temperature", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: ChatCompletionRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ChatCompletionRequestMetadata.from_dict(_metadata)

        chat_completion_request = cls(
            messages=messages,
            model=model,
            stream=stream,
            max_tokens=max_tokens,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            metadata=metadata,
        )

        chat_completion_request.additional_properties = d
        return chat_completion_request

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
