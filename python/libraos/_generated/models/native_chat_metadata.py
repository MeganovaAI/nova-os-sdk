from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.native_chat_metadata_brain import NativeChatMetadataBrain
from ..types import UNSET, Unset

T = TypeVar("T", bound="NativeChatMetadata")


@_attrs_define
class NativeChatMetadata:
    """Opaque per-request metadata. Nova OS does not interpret arbitrary keys (they are threaded through tenant isolation
    and audit), but a few reserved keys control per-call behavior.

        Attributes:
            stream_events (bool | Unset): When true (and streaming), emit granular orchestration events (tool_use /
                tool_result / text / thinking) over SSE.
            stream_thinking (bool | Unset): When true, include model reasoning as `thinking` SSE events. Independent of
                stream_events; default off.
            max_tokens (int | Unset): Per-call output-token cap for the answer, overriding the agent's configured limit.
                Must be > 0; clamped to 32768.
            brain (NativeChatMetadataBrain | Unset): Per-call planning override. One of `always` or `never`; controls
                whether the multi-step planner runs for this turn.
    """

    stream_events: bool | Unset = UNSET
    stream_thinking: bool | Unset = UNSET
    max_tokens: int | Unset = UNSET
    brain: NativeChatMetadataBrain | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stream_events = self.stream_events

        stream_thinking = self.stream_thinking

        max_tokens = self.max_tokens

        brain: str | Unset = UNSET
        if not isinstance(self.brain, Unset):
            brain = self.brain.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if stream_events is not UNSET:
            field_dict["stream_events"] = stream_events
        if stream_thinking is not UNSET:
            field_dict["stream_thinking"] = stream_thinking
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if brain is not UNSET:
            field_dict["brain"] = brain

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stream_events = d.pop("stream_events", UNSET)

        stream_thinking = d.pop("stream_thinking", UNSET)

        max_tokens = d.pop("max_tokens", UNSET)

        _brain = d.pop("brain", UNSET)
        brain: NativeChatMetadataBrain | Unset
        if isinstance(_brain, Unset):
            brain = UNSET
        else:
            brain = NativeChatMetadataBrain(_brain)

        native_chat_metadata = cls(
            stream_events=stream_events,
            stream_thinking=stream_thinking,
            max_tokens=max_tokens,
            brain=brain,
        )

        native_chat_metadata.additional_properties = d
        return native_chat_metadata

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
